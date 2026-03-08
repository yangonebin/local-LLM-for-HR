"""
데이터 준비 스크립트

구성:
  - 일반 한국어 70%: 나무위키
  - 법률 도메인 30%: 한국어 위키피디아 (법률 키워드 필터링)

출력:
  - data/tokenizer_train.txt  (토크나이저 학습용, 1만 문서)
  - data/train.txt            (모델 학습용, 전체)
"""

from datasets import load_dataset
from pathlib import Path
import re

Path("data").mkdir(exist_ok=True)

# 법률 관련 키워드
LEGAL_KEYWORDS = [
    "법", "법률", "조항", "근로", "노동", "임금", "해고", "계약",
    "판례", "판결", "법원", "소송", "민법", "형법", "헌법",
    "노동조합", "퇴직금", "연차", "휴가", "사회보험", "산재",
    "고용", "취업규칙", "징계", "해직", "복직", "부당해고"
]

def is_legal(text):
    """법률 관련 문서 여부 판단"""
    count = sum(1 for kw in LEGAL_KEYWORDS if kw in text)
    return count >= 3

def clean_text(text):
    """텍스트 정제"""
    # 너무 짧은 문서 제거
    if len(text) < 100:
        return None
    # 과도한 특수문자 제거
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\'\"\(\)\[\]\{\}\/\\\-\+\=\<\>\@\#\$\%\^\&\*]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) >= 100 else None


print("=" * 50)
print("1단계: 나무위키 로딩 (일반 한국어 70%)")
print("=" * 50)

namuwiki = load_dataset('heegyu/namuwiki-extracted', split='train')
print(f"나무위키 총 문서: {len(namuwiki):,}")

# 나무위키에서 20만 문서 샘플링
general_texts = []
for item in namuwiki:
    text = clean_text(item.get('text', ''))
    if text:
        general_texts.append(text)
    if len(general_texts) >= 200000:
        break

print(f"나무위키 정제 후: {len(general_texts):,}")


print("\n" + "=" * 50)
print("2단계: 한국어 위키피디아 로딩 (법률 도메인 30%)")
print("=" * 50)

wiki = load_dataset('wikimedia/wikipedia', '20231101.ko', split='train')
print(f"한국어 위키피디아 총 문서: {len(wiki):,}")

# 법률 키워드로 필터링
legal_texts = []
all_wiki_texts = []

for item in wiki:
    text = clean_text(item.get('text', ''))
    if not text:
        continue
    if is_legal(text):
        legal_texts.append(text)
    else:
        all_wiki_texts.append(text)

print(f"법률 관련 위키 문서: {len(legal_texts):,}")
print(f"일반 위키 문서: {len(all_wiki_texts):,}")

# 비율 맞추기 (일반:법률 = 70:30)
total_general = len(general_texts)
target_legal = int(total_general * 0.3 / 0.7)
legal_texts = legal_texts[:target_legal]

print(f"\n최종 구성:")
print(f"  일반 한국어 (나무위키): {len(general_texts):,}")
print(f"  법률 도메인 (위키):     {len(legal_texts):,}")
print(f"  합계:                  {len(general_texts) + len(legal_texts):,}")


print("\n" + "=" * 50)
print("3단계: 파일 저장")
print("=" * 50)

all_texts = general_texts + legal_texts

# 토크나이저 학습용 (1만 문서)
with open("data/tokenizer_train.txt", "w", encoding="utf-8") as f:
    for text in all_texts[:10000]:
        f.write(text + "\n")
print(f"토크나이저 학습 데이터 저장: data/tokenizer_train.txt (10,000 문서)")

# 모델 학습용 (전체)
with open("data/train.txt", "w", encoding="utf-8") as f:
    for text in all_texts:
        f.write(text + "\n")
print(f"모델 학습 데이터 저장: data/train.txt ({len(all_texts):,} 문서)")

import os
size_mb = os.path.getsize("data/train.txt") / (1024 * 1024)
print(f"train.txt 크기: {size_mb:.1f} MB")
print("\n데이터 준비 완료!")
