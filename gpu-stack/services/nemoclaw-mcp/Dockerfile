# NemoClaw MCP sidecars — HTTP tool servers + backend app package (PYTHONPATH=/w/backend)
FROM python:3.12-slim

WORKDIR /w

COPY backend/requirements.txt /w/backend/requirements.txt
RUN pip install --no-cache-dir -r /w/backend/requirements.txt

COPY backend/app /w/backend/app
COPY nemoclaw/mcp_servers /w/nemoclaw/mcp_servers

ENV PYTHONPATH=/w/backend

EXPOSE 3001
CMD ["python", "/w/nemoclaw/mcp_servers/marma_server.py"]
