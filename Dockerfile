FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY zugferd_client ./zugferd_client

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
ENV ZUGFERD_API_KEY="zg_test_ouroboros_001"

ENTRYPOINT ["zugferd-mcp"]
