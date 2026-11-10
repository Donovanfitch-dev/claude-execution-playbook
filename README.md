# Claude Execution Playbook

A decision framework and prompt-template kit for running coding tasks with Claude and Claude
Code. It helps you choose a model, an effort level and an execution topology on purpose, bound
what a session may touch and release, and get back a result you can verify.

> **Unofficial, and an architectural case study.** This project is not affiliated with,
> endorsed by, or certified by Anthropic. Its recommendations are the author's, not Anthropic
> requirements. It generalizes practices from private engineering work and was drafted with AI
> assistance (Claude Code). It does not describe, name or quantify any private system, and it
> contains no measured results.

## The idea

Every run involves five decisions and four boundaries. Most problems with agent-written changes
trace back to one of them having been left implicit.

| Decision | Default | Where it lives |
| --- | --- | --- |
| **Model** | Your environment's default | Applied in the tool |
| **Effort** | The model's documented default | Applied in the tool |
| **Speed** | Standard | Applied in the tool |
| **Topology** | One session | Run card and prompt |
| **Strategy** (checkpoints, unit of work) | No checkpoints; the whole task | Run card and prompt |

| Boundary | The question it answers |
| --- | --- |
| **Scope** | What may change, and what must not? |
| **Authority** | Look, propose or change? Commit, push, release? |
| **Proof** | What observable result means "done"? |
| **Exit** | When to stop and ask; what happens on a miss; what the report contains |

The playbook gives each one a default, a reason to move off the default, and a place on a
one-screen **run card** that travels with the prompt.

## Quick start

**Five minutes, no installation:**

1. Read the [quick reference](docs/quick-reference.md).
2. Copy the [run card](templates/run-card.md) and fill it in for your task.
3. Copy the [quick prompt](templates/quick-prompt.md) for routine work, or the
   [execution prompt](templates/execution-prompt.md) for anything consequential.
4. Compare with a [worked example](examples/README.md).

**As a Claude Code skill**, so `/execution-brief` drafts the run card and prompt for you:

```bash
git clone https://github.com/Donovanfitch-dev/claude-execution-playbook.git
mkdir -p ~/.claude/skills
cp -R claude-execution-playbook/skill/execution-brief ~/.claude/skills/
```

Then, in a Claude Code session:

```text
/execution-brief add rate limiting to the export endpoint
```

The skill drafts only. It does not start the task or change your session's model. To install it
for one repository instead, copy the folder to that repository's `.claude/skills/`.

**As a single file**, to read offline or attach as context to a project or conversation:
[dist/claude-execution-playbook.md](dist/claude-execution-playbook.md).

**As standing rules for a repository:** paste the
[CLAUDE.md snippet](templates/claude-md-snippet.md) into your project's `CLAUDE.md`.

## What is inside

| Path | Contents |
| --- | --- |
| [docs/00-overview.md](docs/00-overview.md) | The five decisions, the four boundaries, and the ground rules |
| [docs/01-model-selection.md](docs/01-model-selection.md) | **Model selection decision guide**: model, effort and speed |
| [docs/02-topology-and-strategy.md](docs/02-topology-and-strategy.md) | **Execution topology and strategy guide**: single session, subagents, workflows; checkpoints and units of work |
| [docs/03-prompt-construction.md](docs/03-prompt-construction.md) | How to build a prompt that states outcome, proof and boundaries |
| [docs/04-authority-and-safety.md](docs/04-authority-and-safety.md) | Task modes, scope, release permissions, what a prompt cannot enforce |
| [docs/05-workspace-isolation.md](docs/05-workspace-isolation.md) | Preflight, one session per work item, Git worktrees |
| [docs/06-verification.md](docs/06-verification.md) | A verification ladder and how to set up independent review |
| [docs/07-fallback-and-escalation.md](docs/07-fallback-and-escalation.md) | Classifying a miss; escalating one step at a time |
| [docs/08-completion-and-release.md](docs/08-completion-and-release.md) | The completion report and release steps |
| [docs/quick-reference.md](docs/quick-reference.md) | Everything above on one page |
| [docs/model-data.md](docs/model-data.md) | Dated snapshot of current models, limits and prices, with sources |
| [templates/](templates/README.md) | Nine copy-ready templates |
| [examples/](examples/README.md) | Four worked examples on fictional repositories |
| [skill/execution-brief/](skill/execution-brief/SKILL.md) | The Claude Code skill |
| [dist/](dist/claude-execution-playbook.md) | The single-file edition, generated from the above |

