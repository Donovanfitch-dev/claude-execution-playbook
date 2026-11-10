# Example 1: Routine coding task

Templates used: [run card](../templates/run-card.md), [quick prompt](../templates/quick-prompt.md).

## Situation

`bookshelf-api` is a small TypeScript service for a library's loan records. `GET /loans` takes a
`limit` query parameter. A non-numeric or out-of-range value currently reaches the database
layer and comes back as a 500. It should be rejected with a 400 and a readable message.

The handler is one file, the tests for it are one file, and the test runner is already set up.

## Configuration

```text
RUN CARD
Task:             GET /loans rejects an invalid limit with a 400 and a clear message, not a 500.
Where:            bookshelf-api, branch fix/loans-limit-validation

Scope
May change:       src/routes/loans.ts, tests/routes/loans.test.ts
Must not change:  responses for valid requests, other routes, existing uncommitted work

Authority
Mode:             change
Permissions:      commit no, push no, pull request no, release no

Proof
Done when:        limit=abc, limit=0 and limit=101 each return 400 with an error body;
                  limit=100 and a missing limit still return 200; tests cover all five (rung 2)
Checks:           npm test -- loans; npm run lint

Exit
Pause when:       the change needs a file outside the two named above
If it misses:     fix the brief once, then effort one level up; 2 attempts; then stop and report

Plan (also stated in the prompt)
Topology:         single session
Checkpoints:      none
Unit of work:     the whole task

Session settings (applied in the tool)
Model:            Everyday (Claude Sonnet 5.5)
Effort:           medium
Speed:            standard
Availability:     /model and /effort status at session start, 2026-11-10
```

### Why this configuration

- **Everyday tier.** The path is known (validate one parameter in one handler) and a test catches
  a wrong result. That is question 2 of the
  [chooser](../docs/01-model-selection.md#choosing-a-starting-model), one tier below the usual
  starting point.
- **Medium effort.** This is the model's default in Claude Code, set explicitly. It is one level
  below the same model's API default, which is acceptable here because the check is strong.
- **Single session, no checkpoints.** There is nothing to split, and a mistake would be caught
  by the tests and is trivial to undo.
- **Quick prompt.** Four lines carry everything the session needs. A full brief would add
  reading and no information.

## Prompt

```text
Make GET /loans return 400 with {"error": "<message>"} when limit is not an integer from 1 to
100, in src/routes/loans.ts. A missing limit keeps the current default behaviour.
Change only what this needs; leave other files and any uncommitted work alone.
Prove it with `npm test -- loans` and `npm run lint` and show me the output. Add tests in
tests/routes/loans.test.ts for limit=abc, 0, 101, 100 and a missing limit.
Do not commit or push. Finish with: what changed, the check results, anything you did not verify.
```

## Validation criteria

Accept the result when all of these hold:

- [ ] The test file has cases for `abc`, `0`, `101`, `100` and a missing `limit`, and the first
      three assert a 400 with an `error` field.
- [ ] `npm test -- loans` output is shown and passes.
- [ ] `npm run lint` output is shown and reports no new warnings.
- [ ] `git diff --stat` lists only the two files named in the scope.
- [ ] The report says the work is uncommitted.

## What would change the recommendation

| If... | Then... |
| --- | --- |
| Validation is shared middleware used by other routes | The scope grows; write a full brief and consider the Advanced tier |
| There is no test runner | Set one up as a separate work item first; without a check, do not step effort down |
| The same fix is needed on twenty routes | Make one route the [unit of work](../docs/02-topology-and-strategy.md#unit-of-work-is-there-a-list), with a per-route check |
