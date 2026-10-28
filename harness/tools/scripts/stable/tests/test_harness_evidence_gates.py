"""Stable gate CLI tests; only isolated synthetic project files are read."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[2] / "stable"
HOSTS = [path for name in ("powershell", "pwsh") if (path := shutil.which(name))]
WORKFLOW = """---
status: active
---
## Task Brief
Goal, scope, acceptance criteria and validation recorded.
AGENTS.md ProjectIndex.md
## Scope
reviewTarget: src/sample.txt
## Trace
Read sample source with stable tools.
## Findings
No blocking issues.
## Execution Plan / Fix Handoff
No code change needed.
## File Change Summary
Inspected the selected file.
## Verification Report / Recheck
Recorded command results.
## User Acceptance / Final Review
acceptedBy = user
## Governance Candidates
No promotion required.
codeReviewState: accepted
userFeedbackState: approved
fixState: not-required
recheckState: passed
finalUserReview: accepted
"""
REPORT = """---
status: active
---
## Candidate Table
No new candidates.
## Approval And Disposition
Approved scope.
## Non-Promotion
Report is not a fact source.
## Validation
Recorded results.
"""


@unittest.skipUnless(HOSTS, "PowerShell host required")
class EvidenceGateCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "projects/sample"
        self.workflow = self.project / "docs/project/workflow/task.md"
        self.workflow.parent.mkdir(parents=True)
        (self.project / "docs/project/reports").mkdir()
        for path in (self.project / "AGENTS.md", self.project / "docs/project/ProjectIndex.md", self.project / "docs/project/reports/README.md"):
            path.write_text("synthetic route", encoding="utf-8")
        (self.root / "registry.json").write_text(json.dumps({"projects": [{"projectId": "sample", "root": "projects/sample"}]}), encoding="utf-8")
        self.workflow.write_text(WORKFLOW, encoding="utf-8")
        (self.project / "docs/project/reports/result.md").write_text(REPORT, encoding="utf-8")

    def invoke(self, host, gate, extra=()):
        command = [host, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPTS / gate), "-Root", str(self.root), "-Registry", "registry.json", "-ProjectId", "sample", "-WorkflowEvidence", "docs/project/workflow/task.md", *extra]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8-sig", timeout=30)
        self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
        return result.returncode, json.loads(result.stdout)

    def assert_outcome(self, gate, extra, expected_code=None):
        for host in HOSTS:
            with self.subTest(host=Path(host).name):
                code, result = self.invoke(host, gate, extra)
                self.assertEqual(code, 0 if expected_code is None else 1, result)
                self.assertEqual(result["status"], "passed" if expected_code is None else "failed")
                if expected_code:
                    self.assertIn(expected_code, [item["code"] for item in result["findings"]])

    def test_closed_loop_success(self):
        self.assert_outcome("test-code-review-workflow-evidence.ps1", ["-RequireClosedLoop"])

    def test_closed_loop_rejects_failed_recheck(self):
        self.workflow.write_text(WORKFLOW.replace("recheckState: passed", "recheckState: failed"), encoding="utf-8")
        self.assert_outcome("test-code-review-workflow-evidence.ps1", ["-RequireClosedLoop"], "codeReviewClosedLoopRecheckMissing")

    def test_closed_loop_rejects_partial_implementation(self):
        self.workflow.write_text(WORKFLOW.replace("fixState: not-required", "fixState: partial"), encoding="utf-8")
        self.assert_outcome("test-code-review-workflow-evidence.ps1", ["-RequireClosedLoop"], "codeReviewClosedLoopFixIncomplete")

    def test_localized_trace_is_read_as_utf8(self):
        text = WORKFLOW.replace("## Trace", "## \u6267\u884c\u8ba1\u5212 / \u68c0\u67e5\u8f68\u8ff9")
        self.workflow.write_text(text, encoding="utf-8")
        self.assert_outcome("test-code-review-workflow-evidence.ps1", ["-RequireClosedLoop"])

    def test_sensitive_path_rejection_is_preserved(self):
        self.workflow.write_text(WORKFLOW + "\nC:/private/example.txt\n", encoding="utf-8")
        self.assert_outcome("test-code-review-workflow-evidence.ps1", ["-RequireClosedLoop"], "codeReviewConcretePrivatePath")

    def test_lifecycle_success_with_report(self):
        self.assert_outcome("test-project-lifecycle-evidence.ps1", ["-ProjectReport", "docs/project/reports/result.md", "-RequireReport", "-RequireUserAcceptance"])

    def test_lf_frontmatter_is_also_valid(self):
        self.workflow.write_bytes(WORKFLOW.encode("utf-8"))
        self.assert_outcome("test-project-lifecycle-evidence.ps1", ["-RequireUserAcceptance"])

    def test_acceptance_heading_alone_is_not_approval(self):
        self.workflow.write_text(WORKFLOW.replace("acceptedBy = user", "").replace("finalUserReview: accepted", ""), encoding="utf-8")
        self.assert_outcome("test-project-lifecycle-evidence.ps1", ["-RequireUserAcceptance"], "lifecycleAcceptanceMissing")

    def test_pending_final_review_overrides_earlier_acceptance(self):
        self.workflow.write_text(WORKFLOW.replace("finalUserReview: accepted", "finalUserReview: pending"), encoding="utf-8")
        self.assert_outcome("test-project-lifecycle-evidence.ps1", ["-RequireUserAcceptance"], "lifecycleAcceptanceMissing")

    def test_empty_final_review_overrides_earlier_acceptance(self):
        self.workflow.write_text(WORKFLOW.replace("finalUserReview: accepted", "finalUserReview:"), encoding="utf-8")
        self.assert_outcome("test-project-lifecycle-evidence.ps1", ["-RequireUserAcceptance"], "lifecycleAcceptanceMissing")


if __name__ == "__main__":
    unittest.main()
