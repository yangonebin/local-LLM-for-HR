import io
import json
import zipfile
import shutil
import redis
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from celery_app import celery_app

router = APIRouter(prefix="/api/models", tags=["models"])
r = redis.Redis(host="redis", port=6379, db=2, decode_responses=True)

MODEL_STATE_KEY = "model:selected"
PRETRAINED_DIR = Path("/app/pretrained")
LLM_DIR = Path("/app/llm")

PRETRAINED_MODELS = [
    {
        "id": "exaone-3.5-7.8b",
        "name": "EXAONE 3.5 7.8B",
        "description": "LG AI Research 개발. 한국어 특화 최강 모델. HR 업무 최적.",
        "hf_repo": "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct",
        "size_gb": 16.0,
        "params": "7.8B",
        "language": "한국어 특화",
        "recommended": True,
    },
    {
        "id": "qwen3-8b",
        "name": "Qwen3 8B",
        "description": "Alibaba 개발. 강력한 다국어 모델. 한국어 성능 우수.",
        "hf_repo": "Qwen/Qwen3-8B",
        "size_gb": 16.5,
        "params": "8B",
        "language": "다국어",
        "recommended": False,
    },
    {
        "id": "llama-3.1-8b",
        "name": "LLaMA 3.1 8B",
        "description": "Meta 개발. 범용 오픈소스 강자. 영어 중심이나 한국어도 준수.",
        "hf_repo": "meta-llama/Llama-3.1-8B-Instruct",
        "size_gb": 16.0,
        "params": "8B",
        "language": "영어 중심",
        "recommended": False,
    },
    {
        "id": "exaone-3.5-2.4b",
        "name": "EXAONE 3.5 2.4B",
        "description": "EXAONE 경량 버전. GPU 메모리가 부족한 환경에 적합.",
        "hf_repo": "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",
        "size_gb": 5.0,
        "params": "2.4B",
        "language": "한국어 특화",
        "recommended": False,
    },
]

MODEL_MAP = {m["id"]: m for m in PRETRAINED_MODELS}


@router.get("/pretrained")
def list_pretrained():
    result = []
    for m in PRETRAINED_MODELS:
        dl_raw = r.get(f"model:download:{m['id']}")
        dl_state = json.loads(dl_raw) if dl_raw else {"status": "idle", "progress": 0.0}
        ready = (PRETRAINED_DIR / m["id"] / "config.json").exists()
        result.append({**m, "download_status": dl_state, "ready": ready})
    return result


@router.get("/selected")
def get_selected():
    raw = r.get(MODEL_STATE_KEY)
    if raw:
        return json.loads(raw)
    return {"track": None, "model_id": None}


@router.post("/select/custom")
def select_custom():
    """트랙 A: 직접 설계 선택"""
    r.set(MODEL_STATE_KEY, json.dumps({"track": "custom", "model_id": "custom"}))
    return {"track": "custom", "message": "직접 설계 모드로 설정되었습니다."}


@router.post("/select/pretrained/{model_id}")
def select_pretrained(model_id: str):
    """트랙 B: 사전학습 모델 선택"""
    if model_id not in MODEL_MAP:
        raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")
    ready = (PRETRAINED_DIR / model_id / "config.json").exists()
    if not ready:
        raise HTTPException(status_code=400, detail="모델을 먼저 다운로드해주세요.")
    r.set(MODEL_STATE_KEY, json.dumps({"track": "pretrained", "model_id": model_id}))
    return {"track": "pretrained", "model_id": model_id}


@router.post("/download/{model_id}")
def start_model_download(model_id: str):
    if model_id not in MODEL_MAP:
        raise HTTPException(status_code=404, detail="모델을 찾을 수 없습니다.")

    dl_raw = r.get(f"model:download:{model_id}")
    if dl_raw:
        state = json.loads(dl_raw)
        if state.get("status") == "running":
            raise HTTPException(status_code=400, detail="이미 다운로드 중입니다.")

    if (PRETRAINED_DIR / model_id / "config.json").exists():
        return {"status": "ready", "message": "이미 다운로드되어 있습니다."}

    celery_app.send_task("tasks.download_model", args=[model_id, MODEL_MAP[model_id]["hf_repo"]])
    return {"status": "started", "message": "다운로드를 시작합니다."}


@router.get("/download/{model_id}/status")
def get_model_download_status(model_id: str):
    if (PRETRAINED_DIR / model_id / "config.json").exists():
        return {"status": "ready", "progress": 1.0, "message": "사용 가능"}
    raw = r.get(f"model:download:{model_id}")
    if raw:
        return json.loads(raw)
    return {"status": "idle", "progress": 0.0, "message": ""}


@router.get("/custom/download")
def download_custom_model():
    """트랙 A: 현재 모델 코드를 ZIP으로 다운로드"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in LLM_DIR.rglob("*.py"):
            if "__pycache__" not in str(f):
                zf.write(f, f.relative_to(LLM_DIR.parent))
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=hr_llm_model.zip"},
    )


@router.post("/custom/upload")
async def upload_custom_model(file: UploadFile = File(...)):
    """트랙 A: 수정한 모델 코드 ZIP 업로드"""
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="ZIP 파일만 업로드 가능합니다.")

    content = await file.read()
    buf = io.BytesIO(content)

    # 기존 코드 백업
    backup_dir = LLM_DIR.parent / "llm_backup"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    shutil.copytree(LLM_DIR, backup_dir)

    # 업로드된 ZIP 적용
    with zipfile.ZipFile(buf) as zf:
        for member in zf.namelist():
            if member.endswith(".py") and ".." not in member:
                target = LLM_DIR.parent / member
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(target, "wb") as dst:
                    dst.write(src.read())

    r.set(MODEL_STATE_KEY, json.dumps({"track": "custom", "model_id": "custom"}))
    return {"message": "모델 코드가 업로드되었습니다."}
