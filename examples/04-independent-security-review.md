# Example 4: Independent security review

Templates used: [run card](../templates/run-card.md), [review brief](../templates/review-brief.md).

## Situation

`notify-gateway` is a service that sends email notifications. A branch,
`feat/unsubscribe-links`, adds one-click unsubscribe: each email carries a link with a signed
token, and `GET /unsubscribe?token=...` turns notifications off for that recipient without a
login. The specification, `docs/specs/unsubscribe-links.md`, describes the token format and the
endpoint's intended behaviour.

An unauthenticated endpoint that changes account state is a
[risky surface](../docs/04-authority-and-safety.md#risky-surfaces-propose-first). The author's
session has finished and reports its task as verified at rung 2, which is what its brief asked
for. This surface needs rung 4 before release, so before a pull request is opened, a reviewer
that did not write the change checks it.

## Configuration

```text
RUN CARD
Task:             A verdict on whether the unsubscribe change meets its security criteria, with evidence per finding.
Where:            notify-gateway, branch feat/unsubscribe-links, clean working tree

Scope
May change:       nothing
Must not change:  every file; the reviewer does not edit, commit or fix

Authority
Mode:             review
Permissions:      commit no, push no, pull request no, release no

Proof
Done when:        a verdict, each criterion marked checked or not checked, and each finding with
                  location, failure scenario, severity and confidence
Checks:           git diff main...feat/unsubscribe-links; npm test -- unsubscribe

Exit
Pause when:       the standard triggers
If it misses:     if criteria cannot be checked from the repository, report which and why; 1 attempt

Plan (also stated in the prompt)
Topology:         single session, fresh, with no access to the author's conversation
Checkpoints:      none
Unit of work:     the whole task

Session settings (applied in the tool)
Model:            Advanced (Claude Opus 5.5)
Effort:           high
Speed:            standard
Availability:     /model and /effort status at session start, 2026-11-10
```

### Why this configuration

- **Fresh session.** The reviewer must not have read the author's reasoning. It gets the
  criteria and the diff. The author's conversation and completion report are left out.
- **Advanced tier at high effort.** The reviewer should be at least as capable as the author,
  and the cost of a missed defect on this surface is high. This is a recommendation, not a
  vendor requirement.
- **Review mode, read-only.** A reviewer that fixes things becomes a second author, and its
  fixes would then need their own review.
- **Single session, no checkpoints.** One coherent reading of one diff. Splitting the review by
  file would hide the defects that live between files.

### Making read-only more than a request

The brief tells the reviewer not to edit. To back that with tooling in Claude Code, run the
review as a subagent whose definition limits its tools. The `tools`, `model` and `effort` fields
are documented in the vendor's subagent reference:

```markdown
---
name: security-reviewer
description: Reviews a diff against stated security criteria. Read-only.
tools: Read, Grep, Glob, Bash
model: opus
effort: high
---

Review the change you are given against the criteria in the brief. Do not edit files.
Report findings with file, line, a failure scenario, severity and confidence.
```

`Bash` is included so the reviewer can run `git diff` and the tests. A shell can also modify
files, so if you need a hard guarantee, remove `Bash` and accept a reading-only review, or add
permission rules that deny write commands.

## Prompt

```text
<task>
Review the diff between main and feat/unsubscribe-links against the criteria below.
Mode: review. Do not edit files or fix what you find.
Permissions: commit no; push no; pull request no; release no.
</task>

<criteria>
The change is correct only if:
- A token cannot be forged or altered without the server's signing key.
- A token is bound to one recipient and one notification list, and cannot be used for another.
- A token expires, and an expired or malformed token changes nothing.
- The endpoint's responses and timing do not reveal whether an email address has an account.
- Using a valid token twice is harmless.
- The endpoint cannot be used to redirect a browser to an arbitrary site.
- The signing key is read from configuration and never logged or returned.
- Requests with a login session behave exactly as before this change.
</criteria>

<sources>
The change: git diff main...feat/unsubscribe-links
The specification: docs/specs/unsubscribe-links.md
You may read any file in the repository and run read-only commands and the test suite,
including npm test -- unsubscribe.
</sources>

<focus>
Report defects that affect: security and the stated criteria.
Skip style, naming and formatting unless they hide a defect.
"No defects found" is an acceptable result; do not invent findings to fill the report.
</focus>

<final_report>
Verdict first: meets the criteria, does not meet them, or cannot tell.
Then one entry per finding, most severe first:
- Where: file and line.
- What is wrong, in one sentence.
- How to see it fail: an input, a command or a sequence of steps.
- Severity: blocks release, should fix, or note.
- Confidence: confirmed by running something, or inferred from reading.
Then: which criteria you checked and how, and which you could not check.
</final_report>
```

## Validation criteria

Accept the review, as a review, when all of these hold:

- [ ] The report opens with one of the three verdicts.
- [ ] Each of the eight criteria is marked checked (with how) or not checked (with why).
- [ ] Every finding has a file and line, a concrete failure scenario, a severity and a
      confidence.
- [ ] `git status --short`, run by you after the review, is empty: the reviewer changed nothing.
- [ ] No finding is about style.

Then, before acting on it:

- [ ] The author's side reproduces each "blocks release" finding. A finding that cannot be
      reproduced goes back to the reviewer with what was tried.
- [ ] Fixes are a new change-mode work item with their own run card, and the fixed diff is
      reviewed again.
- [ ] A person reads the review and the diff before the pull request is merged (rung 5).

## What would change the recommendation

| If... | Then... |
| --- | --- |
| The diff is large and spans unrelated areas | Split it into separate pull requests first; then one review per pull request |
| The review reports "cannot tell" on most criteria | The criteria or the specification are too vague; fix them, which is a brief miss |
| You want a second opinion on one finding | A second fresh reviewer for that finding only, given the criterion and the code, not the first review |
| The change is a routine refactor with no security surface | Rung 2 and a human read are enough; an independent security review is not proportionate |
