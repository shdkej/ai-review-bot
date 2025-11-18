"""Command-line interface helpers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_review_bot.controller.review import ReviewController


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a structured code review report.")
    parser.add_argument(
        "--project",
        required=True,
        help="GitLab 프로젝트 이름 (예: kop-web, kop-api).",
    )
    parser.add_argument(
        "--pr-number",
        required=True,
        help="리뷰 대상 PR 번호 또는 MR ID.",
    )
    parser.add_argument(
        "--diff-file",
        type=Path,
        help="git diff 내용이 담긴 파일 경로. 생략하면 stdin을 사용합니다.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    diff_source = args.diff_file.read_text(encoding="utf-8") if args.diff_file else sys.stdin.read()

    controller = ReviewController()
    report = controller.run(
        project_name=args.project,
        pr_number=args.pr_number,
        raw_diff=diff_source,
    )
    sys.stdout.write(report)
    sys.stdout.flush()
    return 0
