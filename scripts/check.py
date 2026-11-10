#!/usr/bin/env python3
"""Consistency checks for the Claude Execution Playbook.

Offline checks (default, used in CI):
  inventory   every source document is included in the single-file edition
  links       every relative link resolves to a file, and every #fragment to a heading
  templates   each template has one copy block with placeholders
  examples    each example is complete and matches the templates it says it uses
  volatile    versioned model names, model IDs and prices appear only where allowed
  freshness   docs/model-data.md carries a verification date (warning when old)
  hygiene     no personal paths, non-example email addresses or unfinished markers
  generated   the single-file edition and the skill reference files are current

Online check:
  python3 scripts/check.py --external    request every external URL once

Standard library only. Exit status 1 when any check fails.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
GENERATED = {build.SINGLE_FILE, *build.SKILL_REFS}
SKIP_DIRS = {".git", "node_modules", "release", ".venv", "__pycache__"}

# Files allowed to name model versions, IDs and prices.
VOLATILE_ALLOWED = ("docs/model-data.md", "examples/", "CHANGELOG.md")
VOLATILE_PATTERNS = [
    (re.compile(r"\b(?:Haiku|Sonnet|Opus|Fable|Mythos) \d"), "versioned model name"),
    (re.compile(r"\bclaude-(?:haiku|sonnet|opus|fable|mythos)-\d"), "model ID"),
    (re.compile(r"\$\d"), "price"),
]
STALE_AFTER_DAYS = 90

HYGIENE_PATTERNS = [
    (re.compile(r"/Users/|/home/[a-z]|[A-Z]:\\\\Users"), "personal filesystem path"),
    (re.compile(r"\b(?:TODO|FIXME|TBD|XXX)\b"), "unfinished marker"),
    (re.compile(r"\{\{\s*\}\}"), "empty placeholder"),
]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMAIL_OK_RE = re.compile(r"@(?:example\.(?:com|org|net)|[a-z0-9-]+\.test|users\.noreply\.github\.com)$")

URL_RE = re.compile(r"https?://[^\s<>)\]\"'`]+")
PLACEHOLDER_RE = re.compile(r"\{\{[^{}]+\}\}")
TAG_RE = re.compile(r"^</?([a-z_]+)>$")
LABEL_RE = re.compile(r"^([A-Z][A-Za-z ]*?):(?:\s|$)")

EXAMPLE_SECTIONS = [
    "Situation",
    "Configuration",
    "Prompt",
    "Validation criteria",
    "What would change the recommendation",
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"{where}: {message}")


def markdown_files() -> list[str]:
    found = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT)
        if not SKIP_DIRS.intersection(rel.parts):
            found.append(rel.as_posix())
    return found


def prose_lines(text: str):
    """(line number, line) for lines outside fenced code."""
    for number, (line, in_code) in enumerate(build.iter_lines(text), 1):
        if not in_code:
            yield number, line


def fenced_blocks(text: str) -> list[tuple[str, list[str]]]:
    """(info string, content lines) for each fenced block."""
    blocks: list[tuple[str, list[str]]] = []
    fence: tuple[str, int] | None = None
    info = ""
    current: list[str] = []
    for line in text.split("\n"):
        match = build.FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = (match.group(1)[0], len(match.group(1)))
                info = match.group(2).strip()
                current = []
        elif (
            match
            and match.group(1)[0] == fence[0]
            and len(match.group(1)) >= fence[1]
            and not match.group(2).strip()
        ):
            blocks.append((info, current))
            fence = None
        else:
            current.append(line)
    return blocks


def links(text: str):
    """(line number, target) for each link outside code."""
    for number, line in prose_lines(text):
        pieces = build.CODE_SPAN_RE.split(line)
        for index in range(0, len(pieces), 2):
            for match in build.LINK_RE.finditer(pieces[index]):
                yield number, match.group(2)


# ---------------------------------------------------------------- checks


def check_inventory(report: Report, files: list[str]) -> None:
    """Every source document is part of the single-file edition, and nothing listed is missing."""
    listed = [path for _, paths in build.PARTS for path in paths]
    for path in listed:
        if not (ROOT / path).exists():
            report.error(path, "listed in scripts/build.py but missing")
    for path in files:
        if path.startswith(("docs/", "templates/", "examples/")) and path not in listed:
            report.error(path, "not included in the single-file edition (add it to PARTS)")


def check_links(report: Report, files: list[str]) -> None:
    anchors = {
        path: {anchor for _, _, anchor in build.headings(build.read(path))} for path in files
    }
    for path in files:
        for number, target in links(build.read(path)):
            resolved = build.split_target(path, target)
            if resolved is None:
                continue
            rel, fragment = resolved
            if not (ROOT / rel).exists():
                report.error(f"{path}:{number}", f"broken link: {target}")
            elif fragment and rel in anchors and fragment not in anchors[rel]:
                report.error(f"{path}:{number}", f"no heading '#{fragment}' in {rel}")


def copy_block(path: str) -> list[str]:
    blocks = fenced_blocks(build.read(path))
    return blocks[0][1] if blocks else []


def block_tags(lines: list[str]) -> list[str]:
    """Names of XML-style blocks opened in a prompt, in order."""
    tags = []
    for line in lines:
        match = TAG_RE.match(line.strip())
        if match and not line.strip().startswith("</"):
            tags.append(match.group(1))
    return tags


def block_labels(lines: list[str]) -> list[str]:
    return [m.group(1) for line in lines if (m := LABEL_RE.match(line))]


def check_templates(report: Report) -> None:
    for path in build.PARTS[1][1]:
        if path.endswith("README.md"):
            continue
        blocks = fenced_blocks(build.read(path))
        if not blocks:
            report.error(path, "template has no fenced copy block")
            continue
        info, lines = blocks[0]
        if info != "text":
            report.error(path, f"copy block must be a 'text' fence, found '{info}'")
        if not PLACEHOLDER_RE.search("\n".join(lines)):
            report.error(path, "copy block has no {{placeholder}}")
        opened = block_tags(lines)
        closed = [
            TAG_RE.match(line.strip()).group(1)
            for line in lines
            if line.strip().startswith("</") and TAG_RE.match(line.strip())
        ]
        if opened != closed:
            report.error(path, f"unbalanced prompt blocks: opened {opened}, closed {closed}")


def check_examples(report: Report) -> None:
    run_card_labels = block_labels(copy_block("templates/run-card.md"))
    plan_labels = block_labels(copy_block("templates/workflow-plan.md"))
    tag_templates = {
        "execution-prompt.md": block_tags(copy_block("templates/execution-prompt.md")),
        "review-brief.md": block_tags(copy_block("templates/review-brief.md")),
    }
    for path in build.PARTS[2][1]:
        if path.endswith("README.md"):
            continue
        text = build.read(path)
        if PLACEHOLDER_RE.search(text):
            report.error(path, "example still contains a {{placeholder}}")
        titles = [visible for level, visible, _ in build.headings(text) if level == 2]
        for section in EXAMPLE_SECTIONS:
            if section not in titles:
                report.error(path, f"missing section '## {section}'")
        blocks = [lines for _, lines in fenced_blocks(text)]
        used = next(
            (para for para in text.split("\n\n") if para.startswith("Templates used:")), ""
        )
        if not used:
            report.error(path, "missing 'Templates used:' paragraph")

        cards = [lines for lines in blocks if lines and lines[0].strip() == "RUN CARD"]
        if len(cards) != 1:
            report.error(path, f"expected one RUN CARD block, found {len(cards)}")
        else:
            missing = [label for label in run_card_labels if label not in block_labels(cards[0])]
            if missing:
                report.error(path, f"run card is missing fields: {', '.join(missing)}")

        if "workflow-plan.md" in used:
            plans = [lines for lines in blocks if lines and lines[0].strip() == "WORKFLOW PLAN"]
            if len(plans) != 1:
                report.error(path, f"expected one WORKFLOW PLAN block, found {len(plans)}")
            else:
                missing = [label for label in plan_labels if label not in block_labels(plans[0])]
                if missing:
                    report.error(path, f"workflow plan is missing fields: {', '.join(missing)}")

        for name, tags in tag_templates.items():
            if name in used and not any(block_tags(lines) == tags for lines in blocks):
                report.error(path, f"no prompt block with the {name} blocks in order: {tags}")


def check_volatile(report: Report, files: list[str]) -> None:
    for path in files:
        if path in GENERATED or path.startswith(VOLATILE_ALLOWED):
            continue
        for number, line in enumerate(build.read(path).split("\n"), 1):
            for pattern, label in VOLATILE_PATTERNS:
                if pattern.search(line):
                    report.error(
                        f"{path}:{number}",
                        f"{label} outside docs/model-data.md and examples/: {line.strip()[:80]}",
                    )


def check_freshness(report: Report, today: datetime.date) -> None:
    try:
        verified = datetime.date.fromisoformat(build.verified_date())
    except (build.BuildError, ValueError) as error:
        report.error("docs/model-data.md", str(error))
        return
    age = (today - verified).days
    if age < 0:
        report.error("docs/model-data.md", f"verification date {verified} is in the future")
    elif age > STALE_AFTER_DAYS:
        report.warn(
            "docs/model-data.md",
            f"verified {age} days ago ({verified}); re-verify against the vendor documentation",
        )


def check_hygiene(report: Report, files: list[str]) -> None:
    others = [
        p.relative_to(ROOT).as_posix()
        for p in sorted(ROOT.rglob("*"))
        if p.is_file()
        and p.suffix in {".py", ".yml", ".yaml", ".json", ".jsonc", ".txt", ""}
        and not SKIP_DIRS.intersection(p.relative_to(ROOT).parts)
    ]
    for path in files + others:
        try:
            text = build.read(path)
        except UnicodeDecodeError:
            report.error(path, "not valid UTF-8 text")
            continue
        for number, line in enumerate(text.split("\n"), 1):
            if path == "scripts/check.py":
                continue  # the patterns below would match their own definitions
            for pattern, label in HYGIENE_PATTERNS:
                if pattern.search(line):
                    report.error(f"{path}:{number}", f"{label}: {line.strip()[:80]}")
            for email in EMAIL_RE.findall(line):
                if not EMAIL_OK_RE.search(email):
                    report.error(f"{path}:{number}", f"email address: {email}")


def check_generated(report: Report) -> None:
    try:
        outputs = build.generated()
    except build.BuildError as error:
        report.error("scripts/build.py", str(error))
        return
    for problem in build.stale(outputs):
        report.error("generated", f"{problem} (run: python3 scripts/build.py)")


def check_external(report: Report, files: list[str]) -> None:
    urls: dict[str, str] = {}
    skipped: set[str] = set()
    own = build.REPO_URL.rsplit("/", 1)[0]
    for path in files:
        if path in GENERATED:
            continue
        for _, line in prose_lines(build.read(path)):
            for match in URL_RE.finditer(line):
                url = match.group(0).rstrip(".,;:").split("#")[0]
                if url.startswith(own):
                    skipped.add(url)
                else:
                    urls.setdefault(url, path)
    print(f"checking {len(urls)} external URLs")
    if skipped:
        print(f"not requested ({len(skipped)}): links to this project's own repositories")
    for url, path in sorted(urls.items()):
        request = urllib.request.Request(url, headers={"User-Agent": "playbook-link-check/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
        except (urllib.error.URLError, TimeoutError) as error:
            report.error(path, f"{url}: {error}")
            continue
        if status != 200:
            report.error(path, f"{url}: HTTP {status}")
        else:
            print(f"  200 {url}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--external", action="store_true", help="also request external URLs")
    parser.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    args = parser.parse_args(argv)

    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    files = markdown_files()
    report = Report()

    check_inventory(report, files)
    if report.errors:
        for error in report.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    check_links(report, files)
    check_templates(report)
    check_examples(report)
    check_volatile(report, files)
    check_freshness(report, today)
    check_hygiene(report, files)
    check_generated(report)
    if args.external:
        check_external(report, files)

    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}", file=sys.stderr)
    if report.errors:
        print(f"\n{len(report.errors)} problem(s) in {len(files)} Markdown files", file=sys.stderr)
        return 1
    print(f"all checks passed ({len(files)} Markdown files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
