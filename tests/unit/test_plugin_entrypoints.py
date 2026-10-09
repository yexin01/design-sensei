"""Plugin entry points: slash commands (commands/*.md) and subagents (agents/*.md).

Checks front matter, that every CLI command, flag, path and link they mention exists, and that the reviewer
agent stays read-only and covers the whole design-qa rubric. Standard library only.
"""

import argparse
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

from tests import helpers
from dslib import catalog, knowledge
from dslib.paths import resolve_layout
import design_sensei

ROOT = helpers.ROOT
COMMANDS = ROOT / "commands"
AGENTS = ROOT / "agents"
LAUNCHER_REL = "skills/design-sensei/scripts/design-sensei"
PLUGIN_ROOT_VAR = "${CLAUDE_PLUGIN_ROOT}"

EXPECTED_COMMANDS = {"brief", "style", "review", "sources"}
EXPECTED_AGENTS = {"design-reviewer"}
# Subcommands another change may add; markdown may mention them before the CLI has them, and must then offer a fallback.
OPTIONAL_SUBCOMMANDS = {"recommend"}
AGENT_COLORS = {"blue", "cyan", "green", "yellow", "magenta", "red"}
AGENT_MODELS = {"inherit", "sonnet", "opus", "haiku"}
READ_ONLY_TOOLS = {"Read", "Grep", "Glob", "Bash"}
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit", "MultiEdit"}
FORBIDDEN_AGENT_KEYS = {"hooks", "mcpServers", "permissionMode"}  # not supported for plugin agents
PLUGIN_DIRS = ("skills", "knowledge", "catalog", "docs", "scripts", "commands", "agents", "bin")


def command_tree(parser):
    """{name: node} for every argparse sub-command; node = {"flags": set, "sub": {...}}."""
    tree = {}
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, sub in action.choices.items():
                tree[name] = {"flags": set(sub._option_string_actions), "sub": command_tree(sub)}
    return tree


CLI = command_tree(design_sensei.build_parser())


def markdown_files(folder):
    return sorted(folder.rglob("*.md")) if folder.is_dir() else []


def load(path):
    text = path.read_text(encoding="utf-8")
    meta, body, error = knowledge.parse_frontmatter(text)
    return meta, body, error


def as_list(value):
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return list(value)


def code_snippets(body):
    """Text inside fenced blocks (per line) and inline code spans."""
    snippets = []
    for block in re.findall(r"```[^\n]*\n(.*?)```", body, re.S):
        snippets.extend(line for line in block.splitlines() if line.strip())
    rest = re.sub(r"```[^\n]*\n.*?```", "", body, flags=re.S)
    snippets.extend(re.findall(r"`([^`\n]+)`", rest))
    return snippets


def cli_invocations(text):
    """Yield (words after the launcher/`design-sensei`, flags after them) for each mention in a snippet."""
    m = re.search(r"design-sensei\s+(.*)$", text)
    if not m:
        return
    tail = m.group(1)
    words = []
    for token in tail.split():
        if token.startswith("-") or token[0] in "\"'<[$":
            break
        if not re.fullmatch(r"[a-z][a-z-]*", token):
            break
        words.append(token)
    yield words, re.findall(r"(?<![\w-])(--[a-z][a-z-]*)", tail)


