# Multi stage build, build phase
FROM python:3.10-slim AS builder

WORKDIR /build
RUN pip install poetry
COPY poetry.lock pyproject.toml .
RUN poetry export -f requirements.txt --without-hashes --output requirements.txt

# package phase
FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN apt-get update && \ 
    apt-get install --no-install-recommends -y \
      libcairo2-dev \
      libgirepository1.0-dev \
      libopus-dev \
      gstreamer1.0 \
      gstreamer1.0-plugins-base \
      gstreamer1.0-plugins-good \
      libgstreamer1.0 \
      libgstreamer1.0-dev \
      python3-gi \
      python3-gst-1.0

COPY --from=builder /build/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./requirements.txt

COPY ./streamer.py .
COPY ./long.wav ./audrey.wav
