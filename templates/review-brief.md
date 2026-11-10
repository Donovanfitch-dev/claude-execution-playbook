# Review brief

**Use when:** a session that did not write the change should check it. Start a fresh session or
subagent; do not continue the author's conversation.

**How to fill it in:** replace each `{{placeholder}}`. Give the reviewer the criteria and the
change. Leave out the author's explanation of why the change is correct.

```text
<task>
Review {{the diff, branch, pull request or artifact}} against the criteria below.
Mode: review. Do not edit files or fix what you find.
Permissions: commit no; push no; pull request no; release no.
</task>

<criteria>
The change is correct only if:
- {{done condition from the original task}}
- {{done condition from the original task}}
- {{invariant that must still hold}}
</criteria>

<sources>
The change: {{how to see it, for example a git diff command}}
The specification: {{path or text}}
You may read any file in the repository and run read-only commands and the test suite.
</sources>

<focus>
Report defects that affect: {{correctness | security | data integrity | the stated criteria}}.
Skip style, naming and formatting unless they hide a defect.
"No defects found" is an acceptable result; do not invent findings to fill the report.
</focus>

<final_report>
Verdict first: meets the criteria, does not meet them, or cannot tell.
Then one entry per finding, most severe first:
- Where: file and line.
- What is wrong, in one sentence.
- How to see it fail: an input, a command or a sequence of steps.
- Severity: blocks release, should fix, or note.
- Confidence: confirmed by running something, or inferred from reading.
Then: which criteria you checked and how, and which you could not check.
</final_report>
```

## Notes

- **Reviewer capability.** Use a model at least as capable as the author's; see
  [mixed-model runs](../docs/01-model-selection.md#mixed-model-runs).
- **Read-only by construction.** Where your tool allows it, restrict the reviewer's tools so it
  cannot edit, in addition to telling it not to.
- **Verify findings before fixing.** Reproduce each one. A fix for a defect that does not exist
  is a new defect.
