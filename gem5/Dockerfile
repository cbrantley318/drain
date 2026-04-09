FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    python \
    python-dev \
    python-six \
    scons \
    zlib1g-dev \
    m4 \
    libprotobuf-dev \
    protobuf-compiler \
    libgoogle-perftools-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /gem5
