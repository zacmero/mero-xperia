FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    apktool apksigner zipalign && rm -rf /var/lib/apt/lists/*
WORKDIR /work
