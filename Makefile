lint:
		ruff check . --fix
		ruff format .

test:
		pytest

build:
		docker build -t ai-review-bot:test .

all: lint test build