class ComponentFilesTest(unittest.TestCase):
    def test_expected_entry_points_exist(self):
        self.assertEqual({p.stem for p in COMMANDS.glob("*.md")} & EXPECTED_COMMANDS, EXPECTED_COMMANDS)
        self.assertEqual({p.stem for p in AGENTS.glob("*.md")} & EXPECTED_AGENTS, EXPECTED_AGENTS)

    def test_manifest_needs_no_component_paths(self):
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "design-sensei")  # commands are invoked as /design-sensei:<name>
        # commands/ and agents/ are discovered from the plugin root; they must not sit inside .claude-plugin/
        self.assertFalse((ROOT / ".claude-plugin" / "commands").exists())
        self.assertFalse((ROOT / ".claude-plugin" / "agents").exists())
        for key in ("commands", "agents"):  # optional overrides, if ever added, must resolve
            value = manifest.get(key)
            for entry in [value] if isinstance(value, str) else (value if isinstance(value, list) else []):
                self.assertTrue((ROOT / entry).exists(), "plugin.json %s entry %s does not exist" % (key, entry))

    def test_launcher_exists_and_is_executable(self):
        launcher = ROOT / LAUNCHER_REL
        self.assertTrue(launcher.is_file())
        self.assertTrue(os.access(str(launcher), os.X_OK), "%s must be executable" % LAUNCHER_REL)


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.files = markdown_files(COMMANDS)
        self.assertTrue(self.files, "no commands/*.md found")

    def test_front_matter(self):
        for path in self.files:
            meta, body, error = load(path)
            where = path.relative_to(ROOT).as_posix()
            self.assertIsNone(error, "%s: %s" % (where, error))
            self.assertRegex(path.stem, r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", where)
            desc = meta.get("description")
            self.assertIsInstance(desc, str, where)
            self.assertTrue(10 <= len(desc.strip()) <= 80, "%s: description should be 10-80 characters, got %d" % (where, len(desc or "")))
            tools = meta.get("allowed-tools")
            self.assertTrue(tools, "%s: allowed-tools is required" % where)
            self.assertTrue(all(isinstance(t, str) and t.strip() for t in as_list(tools)), where)
            if "$ARGUMENTS" in body:
                self.assertIsInstance(meta.get("argument-hint"), str, "%s uses $ARGUMENTS and needs a string argument-hint" % where)
            self.assertGreater(len(body.strip()), 200, where)

    def test_allowed_tools_never_include_write_tools(self):
        for path in self.files:
            meta, _, _ = load(path)
            names = {t.split("(")[0] for t in as_list(meta["allowed-tools"])}
            self.assertFalse(names & WRITE_TOOLS, "%s grants a write tool" % path.name)

    def test_bash_permissions_point_at_the_launcher_and_real_subcommands(self):
        for path in self.files:
            meta, _, _ = load(path)
            for tool in as_list(meta["allowed-tools"]):
                m = re.fullmatch(r"Bash\((.+)\)", tool)
                if not m:
                    continue
                pattern = m.group(1)
                prefix = "%s/%s " % (PLUGIN_ROOT_VAR, LAUNCHER_REL)
                self.assertTrue(pattern.startswith(prefix), "%s: Bash pattern %r must use %s" % (path.name, pattern, prefix.strip()))
                words = [w for w in pattern[len(prefix):].split() if w != "*"]
                self.assertTrue(words, "%s: %r names no sub-command" % (path.name, pattern))
                self.assert_known_words(words, path.name)

    def assert_known_words(self, words, where):
        node = {"sub": CLI}
        for i, word in enumerate(words):
            if i == 0 and word in OPTIONAL_SUBCOMMANDS and word not in CLI:
                return
            self.assertTrue(word in node["sub"], "%s: unknown design-sensei sub-command %r in %s" % (where, word, " ".join(words)))
            node = node["sub"][word]

    def test_every_cli_mention_is_a_real_command_and_flag(self):
        seen = 0
        for path in self.files + markdown_files(AGENTS):
            _, body, _ = load(path)
            for snippet in code_snippets(body):
                for words, flags in cli_invocations(snippet):
                    if not words:
                        continue
                    seen += 1
                    if words[0] in OPTIONAL_SUBCOMMANDS and words[0] not in CLI:
                        continue
                    node = {"sub": CLI, "flags": set()}
                    for word in words:
                        if word not in node["sub"]:
                            if node is not None and node["sub"]:
                                self.fail("%s: %r is not a sub-command in `%s`" % (path.name, word, snippet))
                            break  # positional argument after a leaf command, for example `search liquid`
                        node = node["sub"][word]
                    for flag in flags:
                        self.assertTrue(flag in node["flags"], "%s: `%s` has no flag %s" % (path.name, snippet, flag))
        self.assertGreater(seen, 10, "expected the commands to mention the CLI")

    def test_style_works_with_and_without_recommend(self):
        _, body, _ = load(COMMANDS / "style.md")
        self.assertIn("recommend --help", body)
        self.assertIn("search", body)
        self.assertIn("--category design-style", body)

    def test_review_covers_widths_and_delegates_to_the_agent(self):
        _, body, _ = load(COMMANDS / "review.md")
        for needle in ("375", "768", "1280", "1920", "reduced-motion", "eval", "design-reviewer"):
            self.assertIn(needle, body)

    def test_brief_stops_before_code_and_asks_for_approval(self):
        _, body, _ = load(COMMANDS / "brief.md")
        self.assertIn("do not write, edit or generate any code", body)
        self.assertRegex(body, r"(?i)approve")

    def test_sources_never_runs_sync_on_its_own(self):
        meta, body, _ = load(COMMANDS / "sources.md")
        self.assertFalse([t for t in as_list(meta["allowed-tools"]) if "sync" in t])
        self.assertIn("never run them", body)
        self.assertIn("sources sync", body)


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.files = markdown_files(AGENTS)
        self.assertTrue(self.files, "no agents/*.md found")

    def test_front_matter(self):
        for path in self.files:
            meta, body, error = load(path)
            where = path.relative_to(ROOT).as_posix()
            self.assertIsNone(error, "%s: %s" % (where, error))
            self.assertRegex(meta.get("name", ""), r"^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]$", where)
            self.assertEqual(meta["name"], path.stem, "%s: name must match the file name" % where)
            self.assertTrue(10 <= len(meta.get("description", "")) <= 5000, where)
            self.assertIn(meta.get("model"), AGENT_MODELS, where)
            self.assertIn(meta.get("color"), AGENT_COLORS, where)
            self.assertFalse(FORBIDDEN_AGENT_KEYS & set(meta), "%s uses front matter keys that plugin agents do not support" % where)
            self.assertTrue(20 <= len(body.strip()) <= 10000, "%s: system prompt length %d" % (where, len(body.strip())))

    def test_reviewer_is_read_only(self):
        meta, body, _ = load(AGENTS / "design-reviewer.md")
        tools = set(as_list(meta["tools"]))
        self.assertTrue(tools <= READ_ONLY_TOOLS, "design-reviewer may only use %s, got %s" % (sorted(READ_ONLY_TOOLS), sorted(tools)))
        self.assertIn("Bash", tools)
        for needle in ("never create, edit", "Never run:", "sources sync", "not verified", "licence", "Prioritised fixes", "Not verified"):
            self.assertIn(needle, body if needle != "licence" else body.lower())

    def test_reviewer_description_names_triggers(self):
        meta, _, _ = load(AGENTS / "design-reviewer.md")
        desc = meta["description"]
        self.assertTrue(desc.startswith("Use this agent"), desc[:40])
        self.assertIn("/design-sensei:review", desc)
        self.assertIn("When to invoke", desc)
        self.assertRegex(desc, r"(?i)do not use")

    def test_reviewer_scores_every_rubric_category(self):
        qa = (ROOT / "skills" / "design-sensei" / "references" / "design-qa.md").read_text(encoding="utf-8")
        categories = re.findall(r"^### \d+\. (.+)$", qa, re.M)
        self.assertEqual(len(categories), 10)
        _, body, _ = load(AGENTS / "design-reviewer.md")
        for name in categories:
            self.assertIn(name.lower(), body.lower(), "design-reviewer does not mention rubric category %r" % name)

    def test_command_references_an_existing_agent(self):
        names = {p.stem for p in AGENTS.glob("*.md")}
        for path in markdown_files(COMMANDS):
            _, body, _ = load(path)
            for ref in re.findall(r"subagent_type: `?([a-z0-9:-]+)", body):
                self.assertIn(ref.split(":")[-1], names, "%s delegates to unknown agent %s" % (path.name, ref))


class ReferenceTests(unittest.TestCase):
    """Paths, links and pattern ids mentioned in commands and agents must resolve."""

    def files(self):
        return markdown_files(COMMANDS) + markdown_files(AGENTS)

    def test_plugin_root_paths_exist(self):
        checked = 0
        for path in self.files():
            text = path.read_text(encoding="utf-8")
            for rel in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)", text):
                rel = rel.rstrip(".,")
                checked += 1
                self.assertTrue((ROOT / rel).exists(), "%s references missing path %s/%s" % (path.name, PLUGIN_ROOT_VAR, rel))
        self.assertGreater(checked, 10)

    def test_bare_repo_paths_exist(self):
        pattern = re.compile(r"`((?:%s)/[^`\s*<>]+)`" % "|".join(PLUGIN_DIRS))
        for path in self.files():
            for rel in pattern.findall(path.read_text(encoding="utf-8")):
                if "..." in rel:
                    continue
                self.assertTrue((ROOT / rel.rstrip(".,")).exists(), "%s references missing path %s" % (path.name, rel))

    def test_markdown_links_resolve(self):
        for path in self.files():
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\((?!https?://|#|mailto:)([^)#\s]+)", text):
                self.assertTrue((path.parent / target).resolve().exists(), "%s has broken link %s" % (path.name, target))

    def test_double_bracket_pattern_links_exist(self):
        with tempfile.TemporaryDirectory(prefix="ds test ") as home:
            pattern_ids = {p["id"] for p in catalog.load_patterns(resolve_layout(root=str(ROOT), home=home))}
        for path in self.files():
            for pid in re.findall(r"\[\[([a-z0-9-]+)\]\]", path.read_text(encoding="utf-8")):
                self.assertIn(pid, pattern_ids, "%s: [[%s]] is not a pattern id" % (path.name, pid))

    def test_no_machine_specific_paths(self):
        for path in self.files():
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"/Users/|/home/[a-z]|C:\\Users", path.name)


if __name__ == "__main__":
    unittest.main()
