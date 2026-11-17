"""Self-tests for the UADR framework automation. Standard library only.

Run: python3 -m unittest discover -s .automation/tests
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AUTOMATION = Path(__file__).resolve().parent.parent
ROOT = AUTOMATION.parent
for sub in ("", "scripts", "validation"):
    sys.path.insert(0, str(AUTOMATION / sub))
import uadr_lib as lib
import route


def uadr(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / ".automation/uadr.py"), *args],
                          capture_output=True, text=True, cwd=root)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class LibraryTests(unittest.TestCase):
    def test_frontmatter_roundtrip(self):
        meta, body = lib.parse_frontmatter("---\npurpose: A: b\nread_when: now\n---\n# Title\n")
        self.assertEqual(meta, {"purpose": "A: b", "read_when": "now"})
        self.assertEqual(body, "# Title\n")
        self.assertEqual(lib.parse_frontmatter("# No frontmatter\n")[0], {})

    def test_glob_match(self):
        self.assertTrue(lib.glob_match("src/billing/**", "src/billing/a/b.py"))
        self.assertTrue(lib.glob_match("src/billing", "src/billing/a.py"))
        self.assertTrue(lib.glob_match("**/*.md", "docs/x/y.md"))
        self.assertTrue(lib.glob_match("docs/**", "docs/a.md"))
        self.assertFalse(lib.glob_match("src/billing/**", "src/billing2/a.py"))
        self.assertFalse(lib.glob_match("src/*.py", "src/a/b.py"))

    def test_most_specific_module_wins(self):
        modules = [{"name": "core", "paths": ["src/**"], "doc": "a"},
                   {"name": "billing", "paths": ["src/billing/**"], "doc": "b"}]
        self.assertEqual(lib.module_for_path("src/billing/x.py", modules)["name"], "billing")
        self.assertEqual(lib.module_for_path("src/other/x.py", modules)["name"], "core")
        self.assertIsNone(lib.module_for_path("tools/x.py", modules))


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.routes = lib.load_routes(ROOT)["routes"]

    def top(self, text: str) -> str:
        return route.classify(text, self.routes)[0][1]

    def test_classification(self):
        self.assertEqual(self.top("fix crash when saving an order"), "bugfix")
        self.assertEqual(self.top("add support for gift cards"), "feature")
        self.assertEqual(self.top("add a column to the users table with a migration"), "database")
        self.assertEqual(self.top("bump the http library version"), "dependency-upgrade")
        self.assertEqual(self.top("checkout page latency is too high, optimise it"), "performance")
        self.assertEqual(self.top("onboard this existing repository"), "onboard-existing-repo")

    def test_every_route_is_complete(self):
        for name, r in self.routes.items():
            self.assertTrue((ROOT / r["workflow"]).is_file(), name)
            for skill in r["skills"]:
                self.assertTrue((ROOT / lib.SKILLS_REL / skill / "SKILL.md").is_file(), f"{name}: {skill}")


class FrameworkGateTests(unittest.TestCase):
    def test_framework_passes_its_own_checks(self):
        result = uadr(ROOT, "check")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_entry_point_within_budget(self):
        budget = lib.load_config(ROOT)["context_budget"]["entry_point_tokens"]
        self.assertLessEqual(lib.file_tokens(ROOT / "AGENTS.md"), budget)


class AdoptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name) / "repo"
        self.target.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_greenfield(self):
        result = uadr(ROOT, "adopt", "--target", str(self.target), "--name", "Demo", "--description", "A demo.")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        cfg = json.loads((self.target / lib.CONFIG_REL).read_text())
        self.assertEqual(cfg["project"], {"name": "Demo", "mode": "greenfield"})
        self.assertEqual(cfg["commands"]["test"], "")
        self.assertTrue((self.target / "docs/architecture/overview.md").is_file())
        self.assertIn("Demo: A demo.", (self.target / "AGENTS.md").read_text())
        self.assertFalse((self.target / lib.ONBOARDING_REL).exists())
        check = uadr(self.target, "check")
        self.assertEqual(check.returncode, 0, check.stdout)
        # Unconfigured commands must be reported as not run, never as passed.
        run = uadr(self.target, "run", "test")
        self.assertEqual(run.returncode, 3)
        self.assertIn("not run", run.stdout)

    def make_existing(self):
        write(self.target, "README.md", "# Legacy app\n\nSee [missing](nowhere.md)\n")
        write(self.target, "AGENTS.md", "# Our old agent notes\n\nAlways use tabs.\n")
        write(self.target, "docs/notes.md", "Old notes without frontmatter\n")
        write(self.target, "package.json", json.dumps(
            {"name": "legacy", "scripts": {"test": "jest", "build": "tsc"}, "dependencies": {"express": "^4"}}))
        write(self.target, "src/billing/invoice.ts", "export const total = (a: number) => a; // TODO\n")
        write(self.target, "src/billing/invoice.test.ts", "test('x', () => {});\n")
        write(self.target, "src/users/index.ts", "export {};\n")

    def test_existing_repository(self):
        self.make_existing()
        before = {p: (self.target / p).read_bytes() for p in
                  ["README.md", "AGENTS.md", "docs/notes.md", "package.json", "src/billing/invoice.ts"]}
        result = uadr(ROOT, "adopt", "--target", str(self.target))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("mode: existing", result.stdout)
        for rel, content in before.items():
            self.assertEqual((self.target / rel).read_bytes(), content, f"{rel} was modified")
        self.assertTrue((self.target / lib.ONBOARDING_REL / "conflicts/AGENTS.md").is_file())
        inventory = (self.target / lib.ONBOARDING_REL / "inventory.md").read_text()
        for expected in ("TypeScript", "`src/billing`", "`src/users`", "npm run test", "express"):
            self.assertIn(expected, inventory)
        self.assertTrue((self.target / lib.ONBOARDING_REL / "migration-report.md").is_file())
        cfg = json.loads((self.target / lib.CONFIG_REL).read_text())
        self.assertIn("docs/notes.md", cfg["docs"]["legacy_paths"])
        # The pre-existing AGENTS.md does not route yet: the gate must say so rather than pass silently.
        check = uadr(self.target, "check")
        self.assertEqual(check.returncode, 1)
        self.assertIn("AGENTS.md must reference", check.stdout)
        self.assertNotIn("nowhere.md", check.stdout)  # legacy docs are exempt until adopted

    def test_module_registration_and_routing(self):
        self.make_existing()
        uadr(ROOT, "adopt", "--target", str(self.target))
        result = uadr(self.target, "new", "module", "billing", "--paths", "src/billing/**")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        routed = uadr(self.target, "route", "bugfix", "--path", "src/billing/invoice.ts").stdout
        self.assertIn("docs/modules/billing.md", routed)
        self.assertIn("billing.md", (self.target / "docs/index.md").read_text())
        adr = uadr(self.target, "new", "adr", "Use PostgreSQL")
        self.assertEqual(adr.returncode, 0, adr.stdout + adr.stderr)
        self.assertTrue((self.target / "docs/decisions/0001-use-postgresql.md").is_file())

    def test_upgrade_keeps_project_owned_files(self):
        uadr(ROOT, "adopt", "--target", str(self.target), "--name", "Demo")
        write(self.target, ".agent/memory/state.md", "---\npurpose: p\nread_when: r\n---\n# Mine\n")
        write(self.target, ".agent/workflows/bugfix.md", "tampered\n")
        result = uadr(ROOT, "adopt", "--target", str(self.target), "--upgrade")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# Mine", (self.target / ".agent/memory/state.md").read_text())
        self.assertEqual((self.target / ".agent/workflows/bugfix.md").read_text(),
                         (ROOT / ".agent/workflows/bugfix.md").read_text())


class GateDetectionTests(unittest.TestCase):
    """Each gate must actually fail on the defect it exists to catch."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name) / "repo"
        uadr(ROOT, "adopt", "--target", str(self.target), "--name", "Demo")

    def tearDown(self):
        self.tmp.cleanup()

    def failing(self, only: str) -> str:
        result = uadr(self.target, "check", "--only", only)
        self.assertEqual(result.returncode, 1, result.stdout)
        return result.stdout

    def test_detects_secret_without_printing_it(self):
        value = "AKIA" + "ABCDEFGHIJKLMNOP"
        write(self.target, "config/settings.py", f'AWS_KEY = "{value}"\n')
        out = self.failing("secrets")
        self.assertIn("config/settings.py:1", out)
        self.assertNotIn(value, out)

    def test_ignores_placeholder_credentials(self):
        write(self.target, "config/sample.py", 'password = "<your-password-here>"\n')
        self.assertEqual(uadr(self.target, "check", "--only", "secrets").returncode, 0)

    def test_detects_broken_link(self):
        write(self.target, "docs/project/extra.md",
              "---\npurpose: p\nread_when: r\nstatus: draft\n---\n# X\n\n[gone](missing.md)\n")
        self.assertIn("broken link", self.failing("links"))

    def test_detects_missing_frontmatter_and_stale_index(self):
        write(self.target, "docs/project/bare.md", "# Bare\n")
        out = self.failing("docs")
        self.assertIn("frontmatter missing 'purpose'", out)
        self.assertIn("out of date", out)

    def test_detects_bloated_entry_point(self):
        with open(self.target / "AGENTS.md", "a", encoding="utf-8") as handle:
            handle.write("\n" + "Extra always-loaded guidance that does not belong here. " * 80 + "\n")
        self.assertIn("entry_point_tokens", self.failing("context"))

    def test_detects_fat_adapter(self):
        write(self.target, ".github/copilot-instructions.md", "\n".join(f"Rule {i}" for i in range(40)) + "\n")
        out = self.failing("instructions")
        self.assertIn("adapter has 40 lines", out)

    def test_detects_incomplete_workflow_and_unrouted_workflow(self):
        write(self.target, ".agent/workflows/custom.md", "---\npurpose: p\nread_when: r\n---\n# W\n\n## Steps\n")
        self.assertIn("nine standard", self.failing("instructions"))
        self.assertIn("not reachable from any route", self.failing("config"))

    def test_detects_missing_required_file(self):
        (self.target / ".agent/policies/approvals.md").unlink()
        self.assertIn("required file missing", self.failing("structure"))


if __name__ == "__main__":
    unittest.main()
