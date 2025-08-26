FROM mcr.microsoft.com/devcontainers/python:3.10-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libpq-dev \
    gcc \
    openssh-client \
    sudo \
    curl \
    sqlite3 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

WORKDIR /workspace

EXPOSE 8000