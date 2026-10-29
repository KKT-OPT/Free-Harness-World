"""Regression cases for conversion, provenance, exact promotion and read-only audit."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest import mock

import fitz

from rag_candidate.cli import main
from rag_candidate.common import execute_cli, read_text, sha256_file, slugify, write_text
from rag_candidate.metadata import metadata, frontmatter, dump_mapping
from rag_candidate.pdf_normalize import normalize_pdf, normalize_text, load_profile, detect_quality, requires_ocr
from rag_candidate.corpus_audit import audit_corpus
from rag_knowledge.commands import _metadata_list_values, _raw_inventory
from rag_knowledge.cli import main as knowledge_main


HERE = Path(__file__).resolve().parents[3]
FIXTURES = HERE / "var/rag/rag-tool-tests"


class RagFixture(unittest.TestCase):
    def setUp(self):
        FIXTURES.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="case-", dir=FIXTURES)
        self.root = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.root.relative_to(FIXTURES.resolve())
        self.tmp.cleanup()

    def call(self, *args, success=True):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main([args[0], "--root", str(self.root), *map(str, args[1:])])
        result = json.loads(output.getvalue())  # Also asserts the single-object CLI contract.
        self.assertEqual(code, 0 if success else 1, result)
        return result

    def prepare(self, count=2):
        sources = []
        for i in range(count):
            raw = self.root / f"user/knowledge/raw/规范/source-{i}.txt"
            norm = self.root / f"user/knowledge/raw/规范/normalized/source-{i}.md"
            write_text(raw, f"original evidence {i}")
            write_text(norm, f"# Source {i}\n\n源材料包括系统组成、接口约束和验证方法。每一项要求保留其适用对象。")
            sources.append({"id": f"s{i}", "sourceRef": raw.relative_to(self.root).as_posix(), "sourceHashSha256": sha256_file(raw),
                            "normalizedMarkdown": norm.relative_to(self.root).as_posix(), "normalizedHashSha256": sha256_file(norm),
                            "candidateAllowed": True, "pageCount": 0})
        normalization = self.root / "var/rag/input/normalization.json"
        write_text(normalization, json.dumps({"sources": sources}, ensure_ascii=False))
        self.call("ingest", "--normalization-manifest", normalization, "--run-id", "fixture")
        self.manifest = self.root / "var/rag/fixture/extracted/metadata-manifest.json"
        self.data = json.loads(read_text(self.manifest))
        self.wiki = self.root / "user/knowledge/candidate/fixture/wiki"
        self.mapping = self.root / "var/rag/fixture/map.json"
        self.items = []
        for i, source in enumerate(self.data["sources"]):
            candidate = self.root / source["candidatePage"]
            text = read_text(candidate)
            text = text[:text.index("## Candidate Summary")]
            sections = {
                "Candidate Summary": f"这是材料{i}的独立知识结论：系统设计应先确认边界、组成与输入输出，再验证接口与异常处理。",
                "Key Claims": "材料规定了接口和系统验证要求，并明确原始数据及派生内容的来源边界。",
                "Entities": "该材料的对象是独立系统及其组成单元，不能替代另一份材料的事实。",
                "Concepts": "- [[StructuredIngestion]]\n- [[CandidateKnowledge]]",
                "Contradictions": "目前未发现内部矛盾；不同来源保持独立，不推断其相互替代关系。",
                "Applicability": "适用于材料范围内的系统设计、接口梳理和验证证据追踪。",
                "Non-Applicability": "不适用于范围之外的系统，不应把结构检查理解为内容正确性证明。",
                "Review Checklist": "来源、使用权和适用边界已经由测试夹具明确；测试不涉及真实用户知识。",
                "Source Overview": "这份材料把系统边界、设计要求和验证证据组织为一个可追踪的框架。",
                "Core Framework": "系统边界决定设计对象，接口规定输入输出，验证覆盖异常处理并保留来源证据。",
            }
            write_text(candidate, text + "\n".join(f"## {key}\n\n{value}\n" for key, value in sections.items()))
            target = self.root / f"user/knowledge/reviewed/规范/item-{i}.md"
            draft = self.root / f"user/knowledge/candidate/fixture/drafts/item-{i}.md"
            fm = {"documentName": target.relative_to(self.root).as_posix(), "version": "v1", "updatedAt": "2026-10-29", "status": "active",
                  "knowledgeRole": "authoritative", "authoritative": True, "tags": ["fixture"], "purpose": "测试来源绑定的精确知识晋升。",
                  "scope": ["reviewed-knowledge", "user-private"], "prerequisites": [], "relatedDocuments": [],
                  "outputTo": [target.relative_to(self.root).as_posix()], "owner": "user", "reviewAfter": "source-updated",
                  "supersededBy": None, "dependsOn": [], "review": {"reviewedBy": "fixture", "reviewedAt": "2026-10-29", "decision": "fixture"}}
            meta = {"knowledgeId": f"item-{i}", "sourceRefs": [source["sourceRef"], source["normalizedMarkdown"]], "reviewedBy": "fixture"}
            body = "---\n" + dump_mapping(fm) + "\n---\n\n# Material\n\n```yaml\n" + dump_mapping(meta) + "\n```\n\n"
            for name in ("Statement", "Source Overview", "Core Framework", "Applicability", "Non-Applicability", "Key Concepts", "Source Trace", "Staleness", "Governance Notes"):
                body += f"## {name}\n\n这是材料{i}有来源的独立结论，保留适用对象、方法和边界，不与其他来源混合。\n\n"
            write_text(draft, body)
            self.items.append({"sourceId": source["id"], "draft": draft.relative_to(self.root).as_posix(), "target": target.relative_to(self.root).as_posix()})
        self.write_map()

    def write_map(self):
        write_text(self.mapping, json.dumps({"items": self.items}, ensure_ascii=False))

    def review(self, mapping=True):
        return self.call("review-package", "--manifest", self.manifest, "--wiki", self.wiki,
                         *(["--promotion-map", self.mapping] if mapping else []))

    def promote(self, *extra, success=True, mapping=True):
        return self.call("promote-reviewed", "--manifest", self.manifest, "--wiki", self.wiki, "--reviewer", "fixture",
                         "--approval-note", "explicit fixture authorization", "--review-after", "source-updated",
                         *(["--promotion-map", self.mapping] if mapping else []), *extra, success=success)


class MetadataTests(RagFixture):
    def test_yaml_variants_and_bom(self):
        text = '\ufeff---\ntags: [甲, "乙: 丙"]\n---\n```yaml\nsourceRefs:\n- user/路径/长文件名\n  第二部分.pdf\n- "user/带 空格/文档.pdf"\n```\n'
        self.assertEqual(_metadata_list_values(text, "sourceRefs"), ["user/路径/长文件名 第二部分.pdf", "user/带 空格/文档.pdf"])
        self.assertEqual(frontmatter(text)["tags"], ["甲", "乙: 丙"])

    def test_duplicate_yaml_key_rejected(self):
        with self.assertRaises(ValueError):
            frontmatter("---\nstatus: active\nstatus: draft\n---\n")

    def test_part_number_does_not_discard_fingerprint(self):
        self.assertEqual(slugify("GB-T-123.10-title-aabb1122"), "gb-t-123-10-title-aabb1122")
        self.assertNotEqual(slugify("GB-T-123.1-aabb"), slugify("GB-T-123.2-aabb"))

    def test_failed_cli_has_one_json_object(self):
        def fail(_):
            print('{"state":"failed","blockingIssues":["evidence"]}')
            raise ValueError("failure")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(execute_cli(fail, None), 1)
        self.assertEqual(json.loads(output.getvalue())["blockingIssues"], ["evidence"])

    def test_home_omits_only_generated_assets(self):
        raw = self.root / "raw"
        for name in ["domain/original.png", "domain/normalized/a.md", "domain/normalized/assets/a/page.png"]:
            write_text(raw / name, "fixture")
        self.assertEqual(len(_raw_inventory(self.root, raw)), 2)


class PromotionTests(RagFixture):
    def test_archive_is_source_centered_and_manifest_stays_resolvable(self):
        from rag_knowledge.commands import _archive_inactive_candidates
        self.prepare(1)
        actions = _archive_inactive_candidates(self.root, self.root/'user/knowledge/candidate', [{
            'runId':'fixture','path':'user/knowledge/candidate/fixture', 'governanceState':'promoted-evidence',
            'reason':'fixture complete', 'markdownCount':4}])
        self.assertIn('/_archive/by-source/', actions[0]['newPath'])
        manifest = json.loads(read_text(self.manifest))
        self.assertTrue((self.root/manifest['sources'][0]['candidatePage']).is_file())

    def test_pipeline_smoke_uses_explicit_draft_without_topic_fabrication(self):
        self.prepare(1)
        raw = self.root/self.data['sources'][0]['sourceRef']
        self.call('ingest', raw, '--run-id','preview','--copy-raw','--raw-domain','规范')
        preview = json.loads(read_text(self.root/'var/rag/preview/extracted/metadata-manifest.json'))['sources'][0]
        draft = self.root/self.items[0]['draft']
        text = read_text(draft).replace(self.data['sources'][0]['normalizedMarkdown'], preview['normalizedMarkdown'])
        write_text(draft, text)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = knowledge_main(['pipeline-smoke', str(raw), '--root', str(self.root), '--run-id', 'smoke-case',
                                   '--domain', '规范', '--reviewed-draft', str(draft), '--copy-raw', '--reviewer', 'fixture',
                                   '--approval-note', 'explicit fixture authorization', '--question', '材料0', '--allowed-tags', 'fixture'])
        result = json.loads(output.getvalue())
        self.assertEqual(code, 0, result)
        self.assertEqual(result['steps']['promoteReviewedConcepts']['promotedCount'], 0)
        self.assertEqual((self.root/self.items[0]['target']).read_bytes(), draft.read_bytes())

    def test_batch_exact_bytes_and_idempotence(self):
        self.prepare()
        self.assertEqual(self.review()["state"], "ready-for-human-review")
        result = self.promote()
        self.assertEqual(result["promotedCount"], 2)
        for item, entry in zip(self.items, result["entries"]):
            self.assertEqual((self.root/item["draft"]).read_bytes(), (self.root/item["target"]).read_bytes())
            self.assertEqual(sha256_file(self.root/item["target"]), entry["contentHashSha256"])
        self.assertEqual(self.promote()["changedCount"], 0)

    def test_changed_draft_blocks_all_writes(self):
        self.prepare(); self.review()
        draft = self.root/self.items[1]["draft"]
        write_text(draft, read_text(draft)+"changed")
        self.promote(success=False)
        self.assertFalse(any((self.root/i["target"]).exists() for i in self.items))

    def test_changed_original_blocks_all_writes(self):
        self.prepare(); self.review()
        write_text(self.root/self.data["sources"][1]["sourceRef"], "changed")
        self.promote(success=False)
        self.assertFalse((self.root/self.items[0]["target"]).exists())

    def test_missing_approval_is_rejected(self):
        self.prepare(); self.review()
        self.promote("--approval-note", "", success=False)
        self.assertFalse((self.root/self.items[0]["target"]).exists())

    def test_existing_target_preflight_is_non_destructive(self):
        self.prepare(); self.review()
        target = self.root/self.items[1]["target"]
        write_text(target, "protected user content")
        self.promote(success=False)
        self.assertEqual(read_text(target), "protected user content")
        self.assertFalse((self.root/self.items[0]["target"]).exists())

    def test_duplicate_target_rejected(self):
        self.prepare()
        self.items[1]["target"] = self.items[0]["target"]; self.write_map()
        self.call("review-package", "--manifest", self.manifest, "--wiki", self.wiki, "--promotion-map", self.mapping, success=False)

    def test_subset_batch_rejected(self):
        self.prepare(); self.items = self.items[:1]; self.write_map(); self.review()
        self.promote(success=False)

    def test_batch_rollback_after_io_failure(self):
        self.prepare(); self.review()
        original = os.replace
        calls = []
        def fail_second(a, b):
            calls.append(b)
            if len(calls) == 2:
                raise OSError("fixture write failure")
            return original(a, b)
        with mock.patch("rag_candidate.promotion.os.replace", side_effect=fail_second):
            self.promote(success=False)
        self.assertFalse(any((self.root/i["target"]).exists() for i in self.items))
        self.assertFalse(list((self.root/'user/knowledge/reviewed').rglob('*.tmp')))

    def test_multiple_sources_never_silently_choose_first(self):
        self.prepare(); self.review(mapping=False)
        self.promote("--target", "user/knowledge/reviewed/规范/generic.md", success=False, mapping=False)

    def test_generic_formatter_uses_selected_source(self):
        self.prepare(); self.review(mapping=False)
        target = "user/knowledge/reviewed/规范/generic.md"
        self.promote("--source-id", self.data["sources"][1]["id"], "--target", target, mapping=False)
        text = read_text(self.root/target)
        self.assertIn("材料1的独立知识结论", text)
        self.assertNotIn("材料0的独立知识结论", text)
        self.assertNotIn("LLM agent", text)
        self.assertNotIn("StructuredIngestion", text)
        self.assertNotIn("CandidateKnowledge", text)

    def test_seal_detects_post_promotion_overwrite(self):
        self.prepare(); self.review(); seal = self.promote()
        page = self.root/self.items[0]["target"]
        write_text(page, read_text(page)+"unaudited overwrite")
        result = audit_corpus(self.root, self.data, self.root/'user/knowledge/reviewed', seal, True)
        self.assertEqual(result['state'], 'failed')
        self.assertIn('promotion-seal-mismatch', result['issues'][0]['issues'])

    def test_crlf_drafts_are_validated_and_promoted_without_byte_rewrites(self):
        self.prepare()
        expected={}
        for item in self.items:
            path=self.root/item['draft']
            content=path.read_text(encoding='utf-8-sig').replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')
            path.write_bytes(content)
            expected[item['target']]=content
        self.review()
        seal=self.promote()
        for target,content in expected.items():
            self.assertEqual((self.root/target).read_bytes(),content)
        self.assertEqual(audit_corpus(self.root,self.data,self.root/'user/knowledge/reviewed',seal,True)['state'],'passed')


class PdfTests(RagFixture):
    def test_ingest_preserves_normalized_physical_page_contract(self):
        result = self.convert(self.pdf())
        path = self.root/'var/rag/normalization-input.json'
        write_text(path,json.dumps({'sources':[result]},ensure_ascii=False))
        self.call('ingest','--normalization-manifest',path,'--run-id','page-contract')
        source=json.loads(read_text(self.root/'var/rag/page-contract/extracted/metadata-manifest.json'))['sources'][0]
        self.assertEqual(source['pageCount'],result['pageCount'])
        self.assertEqual(source['pages'],result['pages'])
    @unittest.skipUnless(os.name == 'nt', 'Windows native command wrappers')
    def test_both_powershell_wrappers_preserve_unicode_json(self):
        source = self.pdf()
        env = dict(os.environ, PYTHONUTF8='1')
        env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env['PATH']
        stable = HERE/'harness/tools/scripts/stable'
        env['PYTHONPATH'] = str(stable)
        for shell in ['powershell','pwsh']:
            with self.subTest(shell=shell):
                proc = subprocess.run([shell,'-NoProfile','-File',str(stable/'invoke-rag-candidate.ps1'),'-Root',str(self.root),
                                       '-Command','normalize-pdf','-InputPath',str(source),'-NormalizedDir',str(source.parent/'normalized'),
                                       '-OcrMode','none'],env=env,capture_output=True,encoding='utf-8',timeout=60)
                self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)
                result = json.loads(proc.stdout.lstrip('\ufeff'))
                self.assertIn('规范',result['sources'][0]['sourceRef'])

    def test_math_glyphs_are_not_misclassified_as_whole_page_ocr(self):
        page = mock.Mock()
        page.get_text.return_value = 'A valid equation uses a Symbol glyph \uf0e7 in ordinary technical text.'
        page.get_fonts.return_value = []
        flags = detect_quality(page)
        self.assertIn('private-use-glyphs-require-visual-review', flags)
        self.assertFalse(requires_ocr(flags))

    def test_substituted_latin_glyphs_require_ocr(self):
        page = mock.Mock()
        page.get_text.return_value = '\u72a0'*12
        page.get_fonts.return_value = []
        self.assertTrue(requires_ocr(detect_quality(page)))

    @unittest.skipUnless(os.name == 'nt', 'Windows Chinese OCR integration')
    def test_actual_offline_chinese_ocr(self):
        source = self.root/'user/knowledge/raw/规范/chinese.pdf';source.parent.mkdir(parents=True)
        with fitz.open() as pdf:
            p = pdf.new_page()
            p.insert_text((40, 100), '无人驾驶航空器系统安全要求', fontname='china-s', fontsize=22)
            pix = p.get_pixmap(dpi=140);pdf.delete_page(0)
            p = pdf.new_page();p.insert_image(p.rect, pixmap=pix);pdf.save(source)
        result = self.convert(source, mode='windows', language='zh-Hans-CN')
        self.assertIn('无人驾驶航空器', read_text(self.root/result['normalizedMarkdown']))

    def pdf(self, scanned=False, watermark=False):
        source = self.root/'user/knowledge/raw/规范/input.pdf'
        source.parent.mkdir(parents=True)
        with fitz.open() as pdf:
            page = pdf.new_page()
            page.insert_text((40, 60), "MH SAFETY REQUIREMENTS: preserve original body", fontsize=12)
            if watermark:
                page.insert_text((40, 500), "MH", fontsize=268, fill_opacity=.4)
            if scanned:
                pixmap = page.get_pixmap(dpi=120)
                pdf.delete_page(0)
                page = pdf.new_page()
                page.insert_image(page.rect, pixmap=pixmap)
            pdf.save(source)
        return source

    def convert(self, source, profile=None, mode='none', language='auto'):
        return normalize_pdf(self.root, source, source.parent/'normalized', self.root/'var/rag/ocr', profile or {}, mode, language)

    def test_normalization_preserves_pages_and_original(self):
        source = self.pdf(); before = sha256_file(source)
        first = self.convert(source); second = self.convert(source)
        self.assertEqual(first, second)
        self.assertEqual(sha256_file(source), before)
        self.assertIn('## PDF 第 1 页', read_text(self.root/first['normalizedMarkdown']))

    def test_unknown_watermark_retained(self):
        source = self.pdf(watermark=True); result = self.convert(source)
        self.assertFalse(result['pages'][0]['filteredWatermarks'])
        self.assertTrue(result['pages'][0]['retainedLowOpacityText'])
        self.assertTrue((self.root/result['pages'][0]['imageRef']).exists())

    def test_exact_source_bound_watermark_filter(self):
        source = self.pdf(watermark=True)
        profile = {'watermarks': [{'text': 'MH', 'font': 'Helvetica', 'minSize': 260, 'maxOpacity': .41,
                                  'sourceHashes': [sha256_file(source)], 'reviewedBy': 'fixture', 'evidence': 'fixture visual confirmation'}]}
        result = self.convert(source, profile)
        self.assertEqual(len(result['pages'][0]['filteredWatermarks']), 1)
        text = read_text(self.root/result['normalizedMarkdown'])
        self.assertIn('MH SAFETY REQUIREMENTS', text)

    def test_broad_watermark_profile_is_rejected(self):
        path = self.root/'profile.json'; write_text(path, '{"watermarks":[{"text":"MH"}]}')
        with self.assertRaises(ValueError): load_profile(path)

    def test_scanned_without_ocr_cannot_enter_candidates(self):
        result = self.convert(self.pdf(scanned=True))
        self.assertFalse(result['candidateAllowed'])
        manifest = self.root/'var/rag/normalization.json'; write_text(manifest, json.dumps({'sources':[result]}))
        self.call('ingest', '--normalization-manifest', manifest, '--run-id', 'blocked', success=False)

    def test_explicit_ocr_language_never_uses_stale_english_output(self):
        source = self.pdf(scanned=True)
        runtime = self.root/'var/rag/ocr'
        write_text(runtime/f'{sha256_file(source)}-001-zh-Hans-CN-en.json',
                   json.dumps({'language':'en-US','text':'stale english'}))
        def fake(jobs, _):
            for job in jobs:
                write_text(Path(job['output']), json.dumps({'language':job['language'],'text':'中文识别结果应采用当前语言',
                           'lines':[{'words':[{'text':'中文识别结果应采用当前语言','x':10,'y':10,'w':200,'h':20}]}]}))
        with mock.patch('rag_candidate.pdf_normalize._run_ocr', side_effect=fake):
            result = self.convert(source, mode='windows', language='zh-Hans-CN')
        text = read_text(self.root/result['normalizedMarkdown'])
        self.assertIn('中文识别结果',text)
        self.assertNotIn('stale english',text)
        self.assertEqual(result['pages'][0]['method'],'offline-ocr-zh-Hans-CN')

    def test_empty_ocr_does_not_qualify_for_ingestion(self):
        source = self.pdf(scanned=True)
        def fake(jobs, _):
            for job in jobs:
                write_text(Path(job['output']), json.dumps({'language':job['language'],'text':'','lines':[]}))
        with mock.patch('rag_candidate.pdf_normalize._run_ocr', side_effect=fake):
            result = self.convert(source, mode='windows')
        self.assertFalse(result['candidateAllowed'])
        self.assertEqual(result['unresolvedPages'],[1])

    def test_superscripts_and_units_not_folded(self):
        self.assertEqual(normalize_text('面积 ２５m²，力㎏'), '面积 25m²,力㎏')

    def test_source_bound_reviewed_page_override(self):
        source = self.pdf(); first = self.convert(source)
        override = {'sourceHashSha256':sha256_file(source),'page':1,
                    'expectedTextHashSha256':first['pages'][0]['textHashSha256'],
                    'text':'Source-verified replacement for a table: 84 kPa–107 kPa; humidity ≤ 85%.',
                    'reviewedBy':'fixture','evidence':'synthetic source visual review'}
        path = self.root/'profile.json'; write_text(path,json.dumps({'pageOverrides':[override]}))
        result = normalize_pdf(self.root,source,source.parent/'normalized',self.root/'var/rag/ocr',load_profile(path),overwrite=True)
        text = read_text(self.root/result['normalizedMarkdown'])
        self.assertIn('84 kPa–107 kPa',text)
        self.assertNotIn('MH SAFETY REQUIREMENTS',text)
        self.assertIn('pageOverride',result['pages'][0])
        self.assertTrue((self.root/result['pages'][0]['imageRef']).exists())
        override['expectedTextHashSha256'] = '0'*64
        write_text(path,json.dumps({'pageOverrides':[override]}))
        with self.assertRaisesRegex(ValueError,'precondition mismatch'):
            normalize_pdf(self.root,source,source.parent/'normalized',self.root/'var/rag/ocr',load_profile(path),overwrite=True)

    def test_page_override_requires_review_evidence(self):
        path = self.root/'profile.json'
        write_text(path,json.dumps({'pageOverrides':[{'sourceHashSha256':'a'*64,'page':1,'expectedTextHashSha256':'b'*64,'text':'unreviewed page text must be rejected'}]}))
        with self.assertRaises(ValueError): load_profile(path)

    def test_audit_detects_missing_physical_page(self):
        result = self.convert(self.pdf())
        path = self.root/result['normalizedMarkdown']; write_text(path, read_text(path).replace('## PDF 第 1 页','## PDF 第 2 页'))
        audit = audit_corpus(self.root, {'sources':[result]})
        self.assertEqual(audit['state'], 'failed')

    @unittest.skipUnless(os.name == 'nt', 'Windows OCR integration')
    def test_actual_offline_english_ocr(self):
        result = self.convert(self.pdf(scanned=True), mode='windows', language='en-US')
        self.assertTrue(result['candidateAllowed'])
        self.assertIn('offline-ocr-en-US', result['pages'][0]['method'])
        self.assertIn('SAFETY', read_text(self.root/result['normalizedMarkdown']))


if __name__ == '__main__':
    unittest.main()
