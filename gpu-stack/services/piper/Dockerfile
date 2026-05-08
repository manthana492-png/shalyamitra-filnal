# Lightweight Piper service — downloads ONNX voice model + Piper CLI binary where possible.
FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Piper CLI + libs from upstream GitHub release (best-effort; WAV fallback remains if layout differs)
RUN set -eux; \
    curl -fsSL -o /tmp/piper.tgz \
      https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz; \
    mkdir -p /opt/piper; \
    tar -xzf /tmp/piper.tgz -C /opt/piper; \
    if [ -f /opt/piper/piper/piper ]; then ln -sf /opt/piper/piper/piper /usr/local/bin/piper; \
    elif [ -f /opt/piper/piper ]; then ln -sf /opt/piper/piper /usr/local/bin/piper; \
    fi; \
    rm -f /tmp/piper.tgz

RUN mkdir -p /models \
 && curl -fsSL -L -o /models/en_US-lessac-medium.onnx \
      https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx \
 && curl -fsSL -L -o /models/en_US-lessac-medium.onnx.json \
      https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

RUN pip install --no-cache-dir fastapi uvicorn

COPY server.py /app/server.py
ENV PIPER_MODEL_PATH=/models/en_US-lessac-medium.onnx

EXPOSE 8090
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8090"]
