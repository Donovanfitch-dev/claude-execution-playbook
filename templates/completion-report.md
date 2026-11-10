# Completion report

**Use when:** a task ends, whether or not it succeeded. This is the shape the
`<final_report>` block of the [execution prompt](execution-prompt.md) asks for.

**How to fill it in:** replace each `{{placeholder}}`. Keep "Not verified" even when it is
empty, and write "none".

```text
OUTCOME
{{one or two sentences: what is true now that was not before}}
Status: {{verified | unverified | partial | blocked | not started}}

CHANGES
- {{file, system or artifact}}: {{why it changed}}

EVIDENCE
- {{command}} -> {{result}} ({{what this covers}})

NOT VERIFIED
- {{check that did not run, and why | claim with no evidence | none}}

DIFFERENCES FROM THE BRIEF
- {{where the work departed from the brief, and why | none}}

WORKSPACE
Branch or worktree: {{name}}
Uncommitted changes: {{none | list}}
Commits: {{hashes or "none"}}   Pushed: {{yes or no}}   Pull request: {{link or "none"}}
Released: {{no | what was merged, tagged, published or deployed, and where}}

FOLLOW-UPS
- {{out-of-scope finding or remaining work, as a separate item | none}}
```

## Notes

- The status word has a fixed meaning; see
  [completion](../docs/08-completion-and-release.md#status-vocabulary).
- Report what was released separately from whether the task succeeded.
- A failing check appears under Evidence with its output. It does not move to Follow-ups.
