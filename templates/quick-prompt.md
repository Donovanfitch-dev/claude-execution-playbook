# Quick prompt

**Use when:** the change is routine and bounded, the path is known, and one command proves it.
If you find yourself adding a second paragraph of context, switch to the
[execution prompt](execution-prompt.md).

**How to fill it in:** replace each `{{placeholder}}`. Four lines are enough.

```text
{{what to change and the result you expect}}, in {{files or directory}}.
Change only what this needs; leave other files and any uncommitted work alone.
Prove it with `{{command}}` and show me the output. Add or update a test if none covers this.
Do not commit or push. Finish with: what changed, the check result, anything you did not verify.
```

## Notes

- State release permissions even here. One line of "do not commit or push" is cheaper than
  finding a surprise commit.
- If the session reports that the change needs to go outside the named files, that is the signal
  to stop and write a full brief, not to say "go ahead".
- Record the settings on a [run card](run-card.md) if the change will be reviewed by someone
  else.
