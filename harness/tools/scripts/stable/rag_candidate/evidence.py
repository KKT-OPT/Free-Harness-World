"""Read-only PDF copy comparison and explicit private evidence bundling."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .common import write_text, sha256_file, sha256_text, safe_run_id, rel, print_json
from .pdf_normalize import under


def run_compare_pdf_copies(args) -> dict:
    import fitz

    root = Path(args.root).resolve()
    paths = [under(root, p, root/'user/knowledge/raw') for p in args.inputs]
    if len(paths) != 2 or paths[0] == paths[1] or any(p.suffix.lower() != '.pdf' for p in paths):
        raise ValueError('compare-pdf-copies requires two distinct raw PDF paths')
    output = root/'var/rag'/safe_run_id(args.run_id)/'copy-comparison'
    if output.exists():
        raise FileExistsError('copy comparison requires a new run id')
    hashes = [sha256_file(p) for p in paths]
    pages = []
    with fitz.open(paths[0]) as left, fitz.open(paths[1]) as right:
        counts = [len(left), len(right)]
        for i in range(min(counts)):
            texts = [''.join(doc[i].get_text().split()) for doc in [left, right]]
            pix = [doc[i].get_pixmap(dpi=args.dpi, alpha=False, colorspace=fitz.csRGB) for doc in [left, right]]
            same_size = (pix[0].width, pix[0].height) == (pix[1].width, pix[1].height)
            samples = [p.samples for p in pix]
            same_render = same_size and samples[0] == samples[1]
            delta = (sum(abs(a-b) for a, b in zip(*samples))/len(samples[0])) if same_size else None
            pages.append({'physicalPage': i+1, 'nativeTextMatches': texts[0] == texts[1],
                          'nativeTextHashes': [sha256_text(t) for t in texts],
                          'nativeTextEmpty': [not t for t in texts], 'renderMatches': same_render,
                          'renderSizeMatches': same_size, 'meanAbsoluteChannelDifference': round(delta, 6) if delta is not None else None})
    if hashes != [sha256_file(p) for p in paths]:
        raise ValueError('PDF changed during comparison')
    result = {'state': 'compared', 'scope': 'raw-copy-comparison-no-merge-no-promotion',
              'sources': [{'path': rel(root, p), 'sha256': h, 'physicalPages': n} for p, h, n in zip(paths, hashes, counts)],
              'sameBytes': hashes[0] == hashes[1], 'samePageCount': counts[0] == counts[1],
              'allNativeTextMatches': counts[0] == counts[1] and all(p['nativeTextMatches'] for p in pages),
              'allRendersMatch': counts[0] == counts[1] and all(p['renderMatches'] for p in pages),
              'nativeTextEmptyPages': [p['physicalPage'] for p in pages if any(p['nativeTextEmpty'])],
              'visualDifferencePages': [p['physicalPage'] for p in pages if not p['renderMatches']],
              'pages': pages, 'dpi': args.dpi, 'disposition': 'review-required-before-canonical-source-selection',
              'semanticAssurance': 'text-render-comparison-not-edition-or-legal-equivalence-proof'}
    output.mkdir(parents=True, exist_ok=False)
    report = output/'comparison.json'
    result['report'] = rel(root, report)
    write_text(report, json.dumps(result, ensure_ascii=False, indent=2))
    print_json(result)
    return result


def run_archive_build_evidence(args) -> dict:
    root = Path(args.root).resolve()
    plan_path = under(root, args.evidence_manifest)
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes.decode('utf-8-sig'))
    artifacts = plan.get('artifacts', [])
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError('evidence manifest requires a nonempty artifacts list')
    parent = under(root, args.audit_dir, root/'user/knowledge/candidate/_audit')
    output = parent/safe_run_id(args.run_id)
    if output.exists():
        raise FileExistsError('evidence archive exists; preserve it and use a new run id')
    pending, seen = [], set()
    for item in artifacts:
        source = under(root, item['source'])
        if not any(source.is_relative_to(p) for p in [root/'var/rag', root/'user/knowledge/candidate']):
            raise ValueError('evidence source must be in private RAG runtime or candidate boundary')
        target = under(root, output/item['target'], output)
        key = str(target).casefold()
        if target == output or key in seen or target.name.casefold() == 'artifactmanifest.json':
            raise ValueError('duplicate, reserved or invalid evidence target')
        content = source.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if not item.get('sha256') or item['sha256'] != digest:
            raise ValueError('evidence artifact hash mismatch: ' + rel(root, source))
        pending.append((target, content, {'source': rel(root, source), 'path': target.relative_to(output).as_posix(), 'sha256': digest}))
        seen.add(key)
    # All inputs and output identities are validated before any archive is written.
    output.mkdir(parents=True, exist_ok=False)
    for target, content, _ in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    result = {'state': 'archived', 'scope': 'private-workflow-evidence-not-authoritative-knowledge',
              'inputManifest': rel(root, plan_path), 'inputManifestHashSha256': hashlib.sha256(plan_bytes).hexdigest(),
              'archive': rel(root, output), 'artifactCount': len(pending), 'files': [p[2] for p in pending],
              'semanticAssurance': 'byte-preservation-only-no-reinterpretation-of-pass-fail-or-approval'}
    write_text(output/'ArtifactManifest.json', json.dumps(result, ensure_ascii=False, indent=2))
    print_json(result)
    return result
