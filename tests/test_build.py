"""Unit tests for the build helpers. Run: python3 -m unittest discover -s tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build  # noqa: E402
import check  # noqa: E402


class SlugTests(unittest.TestCase):
    def test_slug_matches_github_style(self):
        self.assertEqual(build.slugify("The independence test"), "the-independence-test")
        self.assertEqual(
            build.slugify("2. Principles are stable; model facts are not"),
            "2-principles-are-stable-model-facts-are-not",
        )
        self.assertEqual(build.slugify("CLAUDE.md snippet"), "claudemd-snippet")
        self.assertEqual(build.slugify("A & B"), "a--b")

    def test_repeated_headings_get_suffixes(self):
        slugger = build.Slugger()
        self.assertEqual([slugger.slug("Notes") for _ in range(3)], ["notes", "notes-1", "notes-2"])

    def test_heading_text_drops_markup(self):
        self.assertEqual(build.heading_text("Use `git` and [docs](x.md)"), "Use git and docs")


class FenceTests(unittest.TestCase):
    def test_headings_inside_fences_are_ignored(self):
        text = "# Title\n\n```text\n# not a heading\n```\n\n## Real\n"
        self.assertEqual([h[1] for h in build.headings(text)], ["Title", "Real"])

    def test_longer_fence_contains_shorter_one(self):
        text = "````markdown\n```text\ninner\n```\n````\nafter\n"
        flags = [in_code for _, in_code in build.iter_lines(text)]
        self.assertEqual(flags, [True, True, True, True, True, False, False])

    def test_fenced_blocks_returns_info_and_content(self):
        text = "a\n\n```text\none\ntwo\n```\n\n~~~bash\nthree\n~~~\n"
        self.assertEqual(
            check.fenced_blocks(text), [("text", ["one", "two"]), ("bash", ["three"])]
        )


class LinkTests(unittest.TestCase):
    def test_relative_targets_resolve_from_the_source_file(self):
        self.assertEqual(
            build.split_target("docs/a.md", "../templates/run-card.md#field-notes"),
            ("templates/run-card.md", "field-notes"),
        )
        self.assertEqual(build.split_target("docs/a.md", "#top"), ("docs/a.md", "top"))
        self.assertIsNone(build.split_target("docs/a.md", "https://example.com/x"))

    def test_links_in_inline_code_are_left_alone(self):
        line = "See [a](a.md) but not `[b](b.md)`."
        out = build.rewrite_links(line, lambda text, target: f"<{text}>")
        self.assertEqual(out, "See <a> but not `[b](b.md)`.")


class EditionTests(unittest.TestCase):
    def setUp(self):
        self.edition = build.build_single_file()

    def test_every_anchor_link_resolves(self):
        anchors = {anchor for _, _, anchor in build.headings(self.edition)}
        targets = [target for _, target in check.links(self.edition) if target.startswith("#")]
        self.assertGreater(len(targets), 50)
        self.assertEqual([t for t in targets if t[1:] not in anchors], [])

    def test_no_relative_file_links_remain(self):
        relative = [
            target
            for _, target in check.links(self.edition)
            if not target.startswith("#") and build.split_target("x.md", target) is not None
        ]
        self.assertEqual(relative, [])

    def test_templates_keep_their_copy_blocks(self):
        for path in build.PARTS[1][1]:
            if path.endswith("README.md"):
                continue
            block = "\n".join(check.copy_block(path))
            self.assertIn(block, self.edition, path)

    def test_build_is_deterministic(self):
        self.assertEqual(self.edition, build.build_single_file())


class TemplateTests(unittest.TestCase):
    def test_execution_prompt_blocks(self):
        tags = check.block_tags(check.copy_block("templates/execution-prompt.md"))
        self.assertEqual(
            tags, ["task", "proof", "background", "boundaries", "stop_and_ask", "final_report"]
        )

    def test_run_card_fields(self):
        labels = check.block_labels(check.copy_block("templates/run-card.md"))
        self.assertEqual(
            labels,
            ["Task", "Where", "May change", "Must not change", "Mode", "Permissions",
             "Done when", "Checks", "Pause when", "If it misses", "Topology", "Checkpoints", "Unit of work",
             "Model", "Effort", "Speed", "Availability"],
        )


if __name__ == "__main__":
    unittest.main()
