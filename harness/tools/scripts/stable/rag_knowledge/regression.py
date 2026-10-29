"""Frozen, known-case passage regression; never attest an entire agent turn."""
from __future__ import annotations

import json
import hashlib
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

from rag_candidate.common import read_text, write_text, sha256_file, safe_run_id, rel, print_json
from rag_candidate.pdf_normalize import under


def snapshot(root: Path, reviewed: Path) -> dict:
    return {rel(root, under(root, p, reviewed)): sha256_file(p) for p in sorted(reviewed.rglob('*.md'))}


def compact(value: str) -> str:
    return ''.join(value.split())


def validate_cases(root: Path, reviewed: Path, value, limit: int) -> list[dict]:
    cases = value.get('cases', []) if isinstance(value, dict) else value
    if not isinstance(cases, list) or not cases or not 1 <= limit <= 50:
        raise ValueError('regression requires a nonempty cases list and limit between 1 and 50')
    seen = set()
    for case in cases:
        identity = case.get('id', '')
        if not isinstance(identity, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', identity) or identity.casefold() in seen:
            raise ValueError('case IDs must be unique safe ASCII file names')
        seen.add(identity.casefold())
        if not isinstance(case.get('question'), str) or not case['question'].strip():
            raise ValueError('case question must be nonempty')
        case['target'] = rel(root, under(root, case['target'], reviewed))
        rank = case.get('maxRank', min(5, limit))
        if type(rank) is not int or not 1 <= rank <= limit:
            raise ValueError('case maxRank must be within query limit')
        for key in ['required', 'forbidden', 'tableRows', 'unpagedHeadings']:
            if not isinstance(case.get(key, []), list) or any(not isinstance(t, str) or not t.strip() for t in case.get(key, [])):
                raise ValueError(key + ' must contain nonempty strings')
        groups = case.get('requiredGroups', [])
        if not isinstance(groups, list) or any(not isinstance(g, list) or not g or any(not isinstance(t, str) or not t.strip() for t in g) for g in groups):
            raise ValueError('requiredGroups must contain nonempty string groups')
        if not isinstance(case.get('versionEquals', {}), dict):
            raise ValueError('versionEquals must be a mapping')
        if not isinstance(case.get('tableCells', []), list):
            raise ValueError('tableCells must be a list')
        for row in case.get('tableCells', []):
            if not isinstance(row, dict) or not row.get('label') or not isinstance(row.get('cells'), list) or any(not isinstance(c, str) for c in row['cells']):
                raise ValueError('tableCells row requires a label and string cells')
        if case.get('prefix') and not re.fullmatch(r'[A-Za-z]+(?:/[A-Za-z]+)?', case['prefix']):
            raise ValueError('invalid case source prefix')
        if case.get('kind') == 'substantive-question' and not any(case.get(k) for k in ['required', 'requiredGroups', 'tableRows', 'tableCells', 'versionEquals']):
            raise ValueError('substantive-question requires explicit content or version assertions')
    return cases


def check_case(root: Path, reviewed: Path, case: dict, query: dict, limit: int) -> dict:
    matches = query.get('matches', [])
    rank = next((i+1 for i, m in enumerate(matches) if m.get('page') == case['target']), None)
    match = next((m for m in matches if m.get('page') == case['target']), None)
    checks = [{'name': 'target-within-rank', 'passed': rank is not None and rank <= case.get('maxRank', min(5, limit))},
              {'name': 'substantive-reviewed-evidence', 'passed': bool(match and match.get('contentEvidence') == 'substantive-reviewed-text')}]
    citations = []
    if match:
        lines = read_text(under(root, match['page'], reviewed)).splitlines()
        sections = match.get('matchedSections', [])
        checks.append({'name': 'returned-passages-present', 'passed': bool(sections)})
        for section in sections:
            start, end = section.get('startLine'), section.get('endLine')
            valid = type(start) is int and type(end) is int and 1 <= start <= end <= len(lines)
            valid = valid and '\n'.join(lines[start-1:end]).strip() == section.get('excerpt', '').strip()
            if not valid:
                citations.append({'startLine': start, 'endLine': end})
        excerpt = '\n'.join(s.get('excerpt', '') for s in sections)
        body = compact(excerpt)
        for token in case.get('required', []) + case.get('tableRows', []):
            checks.append({'name': 'contains', 'expected': token, 'passed': compact(token) in body})
        for token in case.get('forbidden', []):
            checks.append({'name': 'excludes', 'expected': token, 'passed': compact(token) not in body})
        for group in case.get('requiredGroups', []):
            checks.append({'name': 'contains-one-of', 'expected': group, 'passed': any(compact(t) in body for t in group)})
        for row in case.get('tableCells', []):
            rows = [[c.strip() for c in line.strip().strip('|').split('|')] for line in excerpt.splitlines() if line.strip().startswith('|')]
            checks.append({'name': 'table-cells', 'expected': row, 'passed': any(cells == [row['label']] + row['cells'] for cells in rows)})
        version = match.get('documentVersion', {})
        for key, expected in case.get('versionEquals', {}).items():
            checks.append({'name': 'version-equals', 'field': key, 'expected': expected, 'passed': version.get(key) == expected})
        for heading in case.get('unpagedHeadings', []):
            selected = [s for s in sections if heading in s.get('localHeading', '')]
            checks.append({'name': 'synthesis-unpaged', 'heading': heading, 'passed': bool(selected) and all(not s.get('sourcePages') for s in selected)})
    return {'targetRank': rank, 'checks': checks, 'citationErrors': citations,
            'passed': bool(not citations and all(c['passed'] for c in checks))}


def query_worker(job: dict) -> dict:
    root, reviewed = Path(job['root']), Path(job['reviewed'])
    knowledge, events = root/'user/knowledge', []

    def guard(event, args):
        if event in {'socket.connect', 'socket.getaddrinfo', 'urllib.Request'}:
            events.append({'kind': 'denied-network', 'event': event})
            raise PermissionError('query worker forbids network access')
        if event != 'open' or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if not path.is_relative_to(knowledge):
            return
        mode, flags = args[1], args[2]
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool(flags & (os.O_WRONLY | os.O_RDWR))
        kind = 'denied-knowledge-write' if writing else ('reviewed-read' if path.is_relative_to(reviewed) else 'denied-non-reviewed-read')
        events.append({'kind': kind, 'path': rel(root, path)})
        if kind != 'reviewed-read':
            raise PermissionError('query worker forbids non-reviewed knowledge reads and all knowledge writes')

    sys.addaudithook(guard)
    try:
        from .commands import _query_reviewed
        query = _query_reviewed(root, Path(job['vault']), reviewed, Path(job['graph']), job['question'], job['limit'], job['asOf'], job.get('prefix'))
        query['mode'] = 'knowledge-only'
        return {'query': query, 'guard': {'scope': 'query-python-worker-only-not-whole-turn-proof', 'events': events}}
    except Exception as exc:
        return {'error': str(exc), 'guard': {'scope': 'query-python-worker-only-not-whole-turn-proof', 'events': events}}


def run_query_regression(args) -> dict:
    root = Path(args.root).resolve()
    reviewed = under(root, args.reviewed, root/'user/knowledge/reviewed')
    vault = under(root, args.vault, root/'user/knowledge')
    case_path = under(root, args.cases)
    raw_cases = case_path.read_bytes()
    cases = validate_cases(root, reviewed, json.loads(raw_cases.decode('utf-8-sig')), args.limit)
    before = snapshot(root, reviewed)
    if not before:
        raise ValueError('reviewed snapshot is empty')
    output = root/'var/rag'/safe_run_id(args.run_id)/'query-regression'
    output.mkdir(parents=True, exist_ok=False)
    (output/'cases-input.json').write_bytes(raw_cases)
    write_text(output/'baseline.json', json.dumps({'reviewed': before, 'casesHashSha256': hashlib.sha256(raw_cases).hexdigest()}, ensure_ascii=False, indent=2))
    graph = under(root, args.graph, root/'var/rag') if args.graph else root/'var/rag/reviewed-knowledge/graph/graph.json'
    env = os.environ.copy()
    stable = str(Path(__file__).resolve().parents[1])
    env.update(PYTHONUTF8='1', PYTHONPATH=stable + (os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else ''))
    results = []
    for case in cases:
        job = {'root': str(root), 'reviewed': str(reviewed), 'vault': str(vault), 'graph': str(graph),
               'question': case['question'], 'prefix': case.get('prefix'), 'asOf': args.as_of, 'limit': args.limit}
        job_path = output/(case['id']+'-job.json')
        write_text(job_path, json.dumps(job, ensure_ascii=False))
        start = time.perf_counter()
        try:
            process = subprocess.run([sys.executable, '-m', 'rag_knowledge.regression', '--worker', str(job_path)],
                                     cwd=root, env=env, capture_output=True, encoding='utf-8', timeout=args.timeout)
            packet = json.loads(process.stdout.lstrip('\ufeff')) if process.returncode == 0 else {'error': 'query worker exited nonzero'}
        except (subprocess.TimeoutExpired, ValueError) as exc:
            packet = {'error': type(exc).__name__}
        elapsed = round(time.perf_counter()-start, 4)
        query, guard = packet.get('query', {}), packet.get('guard', {})
        write_text(output/(case['id']+'-query.json'), json.dumps(query, ensure_ascii=False, indent=2))
        write_text(output/(case['id']+'-guard.json'), json.dumps(guard, ensure_ascii=False, indent=2))
        try:
            checked = check_case(root, reviewed, case, query, args.limit)
        except (OSError, ValueError) as exc:
            checked = {'passed': False, 'targetRank': None, 'checks': [{'name': 'citation-file-readable', 'passed': False}], 'citationErrors': [type(exc).__name__]}
        events = guard.get('events', [])
        denied = [e for e in events if e['kind'] != 'reviewed-read']
        checked.update(id=case['id'], question=case['question'], kind=case.get('kind', 'source-discovery'),
                       target=case['target'], elapsedSeconds=elapsed, guardRecorded=bool(events), deniedEvents=denied,
                       reviewedReadEvents=len(events), error=packet.get('error'))
        checked['passed'] = bool(checked['passed'] and events and not denied and not packet.get('error'))
        results.append(checked)
        write_text(output/'results-in-progress.json', json.dumps(results, ensure_ascii=False, indent=2))
    after = snapshot(root, reviewed)
    changed = sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))
    cases_changed = not case_path.is_file() or case_path.read_bytes() != raw_cases
    passed = not changed and not cases_changed and all(c['passed'] for c in results)
    times = [c['elapsedSeconds'] for c in results]
    result = {'state': 'passed' if passed else 'failed', 'scope': 'post-construction-known-case-query-regression',
              'caseCount': len(results), 'passedCount': sum(c['passed'] for c in results), 'results': results,
              'reviewedFrozenCount': len(before), 'reviewedChanged': changed, 'casesChanged': cases_changed,
              'casesInputHashSha256': sha256_file(output/'cases-input.json'),
              'seconds': {'min': min(times), 'median': statistics.median(times), 'max': max(times)},
              'coverageAssurance': 'query-python-worker-only-not-whole-turn-proof',
              'semanticAssurance': 'assertions-and-citations-only-human-answer-review-required',
              'report': rel(root, output/'summary.json')}
    write_text(output/'summary.json', json.dumps(result, ensure_ascii=False, indent=2))
    print_json(result)
    if not passed:
        raise ValueError('query regression failed; preserve this run and use a new run id for corrections')
    return result


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != '--worker':
        raise SystemExit('Use the stable query-regression command facade.')
    print_json(query_worker(json.loads(read_text(Path(sys.argv[2])))))
