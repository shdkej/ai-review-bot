"""Entity definitions for review requests and responses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewContext:
    """Canonical representation of the review input payload."""

    project_name: str
    pr_number: str
    diff: str
    ticket_context: str | None = None
    project_overview: str | None = None

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name must not be empty")
        if not self.pr_number:
            raise ValueError("pr_number must not be empty")
        if not self.diff.strip():
            raise ValueError("diff must not be empty")

