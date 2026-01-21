# Minimal Dockerfile for MCP STDIO Docker Test Server
FROM python:3.13-alpine

ARG VERSION=unknown

LABEL version="${VERSION}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.title="MCP STDIO Docker Test Server" \
      org.opencontainers.image.description="Minimal MCP server for testing Docker stdio communications"

WORKDIR /app

RUN apk add --no-cache \
    bash \
    python3 \
    py3-pip

# Temporary security patch for CVE-2025-8869
RUN pip install --no-cache-dir --break-system-packages --upgrade 'pip>=25.3'

COPY requirements.txt ./
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY src/ ./src/
COPY VERSION ./

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["mcp"]
