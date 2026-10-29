"""Deterministic passage retrieval from reviewed Markdown only, with explicit date context."""
from __future__ import annotations

import math
import re
import json
from collections import Counter
from datetime import date
from pathlib import Path

from rag_candidate.common import read_text, rel
from rag_candidate.metadata import frontmatter, scalar


def source_matches(text: str, prefix: str | None) -> bool:
    """Match a declared identifier family, never infer facts from document year."""
    if not prefix:
        return True
    if not re.fullmatch(r'[A-Za-z]+(?:/[A-Za-z]+)?', prefix):
        raise ValueError('source prefix must be an ASCII identifier family')
    fm = frontmatter(text)
    title = next((line[2:] for line in text.splitlines() if line.startswith('# ')), '')
    identifier = str((fm.get('sourceVersion') or {}).get('standardId') or fm.get('sourceIdentifier') or title)
    match = re.match(r'^([A-Za-z]+(?:/[A-Za-z]+)?)\s*-?\s*\d', identifier.strip())
    family = match[1].upper() if match else ''
    requested = prefix.upper()
    return family == requested or family.startswith(requested + '/')


def _line_context(lines: list[str]) -> list[tuple[int | None, str]]:
    result, page, state, fence = [], None, 'reviewed-text', False
    for i, line in enumerate(lines):
        if line.startswith(('```', '~~~')):
            fence = not fence
        physical = re.fullmatch(r'#{1,6}\s+PDF 第 (\d+) 页\s*', line) if not fence else None
        if physical:
            page = int(physical[1])
            state = ('visual-verified' if '校核级别：原页完整校录' in '\n'.join(lines[i+1:i+4])
                     else 'source-aligned-not-exhaustive')
        result.append((page, state))
    return result


def passages(text: str) -> list[dict]:
    lines = text.splitlines()
    contexts = _line_context(lines)
    start = 0
    if lines and lines[0].lstrip('\ufeff') == '---':
        start = next((i+1 for i in range(1, len(lines)) if lines[i] == '---'), len(lines))
    sections, stack, buffer, first, fence = [], [], [], start+1, False

    def flush():
        raw_body = '\n'.join(buffer)
        body = raw_body.strip()
        if not body:
            return
        heading = ' / '.join(item[1] for item in stack)
        if stack and stack[-1][1] in {'元数据', 'Source Trace', 'Governance Notes', 'Staleness'}:
            return
        # Bound passages by paragraphs, preserving small tables and complete lists.
        chunks, chunk_start, chunk_end = [], None, None
        for paragraph in re.finditer(r'\S.*?(?=\n[ \t]*\n|\Z)', body, re.S):
            if chunk_start is not None and paragraph.end()-chunk_start>1800:
                chunks.append((chunk_start,chunk_end))
                chunk_start = None
            if chunk_start is None:
                chunk_start = paragraph.start()
            chunk_end = paragraph.end()
        if chunk_start is not None:
            chunks.append((chunk_start,chunk_end))
        body_offset = first + raw_body[:raw_body.find(body)].count('\n')
        for begin,end in chunks:
            chunk = body[begin:end]
            offset = body_offset + body[:begin].count('\n')
            if len(chunk.strip()) < 25:
                continue
            end_line = offset + chunk.count('\n')
            context = contexts[offset-1:end_line]
            source_pages = sorted({p for p, _ in context if p is not None})
            states = {state for p, state in context if p is not None}
            verification = 'reviewed-text'
            if states:
                verification = 'visual-verified' if states == {'visual-verified'} else 'source-aligned-not-exhaustive'
            elif '校核级别：原页完整校录' in chunk:
                verification = 'visual-verified'
            sections.append({'heading': heading, 'text': chunk, 'startLine': offset,
                             'localHeading': stack[-1][1] if stack else 'document',
                             'endLine': end_line, 'sourcePage': source_pages[0] if source_pages else None,
                             'sourcePages': source_pages, 'verification': verification,
                             'navigation': chunk.count('](<')>=3 or chunk.count('](')>=3})

    for i in range(start, len(lines)):
        line = lines[i]
        if line.startswith('```') or line.startswith('~~~'):
            fence = not fence
        heading = re.match(r'^(#{1,6})\s+(.+)', line) if not fence else None
        if heading:
            physical = re.fullmatch(r'PDF 第 (\d+) 页', heading[2].strip())
            # A physical page break cannot terminate a numbered logical clause.
            if physical and stack and re.match(r'^\d+(?:\.\d+)*\s*\D', stack[-1][1]):
                buffer.append(line)
                continue
            flush()
            buffer = []
            first = i+2
            level, title = len(heading[1]), heading[2].strip()
            stack = [item for item in stack if item[0] < level] + [(level, title)]
        else:
            buffer.append(line)
    flush()
    return sections


