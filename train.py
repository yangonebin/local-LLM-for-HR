import torch
from torch.utils.data import DataLoader
import math
import time
from pathlib import Path

from config import GPTConfig
from model.gpt import GPT
from data.dataset import TextDataset, preprocess
from tokenizer.bpe import KoreanTokenizer


def get_lr(step, config):
    """Warmup 후 Cosine 감소 스케줄"""
    if step < config.warmup_steps:
        return config.learning_rate * step / config.warmup_steps
    return config.learning_rate * 0.5 * (
        1 + math.cos(math.pi * step / (config.max_epochs * 1000))
    )


def train():
    config = GPTConfig()
    device = torch.device(config.device)

    # 토크나이저 불러오기
    tokenizer = KoreanTokenizer()
    tokenizer.load("tokenizer/saved/spm.model")

    # 전처리 (data/train.bin 없으면 생성)
    bin_path = "data/train.bin"
    if not Path(bin_path).exists():
        preprocess("data/train.txt", tokenizer, "data/train")

    # 데이터셋
    dataset = TextDataset(bin_path, config.max_seq_len)
    dataloader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True, num_workers=0)

    # 모델
    model = GPT(config).to(device)
    print(f"파라미터 수: {model.count_parameters():,}")

    # 옵티마이저
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)

    # 체크포인트 저장 경로
    Path("checkpoints").mkdir(exist_ok=True)

    step = 0
    for epoch in range(config.max_epochs):
        model.train()
        total_loss = 0

        for batch_idx, (x, y) in enumerate(dataloader):
            x, y = x.to(device), y.to(device)

            # Learning rate 스케줄
            lr = get_lr(step, config)
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr

            # Forward
            logits, loss = model(x, y)

            # Backward
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            step += 1

            if batch_idx % 100 == 0:
                print(f"epoch {epoch+1} | step {step} | loss {loss.item():.4f} | lr {lr:.6f}")

        avg_loss = total_loss / len(dataloader)
        print(f"epoch {epoch+1} 완료 | avg loss: {avg_loss:.4f}")

        # 체크포인트 저장
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': avg_loss,
        }, f"checkpoints/epoch_{epoch+1}.pt")
        print(f"체크포인트 저장: checkpoints/epoch_{epoch+1}.pt")


if __name__ == "__main__":
    train()
