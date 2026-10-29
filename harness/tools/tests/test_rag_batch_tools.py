"""Generic fixtures for repeated corpus construction; no private source facts."""
import io
import json
import os
import tempfile
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import fitz

from rag_candidate.common import write_text, read_text, sha256_file
from rag_candidate.metadata import frontmatter, metadata, dump_mapping
from rag_candidate.reviewed_content import run_prepare_reviewed_content, validate_content, START, END
from rag_candidate.promotion import validate_draft, review_snapshot
from rag_candidate.evidence import run_compare_pdf_copies, run_archive_build_evidence
from rag_knowledge.retrieval import passages, source_matches
from rag_knowledge.regression import run_query_regression, validate_cases, check_case, query_worker


class BatchToolTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parents[3]/'var/rag/rag-tool-tests'
        base.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.tmp.name).resolve()
        self.raw = self.root/'user/knowledge/raw/domain'
        self.reviewed = self.root/'user/knowledge/reviewed'
        self.page = self.reviewed/'domain/source.md'

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, function, args):
        with redirect_stdout(io.StringIO()):
            return function(args)

    def pdf(self, name, text='A source with a bounded condition.'):
        path = self.raw/name
        path.parent.mkdir(parents=True, exist_ok=True)
        with fitz.open() as doc:
            page = doc.new_page(width=200, height=200)
            page.insert_text((15, 30), text, fontsize=8)
            doc.save(path)
        return path

    def prep(self):
        original = self.pdf('source.pdf')
        norm = self.raw/'normalized/source.md'
        write_text(norm, '## PDF 第 1 页\n\n来源正文保留输入条件、系统能力以及适用对象，数值上界为120且包括等号。\n')
        wiki = self.root/'user/knowledge/candidate/ingest/wiki'
        candidate = wiki/'source.md'
        source = {'id': 'source', 'sourceRef': original.relative_to(self.root).as_posix(), 'sourceHashSha256': sha256_file(original),
                  'normalizedMarkdown': norm.relative_to(self.root).as_posix(), 'normalizedHashSha256': sha256_file(norm),
                  'extractedMarkdown': norm.relative_to(self.root).as_posix(), 'candidatePage': candidate.relative_to(self.root).as_posix(),
                  'pageCount': 1, 'pages': [{'page': 1, 'method': 'offline-ocr-fixture'}], 'qualityState': 'needs-review'}
        header = {'title': '合成来源系统规范', 'tags': ['fixture'], 'source_file': source['sourceRef'], 'extracted_file': source['extractedMarkdown']}
        sections = {'Candidate Summary': '系统应按输入边界执行能力检查，保留完整条件、单位和适用场景。',
                    'Source Overview': '本文说明系统组成、输入约束和验证方法，并要求保留来源追溯证据。',
                    'Core Framework': '输入条件限定系统行为，输出结果应满足约束，验证记录保留适用边界。',
                    'Applicability': '适用于本文所定义输入范围内的系统能力验证与边界检查。',
                    'Non-Applicability': '不适用于未定义的输入对象，结构通过不能解释为全部语义正确。',
                    'Key Concepts': '系统能力包括输入约束、边界检查和对完整来源证据的可追溯验证。'}
        write_text(candidate, '---\n'+dump_mapping(header)+'\n---\n\n'+ '\n'.join('## '+k+'\n\n'+v+'\n' for k, v in sections.items()))
        manifest = self.root/'var/rag/manifest.json'
        write_text(manifest, json.dumps({'sources': [source]}, ensure_ascii=False))
        targets = self.root/'var/rag/targets.json'
        write_text(targets, json.dumps({'items': [{'sourceId': 'source', 'target': self.page.relative_to(self.root).as_posix()}]}))
        args = SimpleNamespace(root=str(self.root), manifest=str(manifest), reviewed=str(self.reviewed), wiki=str(wiki), target_map=str(targets),
                               run_id='prepare', reviewer='fixture', content_profile=None, scope='user-private', review_after='source-updated')
        return args, source

    def profile(self, args, source, **extra):
        path = self.root/'var/rag/content-profile.json'
        write_text(path, json.dumps({'sources': [{'sourceHashSha256': source['sourceHashSha256'], 'normalizedHashSha256': source['normalizedHashSha256'], **extra}]}, ensure_ascii=False))
        args.content_profile = str(path)

    def test_new_source_preparation_is_candidate_only_lf_and_preserves_profile(self):
        args, source = self.prep()
        copy = self.pdf('copy.pdf', 'Another independently supplied source.')
        self.profile(args, source, sourceVersion={'standardId': 'ZZ/T XXXXX—XXXX', 'sourceDocumentState': 'approval-draft', 'officialStatus': 'not-verified'},
                     aliases=['输入副本别名'], secondarySources=[{'sourceRef': copy.relative_to(self.root).as_posix(), 'sourceHashSha256': sha256_file(copy), 'relationship': 'reviewed-copy-fixture', 'reviewedBy': 'fixture', 'evidence': 'Synthetic review evidence; no edition inference.'}],
                     sections=[{'heading': '补充条款', 'text': '仅当输入满足既定边界时才提供系统能力，上限120且含等号。', 'physicalPages': [1], 'reviewedBy': 'fixture', 'evidence': 'Synthetic page review.'}])
        result = self.call(run_prepare_reviewed_content, args)
        draft = self.root/'user/knowledge/candidate/prepare/drafts/source.md'
        text = read_text(draft)
        self.assertFalse(self.page.exists())
        self.assertNotIn(b'\r\n', draft.read_bytes())
        self.assertLess(text.index('## 补充条款'), text.index(START))
        self.assertIn('## 转换质量', text)
        self.assertEqual(frontmatter(text)['aliases'], ['输入副本别名'])
        self.assertIn(copy.relative_to(self.root).as_posix(), metadata(text)['sourceRefs'])
        self.assertEqual(result['sourceCount'], 1)
        validate_content(self.root, source, self.page, text)
        validate_draft(self.root, source, self.page, text)

    def test_new_source_refuses_existing_target(self):
        args, _ = self.prep()
        write_text(self.page, 'Existing authoritative bytes must remain unchanged.')
        with self.assertRaises(FileExistsError): self.call(run_prepare_reviewed_content, args)
        self.assertFalse((self.root/'user/knowledge/candidate/prepare/drafts').exists())

    def test_clause_review_does_not_default_to_full_page_visual_calibration(self):
        args, source = self.prep()
        self.profile(args, source, sections=[{'heading': '补充条款', 'text': '只审读这段条款的完整条件及适用边界，不代表整页数值、公式与图示已经逐字核对。', 'physicalPages': [1], 'reviewedBy': 'fixture', 'evidence': 'Text-only clause review.'}])
        self.call(run_prepare_reviewed_content, args)
        text = read_text(self.root/'user/knowledge/candidate/prepare/drafts/source.md')
        clause = next(p for p in passages(text) if p['localHeading'] == '补充条款')
        self.assertIn('未声明整页校录', clause['text'])
        self.assertEqual(clause['verification'], 'reviewed-text')
        self.assertEqual(clause['sourcePages'], [])

    def test_new_source_requires_complete_target_map(self):
        args, _ = self.prep()
        write_text(Path(args.target_map), json.dumps({'items': [{'sourceId': 'unknown', 'target': self.page.relative_to(self.root).as_posix()}]}))
        with self.assertRaisesRegex(ValueError, 'every manifest source'): self.call(run_prepare_reviewed_content, args)
        self.assertFalse((self.root/'user/knowledge/candidate/prepare/drafts').exists())

    def test_stale_profile_blocks_new_drafts(self):
        args, source = self.prep()
        self.profile(args, source, normalizedHashSha256='0'*64)
        with self.assertRaisesRegex(ValueError, 'normalized hash mismatch'): self.call(run_prepare_reviewed_content, args)
        self.assertFalse((self.root/'user/knowledge/candidate/prepare/drafts').exists())

    def test_secondary_copy_change_invalidates_snapshot_and_draft(self):
        args, source = self.prep()
        copy = self.pdf('copy.pdf')
        self.profile(args, source, secondarySources=[{'sourceRef': copy.relative_to(self.root).as_posix(), 'sourceHashSha256': sha256_file(copy), 'relationship': 'reviewed-copy', 'reviewedBy': 'fixture', 'evidence': 'Synthetic review.'}])
        result = self.call(run_prepare_reviewed_content, args)
        bindings = json.loads(read_text(self.root/result['promotionMap']))['items']
        before = review_snapshot(self.root, Path(args.manifest), Path(args.wiki), bindings)
        copy.write_bytes(copy.read_bytes()+b'\nchanged')
        self.assertNotEqual(before, review_snapshot(self.root, Path(args.manifest), Path(args.wiki), bindings))
        with self.assertRaisesRegex(ValueError, 'secondary source hash mismatch'):
            validate_draft(self.root, source, self.page, read_text(self.root/bindings[0]['draft']))

    def test_synthesis_after_source_end_does_not_inherit_page_or_visual_state(self):
        text = '# 文本\n\n'+START+'\n### PDF 第 1 页\n\n校核级别：原页完整校录。\n\n此处是完整来源正文，具有明确的数值边界与适用对象。\n'+END+'\n\n## 综合边界\n\n这是另外的综合说明，不应继承最后一页的物理页码或原页校录状态。'
        p = next(p for p in passages(text) if p['localHeading'] == '综合边界')
        self.assertEqual(p['sourcePages'], [])
        self.assertEqual(p['verification'], 'reviewed-text')
        self.assertEqual('\n'.join(text.splitlines()[p['startLine']-1:p['endLine']]), p['text'])

    def test_legacy_peer_heading_resets_physical_scope(self):
        text = '# 来源\n\n## PDF 第 2 页\n\n来源正文保留单位与数值，说明完整条件与适用范围。\n\n## 后续说明\n\n这是独立说明章节，不是PDF第二页的原始正文，也没有逐字图像校核证据。'
        self.assertEqual(passages(text)[-1]['sourcePages'], [])

    def test_placeholder_identifier_needs_explicit_draft_state(self):
        text = '---\nsourceVersion:\n  standardId: ZZ/T XXXXX—XXXX\n  sourceDocumentState: approval-draft\n---\n# 来源\n'
        self.assertTrue(source_matches(text, 'ZZ/T'))
        self.assertFalse(source_matches(text.replace('approval-draft', 'published-copy'), 'ZZ/T'))
        self.assertFalse(source_matches(text, 'GB'))
        self.assertTrue(source_matches(text.replace('XXXXX—XXXX', '××××—××××'), 'ZZ/T'))
        self.assertTrue(source_matches(text.replace('approval-draft', 'unnumbered-draft'), 'ZZ/T'))

    def test_copy_comparison_distinguishes_text_identity_from_visual_difference(self):
        left = self.pdf('left.pdf')
        right = self.raw/'right.pdf'
        with fitz.open(left) as doc:
            doc[0].draw_rect(fitz.Rect(1, 1, 8, 8), color=(1, 0, 0), fill=(1, 0, 0))
            doc.save(right)
        hashes = [sha256_file(p) for p in [left, right]]
        args = SimpleNamespace(root=str(self.root), inputs=[str(left), str(right)], run_id='copies', dpi=72)
        result = self.call(run_compare_pdf_copies, args)
        self.assertFalse(result['sameBytes'])
        self.assertTrue(result['allNativeTextMatches'])
        self.assertEqual(result['visualDifferencePages'], [1])
        self.assertEqual(result['disposition'], 'review-required-before-canonical-source-selection')
        self.assertEqual(hashes, [sha256_file(p) for p in [left, right]])
        with self.assertRaises(FileExistsError): self.call(run_compare_pdf_copies, args)

    def evidence_args(self, target='result.json', digest=None):
        source = self.root/'var/rag/source/result.json'
        write_text(source, '{"state":"failed","reason":"retain original failure"}')
        plan = self.root/'var/rag/evidence-plan.json'
        write_text(plan, json.dumps({'artifacts': [{'source': source.relative_to(self.root).as_posix(), 'target': target, 'sha256': digest or sha256_file(source)}]}))
        return SimpleNamespace(root=str(self.root), evidence_manifest=str(plan), audit_dir='user/knowledge/candidate/_audit/post-promotion', run_id='evidence'), source

    def test_evidence_archive_preserves_failure_bytes_and_refuses_overwrite(self):
        args, source = self.evidence_args()
        result = self.call(run_archive_build_evidence, args)
        self.assertEqual((self.root/result['archive']/'result.json').read_bytes(), source.read_bytes())
        self.assertEqual(result['files'][0]['sha256'], sha256_file(source))
        with self.assertRaises(FileExistsError): self.call(run_archive_build_evidence, args)

    def test_wrong_evidence_hash_leaves_no_archive(self):
        args, _ = self.evidence_args(digest='0'*64)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'): self.call(run_archive_build_evidence, args)
        self.assertFalse((self.root/args.audit_dir/args.run_id).exists())

    def test_evidence_target_cannot_escape_archive(self):
        args, _ = self.evidence_args(target='../escaped.json')
        with self.assertRaises(ValueError): self.call(run_archive_build_evidence, args)
        self.assertFalse((self.root/args.audit_dir/args.run_id).exists())

    def query_fixture(self, required=None, run='queries'):
        write_text(self.page, '---\nknowledgeRole: authoritative\nauthoritative: true\nsourceVersion:\n  standardId: ZZ/T XXXXX—XXXX\n  sourceDocumentState: approval-draft\n  officialStatus: not-verified\n---\n# 合成系统规范\n\n## 系统能力\n\n系统能力仅适用于输入满足完整边界的情形，上限为120且包含等号，不包括未定义场景。\n')
        case = {'id': 'bounded-capability', 'kind': 'substantive-question', 'question': '系统能力的输入边界和数值上限是什么', 'target': self.page.relative_to(self.root).as_posix(), 'prefix': 'ZZ/T', 'required': required or ['上限为120且包含等号', '不包括未定义场景'], 'versionEquals': {'officialStatus': 'not-verified', 'publishedOn': None}}
        cases = self.root/'var/rag/cases.json'
        write_text(cases, json.dumps([case], ensure_ascii=False))
        return SimpleNamespace(root=str(self.root), reviewed=str(self.reviewed), vault=str(self.root/'user/knowledge'), cases=str(cases), run_id=run, limit=5, as_of='2026-10-29', graph=None, timeout=30), case

    def test_batch_regression_uses_worker_and_keeps_immutable_run(self):
        args, _ = self.query_fixture()
        result = self.call(run_query_regression, args)
        self.assertEqual((result['state'], result['passedCount'], result['reviewedFrozenCount']), ('passed', 1, 1))
        guard = json.loads(read_text(self.root/'var/rag/queries/query-regression/bounded-capability-guard.json'))
        self.assertTrue(guard['events'])
        self.assertTrue(all(e['kind'] == 'reviewed-read' for e in guard['events']))
        with self.assertRaises(FileExistsError): self.call(run_query_regression, args)

    def test_failed_assertion_is_preserved_and_not_silently_rewritten(self):
        args, _ = self.query_fixture(required=['impossible missing clause'])
        with self.assertRaisesRegex(ValueError, 'regression failed'): self.call(run_query_regression, args)
        report = self.root/'var/rag/queries/query-regression/summary.json'
        before = report.read_bytes()
        self.assertEqual(json.loads(before)['state'], 'failed')
        with self.assertRaises(FileExistsError): self.call(run_query_regression, args)
        self.assertEqual(before, report.read_bytes())

    def test_substantive_case_cannot_pass_without_assertions(self):
        args, case = self.query_fixture()
        del case['required']; del case['versionEquals']
        with self.assertRaisesRegex(ValueError, 'explicit content'): validate_cases(self.root, self.reviewed, [case], 5)

    def test_case_ids_are_casefold_unique_and_cannot_traverse(self):
        _, case = self.query_fixture()
        for changed in [{**case, 'id': '../outside'}, {**case, 'id': case['id'].upper()}]:
            with self.assertRaises(ValueError): validate_cases(self.root, self.reviewed, [case, changed], 5)

    def test_missing_target_is_a_failed_case(self):
        _, case = self.query_fixture()
        self.assertFalse(check_case(self.root, self.reviewed, case, {'matches': []}, 5)['passed'])

    def test_false_citation_and_wrong_table_cell_do_not_pass(self):
        _, case = self.query_fixture()
        case.update(tableCells=[{'label': '乙', 'cells': ['●', '', '●']}])
        query = {'matches': [{'page': case['target'], 'contentEvidence': 'substantive-reviewed-text', 'documentVersion': {}, 'matchedSections': [{'startLine': 1, 'endLine': 1, 'excerpt': '|乙|●|●|●|'}]}]}
        result = check_case(self.root, self.reviewed, case, query, 5)
        self.assertFalse(result['passed'])
        self.assertTrue(result['citationErrors'])
        self.assertFalse(next(c for c in result['checks'] if c['name'] == 'table-cells')['passed'])

    def test_new_reviewed_file_during_batch_invalidates_baseline(self):
        args, _ = self.query_fixture()
        def worker(*unused, **kwargs):
            write_text(self.reviewed/'domain/added.md', '# Unexpected new knowledge')
            return SimpleNamespace(returncode=0, stdout=json.dumps({'query': {'matches': []}, 'guard': {'events': []}}))
        with mock.patch('rag_knowledge.regression.subprocess.run', side_effect=worker):
            with self.assertRaisesRegex(ValueError, 'regression failed'): self.call(run_query_regression, args)
        result = json.loads(read_text(self.root/'var/rag/queries/query-regression/summary.json'))
        self.assertEqual(result['reviewedChanged'], ['user/knowledge/reviewed/domain/added.md'])

    def test_worker_guard_records_denied_network_and_nonreviewed_read(self):
        args, _ = self.query_fixture()
        for event, values, expected in [('socket.connect', (), 'denied-network'), ('open', (str(self.raw/'secret.pdf'), 'r', 0), 'denied-non-reviewed-read'), ('open', (str(self.page), 'w', os.O_WRONLY), 'denied-knowledge-write')]:
            hooks = []
            def attempted(*unused, **kwargs): hooks[0](event, values)
            job = {'root': str(self.root), 'reviewed': str(self.reviewed), 'vault': args.vault, 'graph': str(self.root/'var/rag/no-graph.json'), 'question': '系统能力', 'limit': 5, 'asOf': '2026-10-29'}
            with mock.patch('sys.addaudithook', side_effect=hooks.append), mock.patch('rag_knowledge.commands._query_reviewed', side_effect=attempted):
                result = query_worker(job)
            self.assertIn('error', result)
            self.assertEqual(result['guard']['events'][0]['kind'], expected)

    def wrapper(self, shell, name, command, values):
        stable = Path(__file__).resolve().parents[1]/'scripts/stable'
        env = dict(os.environ, PYTHONUTF8='1', PYTHONPATH=str(stable))
        env['PATH'] = str(Path(sys.executable).parent)+os.pathsep+env['PATH']
        args = [shell, '-NoProfile', '-File', str(stable/name), '-Root', str(self.root), '-Command', command]
        for key, value in values.items(): args += ['-'+key, str(value)]
        process = subprocess.run(args, env=env, capture_output=True, encoding='utf-8', timeout=60)
        self.assertEqual(process.returncode, 0, process.stdout+process.stderr)
        return json.loads(process.stdout.lstrip('\ufeff'))

    @unittest.skipUnless(os.name == 'nt', 'Windows PowerShell command surfaces')
    def test_both_powershell_new_source_preparation_surfaces(self):
        args, _ = self.prep()
        for shell in ['powershell', 'pwsh']:
            result = self.wrapper(shell, 'invoke-rag-candidate.ps1', 'prepare-reviewed-content', {
                'Manifest': args.manifest, 'Reviewed': args.reviewed, 'Wiki': args.wiki,
                'TargetMap': args.target_map, 'RunId': 'surface-'+shell, 'Reviewer': 'fixture'})
            self.assertEqual(result['state'], 'candidate-prepared')
            self.assertFalse(self.page.exists())

    @unittest.skipUnless(os.name == 'nt', 'Windows PowerShell command surfaces')
    def test_both_powershell_regression_and_evidence_surfaces(self):
        args, _ = self.query_fixture()
        for shell in ['powershell', 'pwsh']:
            result = self.wrapper(shell, 'invoke-rag-knowledge.ps1', 'query-regression', {
                'Cases': args.cases, 'Reviewed': args.reviewed, 'RunId': 'surface-query-'+shell, 'AsOf': '2026-10-29'})
            self.assertEqual(result['state'], 'passed')
            evidence, _ = self.evidence_args()
            result = self.wrapper(shell, 'invoke-rag-candidate.ps1', 'archive-build-evidence', {
                'EvidenceManifest': evidence.evidence_manifest, 'RunId': 'surface-evidence-'+shell})
            self.assertEqual(result['state'], 'archived')


if __name__ == '__main__':
    unittest.main()
