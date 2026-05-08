FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn httpx
COPY server.py /app/server.py
EXPOSE 8080
ENV OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
