# Releasing

A release is a tagged commit plus four assets. Publication is a human decision: everything up to
the draft can be prepared by anyone, and the draft is published only by the maintainer.

## Assets

`python3 scripts/build.py --package` writes these to `dist/release/` (not committed):

| Asset | Contents |
| --- | --- |
| `claude-execution-playbook-vX.Y.Z.md` | The single-file edition |
| `claude-execution-playbook-vX.Y.Z.zip` | The repository at that version: single file, modular documents, templates, examples, skill, scripts and licenses |
| `claude-execution-playbook-skill-vX.Y.Z.zip` | The skill folder only, to unzip into `~/.claude/skills/` |
| `SHA256SUMS.txt` | Checksums for the three files above |

The archives are reproducible: the same commit produces the same bytes. CI builds them on every
push, verifies the checksums and uploads them as a workflow artifact.

## Checklist

1. Re-verify `docs/model-data.md` against the vendor pages and update its date.
2. Set `VERSION`, and move the changelog entries under a new version heading with today's date.
3. Run the local checks (the lint step needs Node.js):

   ```bash
   python3 scripts/build.py --check
   python3 scripts/check.py --external
   python3 -m unittest discover -s tests
   npx --yes markdownlint-cli2@0.24.0
   ```

4. Commit, push, and wait for CI to pass on that commit.
5. Build the assets from a clean checkout of the commit:

   ```bash
   python3 scripts/build.py --package
   (cd dist/release && shasum -a 256 --check SHA256SUMS.txt)
   ```

6. Write the release notes from the changelog entry for the version, in a file outside the
   repository, and create the release as a **draft** that tags the commit CI passed on:

   ```bash
   VERSION=$(cat VERSION)
   gh release create "v$VERSION" dist/release/* \
     --draft --target "$(git rev-parse HEAD)" \
     --title "v$VERSION" --notes-file /path/to/release-notes.md
   ```

   The tag is created when the draft is published, not before.
7. The maintainer reviews the draft and publishes it.

## After publishing

- Confirm the asset checksums on the release page match `SHA256SUMS.txt`.
- Confirm the links in the README resolve for a signed-out visitor.
