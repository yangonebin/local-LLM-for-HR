"""
각 데이터셋 다운로드 + 텍스트 추출 서비스
"""
import os
import bz2
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable

DATA_ROOT = Path("/app/data/datasets")


def get_dataset_dir(dataset_id: str) -> Path:
    d = DATA_ROOT / dataset_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── 공통 유틸 ──────────────────────────────────────────────────────

def stream_download(url: str, dest: Path, progress_cb: Callable[[float], None]):
    """URL에서 파일을 스트리밍으로 다운로드"""
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):  # 1MB
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                progress_cb(downloaded / total)


def text_to_bin(txt_path: Path, dataset_id: str):
    """train.txt → train.bin (토크나이저 적용)"""
    import sys
    sys.path.insert(0, "/app/llm")
    from data.dataset import preprocess
    from tokenizer.bpe import KoreanTokenizer

    tokenizer = KoreanTokenizer()
    tokenizer.load("/app/llm/tokenizer/saved/spm.model")

    out_prefix = str(txt_path.parent / "train")
    preprocess(str(txt_path), tokenizer, out_prefix)


# ── 위키피디아 한국어 ───────────────────────────────────────────────

def download_wikipedia_ko(progress_cb: Callable[[str, float], None]):
    d = get_dataset_dir("wikipedia_ko")
    dump_url = "https://dumps.wikimedia.org/kowiki/latest/kowiki-latest-pages-articles.xml.bz2"
    bz2_path = d / "dump.xml.bz2"
    txt_path = d / "train.txt"

    if not (d / "train.bin").exists():
        # 1. 다운로드
        progress_cb("위키피디아 덤프 다운로드 중...", 0.0)
        stream_download(dump_url, bz2_path, lambda p: progress_cb(f"다운로드 중... {p*100:.0f}%", p * 0.6))

        # 2. XML 파싱 → 텍스트 추출
        progress_cb("텍스트 추출 중...", 0.6)
        _parse_wiki_dump(bz2_path, txt_path)

        # 3. 토크나이저 → bin
        progress_cb("토크나이징 중...", 0.85)
        text_to_bin(txt_path, "wikipedia_ko")

        # 4. 정리
        bz2_path.unlink(missing_ok=True)

    progress_cb("완료", 1.0)


def _parse_wiki_dump(bz2_path: Path, out_path: Path):
    ns = "http://www.mediawiki.org/xml/DTD/mediawiki"
    with bz2.open(bz2_path, "rb") as f_in, open(out_path, "w", encoding="utf-8") as f_out:
        context = ET.iterparse(f_in, events=("end",))
        for event, elem in context:
            if elem.tag == f"{{{ns}}}text" and elem.text:
                text = elem.text.strip()
                # 리다이렉트, 짧은 문서 제외
                if not text.startswith("#넘겨주기") and len(text) > 200:
                    # 위키 마크업 기본 제거
                    lines = [l for l in text.splitlines()
                             if not l.startswith("[[파일:") and not l.startswith("[[File:")]
                    f_out.write("\n".join(lines) + "\n\n")
            elem.clear()


# ── 나무위키 ────────────────────────────────────────────────────────

def download_namuwiki(progress_cb: Callable[[str, float], None]):
    d = get_dataset_dir("namuwiki")
    # 나무위키 최신 덤프 (JSON 형식, 약 6GB)
    dump_url = "https://dump.namucdn.com/namuwiki/latest.json.bz2"
    bz2_path = d / "dump.json.bz2"
    txt_path = d / "train.txt"

    if not (d / "train.bin").exists():
        progress_cb("나무위키 덤프 다운로드 중...", 0.0)
        stream_download(dump_url, bz2_path, lambda p: progress_cb(f"다운로드 중... {p*100:.0f}%", p * 0.6))

        progress_cb("텍스트 추출 중...", 0.6)
        _parse_namuwiki_dump(bz2_path, txt_path)

        progress_cb("토크나이징 중...", 0.85)
        text_to_bin(txt_path, "namuwiki")

        bz2_path.unlink(missing_ok=True)

    progress_cb("완료", 1.0)


