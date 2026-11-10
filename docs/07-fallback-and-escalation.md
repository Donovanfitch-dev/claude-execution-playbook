# Fallback and escalation

A run that misses its done conditions has told you something. The useful response depends on
what it told you, so classify the miss before changing any setting.

## Classify the miss

| Kind of miss | Signs | Response |
| --- | --- | --- |
| **Brief** | It solved a different problem, stopped early, or asked about something you knew | Fix the prompt: add the missing context, tighten the done conditions, name the check |
| **Environment** | A tool failed, access was denied, a dependency was missing, the check itself is broken | Fix the environment; the model was not the problem |
| **Scope** | The task turned out to be two tasks, or needs a change outside the boundaries | Split or re-scope with the task owner |
| **Capability** | The brief was complete, the environment worked, and the reasoning still fell short | Escalate, one step at a time |

Most misses are the first three. Changing the model for a brief problem buys a more expensive
version of the same miss.

## The escalation ladder

For a capability miss, change one thing and re-run.

1. **Raise effort one level** on the same model. Repeat while each step helps and the cost is
   acceptable.
2. **Move up one tier**, starting at that tier's default effort.
3. **Return to the task owner** with what was tried and what was observed.

The ladder is this playbook's. Its order borrows from Anthropic's published guidance, which says
to sweep effort on the current model before adding a second one
([cost guide](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence)).
For the last step up, to the Maximum tier, the vendor's bar is higher than "one level did not
help": the
[choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
page says to move when tests at the two highest effort levels of the tier below still fall
short.

**Topology is not a rung.** Adding agents does not make hard reasoning easier. Change topology
only when the miss showed the work is separable (the session ran out of context on independent
pieces), and apply the [independence test](02-topology-and-strategy.md#the-independence-test)
first.

## Rules for retries

- **Set a budget up front.** The run card's `If it misses` line states the next step and a
  maximum number of attempts. Two is a reasonable default for unattended work.
- **Change one thing per attempt**, and record what changed. Otherwise you cannot tell what
  fixed it.
- **A retry never widens authority.** The second attempt has the same scope, the same mode and
  the same release permissions as the first. If the task cannot be done inside them, that is a
  finding to report.
- **Do not retry what may have partly succeeded** without looking. Check the state first, so a
  second attempt does not apply a change twice.
- **Stop when the failure signal is weak.** If you cannot tell a good result from a bad one,
  another attempt only produces another unverifiable result. Fix the check.

## Outcomes that are not errors

On the Claude API, a response can end for reasons other than a normal finish. Anthropic's
[stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)
page lists them and distinguishes them from request errors: these are successful responses that
need handling.

| `stop_reason` | Meaning, per the documentation | Handling |
| --- | --- | --- |
| `max_tokens` | The response reached your output limit | Treat as truncated. Raise the limit or continue; never use a cut-off tool call |
| `model_context_window_exceeded` | The response filled the context window | Treat as truncated. Reduce or summarize the input, or split the task |
| `pause_turn` | A server-side tool loop reached its iteration limit | Send the response back to let it continue |
| `refusal` | The model declined | Read the details, keep the result, and follow a fallback route you chose in advance |

Two points apply to all four:

- **Always read `stop_reason` before using the content.**
- **None of them is a reason to loosen the task.** In particular, a refusal is an outcome to
  record and route, not a transient fault to hammer on. Anthropic documents retrying on a
  fallback model; if you use one, the fallback inherits the original boundaries.

## When a capability is missing

Sometimes the model, effort level, speed mode or feature on the run card is not available in the
environment: not enabled for the account, restricted by the organization, not offered on the
platform.

- Choose the nearest available configuration **explicitly**, and update the run card.
- Note that tools can substitute. The Claude Code
  [subagents](https://code.claude.com/docs/en/sub-agents) page describes subagents running on a
  substituted model when an organization allowlist blocks the requested one, with a
  warning in interactive sessions; `/tasks` shows the model a subagent actually ran on.
- If the missing capability was the reason for the plan (for example, a long unattended run
  planned around the top tier), re-plan instead of proceeding on a lower tier and hoping.

## Step back down

Escalation should not be a ratchet. After a task succeeds on a raised configuration:

- Try the next similar task one step lower.
- If the fix was really the improved brief, keep the brief and drop the model back.
- Record what worked, so the next run card starts from evidence.
