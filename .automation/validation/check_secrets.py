"""Pattern-based secret detection. Reports location and kind only, never the value."""
import re
from pathlib import Path

import uadr_lib as lib

NAME = "secrets"
PATTERNS = [
    ("AWS access key id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private key block", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Stripe live key", re.compile(r"\b[sr]k_live_[0-9a-zA-Z]{20,}\b")),
    ("JSON web token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}")),
    ("credential in URL", re.compile(r"[a-z][a-z0-9+.-]*://[^/\s:@'\"]+:([^@\s/'\"]{6,})@", re.IGNORECASE)),
    ("hard-coded credential", re.compile(
        r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|auth[_-]?token|token)\b"
        r"\s*[:=]\s*['\"]([^'\"\s]{12,})['\"]")),
]
PLACEHOLDER = re.compile(r"(?i)(<|>|\{|\}|\$|\*{3,}|x{4,}|example|changeme|change-me|your[_-]|placeholder|dummy|redacted|\.\.\.)")
ENV_FILE = re.compile(r"(^|/)\.env(\.[\w-]+)?$")
SAFE_ENV_SUFFIX = (".example", ".sample", ".template", ".dist")


def run(root: Path, cfg: dict) -> tuple[list[str], list[str]]:
    errors = []
    allow = cfg.get("secrets", {}).get("allow_paths", [])
    for rel in lib.list_files(root):
        if any(lib.glob_match(g, rel) for g in allow):
            continue
        if ENV_FILE.search(rel) and not rel.endswith(SAFE_ENV_SUFFIX):
            errors.append(f"{rel}: environment file is not ignored by git; add it to .gitignore and keep secrets out of the repository")
            continue
        path = root / rel
        try:
            if path.stat().st_size > 1_000_000:
                continue
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\0" in raw[:4096]:
            continue
        for number, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
            if "uadr:allow-secret" in line:
                continue
            for kind, pattern in PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                value = match.group(1) if match.groups() else match.group(0)
                if match.groups() and PLACEHOLDER.search(value):
                    continue
                errors.append(f"{rel}:{number}: possible {kind} (value withheld). Remove it and rotate the credential; "
                              f"append 'uadr:allow-secret' to the line only for a verified false positive")
                break
    return errors, []
