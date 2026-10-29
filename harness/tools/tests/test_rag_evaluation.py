"""Evaluation boundary and logical-clause retrieval invariants using synthetic sources."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from rag_candidate.common import write_text, sha256_file
from rag_knowledge.evaluation import audit_record
from rag_knowledge.retrieval import passages, source_matches
from rag_knowledge.commands import _query_reviewed
from rag_knowledge.cli import main


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parents[3]/'var/rag/rag-tool-tests'
        base.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.tmp.name).resolve()
        self.page = self.root/'user/knowledge/reviewed/domain/source.md'
        write_text(self.page, '---\nknowledgeRole: authoritative\nauthoritative: true\n---\n# NX 1000 fixture\n\n## 4.2 Stability\n\nThe fixture requires stable operation under the declared condition, within its stated scope.\n')
        self.evidence = {'id':'e1','kind':'reviewed','path':self.page.relative_to(self.root).as_posix(),
                         'sha256':sha256_file(self.page),'startLine':9,'endLine':9}

    def tearDown(self):
        self.tmp.cleanup()

    def record(self, mode='knowledge-only'):
        return {'mode':mode,'question':'fixture stability requirements','reviewer':'fixture',
                'trace':{'scope':'whole-turn','complete':True,'capturedBy':'reviewer-audited',
                         'events':[{'kind':'knowledge-query'},{'kind':'reviewed-read','path':self.evidence['path']}]},
                'evidence':[dict(self.evidence)],'assessment':'passed'}

    def test_pure_record_passes_without_claiming_runtime_attestation(self):
        result = audit_record(self.root,self.record())
        self.assertTrue(result['knowledgeOnlyAcceptance'])
        self.assertIn('not-runtime-attestation',result['coverageAssurance'])

    def test_status_only_web_lookup_invalidates_test_even_with_local_guard(self):
        record=self.record();record['localFileGuardPassed']=True
        record['trace']['events'].append({'kind':'external-status-check','purpose':'metadata only'})
        result=audit_record(self.root,record)
        self.assertEqual(result['state'],'invalid');self.assertFalse(result['knowledgeOnlyAcceptance'])

    def test_command_only_guard_is_insufficient(self):
        record=self.record();record['trace']['scope']='command'
        self.assertEqual(audit_record(self.root,record)['state'],'inconclusive')

    def test_agent_no_web_declaration_is_not_full_trace_evidence(self):
        record=self.record();record['trace']['capturedBy']='agent-declared'
        self.assertEqual(audit_record(self.root,record)['state'],'inconclusive')

    def test_mixed_usage_is_attributed_and_never_counted_as_pure_test(self):
        record=self.record('mixed');record['trace']['events'].append({'kind':'web-open'})
        record['evidence'].append({'id':'e2','kind':'web','url':'https://example.invalid/fixture'})
        result=audit_record(self.root,record)
        self.assertEqual(result['state'],'mixed-usage-recorded');self.assertFalse(result['knowledgeOnlyAcceptance'])

    def test_candidate_citation_cannot_masquerade_as_reviewed(self):
        record=self.record();record['evidence'][0]['path']='user/knowledge/candidate/fixture.md'
        self.assertEqual(audit_record(self.root,record)['state'],'invalid')

    def test_changed_evidence_and_out_of_range_lines_rejected(self):
        record=self.record();record['evidence'][0]['sha256']='0'*64
        self.assertEqual(audit_record(self.root,record)['state'],'invalid')
        record=self.record();record['evidence'][0]['endLine']=1000
        self.assertEqual(audit_record(self.root,record)['state'],'invalid')

    def test_reasoning_requires_existing_premises(self):
        record=self.record();record['inferences']=[{'statement':'fixture inference','premiseEvidenceIds':['missing']}]
        self.assertEqual(audit_record(self.root,record)['state'],'invalid')

    def test_pre_ingested_url_does_not_count_as_live_web_access(self):
        write_text(self.page,self.page.read_text(encoding='utf-8')+'\nSource record: https://example.invalid/fixture\n')
        self.evidence['sha256']=sha256_file(self.page)
        self.assertTrue(audit_record(self.root,self.record())['knowledgeOnlyAcceptance'])

    def test_unknown_tool_event_prevents_clean_acceptance(self):
        record=self.record();record['trace']['events'].append({'kind':'unclassified-adapter-call'})
        self.assertEqual(audit_record(self.root,record)['state'],'inconclusive')

    def test_wrong_schema_is_rejected(self):
        record=self.record();record['schemaVersion']='unrecognized-schema'
        with self.assertRaises(ValueError):audit_record(self.root,record)

    def test_failed_answer_does_not_gain_acceptance_from_valid_provenance(self):
        record=self.record();record['assessment']='failed'
        result=audit_record(self.root,record)
        self.assertEqual(result['state'],'failed');self.assertFalse(result['knowledgeOnlyAcceptance'])

    def test_audit_never_overwrites_input_record(self):
        path=self.root/'var/rag/evaluation.json';write_text(path,json.dumps(self.record()))
        before=path.read_bytes();output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=main(['audit-query-evaluation','--root',str(self.root),'--evaluation-record',str(path),'--report',str(path)])
        self.assertEqual(code,1);self.assertEqual(path.read_bytes(),before)

    def test_audit_cli_reports_failure_and_preserves_invalid_record_result(self):
        record=self.record();record['trace']['events'].append({'kind':'web-search'})
        path=self.root/'var/rag/evaluation.json';write_text(path,json.dumps(record))
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=main(['audit-query-evaluation','--root',str(self.root),'--evaluation-record',str(path)])
        self.assertEqual(code,1);self.assertIsInstance(json.loads(output.getvalue()),dict)
        report=json.loads((self.root/'var/rag/query-evaluation/query-evaluation-audit.json').read_text(encoding='utf-8'))
        self.assertEqual(report['state'],'invalid')

    def test_query_cli_exposes_mode_prefix_and_command_scope_limit(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=main(['query-reviewed','stability','--root',str(self.root),'--mode','mixed','--source-prefix','NX'])
        result=json.loads(output.getvalue())
        self.assertEqual(code,0);self.assertEqual(result['queryMode'],'mixed')
        self.assertEqual(result['sourcePrefix'],'NX')
        self.assertFalse(result['sourceBoundary']['externalRetrievalByThisCommand'])
        self.assertIn('not-whole-turn-proof',result['sourceBoundary']['coverage'])

    def test_graph_expansion_cannot_bypass_source_prefix(self):
        other=self.root/'user/knowledge/reviewed/domain/industry.md'
        write_text(other,'---\nknowledgeRole: authoritative\nauthoritative: true\n---\n# IX 4000 fixture\n\nA separate source linked only for navigation, outside the requested identifier family.\n')
        graph=self.root/'var/rag/graph.json'
        write_text(graph,json.dumps({'nodes':[{'id':'reviewed/domain/source'},{'id':'reviewed/domain/industry'}],
                                     'edges':[{'from':'reviewed/domain/source','to':'reviewed/domain/industry'}]}))
        result=_query_reviewed(self.root,self.root/'user/knowledge',self.root/'user/knowledge/reviewed',graph,'stability',5,'2026-10-29','NX')
        self.assertTrue(result['matches']);self.assertFalse(any('industry.md' in m['page'] for m in result['matches']))

    def test_graph_navigation_keeps_exact_lines_without_claiming_direct_relevance(self):
        other=self.root/'user/knowledge/reviewed/domain/related.md'
        text='---\nknowledgeRole: authoritative\nauthoritative: true\n---\n# Related fixture\n\nThis document is linked as background and provides a separate subject with its own scope.\n'
        write_text(other,text)
        graph=self.root/'var/rag/graph.json'
        write_text(graph,json.dumps({'nodes':[{'id':'reviewed/domain/source'},{'id':'reviewed/domain/related'}],
                                     'edges':[{'from':'reviewed/domain/source','to':'reviewed/domain/related'}]}))
        result=_query_reviewed(self.root,self.root/'user/knowledge',self.root/'user/knowledge/reviewed',graph,'stability',5,'2026-10-29')
        neighbor=next(m for m in result['matches'] if m['page'].endswith('related.md'))
        self.assertEqual(neighbor['contentEvidence'],'graph-navigation-only')
        section=neighbor['matchedSections'][0]
        self.assertEqual('\n'.join(text.splitlines()[section['startLine']-1:section['endLine']]),section['excerpt'])

    def test_source_prefix_filter_keeps_subfamilies_without_using_body_references(self):
        self.assertTrue(source_matches('# NX/T 2000 Fixture\n', 'NX'))
        self.assertFalse(source_matches('# IX 2000 Fixture\nReferences NX 1000\n','NX'))
        with self.assertRaises(ValueError):source_matches('# NX 1000 Fixture','NX.*')

    def test_cross_page_clause_keeps_continuation_and_exact_citation_lines(self):
        text='# Fixture\n\n## 条款检索正文\n\n### PDF 第 1 页\n\n校核级别：原页完整校录。\n\n### 4.2 Stability\n\nThe fixture shall maintain stable operation under the declared\n\n### PDF 第 2 页\n\n校核级别：来源对齐文本，未逐字校勘。\n\ncondition, with error no greater than 0.25 units in normal operation.\n\n### 4.3 Other\n\nA different requirement must remain in a separate logical clause.\n'
        chunk=next(p for p in passages(text) if p['localHeading']=='4.2 Stability')
        self.assertIn('0.25 units',chunk['text']);self.assertNotIn('different requirement',chunk['text'])
        self.assertEqual(chunk['sourcePages'],[1,2]);self.assertNotEqual(chunk['verification'],'visual-verified')
        self.assertEqual('\n'.join(text.splitlines()[chunk['startLine']-1:chunk['endLine']]),chunk['text'])

    def test_filtered_query_returns_target_clause_ahead_of_repetitive_title(self):
        write_text(self.root/'user/knowledge/reviewed/domain/noise.md', '# NX 3000 generic widget requirements\n\n## Overview\n\n'+('Generic widget requirements are discussed here. '*80))
        write_text(self.root/'user/knowledge/reviewed/domain/industry.md','# IX 4000 widget\n\n## Stability\n\nWidget stability shall satisfy the declared fixture constraints under the test conditions.\n')
        result=_query_reviewed(self.root,self.root/'user/knowledge',self.root/'user/knowledge/reviewed',self.root/'none.json','generic widget stability requirements',5,'2026-10-29','NX')
        self.assertEqual(result['matches'][0]['page'],self.page.relative_to(self.root).as_posix())
        self.assertTrue(all('industry.md' not in m['page'] for m in result['matches']))


if __name__=='__main__':unittest.main()
