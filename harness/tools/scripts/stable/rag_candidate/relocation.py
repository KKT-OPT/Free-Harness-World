"""Copy originals and prepare source-bound relocation drafts; never delete or promote."""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
from contextlib import redirect_stdout
from pathlib import Path
from urllib.parse import unquote

from .common import read_text, write_text, rel, sha256_file, safe_run_id, today
from .metadata import frontmatter, metadata, dump_mapping, load_mapping, list_values
from .pdf_normalize import under
from .reviewed_content import START, END, rendered_content, validate_content


def _json(path):
    return json.loads(read_text(path))


def _links(text, origin, target, moved):
    def replace(match):
        value = match[1] or match[2]
        if value.startswith('#') or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', value):
            return match[0]
        path, mark, anchor = value.partition('#')
        resolved = (origin / unquote(path)).resolve()
        destination = moved.get(resolved, resolved)
        route = Path(os.path.relpath(destination, target.parent)).as_posix()
        return '](<' + route + (mark + anchor if mark else '') + '>)'
    return re.sub(r'\]\((?:<([^>]+)>|([^\s)]+))\)', replace, text)


def _draft(root, source, target, original, old_source, old_normalized, reviewer, note):
    block, coverage = rendered_content(root, source, target)
    old_block = re.search(re.escape(START) + r'.*?' + re.escape(END), original, re.S)
    if not old_block or old_block[0] != block:
        raise ValueError('relocation changed the reviewed source body; use a content repair workflow')
    prefix, suffix = original.split(START, 1)[0], original.split(END, 1)[1]
    moved = {old_source: under(root, source['sourceRef']), old_normalized: under(root, source['normalizedMarkdown'])}
    for previous, current in moved.items():
        prefix = prefix.replace(rel(root, previous), rel(root, current))
        suffix = suffix.replace(rel(root, previous), rel(root, current))
    prefix = _links(prefix, target.parent, target, moved)
    suffix = _links(suffix, target.parent, target, moved)
    fm = frontmatter(prefix)
    version = frontmatter(original).get('sourceVersion')
    if version is not None:
        fm['sourceVersion'] = version
    fm.update(updatedAt=today(), contentCoverage=coverage)
    fm['review'] = {'reviewedBy': reviewer, 'reviewedAt': today(), 'decision': 'source-relocation-candidate-requires-review'}
    prefix = re.sub(r'\A\ufeff?---\n.*?\n---', lambda _: '---\n'+dump_mapping(fm)+'\n---', prefix, count=1, flags=re.S)
    fence = next((m for m in re.finditer(r'(?ms)^```yaml\n(.*?)^```', prefix)
                  if load_mapping(m[1]).get('knowledgeId')), None)
    if not fence:
        raise ValueError('reviewed source metadata missing')
    meta = load_mapping(fence[1])
    if 'contentCoverage' in meta:
        meta['contentCoverage'] = coverage
    if 'sourceVersion' in meta:
        meta['sourceVersion'] = version
    meta.update(reviewedBy=reviewer, reviewedAt=today(), approvalNote=note,
                reviewScope='原件路径及哈希、逐页正文和版本事实不变；候选仍需审核与实际晋升。')
    prefix = prefix[:fence.start()]+ '```yaml\n'+dump_mapping(meta)+'\n```'+prefix[fence.end():]
    result = prefix + block + suffix
    if frontmatter(result).get('sourceVersion') != version:
        raise ValueError('relocation must preserve sourceVersion')
    return result


