FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
COPY AGENTS.md AGENTS.md
COPY main.py main.py
COPY src src
COPY entrypoint.py entrypoint.py

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir .

# ENTRYPOINT ["ai-review-bot"]
ENTRYPOINT ["python", "entrypoint.py"]
