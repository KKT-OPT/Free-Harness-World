"""Synthetic lifecycle regressions; no source facts or machine-specific routes."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import fitz
from rag_candidate.common import write_text, read_text, sha256_file
from rag_candidate.metadata import frontmatter, metadata, dump_mapping
from rag_candidate.pdf_normalize import normalize_pdf
from rag_candidate.promotion import format_reviewed, validate_draft, bindings_from_args
from rag_candidate.reviewed_content import START, END
from rag_candidate.relocation import run_prepare_source_relocation
from rag_candidate.versions import audit_versions
from rag_candidate.corpus_audit import supplied_seals


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parents[3]/'var/rag/rag-tool-tests'
        base.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.tmp.name).resolve()
        self.raw = self.root/'user/knowledge/raw/old/source.pdf'
        self.raw.parent.mkdir(parents=True)
        with fitz.open() as doc:
            p = doc.new_page()
            p.insert_text((40,40), 'Synthetic source. The input condition is bounded. Keep the original evidence and all units.')
            doc.save(self.raw)
        self.record = normalize_pdf(self.root, self.raw, self.raw.parent/'normalized', self.root/'var/rag/normalize',
                                    {'sourceIds': {sha256_file(self.raw): 'sample'}}, ocr_mode='none')
        self.assertTrue(self.record['candidateAllowed'])
        norm = self.record['normalizedMarkdown']
        candidate = self.root/'user/knowledge/candidate/old/wiki/source.md'
        header = {'title': 'Synthetic sample', 'tags': ['fixture'], 'source_file': self.record['sourceRef'], 'extracted_file': norm}
        sections = {'Candidate Summary': '本合成来源保存输入边界、系统条件和可追溯的原始证据，不推断其他场景。',
                    'Core Framework': '原始条件、系统能力和适用边界应一并保留，变更路径不能改变正文和版本事实。',
                    'Applicability': '用于合成系统在明确输入范围内的本地来源追溯与路径迁移验证。',
                    'Non-Applicability': '不用于真实领域结论，不证明当前效力或全部文档语义已逐字核对。',
                    'Key Concepts': '来源哈希、适用范围、输入条件和完整原件追溯是独立的审核要素。'}
        write_text(candidate, '---\n'+dump_mapping(header)+'\n---\n\n'+'\n'.join('## '+k+'\n\n'+v+'\n' for k,v in sections.items()))
        source = {**self.record, 'candidatePage': candidate.relative_to(self.root).as_posix(), 'extractedMarkdown': norm}
        self.page = self.root/'user/knowledge/reviewed/domain/sample.md'
        text = format_reviewed(self.root, {'sources':[source]}, candidate.parent, self.page, 'user-private', 'fixture', 'Fixture approval.', 'source-updated')
        fm = frontmatter(text)
        fm['sourceVersion'] = {'standardId':'ZZ/T 123—2024', 'sourceDocumentState':'approval-draft',
                               'publishedOn':None, 'effectiveOn':None, 'officialStatus':'not-verified'}
        write_text(self.page, '---\n'+dump_mapping(fm)+'\n---'+text.split('---',2)[2])
        self.manifest = self.root/'var/rag/manifest.json'
        write_text(self.manifest, json.dumps({'sources':[self.record]}))
        self.mapping = self.root/'var/rag/relocation.json'
        self.item = {'sourceId':'sample', 'newSourceRef':'user/knowledge/raw/domain/policies/source.pdf',
                     'expectedReviewedHashSha256':sha256_file(self.page)}
        write_text(self.mapping, json.dumps({'items':[self.item]}))
        self.args = SimpleNamespace(root=str(self.root), manifest=str(self.manifest), relocation_map=str(self.mapping),
                                    reviewed=str(self.page.parent), run_id='relocation', apply=False,
                                    reviewer='fixture', approval_note='Explicit synthetic source-copy approval.')

    def tearDown(self): self.tmp.cleanup()

    def call(self):
        with redirect_stdout(io.StringIO()):
            return run_prepare_source_relocation(self.args)

    def test_plan_then_apply_retains_originals_reviewed_bytes_and_versions(self):
        original_page = self.page.read_bytes()
        original_norm = (self.root/self.record['normalizedMarkdown']).read_bytes()
        plan = self.call()
        self.assertEqual(plan['state'], 'planned')
        self.assertFalse((self.root/self.item['newSourceRef']).exists())
        self.args.apply = True
        result = self.call()
        self.assertEqual(result['state'], 'candidate-prepared')
        self.assertEqual(original_page, self.page.read_bytes())
        self.assertEqual(original_norm, (self.root/self.record['normalizedMarkdown']).read_bytes())
        self.assertEqual(sha256_file(self.raw), sha256_file(self.root/self.item['newSourceRef']))
        actual = json.loads(read_text(self.root/result['manifest']))['sources'][0]
        bound = json.loads(read_text(self.root/result['promotionMap']))['items'][0]
        draft = read_text(self.root/bound['draft'])
        validate_draft(self.root, actual, self.page, draft)
        self.assertEqual(frontmatter(draft)['sourceVersion'],frontmatter(original_page.decode())['sourceVersion'])
        self.assertEqual(draft.split(START)[1].split(END)[0], original_page.decode().split(START)[1].split(END)[0])
        self.assertIn(actual['sourceRef'],metadata(draft)['sourceRefs'])
        self.assertNotIn(self.record['sourceRef'],metadata(draft)['sourceRefs'])
        self.assertEqual(bound['expectedTargetHashSha256'],sha256_file(self.page))
        self.assertIn('Agent review required',read_text(self.root/actual['candidatePage']))
        with self.assertRaises(FileExistsError): self.call()

    def test_apply_requires_explicit_approval(self):
        self.args.apply=True;self.args.approval_note=''
        with self.assertRaisesRegex(ValueError,'approval'): self.call()
        self.assertFalse((self.root/self.item['newSourceRef']).exists())

    def test_legacy_fenced_coverage_cannot_override_the_new_frontmatter(self):
        text=read_text(self.page);coverage=frontmatter(text)['contentCoverage']
        text=text.replace('knowledgeId: sample','contentCoverage:\n'+''.join('  '+line+'\n' for line in dump_mapping(coverage).splitlines())+'knowledgeId: sample')
        write_text(self.page,text)
        self.item['expectedReviewedHashSha256']=sha256_file(self.page)
        write_text(self.mapping,json.dumps({'items':[self.item]}));self.args.apply=True
        result=self.call();bound=json.loads(read_text(self.root/result['promotionMap']))['items'][0]
        draft=read_text(self.root/bound['draft'])
        self.assertEqual(metadata(draft)['contentCoverage'],frontmatter(draft)['contentCoverage'])

    def test_plan_detects_changed_reviewed_hash(self):
        self.call()
        write_text(self.page,read_text(self.page)+'\nNew concurrent content.\n')
        self.args.apply=True
        with self.assertRaisesRegex(ValueError,'hash-bound'): self.call()
        self.assertFalse((self.root/self.item['newSourceRef']).exists())

    def test_cannot_overwrite_another_original(self):
        other=self.root/self.item['newSourceRef'];other.parent.mkdir(parents=True);other.write_bytes(b'Other bytes')
        self.args.apply=True
        with self.assertRaises(FileExistsError): self.call()
        self.assertEqual(other.read_bytes(),b'Other bytes')

    def test_destination_must_remain_raw(self):
        self.item['newSourceRef']='user/knowledge/reviewed/domain/source.pdf'
        write_text(self.mapping,json.dumps({'items':[self.item]}))
        with self.assertRaises(ValueError): self.call()

    def test_failure_rolls_back_only_new_raw_files(self):
        self.args.apply=True
        before=self.page.read_bytes()
        with mock.patch('rag_candidate.corpus_audit.audit_corpus',side_effect=ValueError('synthetic failure')):
            with self.assertRaisesRegex(ValueError,'synthetic failure'): self.call()
        self.assertTrue(self.raw.exists());self.assertEqual(self.page.read_bytes(),before)
        self.assertFalse((self.root/self.item['newSourceRef']).exists())
        self.assertTrue((self.root/'var/rag/relocation/failure.json').exists())

    def test_expected_target_hash_is_preserved_in_review_binding(self):
        draft=self.root/'user/knowledge/candidate/draft.md';write_text(draft,'Draft')
        value={'items':[{'sourceId':'sample','target':self.page.relative_to(self.root).as_posix(),
                         'draft':draft.relative_to(self.root).as_posix(),'expectedTargetHashSha256':sha256_file(self.page)}]}
        write_text(self.mapping,json.dumps(value))
        args=SimpleNamespace(promotion_map=str(self.mapping))
        bound=bindings_from_args(self.root,{'sources':[self.record]},args)
        self.assertEqual(bound[0]['expectedTargetHashSha256'],sha256_file(self.page))

    def test_matching_old_seal_is_not_hidden_by_stale_later_input(self):
        entry={'target':self.page.relative_to(self.root).as_posix(),'sourceRef':self.record['sourceRef'],
               'sourceHashSha256':sha256_file(self.raw),'contentHashSha256':sha256_file(self.page)}
        one=self.root/'var/rag/one.json';two=self.root/'var/rag/two.json'
        write_text(one,json.dumps({'entries':[entry]}));write_text(two,json.dumps({'entries':[{**entry,'contentHashSha256':'0'*64}]}))
        for paths in [[str(one),str(two)],[str(two),str(one)]]:
            seals,origins=supplied_seals(self.root,paths)
            self.assertEqual(seals['entries'][0]['contentHashSha256'],sha256_file(self.page))
            self.assertEqual(len(origins),2)

    def test_unknown_dates_stay_unknown_and_draft_does_not_become_current(self):
        value=audit_versions(self.root,self.page.parent,'2026-01-01')
        self.assertEqual(value['state'],'passed')
        self.assertEqual(value['sources'][0]['temporalState'],'date-unknown')
        self.assertIsNone(value['sources'][0]['sourceVersion']['publishedOn'])
        self.assertIn('draft-not-a-formal-version',value['sources'][0]['warnings'])

    def test_official_status_requires_a_real_verification_date(self):
        text=read_text(self.page);fm=frontmatter(text);fm['sourceVersion']['officialStatus']='current'
        write_text(self.page,'---\n'+dump_mapping(fm)+'\n---'+text.split('---',2)[2])
        self.assertEqual(audit_versions(self.root,self.page.parent,'2026-01-01')['state'],'failed')

    def test_future_effective_date_is_not_current_proof(self):
        text=read_text(self.page);fm=frontmatter(text);fm['sourceVersion'].update(sourceDocumentState='published-copy',publishedOn='2025-12-01',effectiveOn='2027-01-01')
        write_text(self.page,'---\n'+dump_mapping(fm)+'\n---'+text.split('---',2)[2])
        self.assertEqual(audit_versions(self.root,self.page.parent,'2026-01-01')['sources'][0]['temporalState'],'not-yet-effective')


if __name__=='__main__':unittest.main()
