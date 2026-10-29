"""Reviewed-content coverage, passage retrieval and read-boundary regression fixtures."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from types import SimpleNamespace

from rag_candidate.common import write_text, sha256_file
from rag_candidate.metadata import dump_mapping
from rag_candidate.reviewed_content import rendered_content, validate_content, source_pages, run_prepare_reviewed_content
from rag_knowledge.commands import _query_reviewed
from rag_knowledge.retrieval import version_context, passages


class ReviewedContentTests(unittest.TestCase):
    def setUp(self):
        base=Path(__file__).resolve().parents[3]/'var/rag/rag-tool-tests'
        base.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=base)
        self.root=Path(self.tmp.name).resolve()
        self.vault=self.root/'user/knowledge'
        self.reviewed=self.vault/'reviewed'
        self.page=self.reviewed/'domain/source.md'

    def tearDown(self):
        self.tmp.cleanup()

    def query(self,question,scope=None):
        return _query_reviewed(self.root,self.vault,scope or self.reviewed,self.root/'missing-graph.json',question,5,'2026-10-29')

    def test_toc_only_and_tampered_copy_cannot_pass_coverage_gate(self):
        norm=self.vault/'raw/domain/normalized/source.md'
        write_text(norm,'## PDF 第 1 页\n\n### 速度区间\n\n甲类：最大真空速≤75 km/h；乙类：75 km/h＜最大真空速≤150 km/h。\n')
        source={'sourceRef':'user/knowledge/raw/domain/source.pdf','normalizedMarkdown':norm.relative_to(self.root).as_posix(),'normalizedHashSha256':sha256_file(norm),'pageCount':1}
        with self.assertRaisesRegex(ValueError,'reviewed-content-coverage'):
            validate_content(self.root,source,self.page,'## Core Framework\n\n[速度分类](source.pdf)')
        block,coverage=rendered_content(self.root,source,self.page)
        text='---\n'+dump_mapping({'contentCoverage':coverage})+'\n---\n'+block
        validate_content(self.root,source,self.page,text)
        with self.assertRaisesRegex(ValueError,'reviewed-content-coverage'):
            validate_content(self.root,source,self.page,text.replace('≤75','＜75'))
        self.assertIn('≤75',block)

    def test_missing_or_duplicate_physical_page_rejected(self):
        for text in ['## PDF 第 2 页\nabc','## PDF 第 1 页\na\n## PDF 第 1 页\nb']:
            with self.assertRaises(ValueError):source_pages(text)

    def test_question_returns_complete_table_ahead_of_repetitive_overview(self):
        write_text(self.page,'# 分类规则\n\n## 4.9 基于最大真空速的分类\n\n校核级别：原页完整校录。\n\n| 类别 | 最大真空速 |\n|---|---|\n| 甲类 | V≤75 km/h |\n| 乙类 | 75＜V≤150 km/h |\n| 丙类 | V＞150 km/h |\n')
        write_text(self.reviewed/'domain/noise.md','# 系统概览\n\n## Overview\n\n'+('航空器最大速度相关概述。'*100))
        result=self.query('基于最大真空速可以分为哪几类')
        self.assertEqual(result['matches'][0]['page'],self.page.relative_to(self.root).as_posix())
        excerpt=result['matches'][0]['matchedSections'][0]['excerpt']
        self.assertIn('甲类',excerpt);self.assertIn('丙类',excerpt);self.assertIn('≤150',excerpt)

    def test_query_never_reads_raw_pdf_candidate_or_runtime_index(self):
        write_text(self.page,'# 速度规则\n\n## 最大真空速\n\n甲类最大真空速≤75 km/h；乙类最大真空速＞75 km/h。该规则适用于测试对象。\n')
        original=io.open;reads=[]
        def guarded(path,*args,**kwargs):
            if isinstance(path,(str,Path)):
                value=Path(path).resolve()
                self.assertTrue(value.is_relative_to(self.reviewed),str(value))
                reads.append(str(value))
            return original(path,*args,**kwargs)
        with mock.patch('io.open',side_effect=guarded):
            result=self.query('最大真空速')
        self.assertTrue(reads);self.assertIn('≤75',result['matches'][0]['matchedSections'][0]['excerpt'])

    def test_passage_citation_lines_equal_actual_reviewed_text(self):
        text='# 测试\n\n## 条款\n\n\n第一段包含条件与对象，说明该条款适用于哪些场景及使用边界。\n\n第二段保留数值≤75以及完整的分类条件和适用对象。\n'
        chunk=passages(text)[0]
        self.assertEqual('\n'.join(text.splitlines()[chunk['startLine']-1:chunk['endLine']]),chunk['text'])

    def test_effective_date_boundary_and_newer_publication_are_not_current_status(self):
        fm={'sourceVersion':{'publishedOn':'2025-12-02','effectiveOn':'2027-01-01','officialStatus':'upcoming','statusVerifiedOn':'2026-10-29'}}
        self.assertEqual(version_context(fm,'2026-12-31')['temporalState'],'not-yet-effective')
        self.assertEqual(version_context(fm,'2027-01-01')['temporalState'],'effective-date-reached-status-needs-verification')
        self.assertEqual(version_context(fm,'2025-01-01')['temporalState'],'not-yet-published')

    def test_yaml_date_values_remain_json_serializable(self):
        write_text(self.page,'---\nreview:\n  reviewedAt: 2026-10-29\nsourceVersion:\n  publishedOn: 2020-01-01\n  effectiveOn: 2020-12-01\n---\n# 规则\n\n## 速度\n\n最大真空速分类条件保留适用对象、上界包含等号以及完整数值和单位。\n')
        result=self.query('最大真空速')
        json.dumps(result)
        self.assertEqual(result['matches'][0]['reviewedAt'],'2026-10-29')

    def test_content_profile_hash_change_blocks_draft_writes(self):
        norm=self.vault/'raw/domain/normalized/source.md'
        write_text(norm,'## PDF 第 1 页\n\n来源正文包括分类条件、完整边界、单位和适用范围。\n')
        ref='user/knowledge/raw/domain/source.pdf'
        write_text(self.page,'---\nknowledgeRole: authoritative\nauthoritative: true\nsourceSha256: "'+('0'*64)+'"\nsourceRefs: ['+ref+']\n---\n# 规则\n')
        source={'id':'source','sourceRef':ref,'sourceHashSha256':'0'*64,'normalizedMarkdown':norm.relative_to(self.root).as_posix(),'normalizedHashSha256':sha256_file(norm),'pageCount':1}
        manifest=self.root/'var/rag/input.json';profile=self.root/'var/rag/profile.json'
        write_text(manifest,json.dumps({'sources':[source]}))
        write_text(profile,json.dumps({'sources':[{'sourceHashSha256':'0'*64,'normalizedHashSha256':'1'*64}]}))
        args=SimpleNamespace(root=str(self.root),manifest=str(manifest),content_profile=str(profile),reviewed=str(self.reviewed),run_id='profile-test',reviewer='fixture')
        with self.assertRaisesRegex(ValueError,'normalized hash mismatch'):run_prepare_reviewed_content(args)
        self.assertFalse((self.vault/'candidate/profile-test/drafts').exists())

    def test_unknown_content_profile_source_is_not_silently_ignored(self):
        manifest=self.root/'var/rag/input.json';profile=self.root/'var/rag/profile.json'
        write_text(manifest,json.dumps({'sources':[]}))
        write_text(profile,json.dumps({'sources':[{'sourceHashSha256':'0'*64}]}))
        args=SimpleNamespace(root=str(self.root),manifest=str(manifest),content_profile=str(profile),reviewed=str(self.reviewed),run_id='unknown-profile',reviewer='fixture')
        with self.assertRaisesRegex(ValueError,'unknown source hashes'):run_prepare_reviewed_content(args)

    def test_preparation_rejects_changed_original_before_copying_old_claims(self):
        norm=self.vault/'raw/domain/normalized/source.md'
        write_text(norm,'## PDF 第 1 页\n\n新来源正文包含新的分类要求，旧已核验结论不能自动继承。\n')
        ref='user/knowledge/raw/domain/source.pdf'
        write_text(self.page,'---\nknowledgeRole: authoritative\nauthoritative: true\nsourceSha256: "'+('0'*64)+'"\nsourceRefs: ['+ref+']\n---\n# 旧规则\n')
        source={'id':'source','sourceRef':ref,'sourceHashSha256':'1'*64,'normalizedMarkdown':norm.relative_to(self.root).as_posix(),'normalizedHashSha256':sha256_file(norm),'pageCount':1}
        manifest=self.root/'var/rag/input.json';write_text(manifest,json.dumps({'sources':[source]}))
        args=SimpleNamespace(root=str(self.root),manifest=str(manifest),content_profile=None,reviewed=str(self.reviewed),run_id='changed-original',reviewer='fixture')
        with self.assertRaisesRegex(ValueError,'original changed'):run_prepare_reviewed_content(args)
        self.assertFalse((self.vault/'candidate/changed-original/drafts').exists())

    def test_coverage_rejects_stale_reviewed_source_hash(self):
        source={'sourceRef':'user/knowledge/raw/domain/source.pdf','sourceHashSha256':'1'*64}
        with self.assertRaisesRegex(ValueError,'source hash mismatch'):
            validate_content(self.root,source,self.page,'---\nsourceSha256: "'+('0'*64)+'"\n---\n旧已核验正文。')


if __name__=='__main__':unittest.main()
