# Example 3: Multi-agent repository workflow

Templates used: [run card](../templates/run-card.md),
[workflow plan](../templates/workflow-plan.md),
[execution prompt](../templates/execution-prompt.md).

## Situation

`storefront-web` is a React and TypeScript front end. About 140 component files call a
deprecated helper, `formatPrice(cents)`, from `src/lib/legacyFormat.ts`. The replacement,
`formatMoney({ amount, currency })` in `src/lib/money.ts`, takes a different argument, so each
call site needs a small, local edit. The components live under six feature directories that do
not import each other's internals.

This passes the [independence test](../docs/02-topology-and-strategy.md#the-independence-test):
each directory can be migrated without another's result, each writer can own one directory, and
the main session reconciles. The same operation repeats across many items, so a workflow fits.

## Configuration

The run card below is for the pilot. The full run reuses it with the pilot slice removed from
the task and the scope.

```text
RUN CARD
Task:             Pilot: no component under src/features/cart/ calls formatPrice; each former call site uses formatMoney with the same output.
Where:            storefront-web, branch chore/format-money; one worktree per writer

Scope
May change:       files under src/features/cart/ that call formatPrice, and their tests
Must not change:  src/lib/money.ts, src/lib/legacyFormat.ts, rendered price text, public component props

Authority
Mode:             change
Permissions:      commit yes (worker branch only), push no, pull request no, release no

Proof
Done when:        zero references to formatPrice under src/features/cart/; type check, unit tests and
                  price snapshot tests pass for the directory (rung 2); each changed file confirmed
                  by an agent that did not edit it
Checks:           npm run typecheck; npm test -- src/features/cart;
                  npm run test:snapshots -- src/features/cart; grep for formatPrice

Exit
Pause when:       the standard triggers, and a changed snapshot or a non-cents value
If it misses:     re-run the failed files once; then report them for a person

Plan (also stated in the prompt)
Topology:         workflow (inventory, migrate, verify, reconcile); 3 agents for the pilot
Checkpoints:      none inside the run; the full run is a separate decision after the pilot
Unit of work:     each file, checked by the type checker, its tests and its snapshots

Session settings (applied in the tool)
Model:            Advanced (Claude Opus 5.5) for the orchestrating session; Everyday (Claude Sonnet 5.5, alias sonnet) for worker agents
Effort:           medium for both
Speed:            standard
Availability:     /model and /effort status at session start, 2026-11-10; worker model read in the workflow script before approving the run
```

### Why this configuration

- **Workflow, not subagents.** The plan is the reusable part: the same four stages apply to each
  directory, and a script holds the loop so the main session's context holds only results.
- **Workers one tier down.** Each edit is mechanical and checked by the type checker and
  snapshot tests. The orchestrating session, which plans and reconciles, stays on the Advanced
  tier at its default effort.
- **A file as the unit of work.** Results are reported per file, so you can point at the ones
  that failed.
- **One worktree per writer.** Six writers in one checkout would see each other's half-finished
  edits.
- **Pilot first.** The plan runs on one directory, and the full run is a separate decision made
  on the pilot's results.

## Workflow plan

Saved in the repository as `docs/plans/format-money-migration.md`, so it is reviewable and the
launch prompt can point to it.

```text
WORKFLOW PLAN
Goal: every formatPrice call under src/features/ replaced by formatMoney with identical rendered output
Items: the six directories under src/features/; call sites listed by the inventory stage
Why a workflow: about 140 files, the same edit in each, independent per directory, deterministic check

Stages
1. Inventory: one read-only agent lists every formatPrice call site -> returns file, line, argument expression, per directory
2. Migrate: one agent per directory rewrites its call sites and updates affected tests -> returns files changed, check output
3. Verify: one agent per directory, which did not edit it, reads the diff and re-runs the checks -> returns verified, failed or unverified, per file
4. Reconcile: the main session compares results with the evidence and resolves conflicts.

Ownership
Writers: stage 2 only; one worktree and one branch per directory; no file is assigned to two writers
Read-only stages: 1 and 3

Settings
Orchestrating session: Advanced tier, medium effort
Worker agents: Everyday tier, medium effort
Size: 13 agents (1 inventory, 6 migrate, 6 verify)

Pilot
Slice: src/features/cart/ only (11 files)
Proceed only if: all 11 files verified, snapshots unchanged, and the pilot's token use makes the full run acceptable

Boundaries
May change: files under src/features/ that call formatPrice, and their tests
Must not change: src/lib/money.ts, src/lib/legacyFormat.ts, rendered price text, public component props
Permissions: commits on worker branches and the task branch; no push

Done when: no formatPrice reference remains in the directory and its checks pass, for every directory, and the whole-repository checks pass after merge
Report: per-file status (verified, failed, unverified), totals, and files needing a person.
```

## Prompt

Sent to the orchestrating session for the pilot. The full run reuses it with the slice removed.

```text
<task>
Run the pilot slice of the formatPrice to formatMoney migration as a workflow, following the
saved plan, and report per-file results.
Mode: change
</task>

<proof>
The task is done when all of these are true:
- No reference to formatPrice remains under src/features/cart/.
- Type check, unit tests and price snapshot tests pass for the directory.
- The verify agent, which made no edits, confirms each changed file against the plan.
Show it with:
- npm run typecheck: the changed call sites compile
- npm test -- src/features/cart: unit tests for the slice
- npm run test:snapshots -- src/features/cart: rendered price text is unchanged
- grep -rn "formatPrice" src/features/cart: expect no matches
For each check give the command, its exit status and the lines of output that matter.
If a check cannot run, say "not run" and why.
If a check fails: re-run that file once, then mark it failed and carry on with the rest.
</proof>

<background>
Why: formatPrice is deprecated and blocks removing src/lib/legacyFormat.ts.
Decided already: the stages, ownership and settings in docs/plans/format-money-migration.md.
This run covers only the pilot slice, src/features/cart/. The full run is a separate decision.
Found so far: formatMoney takes { amount, currency }; amount is in major units, so a cents value
must be divided by 100; currency comes from the existing useCurrency() hook in each feature.
Read first: docs/plans/format-money-migration.md, then src/lib/money.ts and
src/lib/legacyFormat.ts, then the tests and snapshots under src/features/cart/.
If they disagree and it matters: pause and tell me.
</background>

<boundaries>
May change: files under src/features/cart/ that call formatPrice, and their tests
Must not change: src/lib/money.ts, src/lib/legacyFormat.ts, rendered price text, public
component props, or any uncommitted work already in the tree.
Make the smallest change that meets the proof. If you notice something else worth fixing, list
it in the report instead of fixing it.
Topology: a workflow, as planned: 1 inventory agent, 1 migrate agent, 1 verify agent for the
pilot. Run the worker agents on the sonnet model. The migrate agent works in its own worktree.
Agents do not start further agents.
Checkpoints: none
Unit of work: each file, checked and reported one by one
Permissions: commit yes, on the worker branch only; push no; pull request no; release no.
If that line does not grant a step, do not take it.
</boundaries>

<stop_and_ask>
Carry on without asking for anything you can undo. Pause and tell me what you found when:
- the only way forward touches something outside "may change";
- a step cannot be undone and the Permissions line does not grant it;
- you lack access: a permission, a credential or a tool;
- this brief and the repository disagree, and the difference matters;
- you are not sure which repository, branch or environment you are in;
- a snapshot changes, or a call site passes a value that is not a cents integer.
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
Add a table with one row per file and its status: verified, failed or unverified. Add the
number of agents used and the token use the tool reports for the run.
</final_report>
```

## Validation criteria

For the pilot:

- [ ] The plan and script the tool showed before approval matched the saved plan: three agents,
      the stated stages, the worker model.
- [ ] The per-file table has 11 rows and each is "verified", or the exceptions are explained.
- [ ] Snapshot test output is shown and reports no changed snapshots.
- [ ] The `grep` output is shown and empty.
- [ ] The verify agent's report is separate from the migrate agent's and cites the diff.
- [ ] `git worktree list` and `git branch` show the worker branch; nothing is pushed.

For the full run, in addition:

- [ ] Every directory has its own status line; no directory is reported only in aggregate.
- [ ] Whole-repository `npm run typecheck`, `npm test` and `npm run test:snapshots` pass after
      the worker branches are merged into the task branch.
- [ ] Files marked failed or unverified are listed for a person, not retried indefinitely.
- [ ] A person reviews the merged diff before any pull request (rung 5).

## What would change the recommendation

| If... | Then... |
| --- | --- |
| Only a dozen files are affected | One session with a file as the [unit of work](../docs/02-topology-and-strategy.md#unit-of-work-is-there-a-list); a workflow costs more than it saves |
| Feature directories share components that also call the helper | Assign shared files to one writer before starting, or migrate them first in a single session |
| The pilot shows snapshot changes | Stop; the conversion rule in the brief is wrong, which is a brief miss, not a capability miss |
| Someone must approve the inventory before edits begin | Run the inventory as its own workflow, because a run does not pause between stages |
