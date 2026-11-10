# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html): a major version changes the meaning
of a template field or a tier, a minor version adds guidance or templates, and a patch version
corrects text or refreshes the model data.

## [1.0.0] - 2026-11-10

First public edition.

### Added

- Framework reference in nine chapters: overview, model selection, topology and strategy,
  prompt construction, authority and safety, workspace isolation, verification, fallback and
  escalation, completion and release.
- One-page quick reference.
- Model and platform data snapshot, verified against Anthropic's documentation on 2026-11-10:
  Claude Haiku 5.5, Claude Sonnet 5.5, Claude Opus 5.5 and Claude Fable 5.2, with limits,
  default effort on the Claude API and in Claude Code, prices, fast mode, lifecycle dates and
  the Claude Code facts the chapters rely on.
- Nine templates: run card, execution prompt, quick prompt, subagent brief, workflow plan,
  review brief, handoff note, completion report, CLAUDE.md snippet.
- Four worked examples on fictional repositories: routine coding task, complex architectural
  implementation, multi-agent repository workflow, independent security review.
- `execution-brief` skill for Claude Code.
- Single-file edition generated from the modular documents.
- Build script, consistency checker, unit tests and CI.
