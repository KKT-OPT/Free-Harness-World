"""Prepare source-aligned, page-complete reviewed drafts; never promote implicitly."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .common import read_text, write_text, rel, sha256_file, sha256_text, today, safe_run_id, print_json
from .metadata import frontmatter, metadata, list_values, dump_mapping, load_mapping
from .pdf_normalize import under

START = '<!-- harness:reviewed-source-text:start -->'
END = '<!-- harness:reviewed-source-text:end -->'
PAGE = re.compile(r'(?m)^## PDF 第 (\d+) 页[ \t]*$')


def source_pages(text: str) -> list[tuple[int, str]]:
    headings = list(PAGE.finditer(text))
    pages = []
    for i, heading in enumerate(headings):
        block = text[heading.end():headings[i+1].start() if i+1 < len(headings) else len(text)]
        # Drop only the converter's provenance/image wrappers, not source tables or equations.
        block = re.sub(r'(?m)^\[(?:原 PDF 页|PDF 原页)\][^\n]*\n?', '', block)
        block = re.sub(r'(?m)^!\[PDF 第 \d+ 页原图\]\([^\n]+\)\s*$', '', block)
        pages.append((int(heading[1]), block.strip()))
    if not pages or [p[0] for p in pages] != list(range(1, len(pages)+1)):
        raise ValueError('normalized physical pages must be complete, ordered and unique')
    return pages


def _rebase_links(text: str, origin: Path, target: Path) -> str:
    def replace(match):
        value = match[1] or match[2]
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', value) or value.startswith('#'):
            return match[0]
        path, separator, anchor = value.partition('#')
        output = Path(os.path.relpath((origin / path).resolve(), target.parent)).as_posix()
        return '](<' + output + (separator + anchor if separator else '') + '>)'
    return re.sub(r'\]\((?:<([^>]+)>|([^\s)]+))\)', replace, text)


def rendered_content(root: Path, source: dict, target: Path) -> tuple[str, dict]:
    normalized = under(root, source['normalizedMarkdown'], root/'user/knowledge/raw')
    if sha256_file(normalized) != source['normalizedHashSha256']:
        raise ValueError('normalized content changed before draft preparation')
    pages = source_pages(read_text(normalized))
    if source.get('pageCount') != len(pages):
        raise ValueError('normalized page count does not match source manifest')
    methods = {int(p['page']): p for p in source.get('pages', [])}
    lines = [START, '## 条款检索正文', '',
             '以下正文属于本页审核与晋升范围，日常查询直接读取本页。物理页码用于追溯；转换覆盖不等于逐字语义校勘。',
             '各页保留提取方法与校核级别；数值、公式或图表若尚未核实，回答须保留质量限定，不能把原件核对当作检索成功。', '']
    for number, text in pages:
        record = methods.get(number, {})
        method = record.get('method', 'legacy-page-text')
        verified = bool(record.get('pageOverride')) or 'reviewed-page-override' in method
        state = '原页完整校录' if verified else '来源对齐文本，未逐字校勘'
        lines.extend([f'### PDF 第 {number} 页', '', f'提取方法：`{method}`；校核级别：{state}。', '',
                      _rebase_links(text, normalized.parent, target), ''])
    lines.append(END)
    block = '\n'.join(lines)
    coverage = {'schemaVersion': 'harness.reviewedContent.v1', 'sourcePages': len(pages),
                'includedPages': [p[0] for p in pages], 'normalizedHashSha256': sha256_file(normalized),
                'bodyHashSha256': sha256_text(block), 'semanticState': 'source-aligned-selective-visual-review'}
    return block, coverage


def validate_content(root: Path, source: dict, target: Path, text: str) -> None:
    """A TOC, stale copy, omitted page or falsely claimed coverage cannot satisfy this gate."""
    if Path(source['sourceRef']).suffix.lower() != '.pdf':
        return
    if frontmatter(text).get('sourceSha256') != source.get('sourceHashSha256'):
        raise ValueError('reviewed source hash mismatch; re-review preserved claims against current original')
    block, coverage = rendered_content(root, source, target)
    actual = re.search(re.escape(START) + r'.*?' + re.escape(END), text, re.S)
    if not actual or actual[0] != block or frontmatter(text).get('contentCoverage') != coverage:
        raise ValueError('reviewed-content-coverage: require current source-aligned page text, not only chapter links')


def _new_targets(root: Path, manifest: dict, args) -> dict[str, Path] | None:
    mapping, wiki = getattr(args, 'target_map', None), getattr(args, 'wiki', None)
    if not mapping and not wiki:
        return None
    if not mapping or not wiki:
        raise ValueError('new-source preparation requires both --wiki and --target-map')
    under(root, wiki, root/'user/knowledge/candidate')
    value = json.loads(read_text(under(root, mapping)))
    items = value.get('items', []) if isinstance(value, dict) else value
    if not isinstance(items, list) or not items:
        raise ValueError('target map requires a nonempty items list')
    targets, paths = {}, set()
    for item in items:
        identity = item['sourceId']
        target = under(root, item['target'], under(root, args.reviewed, root/'user/knowledge/reviewed'))
        if identity in targets or str(target).casefold() in paths or target.suffix.lower() != '.md':
            raise ValueError('duplicate or invalid preparation target')
        if target.exists():
            raise FileExistsError('new-source target exists; use existing-source repair mode')
        targets[identity] = target
        paths.add(str(target).casefold())
    if set(targets) != {s['id'] for s in manifest.get('sources', [])}:
        raise ValueError('target map must cover every manifest source exactly once')
    return targets


def _apply_extra(root: Path, source: dict, fm: dict, text: str, extra: dict, coverage: dict) -> tuple[dict, str]:
    if not extra:
        return fm, text
    if extra.get('normalizedHashSha256') != source['normalizedHashSha256']:
        raise ValueError('content profile normalized hash mismatch')
    if extra.get('sourceVersion'):
        if not isinstance(extra['sourceVersion'], dict):
            raise ValueError('sourceVersion must be a mapping')
        fm['sourceVersion'] = extra['sourceVersion']
    if extra.get('aliases'):
        if not isinstance(extra['aliases'], list) or any(not isinstance(x, str) for x in extra['aliases']):
            raise ValueError('aliases must be a list of strings')
        fm['aliases'] = list(dict.fromkeys(list_values(fm.get('aliases')) + extra['aliases']))
    if extra.get('secondarySources'):
        seen = set()
        for item in extra['secondarySources']:
            if any(not item.get(k) for k in ['sourceRef', 'sourceHashSha256', 'relationship', 'reviewedBy', 'evidence']):
                raise ValueError('secondary copy requires hash, relationship, reviewer and evidence')
            ref = item['sourceRef']
            if ref == source['sourceRef'] or ref in seen:
                raise ValueError('duplicate secondary source')
            if sha256_file(under(root, ref, root/'user/knowledge/raw')) != item['sourceHashSha256']:
                raise ValueError('secondary source hash mismatch')
            seen.add(ref)
        fm['secondarySources'] = extra['secondarySources']
        fm['dependsOn'] = list(dict.fromkeys(list_values(fm.get('dependsOn')) + [s['sourceRef'] for s in extra['secondarySources']]))
        trace = '\n'.join('- `' + item['sourceRef'] + '`（副本关系与校核证据见secondarySources）' for item in extra['secondarySources'])
        text = re.sub(r'(?m)^## Source Trace[ \t]*$', lambda m: m[0]+'\n\n'+trace, text, count=1)
    for section in extra.get('sections', []):
        if any(not section.get(k) for k in ['heading', 'text', 'reviewedBy', 'evidence', 'physicalPages']):
            raise ValueError('verified section requires reviewer, source evidence and physical pages')
        if any(type(p) is not int or p not in coverage['includedPages'] for p in section['physicalPages']):
            raise ValueError('verified section refers to absent physical page')
        if '\n' in section['heading'] or any(m in section['text'] for m in [START, END]):
            raise ValueError('verified sections cannot inject source block sentinels')
        text += '\n## '+section['heading']+'\n\n校核级别：'+section.get('verification', '来源条款审读，未声明整页校录')+'。\n\n'+section['text']+'\n\n出处：PDF物理第'+', '.join(map(str, section['physicalPages']))+'页；审核：'+section['reviewedBy']+'。'+section['evidence']+'\n'
    return fm, text


def run_prepare_reviewed_content(args) -> dict:
    root = Path(args.root).resolve()
    run = safe_run_id(args.run_id)
    manifest = json.loads(read_text(under(root, args.manifest)))
    profile = json.loads(read_text(under(root,args.content_profile))) if getattr(args,'content_profile',None) else {}
    profiles = {p['sourceHashSha256']:p for p in profile.get('sources',[])}
    if len(profiles) != len(profile.get('sources',[])) or set(profiles)-{s['sourceHashSha256'] for s in manifest.get('sources',[])}:
        raise ValueError('content profile contains duplicate or unknown source hashes')
    reviewed = under(root, args.reviewed, root/'user/knowledge/reviewed')
    new_targets = _new_targets(root, manifest, args)
    refs = {}
    for page in ([] if new_targets is not None else reviewed.rglob('*.md')):
        fm = frontmatter(read_text(page))
        if fm.get('knowledgeRole') != 'authoritative' or fm.get('authoritative') is not True:
            continue
        for ref in list_values(metadata(read_text(page)).get('sourceRefs')):
            refs.setdefault(ref, []).append(page)
    out = root/'user/knowledge/candidate'/run/'drafts'
    if out.exists():
        raise FileExistsError('draft preparation requires a new run id; preserve previous review evidence')
    planned = []
    for source in manifest.get('sources', []):
        if new_targets is not None:
            from .promotion import format_reviewed, source_issues
            issues = source_issues(root, {'sources': [source]})
            if issues:
                raise ValueError('; '.join(issues))
            target = new_targets[source['id']]
            text = format_reviewed(root, {'sources': [source]}, under(root, args.wiki), target,
                                   getattr(args, 'scope', 'user-private'), args.reviewer,
                                   '候选准备；晋升仍需完整审核与明确授权。', getattr(args, 'review_after', 'source-updated'))
        else:
            targets = refs.get(source['sourceRef'], [])
            if len(targets) != 1:
                raise ValueError('expected exactly one existing reviewed source page: ' + source['id'])
            target = targets[0]
            text = read_text(target)
        if frontmatter(text).get('sourceSha256') != source.get('sourceHashSha256'):
            raise ValueError('original changed or prior reviewed source hash missing; re-review preserved claims first')
        block, coverage = rendered_content(root, source, target)
        text = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\s*', '', text, flags=re.S)
        fm = frontmatter(text)
        fm.update(version='v1.2.0-retrievable-content', updatedAt=today(), contentCoverage=coverage)
        fm['review'] = {'reviewedBy': args.reviewer, 'reviewedAt': today(), 'decision': 'source-aligned-content-repair-reviewed-before-promotion'}
        fm, text = _apply_extra(root, source, fm, text, profiles.get(source['sourceHashSha256'], {}), coverage)
        if source.get('qualityState') == 'needs-review' and not re.search(r'(?m)^## (?:转换质量|Conversion Quality)\s*$', text):
            text += '\n## 转换质量\n\n来源包含OCR或图表转换。逐页文字对齐不等于全部语义已校核；未标记完整校录的表格、单位、数值和公式仍需按质量提示使用。\n'
        text = re.sub(r'\A\ufeff?---\n.*?\n---', lambda _: '---\n'+dump_mapping(fm)+'\n---', text, count=1, flags=re.S)
        for match in re.finditer(r'(?ms)^```yaml\n(.*?)^```',text):
            meta = load_mapping(match[1])
            if 'knowledgeId' in meta:
                meta.update(reviewedAt=today(),reviewedBy=args.reviewer,
                            reviewScope='来源哈希、逐页检索正文覆盖及标记的原页校录；未逐字校勘其他OCR、图表和公式。')
                if fm.get('secondarySources'):
                    meta['sourceRefs'] = list(dict.fromkeys(list_values(meta.get('sourceRefs')) + [s['sourceRef'] for s in fm['secondarySources']]))
                text=text[:match.start(1)]+dump_mapping(meta)+'\n'+text[match.end(1):]
                break
        text += '\n' + block + '\n'
        draft = out/target.name
        if any(existing[0] == draft for existing in planned):
            raise ValueError('reviewed draft basename collision; use separately scoped batches')
        planned.append((draft, text, {'sourceId': source['id'], 'target': rel(root, target), 'draft': rel(root, draft)}))
    if not planned:
        raise ValueError('manifest has no sources')
    for draft, text, _ in planned:
        write_text(draft, text)
    mapping = root/'var/rag'/run/'promotion-map.json'
    write_text(mapping, json.dumps({'items': [p[2] for p in planned]}, ensure_ascii=False, indent=2))
    result = {'state': 'candidate-prepared', 'sourceCount': len(planned), 'promotionMap': rel(root, mapping),
              'boundary': 'candidate-only-requires-content-review-and-promotion'}
    print_json(result)
    return result
