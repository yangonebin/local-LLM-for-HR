import json
import redis
from fastapi import APIRouter, HTTPException
from schemas import DatasetInfo, TrainingEstimate, TrainingConfig
from services.downloader import is_ready, NEEDS_API_KEY, DIRECT_DOWNLOAD
from celery_app import celery_app

router = APIRouter(prefix="/api/datasets", tags=["datasets"])
r = redis.Redis(host="redis", port=6379, db=2, decode_responses=True)

DATASETS: list[DatasetInfo] = [
    # 일반 지식
    DatasetInfo(id="namuwiki", name="나무위키",
        description="한국 최대 위키 백과사전. 일상 지식, 문화, 역사 전반 포함",
        estimated_tokens=3_000_000_000, size_gb=8.5, category="일반 지식", available=True),
    DatasetInfo(id="wikipedia_ko", name="한국어 위키피디아",
        description="위키피디아 한국어판. 신뢰도 높은 백과사전 데이터",
        estimated_tokens=500_000_000, size_gb=1.2, category="일반 지식", available=True),
    # 법률
    DatasetInfo(id="law_documents", name="법률 문서",
        description="국가법령정보센터 전체 현행법 전문",
        estimated_tokens=800_000_000, size_gb=2.1, category="법률", available=True),
    DatasetInfo(id="court_cases", name="판례",
        description="대법원 판례 전문. 민사·형사·행정 판례 포함",
        estimated_tokens=600_000_000, size_gb=1.8, category="법률", available=True),
    DatasetInfo(id="civil_law", name="민법",
        description="민법 전문 및 관련 판례. 계약, 불법행위, 채권 등",
        estimated_tokens=150_000_000, size_gb=0.4, category="법률", available=True),
    DatasetInfo(id="employment_equality", name="남녀고용평등법",
        description="육아휴직, 직장 내 성희롱, 모성보호 관련 법령",
        estimated_tokens=30_000_000, size_gb=0.08, category="법률", available=True),
    DatasetInfo(id="privacy_law", name="개인정보보호법",
        description="인사 데이터 처리 필수. 개인정보 수집·이용·파기 관련",
        estimated_tokens=20_000_000, size_gb=0.05, category="법률", available=True),
    # 노동·인사
    DatasetInfo(id="labor_law", name="노동법",
        description="근로기준법, 최저임금법, 산업안전보건법, 퇴직급여법 등",
        estimated_tokens=40_000_000, size_gb=0.1, category="노동·인사", available=True),
    DatasetInfo(id="labor_union_law", name="노동조합법",
        description="노동조합 및 노동관계조정법, 노사협의회법 등",
        estimated_tokens=20_000_000, size_gb=0.05, category="노동·인사", available=True),
    DatasetInfo(id="social_security_law", name="사회보장법",
        description="국민연금법, 건강보험법, 고용보험법, 산재보험법 등",
        estimated_tokens=80_000_000, size_gb=0.2, category="노동·인사", available=True),
    DatasetInfo(id="disability_law", name="장애인고용법",
        description="장애인 의무고용, 부담금, 지원금 관련 법령",
        estimated_tokens=15_000_000, size_gb=0.04, category="노동·인사", available=True),
    DatasetInfo(id="foreign_worker_law", name="외국인고용법",
        description="외국인 근로자 고용허가, 취업 규정 관련 법령",
        estimated_tokens=15_000_000, size_gb=0.04, category="노동·인사", available=True),
    DatasetInfo(id="hr_admin", name="고용노동부 행정해석",
        description="실무 HR 질문에 대한 고용노동부 공식 질의회시 수십만 건",
        estimated_tokens=200_000_000, size_gb=0.5, category="노동·인사", available=True),
]

DATASET_MAP = {d.id: d for d in DATASETS}


def calc_parameters(config: TrainingConfig) -> int:
    d, ff, n, v = config.d_model, config.d_ff, config.n_layers, config.vocab_size
    embedding = v * d
    per_layer = 4 * d * d + 2 * d * ff + 5 * d
    return embedding + per_layer * n + d * v


@router.get("/", response_model=list[DatasetInfo])
def list_datasets():
    return DATASETS


@router.post("/estimate", response_model=TrainingEstimate)
def estimate(config: TrainingConfig):
    selected = [DATASET_MAP[id] for id in config.dataset_ids if id in DATASET_MAP]
    total_tokens = sum(d.estimated_tokens for d in selected)
    total_params = calc_parameters(config)
    estimated_hours = (total_tokens * config.max_epochs) / (1_000_000_000 * config.max_epochs)
    return TrainingEstimate(total_tokens=total_tokens, total_parameters=total_params,
                            estimated_hours=round(estimated_hours, 1), datasets=selected)


@router.get("/{dataset_id}/status")
def get_download_status(dataset_id: str):
    if dataset_id not in DATASET_MAP:
        raise HTTPException(status_code=404, detail="데이터셋을 찾을 수 없습니다.")
    if is_ready(dataset_id):
        return {"status": "ready", "progress": 1.0, "message": "사용 가능"}
    raw = r.get(f"download:state:{dataset_id}")
    if raw:
        return json.loads(raw)
    return {"status": "idle", "progress": 0.0, "message": ""}


@router.post("/{dataset_id}/download")
def start_download(dataset_id: str, body: dict = {}):
    if dataset_id not in DATASET_MAP:
        raise HTTPException(status_code=404, detail="데이터셋을 찾을 수 없습니다.")
    if is_ready(dataset_id):
        return {"status": "ready", "message": "이미 다운로드되어 있습니다."}

    raw = r.get(f"download:state:{dataset_id}")
    if raw:
        state = json.loads(raw)
        if state.get("status") == "running":
            raise HTTPException(status_code=400, detail="이미 다운로드 중입니다.")

    api_key = body.get("api_key")
    if dataset_id in NEEDS_API_KEY and not api_key:
        raise HTTPException(status_code=422,
            detail="이 데이터셋은 국가법령정보센터 API 키가 필요합니다.")

    celery_app.send_task("tasks.download_dataset", args=[dataset_id, api_key])
    return {"status": "started", "message": "다운로드를 시작합니다."}
