"""A reviewed white scan is distinct from an unresolved OCR failure."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import fitz
from rag_candidate.common import write_text, sha256_file
from rag_candidate.pdf_normalize import normalize_pdf, load_profile
from rag_candidate.corpus_audit import audit_corpus


class BlankPageTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parents[3]/'var/rag/rag-tool-tests'
        base.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.tmp.name).resolve()
        self.source = self.root/'user/knowledge/raw/fixture/scan.pdf'
        self.source.parent.mkdir(parents=True)
        self.output = self.source.parent/'normalized'

    def tearDown(self): self.tmp.cleanup()

    def prepare(self, mark=False):
        with fitz.open() as doc:
            p = doc.new_page(width=100, height=100)
            pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 100, 100), False)
            pix.clear_with(255)
            if mark: pix.set_pixel(50, 50, (0, 0, 0))
            p.insert_image(p.rect, stream=pix.tobytes('png'))
            doc.save(self.source)
        with fitz.open(self.source) as doc:
            image = doc[0].get_pixmap(dpi=180, alpha=False).tobytes('png')
        return {'sourceIds': {sha256_file(self.source): 'scan'}, 'blankPages': [{'sourceHashSha256': sha256_file(self.source), 'page': 1, 'expectedImageHashSha256': hashlib.sha256(image).hexdigest(), 'reviewedBy': 'fixture', 'evidence': 'Synthetic image inspection.'}]}

    def normalize(self, profile, mode='auto'):
        def empty_ocr(jobs, runtime):
            for job in jobs: write_text(Path(job['output']), json.dumps({'language': job['language'], 'text': '', 'lines': []}))
        with mock.patch('rag_candidate.pdf_normalize._run_ocr', side_effect=empty_ocr):
            return normalize_pdf(self.root, self.source, self.output, self.root/'var/rag/ocr', profile, ocr_mode=mode)

    def test_reviewed_white_scan_preserves_page_and_passes_structural_audit(self):
        profile = self.prepare()
        result = self.normalize(profile)
        self.assertTrue(result['candidateAllowed'])
        self.assertIn('reviewed-blank-page', result['pages'][0]['method'])
        self.assertTrue((self.root/result['pages'][0]['imageRef']).exists())
        self.assertEqual(audit_corpus(self.root, {'sources': [result]})['state'], 'passed')

    def test_missing_review_keeps_white_scan_blocked(self):
        self.prepare()
        self.assertFalse(self.normalize({})['candidateAllowed'])

    def test_wrong_image_hash_is_rejected(self):
        profile = self.prepare();profile['blankPages'][0]['expectedImageHashSha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'precondition'): self.normalize(profile)

    def test_nonwhite_content_cannot_be_declared_blank_even_with_matching_hash(self):
        profile = self.prepare(mark=True)
        with self.assertRaisesRegex(ValueError, 'non-white'): self.normalize(profile)

    def test_blank_declaration_cannot_bypass_missing_ocr(self):
        profile = self.prepare()
        with self.assertRaisesRegex(ValueError, 'precondition'): self.normalize(profile, mode='none')

    def test_blank_profile_requires_review_evidence(self):
        profile = self.prepare();del profile['blankPages'][0]['evidence']
        p = self.root/'profile.json';write_text(p, json.dumps(profile))
        with self.assertRaisesRegex(ValueError, 'review evidence'): load_profile(p)

    def test_blank_declaration_and_text_override_cannot_describe_same_page(self):
        profile=self.prepare()
        profile['pageOverrides']=[{'sourceHashSha256':sha256_file(self.source),'page':1,
                                  'expectedTextHashSha256':'0'*64,'text':'A complete synthetic transcription of a page.',
                                  'reviewedBy':'fixture','evidence':'Conflicting synthetic review.'}]
        p=self.root/'profile.json';write_text(p,json.dumps(profile))
        with self.assertRaisesRegex(ValueError,'same physical page'):load_profile(p)


if __name__ == '__main__': unittest.main()
