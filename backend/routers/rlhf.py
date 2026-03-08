import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_db, QAPair
from schemas import FeedbackRequest, RLHFStats

router = APIRouter(prefix="/api/rlhf", tags=["rlhf"])

_last_rlhf_at: datetime | None = None


@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    qa = db.query(QAPair).filter(QAPair.id == req.qa_id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="Q&A를 찾을 수 없습니다.")

    qa.rating = req.rating
    qa.comment = req.comment
    db.commit()
    return {"message": "피드백이 저장되었습니다."}


@router.get("/stats", response_model=RLHFStats)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(QAPair).filter(QAPair.rating.isnot(None)).count()
    positive = db.query(QAPair).filter(QAPair.rating == 1).count()
    negative = db.query(QAPair).filter(QAPair.rating == -1).count()
    return RLHFStats(
        total_feedback=total,
        positive=positive,
        negative=negative,
        last_rlhf_at=_last_rlhf_at,
    )


@router.post("/train")
def trigger_rlhf(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """피드백 데이터로 RLHF 학습 트리거"""
    positive_pairs = (
        db.query(QAPair)
        .filter(QAPair.rating == 1)
        .order_by(QAPair.created_at.desc())
        .limit(100)
        .all()
    )
    if len(positive_pairs) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"RLHF 학습에는 최소 10개의 긍정 피드백이 필요합니다. 현재: {len(positive_pairs)}개"
        )

    pairs = [{"question": p.question, "answer": p.answer} for p in positive_pairs]
    background_tasks.add_task(_run_rlhf, pairs)
    return {"message": f"{len(pairs)}개 긍정 피드백으로 RLHF 학습을 시작합니다."}


def _run_rlhf(pairs: list[dict]):
    """긍정 피드백 데이터로 지속 학습 (SFT 방식)"""
    global _last_rlhf_at
    import sys
    import torch

    if "/app/llm" not in sys.path:
        sys.path.insert(0, "/app/llm")

    try:
        import glob
        from config import GPTConfig
        from model.gpt import GPT
        from tokenizer.bpe import KoreanTokenizer
        from pathlib import Path

        checkpoints = sorted(glob.glob("/app/llm/checkpoints/epoch_*.pt"))
        if not checkpoints:
            return

        cfg = GPTConfig()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = GPT(cfg).to(device)

        ckpt = torch.load(checkpoints[-1], map_location=device)
        model.load_state_dict(ckpt["model_state_dict"])

        tokenizer = KoreanTokenizer()
        tokenizer.load("/app/llm/tokenizer/saved/spm.model")

        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
        model.train()

        for pair in pairs:
            text = f"[질문]\n{pair['question']}\n\n[답변]\n{pair['answer']}"
            ids = tokenizer.encode(text)
            if len(ids) < 4:
                continue

            x = torch.tensor([ids[:-1]], dtype=torch.long).to(device)
            y = torch.tensor([ids[1:]], dtype=torch.long).to(device)

            if x.shape[1] > cfg.max_seq_len:
                x = x[:, -cfg.max_seq_len:]
                y = y[:, -cfg.max_seq_len:]

            _, loss = model(x, y)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        rlhf_path = "/app/llm/checkpoints/rlhf_latest.pt"
        torch.save({
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
        }, rlhf_path)

        _last_rlhf_at = datetime.utcnow()

    except Exception as e:
        print(f"RLHF 학습 오류: {e}")
