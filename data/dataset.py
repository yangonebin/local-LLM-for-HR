import torch
import numpy as np
from torch.utils.data import Dataset
from pathlib import Path


def preprocess(file_path, tokenizer, out_path, max_docs=None, chunk_size=100000):
    """
    텍스트 파일을 토크나이징하여 binary 파일로 저장.
    메모리를 절약하기 위해 chunk_size 토큰마다 파일에 직접 씁니다.
    한 번만 실행하면 이후 빠르게 로딩 가능.
    """
    out_path = str(out_path) + ".bin"
    print(f"전처리 시작: {file_path} → {out_path}")

    total_tokens = 0
    buffer = []

    with open(out_path, "wb") as fout, open(file_path, "r", encoding="utf-8") as fin:
        for i, line in enumerate(fin):
            if max_docs and i >= max_docs:
                break
            line = line.strip()
            if not line:
                continue
            buffer.extend(tokenizer.sp.encode(line))
            total_tokens += len(buffer) - (len(buffer) - len(tokenizer.sp.encode(line)))

            # chunk_size 토큰마다 파일에 쓰고 버퍼 비우기
            if len(buffer) >= chunk_size:
                arr = np.array(buffer, dtype=np.uint16)
                arr.tofile(fout)
                total_tokens = (i + 1) * 0  # reset, recalculate below
                buffer = []

            if (i + 1) % 10000 == 0:
                print(f"  {i+1:,} 문서 처리 완료")

        # 남은 버퍼 저장
        if buffer:
            np.array(buffer, dtype=np.uint16).tofile(fout)

    # 전체 토큰 수 계산
    file_size = Path(out_path).stat().st_size
    total_tokens = file_size // 2  # uint16 = 2 bytes
    print(f"전처리 완료: {total_tokens:,} 토큰 → {out_path} ({file_size / 1024**3:.2f} GB)")
    return out_path


class TextDataset(Dataset):
    def __init__(self, bin_path, max_seq_len=1024):
        """
        전처리된 .bin 파일을 메모리맵으로 로딩 (메모리 효율적).
        """
        self.max_seq_len = max_seq_len
        self.data = np.memmap(bin_path, dtype=np.uint16, mode='r')
        self.n_samples = (len(self.data) - 1) // max_seq_len
        print(f"데이터 로딩: {bin_path} ({len(self.data):,} 토큰, {self.n_samples:,} 샘플)")

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        start = idx * self.max_seq_len
        chunk = torch.tensor(
            self.data[start: start + self.max_seq_len + 1].astype(np.int64)
        )
        x = chunk[:-1]
        y = chunk[1:]
        return x, y
