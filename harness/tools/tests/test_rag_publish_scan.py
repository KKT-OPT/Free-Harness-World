"""Publication scan should reject literals, not ordinary tokenizer expressions."""
import importlib.util
from pathlib import Path
import unittest
import subprocess
import tempfile

spec=importlib.util.spec_from_file_location('publish_scan',Path(__file__).resolve().parents[1]/'scripts/stable/scan-publish-content.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class PublishScanTests(unittest.TestCase):
    def codes(self,source):return {x['code'] for x in module.scan_source(source)}

    def test_tokenizer_expressions_are_not_credentials(self):
        self.assertFalse(self.codes('token = parts[0]\nother = "scope:\\ntext"'))
        self.assertFalse(self.codes('token = f"{item}-suffix"'))

    def test_actual_literal_assignment_is_rejected(self):
        self.assertIn('credential-like-literal',self.codes('token = "fixture-token-value"'))
        self.assertIn('credential-like-literal',self.codes('access_token = "fixture-token-value"'))

    def test_dictionary_and_keyword_secrets_are_rejected(self):
        self.assertIn('credential-like-literal',self.codes('config = {"api_key":"fixture-key"}'))
        self.assertIn('credential-like-literal',self.codes('client(password="fixture-value")'))

    def test_annotated_and_attribute_assignments_are_rejected(self):
        self.assertIn('credential-like-literal',self.codes('password: str = "fixture-value"'))
        self.assertIn('credential-like-literal',self.codes('config.secret = "fixture-value"'))

    def test_placeholder_is_not_a_credential(self):
        self.assertFalse(self.codes('token = "<credential-ref>"'))

    def test_decoded_forward_and_escaped_paths_are_rejected(self):
        for separator in ['/',chr(92)]:
            example=chr(81)+':'+separator+'fixture'+separator+'file.txt'
            self.assertIn('concrete-local-path',self.codes('route = '+repr(example)))

    def test_embedded_token_format_is_rejected_without_exposing_value(self):
        value='ghp_'+'x'*24
        result=module.scan_source('payload='+repr(value))
        self.assertTrue(result)
        self.assertNotIn(value,str(result))

    def test_invalid_python_is_not_silently_skipped(self):
        self.assertIn('python-syntax-error',self.codes('invalid python ???'))

    def test_publisher_restores_unset_and_explicit_git_environment(self):
        root=Path(__file__).resolve().parents[3]
        base=root/'var/rag/rag-tool-tests';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as name:
            fixture=Path(name).resolve()
            subprocess.run(['git','init',str(fixture)],check=True,capture_output=True)
            (fixture/'fixture.txt').write_text('Synthetic repository fixture.',encoding='utf-8')
            subprocess.run(['git','-C',str(fixture),'add','.'],check=True,capture_output=True)
            subprocess.run(['git','-C',str(fixture),'-c','commit.gpgsign=false','-c','user.name=fixture',
                            '-c','user.email=fixture@example.invalid','commit','-m','fixture'],check=True,capture_output=True)
            script=fixture/'check.ps1'
            script.write_text('''param([string]$Publisher, [string]$FixtureRoot)
$ErrorActionPreference = 'Stop'
Remove-Item Env:GIT_SSH_COMMAND -ErrorAction SilentlyContinue
& $Publisher -Mode status -Root $FixtureRoot | Out-Null
if (Test-Path Env:GIT_SSH_COMMAND) { throw 'Unset Git command became an empty command' }
$env:GIT_SSH_COMMAND = 'synthetic-no-network-command'
& $Publisher -Mode status -Root $FixtureRoot | Out-Null
if ($env:GIT_SSH_COMMAND -ne 'synthetic-no-network-command') { throw 'Explicit Git command changed' }
''',encoding='ascii')
            for shell in ['powershell','pwsh']:
                p=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),
                                  '-Publisher',str(root/'harness/tools/scripts/stable/publish-harness-agent-branch.ps1'),
                                  '-FixtureRoot',str(fixture)],capture_output=True,text=True,encoding='utf-8',errors='replace')
                self.assertEqual(p.returncode,0,p.stderr)


if __name__=='__main__':unittest.main()
