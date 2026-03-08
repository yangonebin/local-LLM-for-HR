import json
import re
from collections import defaultdict
from pathlib import Path
import sentencepiece as spm


class KoreanTokenizer:
    """
    실제 학습/추론에 사용하는 SentencePiece 기반 토크나이저.
    BPETokenizer는 알고리즘 이해용으로 남겨두고,
    이 클래스를 실제 파이프라인에서 사용합니다.
    """
    PAD_ID = 0
    UNK_ID = 1
    BOS_ID = 2
    EOS_ID = 3

    def __init__(self):
        self.sp = None

    def train(self, input_file, model_prefix="tokenizer/saved/spm", vocab_size=32000):
        Path(model_prefix).parent.mkdir(parents=True, exist_ok=True)
        print(f"SentencePiece 학습 시작: {input_file}")
        spm.SentencePieceTrainer.train(
            input=input_file,
            model_prefix=model_prefix,
            vocab_size=vocab_size,
            character_coverage=0.9995,   # 한국어 전체 커버
            model_type='bpe',
            pad_id=self.PAD_ID,
            unk_id=self.UNK_ID,
            bos_id=self.BOS_ID,
            eos_id=self.EOS_ID,
            pad_piece='[PAD]',
            unk_piece='[UNK]',
            bos_piece='[BOS]',
            eos_piece='[EOS]',
        )
        self.load(model_prefix + ".model")
        print(f"학습 완료. vocab size: {vocab_size}")

    def load(self, model_path):
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(model_path)
        print(f"토크나이저 로딩 완료: {model_path}")

    def encode(self, text):
        return [self.BOS_ID] + self.sp.encode(text) + [self.EOS_ID]

    def decode(self, ids):
        # BOS/EOS 제거 후 디코딩
        ids = [i for i in ids if i not in (self.BOS_ID, self.EOS_ID, self.PAD_ID)]
        return self.sp.decode(ids)

    @property
    def vocab_size(self):
        return self.sp.get_piece_size()





class BPETokenizer:
    def __init__(self):
        self.vocab = {}         # 토큰 → ID
        self.id_to_token = {}   # ID → 토큰
        self.merges = {}        # (a, b) → 합쳐진 토큰

        # 특수 토큰
        self.PAD = "[PAD]"
        self.UNK = "[UNK]"
        self.BOS = "[BOS]"
        self.EOS = "[EOS]"

    def _get_vocab_from_text(self, texts):
        """텍스트에서 단어별 글자 시퀀스 빈도 계산"""
        word_freq = defaultdict(int)
        for text in texts:
            for word in text.strip().split():
                # 단어를 글자 단위로 분리 + 끝에 </w> 표시
                word_freq[" ".join(list(word)) + " </w>"] += 1
        return word_freq

    def _get_pairs(self, vocab):
        """인접한 심볼 쌍의 빈도 계산"""
        pairs = defaultdict(int)
        for word, freq in vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs

    def _merge_vocab(self, pair, vocab):
        """가장 빈도 높은 쌍을 합치기"""
        new_vocab = {}
        bigram = " ".join(pair)
        replacement = "".join(pair)
        for word in vocab:
            new_word = word.replace(bigram, replacement)
            new_vocab[new_word] = vocab[word]
        return new_vocab

    def train(self, texts, vocab_size=32000, verbose=True):
        """BPE 학습"""
        # 특수 토큰 먼저 추가
        special_tokens = [self.PAD, self.UNK, self.BOS, self.EOS]
        for i, tok in enumerate(special_tokens):
            self.vocab[tok] = i
            self.id_to_token[i] = tok

        # 초기 글자 단위 vocab 구성
        word_freq = self._get_vocab_from_text(texts)

        # 초기 글자들을 vocab에 추가
        chars = set()
        for word in word_freq:
            for char in word.split():
                chars.add(char)

        for char in sorted(chars):
            if char not in self.vocab:
                idx = len(self.vocab)
                self.vocab[char] = idx
                self.id_to_token[idx] = char

        # BPE merge 반복
        num_merges = vocab_size - len(self.vocab)
        for i in range(num_merges):
            pairs = self._get_pairs(word_freq)
            if not pairs:
                break

            best_pair = max(pairs, key=pairs.get)
            word_freq = self._merge_vocab(best_pair, word_freq)

            merged = "".join(best_pair)
            self.merges[best_pair] = merged

            if merged not in self.vocab:
                idx = len(self.vocab)
                self.vocab[merged] = idx
                self.id_to_token[idx] = merged

            if verbose and i % 1000 == 0:
                print(f"merge {i}/{num_merges}, vocab size: {len(self.vocab)}")

        print(f"학습 완료. 최종 vocab size: {len(self.vocab)}")

    def _tokenize_word(self, word):
        """단어 하나를 BPE 토큰으로 분리"""
        symbols = list(word) + ["</w>"]

        while True:
            pairs = [(symbols[i], symbols[i+1]) for i in range(len(symbols)-1)]
            mergeable = [(p, self.merges[p]) for p in pairs if p in self.merges]
            if not mergeable:
                break
            # 가장 먼저 학습된 merge 적용
            best = min(mergeable, key=lambda x: list(self.merges.keys()).index(x[0]))
            a, b = best[0]
            new_symbols = []
            i = 0
            while i < len(symbols):
                if i < len(symbols)-1 and symbols[i] == a and symbols[i+1] == b:
                    new_symbols.append(a + b)
                    i += 2
                else:
                    new_symbols.append(symbols[i])
                    i += 1
            symbols = new_symbols

        return symbols

    def encode(self, text):
        """텍스트 → 토큰 ID 리스트"""
        ids = [self.vocab[self.BOS]]
        for word in text.strip().split():
            tokens = self._tokenize_word(word)
            for tok in tokens:
                ids.append(self.vocab.get(tok, self.vocab[self.UNK]))
        ids.append(self.vocab[self.EOS])
        return ids

    def decode(self, ids):
        """토큰 ID 리스트 → 텍스트"""
        tokens = [self.id_to_token.get(i, self.UNK) for i in ids]
        text = "".join(tokens)
        text = text.replace("</w>", " ").replace(self.BOS, "").replace(self.EOS, "")
        return text.strip()

    def save(self, path):
        """토크나이저 저장"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "vocab.json", "w", encoding="utf-8") as f:
            json.dump(self.vocab, f, ensure_ascii=False, indent=2)
        merges_list = {f"{k[0]} {k[1]}": v for k, v in self.merges.items()}
        with open(path / "merges.json", "w", encoding="utf-8") as f:
            json.dump(merges_list, f, ensure_ascii=False, indent=2)
        print(f"토크나이저 저장 완료: {path}")

    def load(self, path):
        """토크나이저 불러오기"""
        path = Path(path)
        with open(path / "vocab.json", "r", encoding="utf-8") as f:
            self.vocab = json.load(f)
        self.id_to_token = {v: k for k, v in self.vocab.items()}
        with open(path / "merges.json", "r", encoding="utf-8") as f:
            merges_raw = json.load(f)
        self.merges = {tuple(k.split(" ")): v for k, v in merges_raw.items()}
        print(f"토크나이저 불러오기 완료. vocab size: {len(self.vocab)}")