def run_prepare_source_relocation(args):
    root = Path(args.root).resolve()
    raw = root/'user/knowledge/raw'
    reviewed = under(root, args.reviewed, root/'user/knowledge/reviewed')
    manifest_path, map_path = under(root, args.manifest), under(root, args.relocation_map)
    manifest, mapping = _json(manifest_path), _json(map_path)
    if mapping.get('schemaVersion', 'harness.sourceRelocationMap.v1') != 'harness.sourceRelocationMap.v1':
        raise ValueError('unsupported relocation map schema')
    sources = {s['id']: s for s in manifest.get('sources', [])}
    items = mapping.get('items', [])
    if (not sources or len(sources) != len(manifest['sources']) or not items
            or len(items) != len(sources) or {x['sourceId'] for x in items} != set(sources)):
        raise ValueError('relocation map must cover each manifest source exactly once')
    output = root/'var/rag'/safe_run_id(args.run_id)
    candidate = root/'user/knowledge/candidate'/safe_run_id(args.run_id)
    plan_path = output/'source-relocation-plan.json'
    if output.exists() and (not plan_path.is_file() or (output/'result.json').exists() or (output/'failure.json').exists()):
        raise FileExistsError('preserve prior relocation evidence and use a new run id')
    if candidate.exists():
        raise FileExistsError('candidate output already exists')
    refs = {}
    for page in reviewed.rglob('*.md'):
        text = read_text(page)
        if frontmatter(text).get('knowledgeRole') == 'authoritative' and frontmatter(text).get('authoritative') is True:
            for ref in list_values(metadata(text).get('sourceRefs')):
                refs.setdefault(ref, []).append(page)
    writes, reserved, prepared, inputs = [], set(), [], []
    def reserve(path, content, allow_identical=False):
        key = str(path).casefold()
        if key in reserved:
            raise ValueError('duplicate relocation output')
        reserved.add(key)
        if path.exists():
            if not allow_identical or not path.is_file() or path.read_bytes() != content:
                raise FileExistsError('relocation target exists: '+rel(root, path))
        else:
            writes.append((path, content))
    for item in items:
        s = sources[item['sourceId']]
        old = under(root, s['sourceRef'], raw)
        normalized = under(root, s['normalizedMarkdown'], raw)
        new = under(root, item['newSourceRef'], raw)
        new_norm = under(root, item.get('newNormalizedMarkdown') or new.parent/'normalized'/normalized.name, raw)
        if (old == new or normalized == new_norm or old.suffix.lower() != '.pdf'
                or new.suffix.lower() != '.pdf' or new_norm.suffix.lower() != '.md'
                or any(p.lower() in {'normalized', 'assets'} for p in new.relative_to(raw).parts[:-1])):
            raise ValueError('require distinct PDF source and normalized destinations')
        if sha256_file(old) != s['sourceHashSha256'] or sha256_file(normalized) != s['normalizedHashSha256']:
            raise ValueError('source or normalized hash changed')
        pages = refs.get(s['sourceRef'], [])
        if len(pages) != 1 or item.get('expectedReviewedHashSha256') != sha256_file(pages[0]):
            raise ValueError('expected exactly one hash-bound reviewed page')
        page, text = pages[0], read_text(pages[0])
        validate_content(root, s, page, text)
        before = read_text(normalized)
        fm = frontmatter(before)
        if fm.get('source') != s['sourceRef'] or fm.get('sourceSha256') != s['sourceHashSha256']:
            raise ValueError('normalized source identity mismatch')
        body = before.split('---', 2)[2]
        body = _links(body, normalized.parent, new_norm, {old: new})
        fm['source'] = rel(root, new)
        normalized_bytes = ('---\n'+dump_mapping(fm)+'\n---'+body).encode('utf-8')
        reserve(new, old.read_bytes(), allow_identical=True)
        reserve(new_norm, normalized_bytes)
        sidecar = normalized.parent/'assets'/normalized.stem/'conversion.json'
        if not sidecar.is_file():
            raise ValueError('relocation requires the conversion sidecar')
        converted = _json(sidecar)
        if (converted.get('sourceRef') != s['sourceRef'] or converted.get('sourceHashSha256') != s['sourceHashSha256']
                or converted.get('normalizedHashSha256') != s['normalizedHashSha256']):
            raise ValueError('conversion sidecar is stale')
        new_hash = hashlib.sha256(normalized_bytes).hexdigest()
        converted.update(sourceRef=rel(root, new), normalizedMarkdown=rel(root, new_norm), normalizedHashSha256=new_hash)
        reserve(new_norm.parent/'assets'/new_norm.stem/'conversion.json',
                (json.dumps(converted, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
        current = {**s, 'sourceRef': rel(root, new), 'normalizedMarkdown': rel(root, new_norm), 'normalizedHashSha256': new_hash}
        for key in ['reviewed', 'normalizationManifest', 'normalizationManifestHashSha256']:
            current.pop(key, None)
        inputs.extend((rel(root, p), sha256_file(p)) for p in [old, normalized, sidecar, page])
        prepared.append((current, page, text, old, normalized))
    material = {'manifestHashSha256': sha256_file(manifest_path), 'mapHashSha256': sha256_file(map_path),
                'inputs': inputs, 'outputs': [(rel(root, p), hashlib.sha256(b).hexdigest()) for p,b in writes],
                'sources': [s for s, *_ in prepared]}
    digest = hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
    plan = {'state': 'planned', 'scope': 'source-copy-and-candidate-preparation-no-delete-no-promotion',
            'snapshotHashSha256': digest, 'sourceCount': len(prepared), **material}
    if plan_path.exists() and _json(plan_path)['snapshotHashSha256'] != digest:
        raise ValueError('relocation inputs changed after plan; use a new run id')
    if not plan_path.exists():
        write_text(plan_path, json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return {**plan, 'report': rel(root, plan_path), 'rawOrReviewedWritten': False}
    if not args.reviewer.strip() or not args.approval_note.strip():
        raise ValueError('apply requires reviewer and explicit approval note')
    created = []
    try:
        # Keep originals and old derivatives intact; only new destinations are written.
        for route, expected in inputs:
            if sha256_file(under(root, route)) != expected:
                raise ValueError('input changed before relocation')
        for p, content in writes:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as stream:
                created.append((p, content))
                stream.write(content)
        from .corpus_audit import audit_corpus
        audit = audit_corpus(root, {'sources': [s for s, *_ in prepared]})
        write_text(output/'normalization-audit.json', json.dumps(audit, ensure_ascii=False, indent=2))
        if audit['state'] != 'passed':
            raise ValueError('relocated normalization audit failed')
        normalization = output/'normalization-manifest.json'
        write_text(normalization, json.dumps({'schemaVersion': 'harness.pdfNormalization.v1',
                   'manifestId': args.run_id, 'conversionOrigin': 'relocated-without-reconversion', 'sources': audit['sources']}, ensure_ascii=False, indent=2))
        from .cli import build_parser
        from .commands import run_ingest
        ingest_args = build_parser().parse_args(['ingest', '--root', str(root), '--normalization-manifest', str(normalization), '--run-id', args.run_id])
        with redirect_stdout(io.StringIO()):
            ingested = run_ingest(ingest_args)
        actual_manifest = output/'extracted/metadata-manifest.json'
        actual = _json(actual_manifest)
        by_norm = {s['normalizedMarkdown']: s for s in actual['sources']}
        if set(by_norm) != {s['normalizedMarkdown'] for s, *_ in prepared}:
            raise ValueError('ingestion did not cover the relocation scope')
        bindings, proofs = [], []
        from .promotion import validate_draft
        for s, target, text, old, old_norm in prepared:
            actual_source = by_norm[s['normalizedMarkdown']]
            draft_text = _draft(root, actual_source, target, text, old, old_norm, args.reviewer, args.approval_note)
            validate_draft(root, actual_source, target, draft_text)
            draft = candidate/'drafts'/target.name
            if draft.exists():
                raise ValueError('reviewed draft basename collision')
            write_text(draft, draft_text)
            expected = sha256_file(target)
            if expected != next(h for route,h in inputs if route == rel(root,target)):
                raise ValueError('reviewed target changed during relocation')
            bindings.append({'sourceId': actual_source['id'], 'target': rel(root,target), 'draft': rel(root,draft),
                             'expectedTargetHashSha256': expected})
            proofs.append({'target': rel(root,target), 'previousReviewedHashSha256': expected,
                           'draftHashSha256': sha256_file(draft), 'sourceBodyUnchanged': True, 'sourceVersionUnchanged': True})
        mapping_path = output/'promotion-map.json'
        write_text(mapping_path, json.dumps({'items': bindings}, ensure_ascii=False, indent=2))
        result = {'state': 'candidate-prepared', 'scope': plan['scope'], 'sourceCount': len(prepared),
                  'manifest': rel(root,actual_manifest), 'normalizationManifest': rel(root,normalization),
                  'wiki': ingested['candidateWiki'], 'promotionMap': rel(root,mapping_path), 'proofs': proofs,
                  'reviewer': args.reviewer, 'approvalNote': args.approval_note,
                  'originalsRetained': True, 'reviewedKnowledgeWritten': False,
                  'nextAction': 'enrich-candidate-review-package-promote-before-authorized-old-file-cleanup'}
        write_text(output/'result.json', json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except Exception as exc:
        recovery = []
        for p, content in reversed(created):
            if p.is_file() and p.read_bytes() == content:
                p.unlink()
                recovery.append({'path': rel(root,p), 'state': 'new-file-removed'})
            else:
                recovery.append({'path': rel(root,p), 'state': 'changed-or-partial-file-preserved'})
        write_text(output/'failure.json', json.dumps({'state': 'failed', 'error': str(exc), 'recovery': recovery}, ensure_ascii=False, indent=2))
        raise
