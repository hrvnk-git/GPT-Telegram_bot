# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13.2
FROM python:${PYTHON_VERSION}-slim as base
# FROM alpine:3.21
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /
RUN pip install uv
USER root
COPY . .
RUN uv sync
CMD uv run main.py
