import os
import subprocess
import sys
from textwrap import dedent

import requests
from openai import OpenAI

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_review_bot.entity.review import ReviewContext
from ai_review_bot.service.review_service import ReviewService


client = OpenAI()  # OPENAI_API_KEY는 환경변수로 자동 인식


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"[llm-code-review] ERROR: required env var {name} is missing", file=sys.stderr)
        sys.exit(1)
    return value


def run_cmd(args, cwd="/workspace", capture_output=True, check=True) -> str:
    """간단한 쉘 명령 실행 헬퍼."""
    print(f"[llm-code-review] run: {' '.join(args)}")
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=capture_output,
        text=True,
    )
    if check and result.returncode != 0:
        print(f"[llm-code-review] command failed: {' '.join(args)}", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout if capture_output else ""


def generate_diff(target_branch: str, commit_sha: str) -> str:
    """origin/타겟 브랜치 기준으로 diff 생성."""
    print(f"[llm-code-review] fetching origin/{target_branch}")
    run_cmd(["git", "fetch", "origin", target_branch])

    print(f"[llm-code-review] generating diff for origin/{target_branch}..{commit_sha}")
    diff_text = run_cmd(["git", "diff", f"origin/{target_branch}..{commit_sha}"])
    if not diff_text.strip():
        print("[llm-code-review] diff is empty – nothing to review.")
    return diff_text

def post_comment_to_gitlab(body: str):
    """GitLab MR 코멘트 생성."""
    gitlab_token = require_env("GITLAB_TOKEN")
    ci_api_v4_url = require_env("CI_API_V4_URL")
    ci_project_id = require_env("CI_PROJECT_ID")
    ci_mr_iid = require_env("CI_MERGE_REQUEST_IID")

    url = f"{ci_api_v4_url}/projects/{ci_project_id}/merge_requests/{ci_mr_iid}/notes"
    print(f"[llm-code-review] posting comment to GitLab: {url}")

    resp = requests.post(
        url,
        headers={
            "PRIVATE-TOKEN": gitlab_token,
            "Content-Type": "application/json",
        },
        json={"body": body},
        timeout=30,
    )

    if not resp.ok:
        print(
            f"[llm-code-review] ERROR: failed to post comment "
            f"(status={resp.status_code}): {resp.text}",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    # 필수 환경변수 확인
    target_branch = require_env("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
    commit_sha = require_env("CI_COMMIT_SHA")
    project_id = require_env("CI_PROJECT_ID")
    mr_iid = require_env("CI_MERGE_REQUEST_IID")

    project_name = os.getenv("LLM_REVIEW_PROJECT_NAME", "kop-web")

    # 1) diff 생성
    diff_text = generate_diff(target_branch, commit_sha)
    if not diff_text.strip():
        # diff 없으면 짧게 코멘트 하나 남기고 종료해도 되고, 그냥 조용히 끝내도 됨
        body = "자동 코드리뷰: 변경된 코드가 없어 리뷰할 내용이 없습니다."
        # 필요 없다면 아래 줄 주석 처리
        post_comment_to_gitlab(body)
        # 파일은 그래도 남겨두면 디버깅에 편함
        with open("/workspace/llm_review.txt", "w", encoding="utf-8") as f:
            f.write(body)
        return

    # 2) OpenAI 호출
    review_text = ReviewService().create_review(
        ReviewContext(
            project_name=project_name,
            pr_number=mr_iid,
            diff=diff_text,
        )
    )

    # 3) 결과 파일로 저장 (CI artifact 용)
    review_path = "/workspace/llm_review.txt"
    print(f"[llm-code-review] writing review to {review_path}")
    with open(review_path, "w", encoding="utf-8") as f:
        f.write(review_text)

    # 4) GitLab MR 코멘트 등록
    post_comment_to_gitlab(review_text)

    print("[llm-code-review] complete.")


if __name__ == "__main__":
    main()
