# Handoff note

**Use when:** work passes from one session to another: plan to implementation, one day to the
next, or author to reviewer. The next session should need nothing but this note and the
repository.

**How to fill it in:** replace each `{{placeholder}}`. Save it in the repository or the pull
request, not only in the conversation.

```text
HANDOFF NOTE
Goal: {{the finished result the work is heading for}}
Status: {{verified | unverified | partial | blocked | not started}}

Decisions made, with the reason for each
- {{decision}}: {{reason}}
- {{decision}}: {{reason}}

Done and verified
- {{item}}: {{check that proved it}}

Done, not verified
- {{item}}: {{what check is missing}}

Not done
- {{item}}

Workspace
Repository: {{name}}   Branch or worktree: {{name}}
Uncommitted changes: {{none | list}}
Commits: {{hashes or "none"}}   Pushed: {{yes or no}}

Next step: {{the single next action, with the file or command to start from}}
Watch out for: {{traps found on the way}}
Open questions for the owner: {{questions | none}}
```

## Notes

- Write the note as if the reader has never seen the conversation, because they have not.
- "Decisions made" saves the most time. A fresh session will otherwise reopen each one.
- If "next step" cannot be stated as one action, the plan is not finished.
