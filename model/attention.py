import torch
import torch.nn as nn
import math


class MultiHeadSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        assert config.d_model % config.n_heads == 0

        self.n_heads = config.n_heads
        self.d_head = config.d_model // config.n_heads  # 768 // 12 = 64
        self.d_model = config.d_model

        # Q, K, V 한번에 생성
        self.qkv = nn.Linear(config.d_model, 3 * config.d_model)
        self.out = nn.Linear(config.d_model, config.d_model)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        B, T, C = x.shape  # (배치, 시퀀스 길이, d_model)

        # Q, K, V 계산
        qkv = self.qkv(x)  # (B, T, 3 * d_model)
        q, k, v = qkv.split(self.d_model, dim=2)  # 각각 (B, T, d_model)

        # 헤드 분할
        q = q.view(B, T, self.n_heads, self.d_head).transpose(1, 2)  # (B, n_heads, T, d_head)
        k = k.view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.d_head).transpose(1, 2)

        # Attention 계산
        scale = math.sqrt(self.d_head)
        scores = torch.matmul(q, k.transpose(-2, -1)) / scale  # (B, n_heads, T, T)

        # Causal Mask: 미래 토큰을 보지 못하게
        mask = torch.triu(torch.ones(T, T, device=x.device), diagonal=1).bool()
        scores = scores.masked_fill(mask, float('-inf'))

        attn = torch.softmax(scores, dim=-1)
        attn = self.dropout(attn)

        # 가중합
        out = torch.matmul(attn, v)  # (B, n_heads, T, d_head)

        # 헤드 합치기
        out = out.transpose(1, 2).contiguous().view(B, T, self.d_model)  # (B, T, d_model)
        out = self.out(out)

        return out
