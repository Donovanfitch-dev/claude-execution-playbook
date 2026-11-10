# Testing and verification

"Done" is a claim. Verification is the evidence for it. This chapter gives a way to say how much
evidence a task needs and how to ask for it.

## The verification ladder

Each rung proves more than the one below it, and costs more.

| Rung | Evidence | What it proves | What it does not prove |
| --- | --- | --- | --- |
| 0. Assertion | "It should work now" | Nothing | Everything |
| 1. Static | Build, type check, lint pass | The code is well-formed | That it does the right thing |
| 2. Tested | Targeted tests pass, including one that failed before the change | The stated behaviour, for the cases tested | Untested paths; integration |
| 3. Observed | The real program was run and the result looked at | The behaviour a user would see | Cases nobody tried |
| 4. Independently reviewed | A reviewer with fresh context checked the change against the criteria | That someone other than the author could not break it | What the criteria left out |
| 5. Human reviewed | A person read the change and the evidence | Accountability | Nothing automatic |

Write the required rung into the prompt's `<proof>` block. If you do not say, you will
usually get rung 1 reported as rung 3.

## Minimum rung by change type

These are the rungs a change should reach before it is merged or released. They are starting
points, not rules. One session often delivers a lower rung, and the rest comes from a separate
review task.

| Change | Minimum |
| --- | --- |
| Documentation, comments, formatting | 1 |
| Routine, bounded code change | 2 |
| Bug fix | 2, with the bug reproduced first |
| User-visible behaviour | 3 |
| [Risky surface](04-authority-and-safety.md#risky-surfaces-propose-first) | 4, then 5 before release |
| Anything published or deployed | 5 |

## Asking for evidence

The Claude Code [best practices](https://code.claude.com/docs/en/best-practices) page advises
asking for evidence whichever check you use: the command that was run and its output. "All tests
pass" on its own tells you very little, and for a session you were not watching it is the only
evidence you have.

Ask for three things per check:

1. The exact command.
2. The result: exit status and the relevant lines of output, not the whole log.
3. What the check covers, in one line.

### Reproduce before fixing

For a bug, the first deliverable is a failing check: a test or a command that shows the bug. The
fix is finished when that same check passes. Without the "before", a passing "after" proves
little.

### Unknown is not pass

A check that did not run is reported as **not run**, with the reason. It is never folded into
"passing". The same goes for a check that was skipped, timed out, or ran against the wrong
target. A final report needs a place for this; the
[completion report](../templates/completion-report.md) has one.

### Match the check to the claim

| Claim | A check that supports it |
| --- | --- |
| "It compiles" | Build |
| "The function returns the right value" | Unit test on that function |
| "The endpoint rejects bad input" | A request with bad input and the observed response |
| "The migration is reversible" | Apply, roll back, apply again on a copy of the data |
| "Nothing else changed" | The diff, limited to the scope; the existing test suite |

## Independent review

Self-review catches slips. It rarely catches a wrong assumption, because the reviewer shares it.
An independent reviewer is a session that did not write the change and has not read the author's
reasoning.

How to set one up:

- **Give it the criteria and the change, not the story.** The reviewer receives the task's done
  conditions and the diff or artifact. It does not receive the author's explanation of why the
  change is right.
- **Make it read-only.** A reviewer that edits becomes a second author.
- **Tell it what matters.** The Claude Code
  [best practices](https://code.claude.com/docs/en/best-practices) page notes that a reviewer asked to find problems
  will always find something, and recommends telling it to report gaps that affect correctness
  and skip style. Fixing every finding adds abstraction and tests for cases that cannot happen.
- **Ask for evidence with each finding**: file and line, why it is a defect, and a way to see it
  fail.
- **Allow "nothing found".** A review that must produce findings will invent them.

Then verify the findings before acting on them. A reviewer's claim is evidence, in the same
confident voice whether it is right or wrong.

In Claude Code, a fresh subagent or a second session both work as reviewers; the best practices
page describes each. The [review brief](../templates/review-brief.md) is written for this.

## Checks the session can run by itself

A check the session can run closes the loop without you. The best practices page lists the
options from loosest to strictest: an instruction in the prompt, a goal condition evaluated
after each turn, a stop hook that sends the session back to work when a script fails, and a
review by a session that did not write the code. Pick the weakest one that is strong enough for
the task.

Put the command that runs your checks in the project instruction file. It is the most useful
line in it.

## What verification is not

- **Not more agents.** Three sessions agreeing on an unverified claim is one unverified claim.
- **Not more effort.** A session checking its own work shares its own assumptions, however much
  effort it spends.
- **Not a longer report.** Evidence is a command and its output, not a paragraph of reassurance.
