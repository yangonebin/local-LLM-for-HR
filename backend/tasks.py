import sys
import os
import json
import time
import math

sys.path.insert(0, "/app/llm")

from celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# 학습 진행 상태를 Redis에 저장하는 키
TRAINING_STATE_KEY = "training:state"


def save_state(redis_client, state: dict):
    redis_client.set(TRAINING_STATE_KEY, json.dumps(state))


@celery_app.task(bind=True, name="tasks.run_training")
def run_training(self, config: dict, dataset_paths: list[str]):
    import redis
    import torch
    from torch.utils.data import DataLoader, ConcatDataset
    from pathlib import Path

    r = redis.Redis(host="redis", port=6379, db=2)

    def update(state: dict):
        self.update_state(state="PROGRESS", meta=state)
        r.set(TRAINING_STATE_KEY, json.dumps(state))

    try:
        update({"status": "running", "epoch": 0, "step": 0, "loss": 0.0,
                "progress": 0.0, "message": "모델 초기화 중..."})

        # ── 모델 설정 로드 ─────────────────────────────────────
        from config import GPTConfig
        from model.gpt import GPT
        from data.dataset import TextDataset
        from tokenizer.bpe import KoreanTokenizer

        cfg = GPTConfig()
        for k, v in config.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # ── 토크나이저 ────────────────────────────────────────
        tokenizer = KoreanTokenizer()
        tokenizer.load("/app/llm/tokenizer/saved/spm.model")

        # ── 데이터셋 ──────────────────────────────────────────
        update({"status": "running", "epoch": 0, "step": 0, "loss": 0.0,
                "progress": 0.0, "message": "데이터 로딩 중..."})

        datasets = []
        for path in dataset_paths:
            if path.endswith(".bin") and os.path.exists(path):
                datasets.append(TextDataset(path, cfg.max_seq_len))

        if not datasets:
            # 기본 데이터로 fallback
            default_bin = "/app/llm/data/train.bin"
            if os.path.exists(default_bin):
                datasets.append(TextDataset(default_bin, cfg.max_seq_len))

        dataset = ConcatDataset(datasets)
        dataloader = DataLoader(dataset, batch_size=cfg.batch_size,
                                shuffle=True, num_workers=0)

        # ── 모델 & 옵티마이저 ─────────────────────────────────
        model = GPT(cfg).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate)
        Path("/app/llm/checkpoints").mkdir(exist_ok=True)

        total_steps = len(dataloader) * cfg.max_epochs
        step = 0
        start_time = time.time()

        def get_lr(s):
            if s < cfg.warmup_steps:
                return cfg.learning_rate * s / max(cfg.warmup_steps, 1)
            return cfg.learning_rate * 0.5 * (
                1 + math.cos(math.pi * s / total_steps)
            )

        for epoch in range(cfg.max_epochs):
            # 중지 신호 확인
            if r.get("training:stop"):
                r.delete("training:stop")
                update({"status": "stopped", "epoch": epoch, "step": step,
                        "loss": 0.0, "progress": step / max(total_steps, 1),
                        "message": "사용자에 의해 중지됨"})
                return

            model.train()
            total_loss = 0.0

            for batch_idx, (x, y) in enumerate(dataloader):
                if r.get("training:stop"):
                    break

                x, y = x.to(device), y.to(device)

                lr = get_lr(step)
                for pg in optimizer.param_groups:
                    pg["lr"] = lr

                logits, loss = model(x, y)
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

                total_loss += loss.item()
                step += 1

                if batch_idx % 20 == 0:
                    elapsed = time.time() - start_time
                    progress = step / max(total_steps, 1)
                    update({
                        "status": "running",
                        "epoch": epoch + 1,
                        "total_epochs": cfg.max_epochs,
                        "step": step,
                        "loss": round(loss.item(), 4),
                        "progress": round(progress, 4),
                        "elapsed_seconds": round(elapsed, 1),
                        "message": f"epoch {epoch+1}/{cfg.max_epochs} | step {step}"
                    })

            avg_loss = total_loss / max(len(dataloader), 1)
            ckpt_path = f"/app/llm/checkpoints/epoch_{epoch+1}.pt"
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "loss": avg_loss,
                "config": config,
            }, ckpt_path)

        final = {
            "status": "completed",
            "epoch": cfg.max_epochs,
            "total_epochs": cfg.max_epochs,
            "step": step,
            "loss": round(avg_loss, 4),
            "progress": 1.0,
            "elapsed_seconds": round(time.time() - start_time, 1),
            "message": "학습 완료!",
        }
        update(final)
        return final

    except Exception as e:
        err = {"status": "failed", "message": str(e), "progress": 0.0,
               "epoch": 0, "step": 0, "loss": 0.0, "elapsed_seconds": 0.0}
        r.set(TRAINING_STATE_KEY, json.dumps(err))
        raise


