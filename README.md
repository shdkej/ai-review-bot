# AI Review Bot

클린 아키텍처로 구성된 AI 코드 리뷰 봇입니다. Git diff와 프로젝트 정보를 입력하면 OpenAI GPT-5 계열 모델을 호출해 팀 규칙에 맞는 리뷰 리포트를 생성합니다.

## 요구사항
- Docker 24+ (설치·테스트·실행은 모두 Docker 기반)
- OpenAI API 키: `OPENAI_API_KEY` 환경 변수에 설정
- 선택: `OPENAI_REVIEW_MODEL`(기본 `gpt-5.1`), `OPENAI_REVIEW_REASONING_EFFORT`(예: `minimal`, `medium`)

## 빠른 시작
아래 명령으로 이미지를 빌드하고 리뷰를 실행합니다.
```bash
docker build -t ai-review-bot .

# diff 파일을 넘겨 실행
docker run --rm -i \
  -e OPENAI_API_KEY=sk-... \
  -v "$PWD":/app \
  ai-review-bot \
  --project kop-web \
  --pr-number 123 \
  --diff-file sample.diff

# 파이프로 diff 전달
cat sample.diff | docker run --rm -i \
  -e OPENAI_API_KEY=sk-... \
  ai-review-bot \
  --project kop-api \
  --pr-number 456
```

## CLI 입력값
- `--project`: 프로젝트 식별자(예: `kop-web`, `kop-api`, `hybris`)
- `--pr-number`: 리뷰 대상 PR/MR 번호
- `--diff-file`: diff가 담긴 파일 경로(없으면 stdin 사용)

## 테스트와 품질 점검 (컨테이너 내부)
런타임 이미지는 최소 의존성만 포함합니다. 필요 시 컨테이너 안에서 dev 의존성을 설치해 검증합니다.
```bash
# 셸 진입 후 검사 실행
docker run --rm -it -v "$PWD":/app --entrypoint /bin/sh ai-review-bot
pip install -e .[dev]
pytest
ruff format src tests && ruff check src tests
```

## 디렉터리 안내
- `main.py`: 엔트리포인트 래퍼
- `src/controller`: Lambda 스타일 핸들러(`ReviewController`)
- `src/service`: 워크플로 조합(`ReviewService`)
- `src/domain`: 프롬프트 생성 등 순수 비즈니스 로직
- `src/entity`: 입력/출력 데이터 클래스
- `src/support`: LLM 클라이언트 등 헬퍼
- `tests/`: 단위 테스트와 diff 픽스처
- `PLAN.md`, `TECH_SPEC.md`: 동작 요구사항과 설계 규칙
- `Dockerfile`: 런타임 이미지 정의

## 추가 팁
- 도움말: `docker run --rm ai-review-bot --help`
- 출력 포맷과 리뷰 스타일은 `PLAN.md`와 `TECH_SPEC.md` 규칙을 우선합니다.