def _parse_namuwiki_dump(bz2_path: Path, out_path: Path):
    with bz2.open(bz2_path, "rt", encoding="utf-8") as f_in, \
         open(out_path, "w", encoding="utf-8") as f_out:
        for line in f_in:
            try:
                obj = json.loads(line)
                title = obj.get("title", "")
                text = obj.get("text", "")
                if text and len(text) > 100:
                    f_out.write(f"# {title}\n{text}\n\n")
            except json.JSONDecodeError:
                continue


# ── 국가법령정보센터 API ────────────────────────────────────────────

LAW_API_BASE = "https://www.law.go.kr/DRF"

# dataset_id → 법령 검색 키워드 목록
LAW_KEYWORDS: dict[str, list[str]] = {
    "labor_law":          ["근로기준법", "최저임금법", "산업안전보건법", "근로자퇴직급여"],
    "labor_union_law":    ["노동조합및노동관계조정법", "노사협의회법", "근로자참여"],
    "social_security_law":["국민연금법", "국민건강보험법", "고용보험법", "산업재해보상보험법"],
    "civil_law":          ["민법", "민사소송법", "상법"],
    "law_documents":      ["노동법", "근로", "임금", "해고", "휴가", "휴일"],
    "court_cases":        ["근로기준법위반", "부당해고", "임금체불", "직장내괴롭힘"],
    "employment_equality":["남녀고용평등법", "육아휴직", "직장내성희롱"],
    "privacy_law":        ["개인정보보호법"],
    "disability_law":     ["장애인고용촉진"],
    "foreign_worker_law": ["외국인근로자"],
    "hr_admin":           ["고용노동부", "행정해석", "질의회시"],
}


def download_law_dataset(dataset_id: str, api_key: str, progress_cb: Callable[[str, float], None]):
    d = get_dataset_dir(dataset_id)
    txt_path = d / "train.txt"

    if (d / "train.bin").exists():
        progress_cb("완료 (캐시)", 1.0)
        return

    keywords = LAW_KEYWORDS.get(dataset_id, [dataset_id])
    all_texts: list[str] = []

    for i, keyword in enumerate(keywords):
        progress_cb(f"법령 검색 중: {keyword}", i / len(keywords) * 0.7)
        texts = _fetch_law_texts(keyword, api_key)
        all_texts.extend(texts)

    if dataset_id == "court_cases":
        progress_cb("판례 검색 중...", 0.5)
        for keyword in keywords:
            texts = _fetch_precedent_texts(keyword, api_key)
            all_texts.extend(texts)

    progress_cb("텍스트 저장 중...", 0.8)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_texts))

    progress_cb("토크나이징 중...", 0.9)
    text_to_bin(txt_path, dataset_id)
    progress_cb("완료", 1.0)


def _fetch_law_texts(keyword: str, api_key: str) -> list[str]:
    """국가법령정보센터 법령 본문 수집"""
    texts = []
    try:
        # 법령 목록 검색
        list_url = f"{LAW_API_BASE}/lawSearch.do"
        params = {"OC": api_key, "target": "law", "type": "JSON",
                  "query": keyword, "display": 20}
        resp = requests.get(list_url, params=params, timeout=30)
        data = resp.json()

        laws = data.get("LawSearch", {}).get("law", [])
        if isinstance(laws, dict):
            laws = [laws]

        for law in laws[:10]:
            law_id = law.get("법령ID") or law.get("MST")
            if not law_id:
                continue
            # 법령 본문 가져오기
            text_url = f"{LAW_API_BASE}/lawService.do"
            text_params = {"OC": api_key, "target": "law", "type": "JSON", "ID": law_id}
            text_resp = requests.get(text_url, params=text_params, timeout=30)
            text_data = text_resp.json()

            law_name = law.get("법령명한글", keyword)
            articles = text_data.get("법령", {}).get("조문", {}).get("조문단위", [])
            if isinstance(articles, dict):
                articles = [articles]

            law_text = f"[{law_name}]\n"
            for article in articles:
                art_no = article.get("조문번호", "")
                art_content = article.get("조문내용", "")
                if art_content:
                    law_text += f"제{art_no}조 {art_content}\n"
            texts.append(law_text)

    except Exception as e:
        print(f"법령 수집 오류 ({keyword}): {e}")

    return texts


