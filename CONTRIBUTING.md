# Contributing

Corrections and improvements are welcome. Open an issue or a pull request.

## Ground rules

- **Edit the sources, not the generated files.** `docs/`, `templates/` and `examples/` are the
  source. `dist/claude-execution-playbook.md` and the three reference files next to
  `skill/execution-brief/SKILL.md` are generated; run `python3 scripts/build.py` after a change
  and commit the result.
- **Keep volatile facts in one place.** Model versions, model IDs, prices and product limits go
  in `docs/model-data.md`, each with a link to the vendor page it came from. Chapters and
  templates use tier names. The checker fails otherwise.
- **Mark the difference between a vendor fact and a recommendation.** A vendor fact names the
  page and links to it. Everything else is this project's opinion and should read that way.
- **No unmeasured claims.** Do not add numbers, benchmarks or "faster" and "cheaper" statements
  unless they are quoted from a linked public source.
- **Examples use fictional repositories** and `example.com` or `.test` domains.
- **Do not include private material**: no internal names, paths, identifiers or policies from
  any organization.

## Before opening a pull request

The scripts need Python 3.10 or later. The lint step needs Node.js.

```bash
python3 scripts/build.py
python3 scripts/build.py --check
python3 scripts/check.py
python3 -m unittest discover -s tests
npx --yes markdownlint-cli2@0.24.0
```

## Updating the model data

1. Read each source page linked in `docs/model-data.md` and update the tables.
2. Update the tier mapping if the lineup changed, and the examples if a model they name is no
   longer current.
3. Set the **Verified** date at the top of the file to the day you checked.
4. Run `python3 scripts/check.py --external` to confirm the source links still resolve.
5. Add a patch entry to `CHANGELOG.md`.

## Adding a template or an example

- A template has one fenced `text` block to copy, with `{{placeholders}}`, and a short notes
  section. Add it to `PARTS` in `scripts/build.py` and to `templates/README.md`.
- An example has the five sections the checker requires (Situation, Configuration, Prompt,
  Validation criteria, What would change the recommendation), names the templates it
  uses, and leaves no placeholder unfilled.

## Licensing of contributions

By contributing you agree that text is licensed under CC BY 4.0 and that templates, skill files
and scripts are licensed under MIT No Attribution, as described in `LICENSE` and
`LICENSE-TEMPLATES`.
