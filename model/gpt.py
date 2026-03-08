import torch
import torch.nn as nn
from model.block import TransformerBlock


class GPT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

        # 입력 임베딩
        self.token_emb = nn.Embedding(config.vocab_size, config.d_model)
        self.pos_emb = nn.Embedding(config.max_seq_len, config.d_model)
        self.dropout = nn.Dropout(config.dropout)

        # Transformer Block x 12
        self.blocks = nn.ModuleList([TransformerBlock(config) for _ in range(config.n_layers)])

        # 마지막 LayerNorm + 출력
        self.norm = nn.LayerNorm(config.d_model)
        self.head = nn.Linear(config.d_model, config.vocab_size, bias=False)

        # 가중치 초기화
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        device = idx.device

        # 토큰 + 위치 임베딩
        tok = self.token_emb(idx)                                      # (B, T, d_model)
        pos = self.pos_emb(torch.arange(T, device=device))            # (T, d_model)
        x = self.dropout(tok + pos)

        # Transformer Block 12번 통과
        for block in self.blocks:
            x = block(x)

        # 마지막 LayerNorm
        x = self.norm(x)

        # 출력
        logits = self.head(x)  # (B, T, vocab_size)

        # 학습 시 loss 계산
        loss = None
        if targets is not None:
            loss = nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1)
            )

        return logits, loss

    def count_parameters(self):
        return sum(p.numel() for p in self.parameters())