def _fetch_precedent_texts(keyword: str, api_key: str) -> list[str]:
    """국가법령정보센터 판례 수집"""
    texts = []
    try:
        url = f"{LAW_API_BASE}/lawSearch.do"
        params = {"OC": api_key, "target": "prec", "type": "JSON",
                  "query": keyword, "display": 20}
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()

        cases = data.get("PrecSearch", {}).get("prec", [])
        if isinstance(cases, dict):
            cases = [cases]

        for case in cases[:10]:
            case_id = case.get("판례일련번호")
            if not case_id:
                continue
            text_url = f"{LAW_API_BASE}/lawService.do"
            text_params = {"OC": api_key, "target": "prec", "type": "JSON", "ID": case_id}
            text_resp = requests.get(text_url, params=text_params, timeout=30)
            text_data = text_resp.json()

            prec = text_data.get("PrecService", {})
            case_name = prec.get("사건명", "")
            judgment = prec.get("판결요지", "")
            reason = prec.get("판결이유", "")
            if judgment or reason:
                texts.append(f"[판례: {case_name}]\n판결요지: {judgment}\n\n{reason}")

    except Exception as e:
        print(f"판례 수집 오류 ({keyword}): {e}")

    return texts


# ── 고용노동부 행정해석 ─────────────────────────────────────────────

def download_hr_admin(api_key: str, progress_cb: Callable[[str, float], None]):
    """고용노동부 행정해석(질의회시) 수집"""
    d = get_dataset_dir("hr_admin")
    txt_path = d / "train.txt"

    if (d / "train.bin").exists():
        progress_cb("완료 (캐시)", 1.0)
        return

    keywords = ["근로기준", "임금", "해고", "휴가", "육아휴직", "퇴직금", "4대보험"]
    all_texts = []

    for i, kw in enumerate(keywords):
        progress_cb(f"행정해석 수집 중: {kw}", i / len(keywords) * 0.8)
        texts = _fetch_law_texts(kw, api_key)
        all_texts.extend(texts)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_texts))

    progress_cb("토크나이징 중...", 0.9)
    text_to_bin(txt_path, "hr_admin")
    progress_cb("완료", 1.0)


# ── 통합 다운로드 함수 ─────────────────────────────────────────────

NEEDS_API_KEY = {
    "law_documents", "court_cases", "labor_law", "labor_union_law",
    "social_security_law", "civil_law", "employment_equality",
    "privacy_law", "disability_law", "foreign_worker_law", "hr_admin",
}

DIRECT_DOWNLOAD = {"wikipedia_ko", "namuwiki"}


def download_dataset(dataset_id: str, api_key: str | None,
                     progress_cb: Callable[[str, float], None]):
    if dataset_id == "wikipedia_ko":
        download_wikipedia_ko(progress_cb)
    elif dataset_id == "namuwiki":
        download_namuwiki(progress_cb)
    elif dataset_id == "hr_admin":
        if not api_key:
            raise ValueError("국가법령정보센터 API 키가 필요합니다.")
        download_hr_admin(api_key, progress_cb)
    elif dataset_id in NEEDS_API_KEY:
        if not api_key:
            raise ValueError("국가법령정보센터 API 키가 필요합니다.")
        download_law_dataset(dataset_id, api_key, progress_cb)
    else:
        raise ValueError(f"알 수 없는 데이터셋: {dataset_id}")


def is_ready(dataset_id: str) -> bool:
    """이미 전처리된 데이터가 있는지 확인"""
    return (DATA_ROOT / dataset_id / "train.bin").exists()
