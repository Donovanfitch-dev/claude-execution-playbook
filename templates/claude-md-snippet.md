# CLAUDE.md snippet

**Use when:** you want the playbook's standing rules applied to every Claude Code session in a
repository, without repeating them in each prompt.

**How to fill it in:** replace each `{{placeholder}}`, delete what does not fit your project,
and paste the block into the project's `CLAUDE.md`. Keep the file short. These lines are
guidance to the model; anything that must hold every time belongs in permission rules, hooks or
CI (see [authority and safety](../docs/04-authority-and-safety.md#prompts-are-not-enforcement)).

```text
## Working agreement

- Checks: run `{{command that runs tests, types and lint}}` before reporting a change as done,
  and show the output.
- Scope: change only what the task needs. Leave unrelated files and existing uncommitted work
  alone; list anything else worth fixing as a follow-up.
- Permissions: do not commit, push, open pull requests or release (merge, tag, publish, deploy)
  unless the task says so and names the target.
- Risky areas: for {{the parts of this project where a mistake is expensive or hard to undo}},
  write a short proposal (today and after, what breaks if wrong, rollback, proof) and wait for
  a go-ahead.
- Pause and ask when the way forward is out of scope, a step cannot be undone, or access is
  missing. Otherwise carry on.
- Delegation: work in this session by default. Use a subagent only for independent, read-heavy
  or fresh-eyes work, and give each writer its own worktree.
- Reports: outcome and status first (verified, unverified, partial, blocked, not started), then
  changes, evidence, what was not verified, and the branch, commit and push state.
```

## Notes

- The first line is the most valuable one. If you keep only one, keep the check command.
- Do not put model names or effort levels here. They are session settings and they change; see
  [model data](../docs/model-data.md).
- Review the file when you change models. Instructions written for an older model are often
  more prescriptive than a newer one needs.
