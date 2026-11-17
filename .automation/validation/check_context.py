"""Agent context stays within the token budgets in uadr.json."""
from pathlib import Path

import context_audit

NAME = "context"


def run(root: Path, cfg: dict) -> tuple[list[str], list[str]]:
    return list(context_audit.audit(root)["violations"]), []
