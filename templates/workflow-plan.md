# Workflow plan

**Use when:** the same operation repeats across many items, or the orchestration itself needs to
be repeatable. Write this before asking for the workflow, and review it against the plan the
tool shows you before approving the run.

**How to fill it in:** replace each `{{placeholder}}`. Every stage needs an owner for its output
and a check.

```text
WORKFLOW PLAN
Goal: {{the result across all items}}
Items: {{what the unit of work is, and how the list is produced}}
Why a workflow: {{why one session or a few subagents would not do}}

Stages
1. {{name}}: {{what each agent does}} -> returns {{shape of result}}
2. {{name}}: {{what each agent does}} -> returns {{shape of result}}
3. Verify: {{how each item's result is checked, by an agent that did not produce it}}
4. Reconcile: the main session compares results with the evidence and resolves conflicts.

Ownership
Writers: {{which stage edits files; one checkout per writer; no shared files}}
Read-only stages: {{which stages only read}}

Settings
Orchestrating session: {{tier, effort}}
Worker agents: {{tier, effort}}
Size: {{expected number of agents}}

Pilot
Slice: {{one directory or a small sample}}
Proceed only if: {{what the pilot must show: correctness, spend, time}}

Boundaries
May change: {{paths}}
Must not change: {{paths, interfaces}}
Permissions: {{none during the run | what is granted, per target}}

Done when: {{per-item condition}} for every item, and {{whole-run condition}}
Report: per-item status (verified, failed, unverified), totals, and items needing a person.
```

## Notes

- **A run does not pause between stages.** If a person must approve stage one's output, make the
  later stages a separate run.
- **Unverified is a result.** When the verify stage cannot check an item, report it as
  unverified. Do not count it as verified or as failed.
- **Start from the pilot's numbers.** Use what the pilot spent to decide whether the full run is
  worth it.
