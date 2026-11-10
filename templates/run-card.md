# Run card

**Use when:** any task worth reviewing afterwards. Fill it in before writing the prompt.

**How to fill it in:** replace each `{{placeholder}}`; where options are separated by `|`, keep
one. The groups follow the [overview](../docs/00-overview.md): the four boundaries, then the run
plan, then the session settings. Boundaries and plan are restated in the prompt. Session
settings are applied in the tool by whoever starts the session.

```text
RUN CARD
Task:             {{one sentence describing the finished result}}
Where:            {{repository}}, {{branch or worktree}}

Scope
May change:       {{paths, components or systems}}
Must not change:  {{interfaces, files, behaviours, existing uncommitted work}}

Authority
Mode:             investigate | propose | change | review
Permissions:      commit {{yes or no}}, push {{yes or no}}, pull request {{yes or no}}, release {{yes or no}}

Proof
Done when:        {{observable conditions, and the verification rung required}}
Checks:           {{commands the session runs, and the evidence to capture}}

Exit
Pause when:       the standard triggers | the standard triggers, and {{task-specific trigger}}
If it misses:     {{what to try next, and how many attempts before stopping}}

Plan (also stated in the prompt)
Topology:         single session | subagents ({{count}}: {{purpose of each}}) | workflow ({{stages}})
Checkpoints:      none | {{where the run pauses, and what evidence it shows}}
Unit of work:     the whole task | each {{item}}, checked by {{check}}

Session settings (applied in the tool)
Model:            {{tier}} ({{model as your environment names it}})
Effort:           {{level}}
Speed:            standard | fast
Availability:     {{how and when you confirmed these in your environment | assumed}}
```

## Field notes

| Field | Guidance |
| --- | --- |
| Task | A result, not an activity. If you need "and", you may have two work items. |
| Mode | Sets the ceiling for the run. See [authority and safety](../docs/04-authority-and-safety.md#task-mode). |
| Permissions | Name the target next to each "yes": which branch, which remote, which repository. "Release" covers merge, tag, publish and deploy. |
| Done when | Include the [verification rung](../docs/06-verification.md#the-verification-ladder) you require. |
| Pause when | The standard triggers are the five in the [execution prompt](execution-prompt.md). Add one only if the task needs it. |
| If it misses | For example "fix the brief, then effort one level up; 2 attempts; then stop and report". See [fallback](../docs/07-fallback-and-escalation.md). |
| Topology | For subagents, one purpose per worker. For a workflow, the stages and the pilot slice. |
| Checkpoints, Unit of work | Together these are the [execution strategy](../docs/02-topology-and-strategy.md#execution-strategy). Most tasks keep both defaults. |
| Model | Tier first, so the card still makes sense after the next release. This is the session's model, set in the tool. A model for subagents or workflow agents is noted here too, and requested in the prompt or in their definitions. |
| Effort | Set it explicitly even when it equals the default. |
| Availability | For example "`/model` and `/effort status` in this session, today". "Assumed" is an honest answer and a flag. |
