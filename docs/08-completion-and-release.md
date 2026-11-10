# Release and completion reporting

The final report is what a reviewer reads instead of the conversation. It should let them decide,
quickly, whether to accept the work, and it should never claim more than the evidence supports.

## The completion report

Use the [completion report template](../templates/completion-report.md). Its parts, in order:

| Part | Content |
| --- | --- |
| **Outcome** | One or two sentences: what is true now that was not before, and the status word |
| **Changes** | Files, systems or artifacts touched, with a line each on why |
| **Evidence** | Each check: command, result, what it covers |
| **Not verified** | Checks that did not run, claims with no evidence, anything assumed |
| **Differences** | Where the work departed from the brief, and why |
| **Workspace** | Branch, worktree, uncommitted changes, commits, push and release state |
| **Follow-ups** | Out-of-scope findings and remaining work, as separate items |

Lead with the outcome. A reader who stops after the first two lines should still know whether
the task succeeded.

## Status vocabulary

Use one word, and use it precisely.

| Status | Meaning |
| --- | --- |
| **Verified** | Done, and the required checks ran and passed |
| **Unverified** | Done as far as the author can tell; one or more required checks did not run |
| **Partial** | Some done conditions met; the report says which |
| **Blocked** | Stopped at a stop-and-ask trigger; the report says what is needed |
| **Not started** | Nothing changed |

When a report covers a list of items, as in a workflow or an item-by-item run, each item gets
one of three: **verified** (its check ran and passed), **failed** (its check ran and failed) or
**unverified** (its check did not run).

"Verified" has a specific meaning: the rung the task's done conditions asked for was reached
(see [verification](06-verification.md)). A task can be verified at its own rung while the
change still needs a higher one before release. Work that passed a build but was asked for observed
behaviour is "unverified", however confident the author is.

## Reporting rules

- **Ground every claim in this session.** If the report says tests pass, the session ran them
  and can show the output.
- **Separate what was done from what was released.** "Implemented and verified; not committed"
  is a complete and useful statement.
- **State failures plainly.** A failing check goes in the report with its output, not in a
  footnote.
- **Do not round up.** "9 of 11 checks pass; 2 not run because the staging database was
  unreachable" is better than "checks pass".
- **Keep it readable.** The report is for someone who was not there. Full sentences, no private
  shorthand from the session, no log dumps.

## Before each release step

A release step is anything on the permission ladder in
[authority and safety](04-authority-and-safety.md#release-permissions). Before taking one,
confirm:

- [ ] The step was explicitly granted for this task and this target.
- [ ] The diff contains only in-scope changes.
- [ ] Required checks ran on the exact state being released.
- [ ] No secrets, credentials, personal paths or private identifiers are in the diff, the commit
      message or generated files.
- [ ] The commit message says what changed and why.

### Commits and pull requests

- One work item per commit series and per pull request.
- The pull request description carries the run card and the completion report, so the review
  does not depend on a conversation nobody else can see.
- Follow your project's policy on disclosing AI assistance. If it has none, saying so in the
  pull request costs nothing.

### Versioned releases

For anything with a version number (a package, a document set, a tagged release):

1. Update the changelog and the version in one change.
2. Build the release artifacts from a clean checkout of the exact commit.
3. Record checksums for the artifacts.
4. Prepare the release as a draft.
5. Publish only on explicit approval from the person accountable for it.

Publication is the one step that should always have a human decision directly in front of it. A
session can prepare everything up to that point.

## Leave the documentation true

When a change makes a document wrong, fixing the document is part of the change. Decisions and
the reasons for them belong somewhere durable: the commit message, the pull request, the
changelog or the docs. A conversation is not durable, and the next person will not have it.
