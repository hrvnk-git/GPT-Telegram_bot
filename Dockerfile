# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm
ENV PATH /usr/local/bin:$PATH
WORKDIR /
RUN apt-get update && apt install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*
USER root
COPY . .
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN . $HOME/.local/bin/env && \
    uv sync
CMD . $HOME/.local/bin/env && \
    uv run main.py
