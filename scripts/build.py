#!/usr/bin/env python3
"""Build the generated files of the Claude Execution Playbook.

The modular documents under docs/, templates/ and examples/ are the only source.
This script generates, from them:

  dist/claude-execution-playbook.md      the single-file edition
  skill/execution-brief/*.md             reference copies bundled with the skill
  dist/release/*                         versioned release assets (with --package)

Usage:
  python3 scripts/build.py            write the generated files
  python3 scripts/build.py --check    exit 1 if a generated file is missing or stale
  python3 scripts/build.py --package  also write the release assets

Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import posixpath
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = "claude-execution-playbook"
REPO_URL = "https://github.com/Donovanfitch-dev/claude-execution-playbook"
SINGLE_FILE = f"dist/{NAME}.md"

# Order of the single-file edition. Each entry is (group title, files).
PARTS: list[tuple[str, list[str]]] = [
    (
        "Reference",
        [
            "docs/00-overview.md",
            "docs/01-model-selection.md",
            "docs/02-topology-and-strategy.md",
            "docs/03-prompt-construction.md",
            "docs/04-authority-and-safety.md",
            "docs/05-workspace-isolation.md",
            "docs/06-verification.md",
            "docs/07-fallback-and-escalation.md",
            "docs/08-completion-and-release.md",
            "docs/quick-reference.md",
            "docs/model-data.md",
        ],
    ),
    (
        "Templates",
        [
            "templates/README.md",
            "templates/run-card.md",
            "templates/execution-prompt.md",
            "templates/quick-prompt.md",
            "templates/subagent-brief.md",
            "templates/workflow-plan.md",
            "templates/review-brief.md",
            "templates/handoff-note.md",
            "templates/completion-report.md",
            "templates/claude-md-snippet.md",
        ],
    ),
    (
        "Examples",
        [
            "examples/README.md",
            "examples/01-routine-coding-task.md",
            "examples/02-architectural-implementation.md",
            "examples/03-multi-agent-workflow.md",
            "examples/04-independent-security-review.md",
        ],
    ),
]

# Reference files bundled with the skill: output path -> source files.
SKILL_DIR = "skill/execution-brief"
SKILL_REFS: dict[str, list[str]] = {
    f"{SKILL_DIR}/quick-reference.md": ["docs/quick-reference.md"],
    f"{SKILL_DIR}/model-data.md": ["docs/model-data.md"],
    f"{SKILL_DIR}/templates.md": [f for f in PARTS[1][1] if not f.endswith("README.md")],
}

# Files and directories copied into the release archive.
PACKAGE_FILES = [
    "README.md",
    "LICENSE",
    "LICENSE-TEMPLATES",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "RELEASING.md",
    "VERSION",
    ".gitignore",
    ".markdownlint-cli2.jsonc",
    ".github/workflows/ci.yml",
]
PACKAGE_DIRS = ["docs", "templates", "examples", "skill", "scripts", "tests"]

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
CODE_SPAN_RE = re.compile(r"(`+[^`]*`+)")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
VERIFIED_RE = re.compile(r"\*\*Verified: (\d{4}-\d{2}-\d{2})\*\*")


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- markdown helpers


def iter_lines(text: str):
    """Yield (line, in_code). in_code is True for fence lines and everything inside a fence."""
    fence: tuple[str, int] | None = None
    for line in text.split("\n"):
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = (match.group(1)[0], len(match.group(1)))
                yield line, True
            else:
                yield line, False
        else:
            closes = (
                match is not None
                and match.group(1)[0] == fence[0]
                and len(match.group(1)) >= fence[1]
                and not match.group(2).strip()
            )
            if closes:
                fence = None
            yield line, True


def heading_text(raw: str) -> str:
    """Visible text of a heading: code spans and links reduced to their text."""
    text = re.sub(r"`([^`]*)`", r"\1", raw)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("*", "")
    return text.strip()


def slugify(text: str) -> str:
    """GitHub-style heading anchor, before de-duplication."""
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


class Slugger:
    """Assigns anchors the way GitHub does: repeats get -1, -2, ..."""

    def __init__(self) -> None:
        self.seen: dict[str, int] = {}

    def slug(self, text: str) -> str:
        base = slugify(text)
        count = self.seen.get(base, 0)
        self.seen[base] = count + 1
        return base if count == 0 else f"{base}-{count}"


def headings(text: str) -> list[tuple[int, str, str]]:
    """(level, visible text, anchor within this file) for each heading outside code."""
    slugger = Slugger()
    found = []
    for line, in_code in iter_lines(text):
        if in_code:
            continue
        match = HEADING_RE.match(line)
        if match:
            visible = heading_text(match.group(2))
            found.append((len(match.group(1)), visible, slugger.slug(visible)))
    return found


def split_target(source: str, target: str) -> tuple[str, str] | None:
    """Resolve a link target to (repo-relative path, fragment). None for external links."""
    if SCHEME_RE.match(target):
        return None
    path, _, fragment = target.partition("#")
    if not path:
        return source, fragment
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), path)), fragment


def rewrite_links(line: str, replace) -> str:
    """Apply replace(text, target) -> str to every link outside inline code."""
    pieces = CODE_SPAN_RE.split(line)
    for index in range(0, len(pieces), 2):
        pieces[index] = LINK_RE.sub(lambda m: replace(m.group(1), m.group(2)), pieces[index])
    return "".join(pieces)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def version() -> str:
    return read("VERSION").strip()


def verified_date() -> str:
    match = VERIFIED_RE.search(read("docs/model-data.md"))
    if not match:
        raise BuildError("docs/model-data.md has no '**Verified: YYYY-MM-DD**' line")
    return match.group(1)


# ---------------------------------------------------------------- single-file edition


def build_single_file() -> str:
    files = [path for _, paths in PARTS for path in paths]
    texts = {path: read(path) for path in files}

    slugger = Slugger()
    slugger.slug("Claude Execution Playbook")
    slugger.slug("Contents")

    anchor: dict[tuple[str, str], str] = {}  # (file, anchor in file) -> anchor in edition
    file_anchor: dict[str, str] = {}
    titles: dict[str, str] = {}
    for path in files:
        found = headings(texts[path])
        if not found or found[0][0] != 1:
            raise BuildError(f"{path}: must start with a level-1 heading")
        for index, (_, visible, local) in enumerate(found):
            final = slugger.slug(visible)
            anchor[(path, local)] = final
            if index == 0:
                file_anchor[path] = final
                titles[path] = visible

    out: list[str] = [
        "# Claude Execution Playbook",
        "",
        f"Single-file edition, version {version()}. Generated from the modular documents in the",
        "repository by `scripts/build.py`. Do not edit this file by hand.",
        "",
        f"- Model and platform data verified: {verified_date()}",
        "- Text licensed under CC BY 4.0. Templates, skill and scripts under MIT-0.",
        "- Unofficial. Not affiliated with, endorsed by, or certified by Anthropic.",
        f"- Source: <{REPO_URL}>",
        "",
        "## Contents",
        "",
    ]
    for title, paths in PARTS:
        out.append(f"- {title}")
        for path in paths:
            out.append(f"  - [{titles[path]}](#{file_anchor[path]})")
    out.append("")

    for path in files:

        def replace(text: str, target: str, source: str = path) -> str:
            resolved = split_target(source, target)
            if resolved is None:
                return f"[{text}]({target})"
            rel, fragment = resolved
            if rel not in texts:
                raise BuildError(f"{source}: link to '{target}' leaves the single-file edition")
            if not fragment:
                return f"[{text}](#{file_anchor[rel]})"
            if (rel, fragment) not in anchor:
                raise BuildError(f"{source}: no heading '#{fragment}' in {rel}")
            return f"[{text}](#{anchor[(rel, fragment)]})"

        out.append("---")
        out.append("")
        for line, in_code in iter_lines(texts[path].rstrip("\n")):
            if in_code:
                out.append(line)
                continue
            match = HEADING_RE.match(line)
            if match:
                if len(match.group(1)) >= 6:
                    raise BuildError(f"{path}: heading too deep to demote: {line}")
                out.append("#" + line)
            else:
                out.append(rewrite_links(line, replace))
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


# ---------------------------------------------------------------- skill reference files


def build_skill_ref(sources: list[str], title: str | None = None) -> str:
    """Concatenate sources for use outside the repository: relative links become plain text.

    With a title, the sources become sections under one level-1 heading.
    """

    def replace(text: str, target: str) -> str:
        return f"[{text}]({target})" if SCHEME_RE.match(target) else text

    out: list[str] = []
    if title:
        out += [f"# {title}", ""]
    out += ["<!-- Generated by scripts/build.py from the playbook sources. Do not edit. -->", ""]
    for index, path in enumerate(sources):
        if index:
            out += ["---", ""]
        for line, in_code in iter_lines(read(path).rstrip("\n")):
            if in_code:
                out.append(line)
            elif title and HEADING_RE.match(line):
                out.append("#" + line)
            else:
                out.append(rewrite_links(line, replace))
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def generated() -> dict[str, str]:
    outputs = {SINGLE_FILE: build_single_file()}
    for target, sources in SKILL_REFS.items():
        title = "Templates" if len(sources) > 1 else None
        outputs[target] = build_skill_ref(sources, title)
    return outputs


# ---------------------------------------------------------------- release package


def _zip(target: Path, members: list[tuple[str, bytes]]) -> None:
    """Write a reproducible archive: sorted names, fixed timestamps and permissions."""
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)


def package(outputs: dict[str, str]) -> list[Path]:
    tag = f"v{version()}"
    release = ROOT / "dist" / "release"
    release.mkdir(parents=True, exist_ok=True)
    for old in release.iterdir():
        old.unlink()

    single = release / f"{NAME}-{tag}.md"
    single.write_bytes(outputs[SINGLE_FILE].encode("utf-8"))

    prefix = f"{NAME}-{tag}"
    members: list[tuple[str, bytes]] = [
        (f"{prefix}/{SINGLE_FILE}", outputs[SINGLE_FILE].encode("utf-8"))
    ]
    for name in PACKAGE_FILES:
        members.append((f"{prefix}/{name}", (ROOT / name).read_bytes()))
    for directory in PACKAGE_DIRS:
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and path.name != ".DS_Store" and "__pycache__" not in path.parts:
                rel = path.relative_to(ROOT).as_posix()
                members.append((f"{prefix}/{rel}", path.read_bytes()))
    full = release / f"{NAME}-{tag}.zip"
    _zip(full, members)

    skill_members = [
        (f"execution-brief/{path.name}", path.read_bytes())
        for path in sorted((ROOT / SKILL_DIR).iterdir())
        if path.is_file() and path.name != ".DS_Store"
    ]
    skill = release / f"{NAME}-skill-{tag}.zip"
    _zip(skill, skill_members)

    assets = [single, full, skill]
    sums = release / "SHA256SUMS.txt"
    sums.write_text(
        "".join(
            f"{hashlib.sha256(asset.read_bytes()).hexdigest()}  {asset.name}\n" for asset in assets
        ),
        encoding="utf-8",
    )
    return assets + [sums]


# ---------------------------------------------------------------- entry point


def stale(outputs: dict[str, str]) -> list[str]:
    problems = []
    for target, content in outputs.items():
        path = ROOT / target
        if not path.exists():
            problems.append(f"{target}: missing")
        elif path.read_text(encoding="utf-8") != content:
            problems.append(f"{target}: out of date")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="verify generated files are current")
    parser.add_argument("--package", action="store_true", help="also write release assets")
    args = parser.parse_args(argv)

    try:
        outputs = generated()
    except BuildError as error:
        print(f"build error: {error}", file=sys.stderr)
        return 1

    if args.check:
        problems = stale(outputs)
        for problem in problems:
            print(f"stale: {problem}", file=sys.stderr)
        if problems:
            print("run: python3 scripts/build.py", file=sys.stderr)
            return 1
        print(f"generated files are current ({len(outputs)} files)")
        return 0

    for target, content in outputs.items():
        path = ROOT / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {target}")
    if args.package:
        for asset in package(outputs):
            print(f"wrote {asset.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
