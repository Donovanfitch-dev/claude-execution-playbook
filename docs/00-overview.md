# Overview: the decisions behind every run

When you hand a coding task to Claude, a set of decisions gets made whether or not you make them
on purpose: which model runs, how hard it thinks, whether one session or several do the work,
what it is allowed to touch, and what counts as finished. Left implicit, those decisions default
to whatever the session happened to be set to, and the result is hard to review afterwards.

This playbook makes each decision explicit, gives a default and a reason to move off it, and
records the outcome on a short **run card** that travels with the prompt.

## Five decisions

Three are **session settings**. Whoever starts the session applies them in the tool, for example
with `/model` and `/effort` in Claude Code or with request parameters on the API. A prompt
cannot change them for its own session. (A model for subagents or workflow agents is a separate
choice, made in their definitions or requested in the prompt.)

| Setting | The question it answers | Default | Chapter |
| --- | --- | --- | --- |
| Model | How much judgment does the task need? | Your environment's default model | [Model selection](01-model-selection.md) |
| Effort | How deeply should the model reason and check its own work? | The model's documented default | [Model selection](01-model-selection.md#effort) |
| Speed | Is a person waiting on the output? | Standard | [Model selection](01-model-selection.md#speed) |

Two make up the **run plan**. You decide them up front, write them on the run card, and also
state them in the prompt, because the model carries them out.

| Plan | The question it answers | Default | Chapter |
| --- | --- | --- | --- |
| Topology | Does the work split into independent pieces? | One session | [Topology and strategy](02-topology-and-strategy.md) |
| Strategy (checkpoints, unit of work) | Where does the run pause, and is it working through a list? | No checkpoints; the whole task | [Topology and strategy](02-topology-and-strategy.md#execution-strategy) |

## Four boundaries

These go into the prompt, because the model has to act on them.

| Boundary | The question it answers | Chapter |
| --- | --- | --- |
| Scope | What may change, and what must not? | [Authority and safety](04-authority-and-safety.md#scope) |
| Authority | May it only look, propose, or change things? May it commit, push or release? | [Authority and safety](04-authority-and-safety.md) |
| Proof | What observable result means the task is done, and which checks show it? | [Verification](06-verification.md) |
| Exit | When does it stop and ask, what happens on a miss, and what does the report contain? | [Fallback](07-fallback-and-escalation.md), [Completion](08-completion-and-release.md) |

[Prompt construction](03-prompt-construction.md) turns the plan and the boundaries into a
prompt, and [Workspace isolation](05-workspace-isolation.md) covers the Git state the session
runs in.

## Two ground rules

### 1. The decisions are independent

A stronger model is not a reason to add agents. A large task is not a reason to raise effort.
Parallel workers do not make an answer more correct. Decide each one on its own evidence.

Vendor tooling draws the same line. The Claude Code documentation describes ultracode as "a
Claude Code setting rather than a model effort level": it turns on workflow orchestration for the
session at whichever effort level the session runs at
([model configuration](https://code.claude.com/docs/en/model-config)). When a product bundles
decisions behind one switch, write each underlying decision on the run card anyway.

### 2. Principles are stable; model facts are not

Which model is current, what it costs, which effort levels it accepts and where a feature is
available all change, sometimes within weeks. This playbook keeps every such fact in one dated
file, [model data](model-data.md), and the chapters refer to four tier names instead:

| Tier | Role |
| --- | --- |
| Light | High-volume, latency-sensitive, narrow sub-tasks |
| Everyday | Known-path implementation with a strong check |
| Advanced | Judgment-heavy and long-running work; the usual starting point |
| Maximum | The hardest reasoning and longest-horizon work, after a measured shortfall |

The snapshot in this repository is the least reliable source you have for what a model can do.
Current vendor documentation is better, and it tells you a capability exists. Only your own
environment tells you the capability is switched on for your account, your provider and your
client version, so look there before a run card depends on it.

## How to read the text

Two kinds of statement appear in these chapters.

- **Vendor facts** say what Anthropic documents and name the page. They were checked on the date
  shown in [model data](model-data.md) and can go stale.
- **Recommendations** are everything else. They are this playbook's opinion: illustrative
  defaults, not Anthropic requirements, and not validated on your workload.

If the task owner or the repository's own instructions say something different from this
playbook, follow them. This project is not affiliated with, endorsed by, or certified by
Anthropic.

## Where to start

| If you want to... | Read |
| --- | --- |
| Use it in five minutes | [Quick reference](quick-reference.md), then copy a [template](../templates/README.md) |
| Pick a model and effort level | [Model selection](01-model-selection.md) |
| Decide whether to use subagents or a workflow | [Topology and strategy](02-topology-and-strategy.md) |
| Write a prompt that holds up | [Prompt construction](03-prompt-construction.md) |
| See it applied | [Examples](../examples/README.md) |

## Terms

- **Run card**: the one-screen record of the decisions and boundaries for a task.
- **Operator**: the person (or script) that starts the session and applies its settings.
- **Work item**: one task with one objective, one repository and one definition of done.
- **Check**: something runnable whose result is pass or fail.
- **Miss**: a run that ended without meeting its done conditions.
