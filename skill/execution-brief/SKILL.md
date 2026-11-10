---
name: execution-brief
description: Drafts a run card and a copy-ready prompt for a coding task, using the Claude Execution Playbook. Use when the user asks to prepare, scope, brief or write a prompt for a task before running it, or asks which model, effort level or topology a task should use.
argument-hint: [task description]
---

# Execution brief

Draft a run card and a prompt for this task: $ARGUMENTS

If no task was given, ask what the task is and wait.

## Reference files

These are in this skill's directory. Read the first two before choosing anything, and the third
when you fill in a template.

- [quick-reference.md](quick-reference.md): the decision rules on one page, including the tier
  roles, the independence test, the verification rungs and the rule for risky surfaces.
- [model-data.md](model-data.md): which model fills each tier, with a verification date.
- [templates.md](templates.md): the run card and every prompt template.

## How to draft

1. **Look before asking.** In a repository, read what it can tell you: where you are, the
   branch, whether the tree is clean, and the command that runs the checks. Then see what is
   still unknown. The usual gaps are the result the user wants, what has to stay as it is, and
   whether commit, push, pull request or release are allowed. Put those to the user together,
   once, skipping any they have already answered.
2. **Choose the session settings and the run plan** from quick-reference.md. For each choice
   that is not the default, give the reason in a few words. Write the tier first and then the
   model that model-data.md lists for it, and tell the user to confirm it is available where
   they work. If model-data.md was verified more than 90 days ago, say so.
3. **Pick the template** from templates.md: the quick prompt for a routine, bounded change with
   one obvious check; the execution prompt otherwise; the review brief for a review. Add a
   workflow plan when the topology is a workflow. If the task is on a risky surface and no
   proposal exists yet, draft a propose-mode brief instead of a change-mode one, and say why.
4. **Fill everything in.** No placeholder braces left. Write all four permissions out even when
   each is "no". Make the done conditions checkable and name the commands.
5. **Return the run card and the prompt**, each in its own fenced block so they can be copied,
   and the workflow plan as a third block when there is one. If you assumed something the user
   should confirm, add it underneath in a line or two.

## Limits

- Draft only. Do not start the task, edit files, or change the session's model or effort.
- Default to a single session with no checkpoints. Recommend subagents or a workflow only when
  the work passes the independence test, and name the independent pieces.
- Raise the tier or the effort level for hard reasoning or a weak check, and say which. Task
  size is not a reason.
- These are the playbook's recommendations, not Anthropic requirements. Where the user or the
  repository says something different, do what they say and mention the difference.
