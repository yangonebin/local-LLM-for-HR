class GPTConfig:
    # 모델 아키텍처
    vocab_size: int = 32000
    max_seq_len: int = 1024
    d_model: int = 768
    n_layers: int = 12
    n_heads: int = 12
    d_ff: int = 3072
    dropout: float = 0.1

    # 학습
    batch_size: int = 16
    learning_rate: float = 3e-4
    max_epochs: int = 10
    warmup_steps: int = 2000

    # 기타
    device: str = "cuda"
