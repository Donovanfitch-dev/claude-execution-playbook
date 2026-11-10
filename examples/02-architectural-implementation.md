# Example 2: Complex architectural implementation

Templates used: [run card](../templates/run-card.md),
[execution prompt](../templates/execution-prompt.md).

## Situation

`invoice-service` is a Python service that records payments when a payment provider calls its
webhook. The provider retries deliveries, and a retried delivery currently creates a second
payment record for the same event. The fix is to make the handler idempotent: remember which
provider events have been processed, and make a repeat delivery a no-op.

This touches a payment path and needs a database migration, so it is a
[risky surface](../docs/04-authority-and-safety.md#risky-surfaces-propose-first). The work is
split into two work items:

1. **Propose.** A session in propose mode wrote `docs/proposals/webhook-idempotency.md`: a new
   `processed_events` table with a unique key on the provider's event ID, an insert-first
   handler flow inside one transaction, and a rollback plan. A person reviewed and approved it.
2. **Change.** This example. A fresh session implements the approved proposal, pausing at
   [checkpoints](../docs/02-topology-and-strategy.md#checkpoints-where-does-the-run-pause).

## Configuration

```text
RUN CARD
Task:             A repeated webhook delivery for the same provider event creates no second payment record.
Where:            invoice-service, worktree webhook-idempotency (branch worktree-webhook-idempotency)

Scope
May change:       migrations/, app/webhooks/, app/models/processed_event.py, tests/webhooks/
Must not change:  the webhook's response codes and body, the payments table schema,
                  provider signature verification, existing uncommitted work

Authority
Mode:             change
Permissions:      commit yes (this branch), push no, pull request no, release no

Proof
Done when:        a test that delivers the same event twice fails before the change and passes after;
                  a concurrent-delivery test passes; the migration applies, rolls back and re-applies;
                  the existing suite passes (rung 2 in this session; the independent review that
                  this surface needs, rung 4, is a separate work item)
Checks:           pytest tests/webhooks -q; pytest -q; make migrate-test

Exit
Pause when:       the standard triggers, and a failed checkpoint or a migration that would rewrite rows
If it misses:     report at the failed checkpoint and do not continue past it; 1 attempt per checkpoint

Plan (also stated in the prompt)
Topology:         single session
Checkpoints:      after the failing test; after the migration; after the handler change
Unit of work:     the whole task

Session settings (applied in the tool)
Model:            Advanced (Claude Opus 5.5)
Effort:           high
Speed:            standard
Availability:     /model and /effort status at session start, 2026-11-10
```

### Why this configuration

- **Advanced tier.** The handler has to be correct under concurrency, and the cost of a subtle
  mistake is duplicate or missing payments. That is judgment, not a known path.
- **High effort.** One level above this model's default, because a wrong result here would be
  expensive to find later. This is a recommendation; if your own tests show the default holds
  for work like this, use the default.
- **Single session.** The migration, the model and the handler depend on each other. Splitting
  them would fail the first question of the
  [independence test](../docs/02-topology-and-strategy.md#the-independence-test).
- **Three checkpoints.** Each one's result decides whether the next step should happen at all.
- **A fresh session, briefed from the approved proposal.** The planning conversation is not
  carried over.
- **Commit only.** Local commits on the task branch make each checkpoint reviewable. Pushing and
  opening a pull request wait for the independent review in
  [example 4](04-independent-security-review.md).

## Prompt

```text
<task>
Implement the approved proposal so that a repeated webhook delivery for the same provider event
creates no second payment record.
Mode: change
</task>

<proof>
The task is done when all of these are true:
- A test that delivers the same event twice failed before the handler change and passes after it.
- A test that sends the same event from two concurrent requests records exactly one payment.
- The migration applies, rolls back and re-applies cleanly on the test database.
- The full existing test suite passes.
Show it with:
- pytest tests/webhooks -q: the new tests, before and after
- make migrate-test: apply, roll back, re-apply on the test database
- pytest -q: the full suite
For each check give the command, its exit status and the lines of output that matter.
If a check cannot run, say "not run" and why.
If a check fails: stop at that checkpoint and report; do not continue past it.
</proof>

<background>
Why: the provider retries deliveries, and each retry currently records the payment again.
Finance corrects these by hand.
Decided already: the design in docs/proposals/webhook-idempotency.md is approved. Do not
redesign it. If you believe it is wrong, pause and say why.
Found so far: the duplicate is reproducible by posting the same event body twice to the
webhook route in the test client.
Read first: docs/proposals/webhook-idempotency.md, then app/webhooks/, app/models/ and the
existing files under migrations/, then tests/webhooks/ and the README section on migrations.
If they disagree and it matters: pause and tell me.
</background>

<boundaries>
May change: migrations/, app/webhooks/, app/models/processed_event.py, tests/webhooks/
Must not change: the webhook's response codes and body, the payments table schema, provider
signature verification, or any uncommitted work already in the tree.
Make the smallest change that meets the proof. If you notice something else worth fixing, list
it in the report instead of fixing it.
Topology: single session
Checkpoints: pause, show me the evidence, and wait at each of these:
  1. after writing the duplicate-delivery test and showing it fail;
  2. after writing the migration and showing it apply, roll back and re-apply;
  3. after the handler change, with the duplicate-delivery and concurrent-delivery tests passing.
Unit of work: the whole task
Permissions: commit yes, on the current branch, one commit per checkpoint; push no; pull request no; release no.
If that line does not grant a step, do not take it.
</boundaries>

<stop_and_ask>
Carry on without asking for anything you can undo. Pause and tell me what you found when:
- the only way forward touches something outside "may change";
- a step cannot be undone and the Permissions line does not grant it;
- you lack access: a permission, a credential or a tool;
- this brief and the repository disagree, and the difference matters;
- you are not sure which repository, branch or environment you are in;
- a checkpoint fails, or the migration would need to rewrite or delete existing rows.
</stop_and_ask>

<final_report>
First line: what is true now, and one status word (verified, unverified, partial, blocked,
not started). Then, briefly and in this order:
- Changes: what you touched and why.
- Evidence: each check with its command and result.
- Not verified: checks that did not run, and anything you assumed.
- Differences from this brief, if any, and why.
- Workspace: branch, uncommitted changes, commits, and whether anything was pushed or released.
- Follow-ups: things you noticed and left alone.
Report only what you ran or read during this task, and mark anything that is an inference.
</final_report>
```

## Validation criteria

Accept the result when all of these hold:

- [ ] The report shows the duplicate-delivery test **failing** at checkpoint 1, with output.
- [ ] `make migrate-test` output shows apply, rollback and re-apply succeeding.
- [ ] The concurrent-delivery test exists and asserts exactly one payment record.
- [ ] `pytest -q` output is shown and passes.
- [ ] `git log --oneline` shows one commit per checkpoint on the task branch, and nothing is pushed.
- [ ] `git diff main --stat` lists only paths inside the scope.
- [ ] The response codes and body of the webhook are unchanged, shown by existing tests.
- [ ] Before anything is pushed: an independent review (rung 4) finds no release-blocking
      defect, and a person reviews before merge (rung 5). The session's own "verified" covers
      rung 2 only.

## What would change the recommendation

| If... | Then... |
| --- | --- |
| No approved proposal exists | Run propose mode first; do not start with edits |
| The same pattern is needed in four other webhook handlers | Finish and review this one, then treat the rest as a separate task with one handler as the unit of work |
| The session misses at high effort after the brief is confirmed complete | Follow the [escalation ladder](../docs/07-fallback-and-escalation.md#the-escalation-ladder): raise effort a level at a time, then consider the Maximum tier |
| The migration must change existing payment rows | That is a different, larger change; stop and return to the proposal |
