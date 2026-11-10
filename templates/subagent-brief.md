# Subagent brief

**Use when:** handing one bounded, independent task to a worker session. Apply the
[independence test](../docs/02-topology-and-strategy.md#the-independence-test) first.

**How to fill it in:** replace each `{{placeholder}}`. The worker knows only what is written
here, so include what you have already ruled out and where to look. Ask for the answer in the
exact shape you need, because the summary is all you will see.

```text
Goal: {{the one question to answer or the one change to make}}
Why: {{what the result will be used for}}

What is already known:
- {{finding or decision, so the worker does not redo it}}
- {{what has been ruled out}}

Where to look: {{files, directories, commands; or a bounded way to find them}}
Out of bounds: {{what not to read, run or change}}

You may: {{read only | edit these paths in your own worktree: ...}}
You may not: commit, push, release, contact external services, or start further workers.

Return exactly this:
1. Answer: {{one paragraph | a list of items with file and line}}
2. Evidence: the commands you ran and the relevant output, per item.
3. Confidence: what you checked directly, and what you inferred.
4. Not done: anything you could not complete, and why.
Keep the report under {{length}}. Do not include full file contents or logs.
```

## Notes

- **One purpose per worker.** A brief with two goals returns two half-answers.
- **Writers get their own checkout.** See
  [workspace isolation](../docs/05-workspace-isolation.md#for-delegated-writers).
- **Set the worker's model and effort deliberately.** Collection and mechanical work rarely need
  the main session's settings.
- **Verify before acting.** Treat the returned report as evidence to check, not as a result to
  paste into your own report.
