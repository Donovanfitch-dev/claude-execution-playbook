# Authority and safety boundaries

Authority is what a session is permitted to do. It is separate from what the model is capable of
doing, and it should be written down before the run, not inferred afterwards.

## Task mode

Every task has one mode. It sets the ceiling for the whole run.

| Mode | The session may | The session may not |
| --- | --- | --- |
| **Investigate** | Read, search, run read-only commands, report findings | Edit files or change any state |
| **Propose** | Everything in investigate, plus write a plan or a draft diff for review | Apply the change |
| **Change** | Edit within the stated scope, run checks, fix what its own change broke | Go outside the scope, or take a release step without a separate grant |
| **Review** | Read the change and the criteria, run checks, report findings | Edit. Fixing a finding is a new change-mode task |

If a run in one mode discovers it needs another, it pauses and says so.

## Scope

State scope as two lists.

- **May change**: paths, components or systems the session is allowed to modify.
- **Must not change**: interfaces, files, behaviours and data that stay as they are, including
  work already sitting uncommitted in the tree.

Then ask for the smallest change that meets the proof, and for anything else the session
notices to be listed in the report instead of fixed. That one sentence prevents most scope
growth: the tidy-up nobody asked for arrives as a suggestion you can accept or ignore.

## Release permissions

Getting a change from an edit to production is a ladder. Each rung above the first is a separate
permission, and each is off unless the task owner turns it on.

| Rung | Default | Grant it by naming |
| --- | --- | --- |
| Edit files in the working tree | On, in change mode | The scope |
| Commit | Off | The branch |
| Push | Off | The remote and branch |
| Pull request | Off | The target repository |
| Release: merge, tag, publish or deploy | Off | Exactly what and where, each time |

The run card and the prompt carry these as one `Permissions` line with four entries: commit,
push, pull request, release.

Two rules keep the ladder honest:

- **A grant covers what it names.** Permission to push one branch is not permission to push
  another, and permission given for one task does not carry to the next.
- **Report the rung you reached.** The final report states the commit, push and release state
  separately from whether the task succeeded. See [completion](08-completion-and-release.md).

## Actions that are hard to undo

Pause and confirm before any action that deletes data, rewrites history, overwrites a file the
session did not create, sends something outside the workspace, or spends money. Look at the
target first: list what a delete would remove, read the file an overwrite would replace.

Sending content to an external service is publishing it. It may be cached or indexed even if it
is deleted afterwards.

## Risky surfaces: propose first

A surface is risky when a mistake on it is expensive, slow to notice, or hard to reverse. In
most codebases that means anything that decides who is allowed to do what, anything that
rewrites stored data, anything that moves money, and anything that changes what production
runs. For these, do not start by editing. Run the task in propose mode and ask for a short note
that answers four questions:

| Question | A good answer contains |
| --- | --- |
| What is true today, and what will be true after? | The current behaviour with file references, and the intended behaviour |
| What breaks if this is wrong? | Who and what is affected, and how quickly anyone would notice |
| How do we back it out? | A concrete rollback, tested where that is practical |
| How will we know it worked? | The checks, including one that fails before the change and passes after |

Review the note, then run the change as a second work item, usually with
[checkpoints](02-topology-and-strategy.md#checkpoints-where-does-the-run-pause).

## Prompts are not enforcement

A prompt is a request. A model will follow "never read `.env`" almost every time, and "almost"
is the problem for rules that cannot have exceptions.

The Claude Code [best practices](https://code.claude.com/docs/en/best-practices) page says this
directly: if something has to happen every time, make it a hook, a deny rule or a managed
setting, because an instruction file is for guidelines and the model is allowed to decide a
guideline does not apply. The mechanisms are documented under
[permissions](https://code.claude.com/docs/en/permissions) and
[hooks](https://code.claude.com/docs/en/hooks-guide).

| The rule is... | Put it in |
| --- | --- |
| A preference or convention | The prompt or the project instruction file |
| A boundary for this task | The prompt's `<boundaries>` block |
| Absolute | Tooling: permission rules, hooks, a sandbox, branch protection, CI |

## Untrusted content

Files, web pages, issue comments, tool output and messages from other agents can all contain
text shaped like instructions. Treat that text as information about the content, not as a
request from the task owner. An action that changes something outside the session needs a basis
in what the owner actually asked for.

In delegated work this applies in both directions: a worker's summary is evidence to weigh, and
a brief passed to a worker should say which sources it may trust.

## Secrets and credentials

- Do not paste credentials into prompts, briefs, reports or commit messages.
- Do not have a session create credentials, weaken sign-in, or work around an access control in
  order to finish a task. Missing access is a reason to pause.
- Keep secrets out of files the session can read where your tooling allows it, and out of
  anything copied into a new worktree unless the task needs it.

## Stop-and-ask triggers

The [execution prompt](../templates/execution-prompt.md) tells the session to carry on without
asking for anything it can undo, and to pause, saying what it found, in five cases:

- the only way forward touches something outside "may change";
- a step cannot be undone and the permissions do not grant it;
- access is missing: a permission, a credential or a tool;
- the brief and the repository disagree, and the difference matters;
- it is not sure which repository, branch or environment it is in.

Add task-specific triggers sparingly. A session that pauses for routine, reversible decisions is
as unhelpful as one that never pauses.