# ── 데이터셋 다운로드 태스크 ───────────────────────────────────────

DOWNLOAD_STATE_KEY = "download:state:{dataset_id}"


@celery_app.task(bind=True, name="tasks.download_dataset")
def download_dataset(self, dataset_id: str, api_key: str | None = None):
    import redis
    from services.downloader import download_dataset as _download

    r = redis.Redis(host="redis", port=6379, db=2, decode_responses=True)
    state_key = f"download:state:{dataset_id}"

    def progress_cb(message: str, progress: float):
        state = {"status": "running", "message": message, "progress": round(progress, 3)}
        self.update_state(state="PROGRESS", meta=state)
        r.set(state_key, json.dumps(state), ex=3600)

    try:
        r.set(state_key, json.dumps({"status": "running", "message": "시작 중...", "progress": 0.0}), ex=3600)
        _download(dataset_id, api_key, progress_cb)
        done = {"status": "completed", "message": "다운로드 완료", "progress": 1.0}
        r.set(state_key, json.dumps(done), ex=3600)
        return done
    except Exception as e:
        err = {"status": "failed", "message": str(e), "progress": 0.0}
        r.set(state_key, json.dumps(err), ex=3600)
        raise


# ── 사전학습 모델 다운로드 태스크 ─────────────────────────────────

@celery_app.task(bind=True, name="tasks.download_model")
def download_model(self, model_id: str, hf_repo: str):
    import redis as _redis
    from huggingface_hub import snapshot_download
    from pathlib import Path

    r = _redis.Redis(host="redis", port=6379, db=2, decode_responses=True)
    state_key = f"model:download:{model_id}"
    dest = Path(f"/app/pretrained/{model_id}")
    dest.mkdir(parents=True, exist_ok=True)

    def update(msg, progress):
        state = {"status": "running", "message": msg, "progress": round(progress, 3)}
        self.update_state(state="PROGRESS", meta=state)
        r.set(state_key, json.dumps(state), ex=86400)

    try:
        update("HuggingFace에서 모델 다운로드 중...", 0.05)
        snapshot_download(
            repo_id=hf_repo,
            local_dir=str(dest),
            ignore_patterns=["*.msgpack", "flax_model*", "tf_model*", "rust_model*"],
        )
        done = {"status": "completed", "message": "다운로드 완료", "progress": 1.0}
        r.set(state_key, json.dumps(done), ex=86400)
        return done
    except Exception as e:
        err = {"status": "failed", "message": str(e), "progress": 0.0}
        r.set(state_key, json.dumps(err), ex=86400)
        raise


# ── 사전학습 모델 파인튜닝 태스크 ─────────────────────────────────