Chapters 00 to 08, the quick reference and the model data together are the framework reference.

## Examples

| Example | Configuration it demonstrates |
| --- | --- |
| [Routine coding task](examples/01-routine-coding-task.md) | One tier down; four-line prompt |
| [Complex architectural implementation](examples/02-architectural-implementation.md) | Propose first; a change with checkpoints on a payment path |
| [Multi-agent repository workflow](examples/03-multi-agent-workflow.md) | Planned fan-out with a pilot, one worktree per writer, a verify stage |
| [Independent security review](examples/04-independent-security-review.md) | Fresh, read-only reviewer working from criteria |

Each has a filled-in run card, a complete prompt, validation criteria, and a note on what would
change the recommendation.

## How current is the model information

Model names, IDs, limits and prices change often, so they live in one file,
[docs/model-data.md](docs/model-data.md), with a verification date and a link to the Anthropic
page each fact came from. The chapters and templates use tier names instead, and a CI check
fails if a versioned model name or a price appears anywhere else.

Treat that file as a snapshot. Before a decision depends on it, check the vendor page and your
own environment; the [model selection guide](docs/01-model-selection.md#verify-before-you-depend-on-it)
shows how.

## Status and limits

Checked on every push by CI:

- Internal links and heading anchors resolve.
- Every template has a copy block. Every example is complete, has no unfilled placeholders, and
  contains every run card field and every block of the structured templates it uses.
- Versioned model names and prices appear only in the model data file and the examples.
- The single-file edition and the skill's reference files match their sources.
- Markdown lint, and unit tests for the build script.

Checked by hand at release time: external links, and the model data against the vendor pages.

Not done, and not claimed:

- **No benchmarks.** The suggested settings are reasoned defaults. Nothing here was
  measured against alternatives, and none of it is validated on your workload.
- **The examples are illustrative.** The repositories are fictional, so their prompts have not
  been run against real code.
- **The skill is checked for format, not for output quality.** Its files follow the documented
  skill layout; the briefs it drafts have not been evaluated.
- **Claude Code specifics age.** Commands and limits are cited to the vendor documentation as of
  the verification date.

## Related repositories

- [llm-routing-gateway](https://github.com/Donovanfitch-dev/llm-routing-gateway): the same
  subject as running code. Policy-based model routing with explained decisions, fallbacks and
  replay testing. This playbook is the decision policy for a person or an agent; the gateway is
  a reference implementation of routing policy in a service. Neither depends on the other.
- [governed-agent-systems](https://github.com/Donovanfitch-dev/governed-agent-systems): design
  notes on agents that are allowed to act.

## Development

The modular documents are the only source. The single-file edition and the skill's reference
files are generated. The scripts need Python 3.10 or later and nothing else. The lint step
needs Node.js and network access.

```bash
python3 scripts/build.py                  # regenerate dist/ and the skill reference files
python3 scripts/build.py --check          # fail if a generated file is stale
python3 scripts/check.py                  # links, templates, examples, volatile data, freshness
python3 -m unittest discover -s tests     # unit tests for the build helpers
npx --yes markdownlint-cli2@0.24.0        # Markdown lint
python3 scripts/check.py --external       # also request every external URL
python3 scripts/build.py --package        # write release assets to dist/release/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to update the model data and
[RELEASING.md](RELEASING.md) for the release procedure. Changes are listed in
[CHANGELOG.md](CHANGELOG.md).

## License

- Text (documents, examples, README, single-file edition): [CC BY 4.0](LICENSE).
- Templates, skill and scripts: [MIT No Attribution](LICENSE-TEMPLATES). Copy a template into
  your own prompts without attribution.

Short quotations from Anthropic's documentation are attributed where they appear. "Claude" and
"Anthropic" are trademarks of Anthropic, PBC.
