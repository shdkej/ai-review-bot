"""GitHub Actions 관련 동작을 검증하는 테스트."""

from pathlib import Path

WORKFLOW_PATH = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "docker-build.yml"


def test_docker_build_workflow_file_exists():
    """워크플로 파일이 존재해야 한다."""
    assert WORKFLOW_PATH.exists(), "docker-build.yml 파일이 존재하지 않습니다."


def test_workflow_triggers_buildx_on_pull_request():
    """PR 생성 시 buildx 명령을 실행하도록 구성되어야 한다."""
    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "pull_request" in content, "pull_request 이벤트가 설정되지 않았습니다."
    assert (
        "docker buildx build --platform linux/amd64 -t shdkej/ai-code-review-bot:latest --push ."
    ) in content, "buildx 실행 명령이 누락되었습니다."