@celery_app.task(bind=True, name="tasks.finetune_model")
def finetune_model(self, model_id: str, dataset_paths: list, config: dict):
    import redis as _redis
    import torch
    from pathlib import Path
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    from transformers import DataCollatorForLanguageModeling
    from peft import LoraConfig, get_peft_model, TaskType
    from torch.utils.data import Dataset as TorchDataset

    r = _redis.Redis(host="redis", port=6379, db=2, decode_responses=True)

    def update(state_dict):
        self.update_state(state="PROGRESS", meta=state_dict)
        r.set("training:state", json.dumps(state_dict), ex=86400)

    try:
        model_dir = f"/app/pretrained/{model_id}"
        update({"status": "running", "epoch": 0, "step": 0, "loss": 0.0,
                "progress": 0.0, "message": "토크나이저 로딩 중..."})

        tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        update({"status": "running", "epoch": 0, "step": 0, "loss": 0.0,
                "progress": 0.05, "message": "모델 로딩 중..."})

        model = AutoModelForCausalLM.from_pretrained(
            model_dir, torch_dtype=torch.float16,
            device_map="auto", trust_remote_code=True,
        )

        # LoRA 설정 (메모리 효율적 파인튜닝)
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16, lora_alpha=32, lora_dropout=0.05,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        )
        model = get_peft_model(model, lora_config)

        update({"status": "running", "epoch": 0, "step": 0, "loss": 0.0,
                "progress": 0.1, "message": "데이터 로딩 중..."})

        # 텍스트 파일 로드
        texts = []
        for path in dataset_paths:
            txt = Path(path.replace("train.bin", "train.txt"))
            if txt.exists():
                with open(txt, encoding="utf-8", errors="ignore") as f:
                    texts.append(f.read())

        if not texts:
            txt_fallback = Path("/app/llm/data/train.txt")
            if txt_fallback.exists():
                with open(txt_fallback, encoding="utf-8", errors="ignore") as f:
                    texts.append(f.read())

        class TextDS(TorchDataset):
            def __init__(self, text, tok, max_len=512):
                chunks = [text[i:i+max_len*4] for i in range(0, min(len(text), 5_000_000), max_len*4)]
                self.encodings = [tok(c, truncation=True, max_length=max_len,
                                      return_tensors="pt") for c in chunks[:5000]]
            def __len__(self): return len(self.encodings)
            def __getitem__(self, i):
                item = {k: v.squeeze() for k, v in self.encodings[i].items()}
                item["labels"] = item["input_ids"].clone()
                return item

        dataset = TextDS("\n\n".join(texts), tokenizer)
        collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

        max_epochs = config.get("max_epochs", 3)
        output_dir = f"/app/llm/checkpoints/pretrained_{model_id}"

        class ProgressCallback:
            def on_log(self, args, state, control, logs=None, **kwargs):
                if logs:
                    progress = state.global_step / max(state.max_steps, 1)
                    update({
                        "status": "running",
                        "epoch": int(state.epoch or 0),
                        "total_epochs": max_epochs,
                        "step": state.global_step,
                        "loss": round(logs.get("loss", 0.0), 4),
                        "progress": round(progress, 4),
                        "elapsed_seconds": 0,
                        "message": f"step {state.global_step}",
                    })

        from transformers import TrainerCallback
        class CB(TrainerCallback):
            def on_log(self, args, state, control, logs=None, **kwargs):
                ProgressCallback().on_log(args, state, control, logs)

        args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=max_epochs,
            per_device_train_batch_size=config.get("batch_size", 2),
            learning_rate=config.get("learning_rate", 2e-4),
            fp16=True, logging_steps=10,
            save_strategy="epoch",
            report_to="none",
        )
        trainer = Trainer(
            model=model, args=args,
            train_dataset=dataset,
            data_collator=collator,
            callbacks=[CB()],
        )
        trainer.train()
        model.save_pretrained(output_dir)

        final = {"status": "completed", "epoch": max_epochs, "total_epochs": max_epochs,
                 "step": 0, "loss": 0.0, "progress": 1.0,
                 "elapsed_seconds": 0, "message": "파인튜닝 완료!"}
        r.set("training:state", json.dumps(final), ex=86400)
        return final

    except Exception as e:
        err = {"status": "failed", "message": str(e), "progress": 0.0,
               "epoch": 0, "step": 0, "loss": 0.0, "elapsed_seconds": 0}
        r.set("training:state", json.dumps(err), ex=86400)
        raise
