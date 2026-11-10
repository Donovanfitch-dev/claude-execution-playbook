# Templates

Copy-ready blocks. Each file has one fenced block to copy, with `{{placeholders}}` to replace,
followed by short notes.

| Template | Use it to |
| --- | --- |
| [Run card](run-card.md) | Record model, effort, topology, scope and proof for a task |
| [Execution prompt](execution-prompt.md) | Brief a consequential or unattended task |
| [Quick prompt](quick-prompt.md) | Brief a routine, bounded change in four lines |
| [Subagent brief](subagent-brief.md) | Hand one independent task to a worker |
| [Workflow plan](workflow-plan.md) | Plan a fan-out before asking for it |
| [Review brief](review-brief.md) | Get an independent review from a fresh session |
| [Handoff note](handoff-note.md) | Pass work between sessions |
| [Completion report](completion-report.md) | Report the result |
| [CLAUDE.md snippet](claude-md-snippet.md) | Set standing rules for a repository |

## Conventions

- `{{lower_case text}}` is a placeholder. Replace it, braces included.
- `a | b | c` inside a line is a choice. Keep one option.
- Delete lines that do not apply. Do not leave a placeholder in a prompt you send.
- The templates contain no model names. Write the tier and the model your environment shows on
  the run card; current names are in [model data](../docs/model-data.md).

The [examples](../examples/README.md) show the run card and the prompts filled in.
