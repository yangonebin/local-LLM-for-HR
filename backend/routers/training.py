import json
import redis
from fastapi import APIRouter, HTTPException
from schemas import TrainingConfig, TrainingStatus
from celery_app import celery_app
from routers.datasets import DATASET_MAP

router = APIRouter(prefix="/api/training", tags=["training"])

r = redis.Redis(host="redis", port=6379, db=2, decode_responses=True)
TRAINING_STATE_KEY = "training:state"
CURRENT_TASK_KEY = "training:task_id"


def _get_state() -> dict:
    raw = r.get(TRAINING_STATE_KEY)
    if raw:
        return json.loads(raw)
    return {"status": "idle", "epoch": 0, "step": 0, "loss": 0.0,
            "progress": 0.0, "message": ""}


@router.post("/start", response_model=TrainingStatus)
def start_training(config: TrainingConfig):
    state = _get_state()
    if state.get("status") == "running":
        raise HTTPException(status_code=400, detail="이미 학습이 진행 중입니다.")

    dataset_paths = []
    for ds_id in config.dataset_ids:
        ds = DATASET_MAP.get(ds_id)
        if ds:
            # 실제 경로 매핑 (Docker 볼륨 마운트 기준)
            dataset_paths.append(f"/app/data/datasets/{ds_id}/train.bin")

    # 기존 데이터가 없으면 현재 train.bin 사용
    if not dataset_paths:
        dataset_paths = ["/app/llm/data/train.bin"]

    r.delete("training:stop")
    task = celery_app.send_task(
        "tasks.run_training",
        args=[config.model_dump(), dataset_paths],
    )
    r.set(CURRENT_TASK_KEY, task.id)
    r.set(TRAINING_STATE_KEY, json.dumps({
        "status": "running", "epoch": 0, "step": 0, "loss": 0.0,
        "progress": 0.0, "message": "학습 준비 중..."
    }))

    return TrainingStatus(task_id=task.id, status="running",
                          message="학습을 시작합니다.")


@router.get("/status", response_model=TrainingStatus)
def get_status():
    state = _get_state()
    task_id = r.get(CURRENT_TASK_KEY)
    return TrainingStatus(
        task_id=task_id,
        status=state.get("status", "idle"),
        epoch=state.get("epoch", 0),
        total_epochs=state.get("total_epochs", 0),
        step=state.get("step", 0),
        loss=state.get("loss", 0.0),
        progress=state.get("progress", 0.0),
        elapsed_seconds=state.get("elapsed_seconds", 0.0),
        message=state.get("message", ""),
    )


@router.post("/stop", response_model=TrainingStatus)
def stop_training():
    state = _get_state()
    if state.get("status") != "running":
        raise HTTPException(status_code=400, detail="실행 중인 학습이 없습니다.")
    r.set("training:stop", "1")
    return TrainingStatus(task_id=r.get(CURRENT_TASK_KEY),
                          status="stopping", message="중지 신호를 보냈습니다.")
