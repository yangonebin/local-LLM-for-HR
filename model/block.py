import torch.nn as nn
from model.attention import MultiHeadSelfAttention
from model.ffn import FeedForward


class TransformerBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.norm1 = nn.LayerNorm(config.d_model)
        self.attn = MultiHeadSelfAttention(config)
        self.norm2 = nn.LayerNorm(config.d_model)
        self.ffn = FeedForward(config)

    def forward(self, x):
        # Pre-LayerNorm + 잔차 연결
        x = x + self.attn(self.norm1(x))
        x = x + self.ffn(self.norm2(x))
        return x
