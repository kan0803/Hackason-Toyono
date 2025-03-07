# 開発用ステージ
FROM python:3.11.9-slim AS developer

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ビルド用ステージ
FROM python:3.11.9-slim AS builder
WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -v

# 最終用ステージ
FROM python:3.11.9-slim AS production

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11

ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
COPY --from=builder /app/ .
