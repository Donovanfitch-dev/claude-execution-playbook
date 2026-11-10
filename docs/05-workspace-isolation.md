# Workspace and Git isolation

Most damage from an agent session is not a bad line of code. It is a good change made in the
wrong place: the wrong repository, a stale branch, or a checkout another session was already
using. This chapter is about making the place unambiguous, and Git worktrees are the main tool.

## One writer per checkout

Two sessions writing to the same checkout each see the other's half-finished edits as the state
of the code. Tests fail for reasons neither caused, and each "fixes" the other's work. The rule
that prevents it is simple: at any moment, a checkout has one writer.

Across repositories that happens naturally: a directory and a session for each. Inside one
repository it takes a worktree for each task, which gives every session its own directory and
branch over the same history.

## Worktrees

### With Claude Code

Claude Code can create the worktree for you
([worktrees](https://code.claude.com/docs/en/worktrees)):

```bash
claude --worktree feature-auth     # or: claude -w feature-auth
```

That page says this creates the worktree under `.claude/worktrees/<name>/` at the repository
root on a new branch named `worktree-<name>`, branched by default from the repository's default
branch, and it recommends adding `.claude/worktrees/` to `.gitignore`.

A worktree is a fresh checkout: gitignored files such as `.env` are not there and dependencies
are not installed. The same page describes a `.worktreeinclude` file at the repository root that
copies the gitignored files you list into each new worktree. The Claude Code
[best practices](https://code.claude.com/docs/en/best-practices) page advises keeping that list
to small files, because it copies. This playbook adds: do not copy credentials a task does not
need.

### With plain Git

```bash
git worktree add ../project-feature-a -b feature-a    # new branch in a new directory
cd ../project-feature-a && claude                     # start the session there

git worktree list                                     # see what exists
git worktree remove ../project-feature-a              # clean up when merged
```

### For delegated writers

When a subagent or a workflow agent edits files, give it its own checkout. In Claude Code, a
subagent definition can set `isolation: worktree`
([subagents](https://code.claude.com/docs/en/sub-agents)):

```markdown
---
name: call-site-migrator
description: Rewrites call sites of one function across the files it is given
isolation: worktree
---

Rewrite every call site in the files you are given, run the checks named in the
brief, and report the result per file.
```

Read-only workers do not need isolation; writers do.

### Cleaning up

What Claude Code does with a worktree when an interactive session exits depends on its state,
according to the [worktrees](https://code.claude.com/docs/en/worktrees) page:

- A clean worktree from an unnamed session is removed automatically, with its branch.
- A clean worktree from a named session, and any worktree with work in it, gets a prompt to keep
  or remove.
- Non-interactive runs (`claude -p --worktree`) have no exit prompt, so nothing is cleaned up.
  Remove those yourself with `git worktree remove <path>`; if Git refuses because the worktree
  is locked, run `git worktree unlock <path>` first.

Put the worktree and branch state in the final report so nothing is left orphaned.

## Before the first edit

Four commands establish where a session is:

```bash
git rev-parse --show-toplevel     # which repository
git branch --show-current         # which branch
git status --short                # what is already modified
git worktree list                 # which checkouts exist
```

If `git status` shows modifications the task did not make, they belong to someone. Leave them
alone: no stash, no reset, no reformatting. Mention them in the report.

## Keeping a session on one task

A session that drifts across tasks ends with a diff nobody can review. Two habits keep it on
one:

- **Side findings become notes.** When the session notices an unrelated problem, it lists it as
  a follow-up and carries on.
- **A change that spans repositories is several tasks.** Write down what the repositories must
  agree on (the interface, the order of release) first, then run one task per repository, each
  with its own scope and checks.

## Handing over

A long conversation accumulates context that was true earlier and may not be now. Start a new
session when the old context would mislead more than it helps:

- **A different place.** Another repository or another worktree.
- **A different goal.** The task that follows is not a continuation of this one.
- **A different role.** The next step is a review, and the reviewer should not have watched the
  work being done.

Moving from planning to implementation is the most common boundary. Hand over with a written
[handoff note](../templates/handoff-note.md) instead of relying on conversation history. The
note has to stand on its own: goal, decisions made, state of the workspace, what is verified,
what is next. If you cannot write it, the plan is not finished.

## Leaving the workspace clean

A session ends cleanly when its final report answers three questions.

| Question | Evidence |
| --- | --- |
| What changed? | `git status` and `git diff`, with every changed file explained by the task |
| What proves it? | The checks that ran and their output; the checks that did not run |
| What is left behind? | Branches, worktrees, uncommitted edits, stale documentation, follow-up items |

Someone who never saw the conversation should be able to pick the work up from that report and
the repository alone.
