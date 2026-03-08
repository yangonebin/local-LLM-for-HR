FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# llm 코드는 프로젝트 루트에 있음
COPY config.py ./llm/config.py
COPY train.py ./llm/train.py
COPY prepare_data.py ./llm/prepare_data.py
COPY model/ ./llm/model/
COPY tokenizer/ ./llm/tokenizer/
COPY data/ ./llm/data/

ENV PYTHONPATH=/app/backend:/app/llm

WORKDIR /app/backend
