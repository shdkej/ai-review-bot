FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
COPY AGENTS.md AGENTS.md
COPY main.py main.py
COPY src src

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir .

ENTRYPOINT ["ai-review-bot"]