def version_context(fm: dict, as_of: str) -> dict:
    value = json.loads(json.dumps(fm.get('sourceVersion') or {}, default=str))
    effective = str(value.get('effectiveOn') or '')
    published = str(value.get('publishedOn') or '')
    if effective:
        date.fromisoformat(effective)
    if published:
        date.fromisoformat(published)
    temporal = 'not-yet-effective' if effective and effective > as_of else 'date-unknown'
    if effective and effective <= as_of:
        temporal = 'effective-date-reached-status-needs-verification'
        if value.get('officialStatus') == 'current':
            temporal = 'current-as-last-verified'
    if published and published > as_of:
        temporal = 'not-yet-published'
    return {**value, 'asOf': as_of, 'temporalState': temporal,
            'selectionRule': 'same-subject-scope-and-replacement-before-recency; reviewedAt-is-not-effectiveOn'}


def rank_pages(root: Path, vault: Path, pages: list[Path], terms: list[str], as_of: str) -> dict:
    date.fromisoformat(as_of)
    docs = []
    frequency = Counter()
    for path in pages:
        text = read_text(path)
        fm = frontmatter(text)
        title = next((line[2:].strip() for line in text.splitlines() if line.startswith('# ')), path.stem)
        chunks = passages(text)
        searchable = '\n'.join(p['heading']+'\n'+p['text'] for p in chunks).lower()
        frequency.update(term for term in terms if term.lower() in searchable)
        docs.append((path, text, fm, title, chunks))
    weights = {term: math.log(1+(len(docs)-frequency[term]+.5)/(frequency[term]+.5)) for term in terms}
    scored = {}
    for path, text, fm, title, chunks in docs:
        ranked = []
        for chunk in chunks:
            body, heading = chunk['text'].lower(), chunk['localHeading'].lower()
            score, matched = 0., []
            for term in terms:
                token = term.lower()
                hits = body.count(token)
                head = token in heading
                if not hits and not head:
                    continue
                matched.append(term)
                # Saturated term frequency avoids rewarding long boilerplate/fulltext.
                score += weights[term]*(hits/(hits+1.2) if hits else 0)
                if head:
                    score += weights[term]*16
                if len(term)>=3:
                    score += weights[term]*min(len(term),12)*(2 if head else 1)
            if not matched:
                continue
            if chunk['navigation']:
                score *= .12
            ranked.append({**chunk, 'score': round(score,4), 'matchedTerms': matched})
        ranked.sort(key=lambda p: (-p['score'], p['startLine']))
        if not ranked:
            continue
        best = ranked[0]
        score = best['score'] + sum(min(p['score'],best['score'])*.02 for p in ranked[1:4])
        score += sum(weights[t]*.35 for t in terms if t.lower() in title.lower())
        scope = '\n'.join(p['text'] for p in chunks if p['localHeading'] in {'Statement','Applicability'}).lower()
        score += sum(weights[t]*2 for t in terms if t.lower() in scope)
        selected = ranked[:5]
        # Include a directly matching data table instead of five definitions or navigation snippets.
        tables = [p for p in ranked if not p['navigation'] and re.search(r'(?m)^\|.*\d.*\|',p['text'])
                  and any(t.lower() in p['text'].lower() for t in terms)]
        if tables and tables[0] not in selected:
            selected = selected[:4] + [tables[0]]
        scored[path] = {'page': rel(root,path), 'vaultPath':rel(vault,path), 'title':title,
                        'score':round(score,3), 'reason':['reviewed-passage-match'],
                        'reviewedAt':scalar(fm.get('review',{}).get('reviewedAt') or fm.get('reviewedAt')),
                        'reviewedBy':scalar(fm.get('review',{}).get('reviewedBy') or fm.get('reviewedBy')),
                        'documentVersion':version_context(fm,as_of),
                        'contentEvidence':'navigation-only' if best['navigation'] else 'substantive-reviewed-text',
                        'matchedSections':[{**{k:v for k,v in p.items() if k not in {'text','navigation'}},
                                            'excerpt':p['text']} for p in selected],
                        'wikilinks':sorted(set(re.findall(r'\[\[([^\]]+)\]\]',text)))[:20]}
    return scored
