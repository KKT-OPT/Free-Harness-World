"""Behavioral fixtures for the stable receipt tool; only temporary data is changed."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1] / "verify-artifact-cleanup.py"
SPEC = importlib.util.spec_from_file_location("cleanup_tool", TOOL)
cleanup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cleanup)


class CleanupReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "old.txt").write_text("obsolete", encoding="utf-8")
        (self.root / "fixture.json").write_text('{"stable": true}', encoding="utf-8")
        self.manifest = {"schemaVersion": cleanup.SCHEMA, "remove": ["old.txt"], "protect": ["fixture.json"]}

    def codes(self, result):
        return [item["code"] for item in result["findings"]]

    def test_snapshot_is_read_only_and_removal_is_not_automatic(self):
        receipt = cleanup.snapshot(self.root, self.manifest)
        self.assertEqual((self.root / "old.txt").read_text(), "obsolete")
        self.assertIn("removalTargetStillPresent", self.codes(cleanup.verify(self.root, receipt)))

    def test_exact_removal_and_protection(self):
        receipt = cleanup.snapshot(self.root, self.manifest)
        (self.root / "old.txt").unlink()
        self.assertEqual(cleanup.verify(self.root, receipt)["status"], "passed")

    def test_changed_protected_content_fails_even_with_same_size(self):
        receipt = cleanup.snapshot(self.root, self.manifest)
        (self.root / "fixture.json").write_text('{"stable": null}', encoding="utf-8")
        self.assertIn("protectedFileChanged", self.codes(cleanup.verify(self.root, receipt)))

    def test_missing_protected_file_fails(self):
        receipt = cleanup.snapshot(self.root, self.manifest)
        (self.root / "fixture.json").unlink()
        self.assertIn("protectedFileMissing", self.codes(cleanup.verify(self.root, receipt)))

    def test_unsafe_and_noncanonical_paths_rejected(self):
        for value in ("../outside", "/tmp/outside", "C:/outside", "x/../old.txt", "./old.txt", "a//b", "x\\y", "old.txt:stream", "old.txt.", "old.txt ", ""):
            with self.subTest(path=value), self.assertRaises(ValueError):
                cleanup.resolve_entry(self.root, value)

    def test_duplicates_and_role_overlap_rejected(self):
        for value in (["old.txt", "old.txt"], ["fixture.json"]):
            manifest = dict(self.manifest, remove=value)
            with self.assertRaises(ValueError):
                cleanup.snapshot(self.root, manifest)

    def test_directories_and_empty_protection_rejected(self):
        (self.root / "directory").mkdir()
        for manifest in (dict(self.manifest, remove=["directory"]), dict(self.manifest, protect=[])):
            with self.assertRaises(ValueError):
                cleanup.snapshot(self.root, manifest)

    def test_symlink_rejected_if_host_allows_creation(self):
        link = self.root / "link"
        try:
            link.symlink_to(self.root / "fixture.json")
        except OSError:
            self.skipTest("host does not permit symlink creation")
        with self.assertRaises(ValueError):
            cleanup.resolve_entry(self.root, "link")

    def test_invalid_receipt_rejected(self):
        receipt = cleanup.snapshot(self.root, self.manifest)
        receipt["protect"][0]["sha256"] = "invalid"
        with self.assertRaises(ValueError):
            cleanup.verify(self.root, receipt)

    def test_symlink_guard_without_host_link_privilege(self):
        with patch.object(Path, "is_symlink", return_value=True):
            with self.assertRaisesRegex(ValueError, "symbolic links"):
                cleanup.resolve_entry(self.root, "fixture.json")

    def test_reparse_attribute_guard_without_host_link_privilege(self):
        flag = getattr(cleanup.stat, "FILE_ATTRIBUTE_REPARSE_POINT", None)
        if flag is None:
            self.skipTest("runtime does not expose Windows file attributes")
        attributes = SimpleNamespace(st_mode=cleanup.stat.S_IFREG, st_file_attributes=flag)
        with patch.object(Path, "is_symlink", return_value=False), patch.object(Path, "is_junction", return_value=False, create=True), patch.object(Path, "lstat", return_value=attributes):
            with self.assertRaises(ValueError):
                cleanup.resolve_entry(self.root, "fixture.json")

    def test_unicode_file_names_and_content(self):
        name = "\u5939\u5177.json"
        (self.root / name).write_text('\u6b63\u6587', encoding="utf-8")
        receipt = cleanup.snapshot(self.root, dict(self.manifest, remove=[], protect=[name]))
        self.assertEqual(cleanup.verify(self.root, receipt)["status"], "passed")

    def test_cli_receipt_is_portable_exclusive_and_redacted(self):
        manifest = self.root / "manifest.json"
        receipt = self.root / "receipt.json"
        manifest.write_text(json.dumps(self.manifest), encoding="utf-8")
        command = [sys.executable, "-B", str(TOOL), "snapshot", "--root", str(self.root), "--manifest", str(manifest), "--receipt", str(receipt)]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertNotIn(str(self.root), receipt.read_text(encoding="utf-8"))
        before = receipt.read_bytes()
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(second.returncode, 1)
        self.assertEqual(receipt.read_bytes(), before)
        (self.root / "old.txt").unlink()
        verified = subprocess.run([sys.executable, "-B", str(TOOL), "verify", "--root", str(self.root), "--receipt", str(receipt)], capture_output=True, text=True)
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
        self.assertEqual(json.loads(verified.stdout)["protectedCount"], 1)

    def test_cli_failures_are_nonzero_and_structured(self):
        manifest = self.root / "manifest.json"
        receipt = self.root / "receipt.json"
        manifest.write_text(json.dumps(self.manifest), encoding="utf-8")
        base = [sys.executable, "-B", str(TOOL)]
        created = subprocess.run(base + ["snapshot", "--root", str(self.root), "--manifest", str(manifest), "--receipt", str(receipt)], capture_output=True, text=True)
        self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
        for change, code in ((None, "removalTargetStillPresent"), ("changed", "protectedFileChanged"), ("missing", "protectedFileMissing")):
            if change == "changed":
                (self.root / "fixture.json").write_text("changed", encoding="utf-8")
            elif change == "missing":
                (self.root / "fixture.json").unlink()
            result = subprocess.run(base + ["verify", "--root", str(self.root), "--receipt", str(receipt)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn(code, self.codes(json.loads(result.stdout)))
        receipt.write_text("{invalid", encoding="utf-8")
        result = subprocess.run(base + ["verify", "--root", str(self.root), "--receipt", str(receipt)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["failureMode"], "invalid-input-or-filesystem")
        self.assertNotIn(str(self.root), result.stdout)
        self.assertEqual(subprocess.run(base, capture_output=True).returncode, 2)

    @unittest.skipUnless(sys.platform == "win32", "Windows junction integration")
    def test_real_junction_is_rejected(self):
        target = self.root / "actual"
        target.mkdir()
        (target / "keep.txt").write_text("keep", encoding="utf-8")
        link = self.root / "junction"
        created = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        if created.returncode:
            self.skipTest("host does not permit junction creation")
        try:
            with self.assertRaises(ValueError):
                cleanup.resolve_entry(self.root, "junction/keep.txt")
        finally:
            # Remove only the verified junction itself, never recurse through its target.
            self.assertEqual(link.parent.resolve(), self.root)
            link.rmdir()
        self.assertEqual((target / "keep.txt").read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
