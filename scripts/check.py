#!/usr/bin/env python3
"""Pre-ingestion check for agent-memory-starter files.

    python3 scripts/check.py projects decisions procedures
    python3 scripts/check.py path/to/file.md

Checks the rules that can be checked mechanically: frontmatter fields,
type matching the folder, ISO dates, headings and first sentences that
carry the subject, related files that exist, relative dates, and a few
secret patterns. It reports
and exits non-zero on failure. It never rewrites a file.
"""
import re
import sys
import pathlib

FIELDS = ["title", "type", "project", "tags", "date", "status", "related"]
TYPES = {"projects": "project", "decisions": "decision", "procedures": "procedure"}
STATUS = {
    "project": {"active", "delivered", "paused"},
    "decision": {"raw", "promoted"},
    "procedure": {"draft", "stable"},
}
RELATIVE = re.compile(
    r"\b(yesterday|today|tomorrow|last (week|month|quarter|year)|next (week|month|quarter|year)|recently"
    r"|hier|aujourd'hui|demain|la semaine derni[eè]re|le mois dernier|r[eé]cemment)\b",
    re.I,
)
SECRETS = re.compile(
    r"(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*\S{6,}"
    r"|https?://[^\s/]+:[^\s@]+@)",
    re.I,
)
STOP = {"the", "and", "for", "with", "over", "from", "into", "des", "les", "une", "pour", "sur", "chose", "new"}


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def subject_tokens(title):
    words = re.findall(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9'-]{2,}", title)
    return [w.lower() for w in words if w.lower() not in STOP]


def check(path):
    errors = []
    text = path.read_text(encoding="utf-8")
    fm, body = frontmatter(text)
    if fm is None:
        return [f"{path}: no frontmatter"]
    for f in FIELDS:
        if f not in fm or not fm[f] or fm[f].startswith("<"):
            errors.append(f"{path}: frontmatter field `{f}` missing or unfilled")
    folder = path.parent.name
    if folder in TYPES and fm.get("type") != TYPES[folder]:
        errors.append(f"{path}: type `{fm.get('type')}` does not match folder `{folder}`")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fm.get("date", "")):
        errors.append(f"{path}: date `{fm.get('date')}` is not YYYY-MM-DD")
    t = fm.get("type")
    if t in STATUS and fm.get("status") not in STATUS[t]:
        errors.append(f"{path}: status `{fm.get('status')}` not in {sorted(STATUS[t])}")

    tokens = subject_tokens(fm.get("title", ""))
    sections = re.split(r"^(?=## )", body, flags=re.M)
    for sec in sections:
        if not sec.startswith("## "):
            continue
        heading, _, rest = sec.partition("\n")
        first = re.sub(r"\s+", " ", rest.strip().split("\n\n")[0])[:300]
        h = heading.lower()
        if t != "decision" and tokens and not any(tok in h for tok in tokens):
            errors.append(f"{path}: heading `{heading[3:].strip()}` does not name the subject")
        if tokens and first and not any(tok in first.lower() for tok in tokens):
            errors.append(f"{path}: first sentence under `{heading[3:].strip()}` does not name the subject")

    for m in RELATIVE.finditer(body):
        errors.append(f"{path}: relative date `{m.group(0)}`")
    for m in SECRETS.finditer(text):
        errors.append(f"{path}: possible secret `{m.group(0)[:20]}…`")
    base = path.parent.parent
    for rel in [r.strip() for r in fm.get("related", "").strip("[]").split(",") if r.strip()]:
        if not (base / rel).exists():
            errors.append(f"{path}: related file `{rel}` not found")
    if "<" in fm.get("title", "") or re.search(r"^# <", body, re.M):
        errors.append(f"{path}: template placeholders left in place")
    return errors


def main(args):
    files = []
    for a in args or ["projects", "decisions", "procedures"]:
        p = pathlib.Path(a)
        if p.is_dir():
            files += sorted(p.glob("*.md"))
        elif p.is_file():
            files.append(p)
    if not files:
        print(__doc__)
        return 2
    errors = []
    for f in files:
        errors += check(f)
    for e in errors:
        print(e)
    print(f"{len(files)} file(s) checked, {len(errors)} issue(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
