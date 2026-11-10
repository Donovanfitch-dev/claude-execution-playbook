# Execution prompt

**Use when:** the task is consequential, multi-step, or will run unattended. For routine work use
the [quick prompt](quick-prompt.md).

**How to fill it in:** replace each `{{placeholder}}` and delete lines that do not apply. Keep
all six blocks; an empty block is a decision you have not made yet. Paste long reference
material above the prompt, not inside it. Background:
[prompt construction](../docs/03-prompt-construction.md).

```text
<task>
{{the finished result, in one or two sentences}}
Mode: {{investigate | propose | change | review}}
</task>

<proof>
The task is done when all of these are true:
- {{observable condition}}
- {{observable condition}}
- {{the verification rung you require, for example: targeted tests pass, including one that failed before}}
Show it with:
- {{command}}: {{what it demonstrates}}
- {{command}}: {{what it demonstrates}}
For each check give the command, its exit status and the lines of output that matter.
If a check cannot run, say "not run" and why.
If a check fails: {{what to try, and how many attempts before you stop and report}}.
</proof>

<background>
Why: {{who needs this and what it unblocks}}
Decided already: {{decisions and constraints that are not written in the repository}}
Found so far: {{earlier findings, and where each came from}}
Read first: {{specification or ticket}}, then {{the code involved}}, then {{tests and documents}}.
If they disagree and it matters: {{which one is right | pause and tell me}}.
</background>

<boundaries>
May change: {{paths, components or systems}}
Must not change: {{interfaces, files, behaviours}}, or any uncommitted work already in the tree.
Make the smallest change that meets the proof. If you notice something else worth fixing, list
it in the report instead of fixing it.
Topology: {{single session | up to N subagents, one purpose each | a workflow, as planned}}
Checkpoints: {{none | pause after ..., show me ..., and wait}}
Unit of work: {{the whole task | each ..., checked and reported one by one}}
Permissions: commit {{yes or no}}; push {{yes or no}}; pull request {{yes or no}}; release {{yes or no}}.
If that line does not grant a step, do not take it.
</boundaries>

<stop_and_ask>
Carry on without asking for anything you can undo. Pause and tell me what you found when:
- the only way forward touches something outside "may change";
- a step cannot be undone and the Permissions line does not grant it;
- you lack access: a permission, a credential or a tool;
- this brief and the repository disagree, and the difference matters;
- you are not sure which repository, branch or environment you are in;
- {{task-specific trigger}}
</stop_and_ask>

<final_report>
First line: what is true now, and one status word (verified, unverified, partial, blocked,
not started). Then, briefly and in this order:
- Changes: what you touched and why.
- Evidence: each check with its command and result.
- Not verified: checks that did not run, and anything you assumed.
- Differences from this brief, if any, and why.
- Workspace: branch, uncommitted changes, commits, and whether anything was pushed or released.
- Follow-ups: things you noticed and left alone.
Report only what you ran or read during this task, and mark anything that is an inference.
</final_report>
```

## Variations

- **Investigate or propose mode:** write "nothing" under `May change` and set every permission
  to "no". The proof becomes "the report answers these questions, with evidence".
- **Checkpoints:** name each one and the evidence it needs, for example "after the migration is
  written, show it applying and rolling back on the test database, then wait".
- **A list of items:** say what the item is and which check applies to each, and ask for a
  result per item in the report.
- **"Release"** on the Permissions line covers merge, tag, publish and deploy. If you grant it,
  name exactly what and where.
