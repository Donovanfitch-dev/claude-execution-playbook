# Prompt construction

A good execution prompt answers the questions a capable engineer would ask before starting
someone else's task: what is the finished result, how will we know it worked, what do I need to
know that is not written down, what am I allowed to touch, when should I stop and ask, and what
do you want back.

## Principles

**State the outcome, not the activity.** "Investigate the login failures" describes motion.
"Find why logins fail for accounts created before the migration and report the cause with
evidence; do not change code" describes a result and a boundary.

**Say how it will be proven right after you say what it is.** The Claude Code
[best practices](https://code.claude.com/docs/en/best-practices) page puts the reason plainly: a
model stops when the work looks done, and without something that returns pass or fail, "looks
done" is all it has. Writing the proof straight after the task also tests the task. If you
cannot say how you would check it, the task is not defined yet.

**Write down only what the model cannot find.** The same page gives a two-part test: could it
find this by reading the code, and would it actually go and look? If both are yes, leave it out.
What belongs in the prompt is the decision made in a meeting and the constraint that lives in
someone's head.

**Use tags to separate kinds of content.** Anthropic's
[prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
recommend XML tags when a prompt mixes instructions, context, examples and inputs. The tag names
are yours to choose; consistency matters more than the names.

**Put long material first and the ask last.** The same page recommends placing long documents
near the top of the prompt, above the instructions.

**Add examples only when they remove ambiguity.** When you do, the vendor guidance is three to
five, varied enough that the model does not copy one of them.

**Say each thing once.** A rule repeated in capitals competes with everything else you wrote.
If it must hold every time, a prompt is the wrong place for it; see
[authority and safety](04-authority-and-safety.md#prompts-are-not-enforcement).

## The run card and the prompt

A prompt cannot set its own model, effort or speed. Those are applied in the tool by whoever
starts the session. Everything else on the [run card](../templates/run-card.md) is restated in
the prompt, because the model has to act on it: the boundaries, and the run plan (topology,
checkpoints, unit of work).

Keep the two next to each other, for example the run card in the pull request description and
the prompt beneath it.

## Anatomy of an execution prompt

The [execution prompt template](../templates/execution-prompt.md) has six blocks.

| Block | Carries | Write |
| --- | --- | --- |
| `<task>` | The finished result and the task mode | One or two sentences; the mode is investigate, propose, change or review |
| `<proof>` | The Proof boundary, and from Exit what to do when a check fails | Observable done conditions, the checks that show them, and the retry rule |
| `<background>` | What is not in the repository | Why it matters, what is already decided, what was found earlier, what to read first |
| `<boundaries>` | Scope, Authority and the run plan | May change, must not change, topology, checkpoints, unit of work, permissions |
| `<stop_and_ask>` | From Exit, when to pause | The triggers for pausing instead of deciding |
| `<final_report>` | From Exit, the report | Outcome and status first, then evidence, gaps and workspace state |

Notes on individual blocks:

- **`<proof>`: avoid conditions only you can judge.** "Clean code" is not checkable. "No new
  lint warnings; public function signatures unchanged" is. Match each check to the claim it
  supports: a build proves the code compiles, not that the bug is fixed. See
  [verification](06-verification.md).
- **`<background>`: say which source is right.** When the specification and the code disagree,
  name the one to believe, or say "pause and tell me". Otherwise the model picks one.
- **`<boundaries>`: write the permissions out even when they are all "no".** An explicit "commit
  no" reads differently from silence. See [authority and safety](04-authority-and-safety.md).
- **`<stop_and_ask>`: keep it short and real.** A handful of triggers that matter beat fifteen
  that cause a stop on every run.

## Size the prompt to the task

Not every task needs six blocks.

| Task | Use |
| --- | --- |
| A routine, bounded change with an obvious check | The [quick prompt](../templates/quick-prompt.md): task, scope, check, report |
| A consequential or multi-step change | The full [execution prompt](../templates/execution-prompt.md) |
| A handoff to a worker | The [subagent brief](../templates/subagent-brief.md) |
| A review by a fresh session | The [review brief](../templates/review-brief.md) |

A full template wrapped around a one-line fix adds reading time and nothing else, and a
one-line fix does not need a plan.

## Model-specific tuning

Prompts are not fully portable across models, and the vendor publishes a prompting page for each
current model. Read the page for the model you are using instead of relying on a summary here.
Two points are worth knowing when you move a prompt between tiers:

- For reasoning-heavy work, Anthropic's general
  [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  advise preferring general instructions over prescriptive step-by-step plans.
- A prompt carried over from an older model deserves a reread. The run card's tier line is a
  useful reminder: when the model behind a tier changes, revisit the prompts written for it.

## Standing instructions

Rules that apply to every task in a repository belong in the project's instruction file, not in
each prompt. In Claude Code that is `CLAUDE.md`
([memory](https://code.claude.com/docs/en/memory)). Keep it short: the vendor guidance is to
target under 200 lines, and the best practices page calls the command that runs your checks the
single most useful line in it. The [CLAUDE.md snippet](../templates/claude-md-snippet.md) is a
starting point.

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
| --- | --- | --- |
| "Be thorough" or "be careful" in place of criteria | It does not say what done looks like or how to check it | State the proof |
| A job title in place of content | A title does not supply missing context | Say what the work is for and who will use it |
| Scope by omission | Silence is read as permission | List what may change |
| Proof left to the end, or left out | The task gets defined by whatever was built | Write `<proof>` second |
| One prompt for two unrelated tasks | Neither gets a clear done condition | Split into two work items |
