FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir httpx==0.28.1 fastapi==0.115.12 uvicorn==0.34.2

COPY main.py /app/main.py

EXPOSE 9100
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9100"]
