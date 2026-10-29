"""Validate a supplied whole-turn evidence record; never claim runtime attestation."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from urllib.parse import urlparse

from rag_candidate.common import read_text, write_text, sha256_file, print_json, rel, safe_run_id
from rag_candidate.metadata import frontmatter
from rag_candidate.pdf_normalize import under

LOCAL_EVENTS = {'knowledge-query', 'reviewed-read', 'guidance-read', 'evidence-write', 'local-check'}
EXTERNAL_EVENTS = {'web-search', 'web-open', 'external-status-check', 'raw-read', 'image-read'}


def audit_record(root: Path, record: dict) -> dict:
    if record.get('schemaVersion', 'harness.queryEvaluationRecord.v1') != 'harness.queryEvaluationRecord.v1':
        raise ValueError('unsupported query evaluation record schema')
    mode = record.get('mode')
    if mode not in {'knowledge-only', 'mixed'}:
        raise ValueError('evaluation mode must be knowledge-only or mixed')
    issues, incomplete = [], []
    if not record.get('question') or not record.get('reviewer'):
        incomplete.append('question and reviewer are required')
    trace = record.get('trace') or {}
    if trace.get('scope') != 'whole-turn' or trace.get('complete') is not True:
        incomplete.append('a local file guard is not a complete whole-turn trace')
    if trace.get('capturedBy') not in {'runtime-export', 'reviewer-audited'}:
        incomplete.append('agent declarations alone do not establish whole-turn coverage')
    events = trace.get('events') or []
    if not events:
        incomplete.append('tool events are required')
    external = []
    for event in events:
        kind = event.get('kind')
        if kind in EXTERNAL_EVENTS:
            external.append(kind)
        elif kind not in LOCAL_EVENTS:
            incomplete.append('unclassified tool event')
        if kind in {'reviewed-read', 'raw-read', 'image-read'} and event.get('path'):
            try:
                under(root, event['path'], root/'user/knowledge/reviewed')
            except ValueError:
                if mode == 'knowledge-only':
                    issues.append('answer-source read outside reviewed boundary')
    if mode == 'knowledge-only' and external:
        issues.append('external retrieval invalidates knowledge-only evaluation, including metadata verification')
    evidence = record.get('evidence') or []
    if not evidence:
        incomplete.append('answer evidence is required')
    seen = set()
    for item in evidence:
        identity = item.get('id')
        if not identity or identity in seen:
            issues.append('evidence IDs must be present and unique')
        seen.add(identity)
        if item.get('kind') == 'reviewed':
            try:
                path = under(root, item['path'], root/'user/knowledge/reviewed')
                content = path.read_bytes()
                text = content.decode('utf-8-sig')
                fm = frontmatter(text)
                if fm.get('authoritative') is not True or fm.get('knowledgeRole') != 'authoritative':
                    raise ValueError('answer evidence must be an authoritative reviewed source page')
                if hashlib.sha256(content).hexdigest() != item.get('sha256'):
                    raise ValueError('reviewed evidence hash changed')
                first, last = item['startLine'], item['endLine']
                if type(first) is not int or type(last) is not int or not 1 <= first <= last <= len(text.splitlines()):
                    raise ValueError('invalid reviewed citation lines')
            except (ValueError, KeyError, OSError) as exc:
                issues.append(str(exc))
        elif item.get('kind') == 'web':
            if mode == 'knowledge-only':
                issues.append('web evidence cannot support a knowledge-only answer')
            parsed = urlparse(item.get('url', ''))
            if parsed.scheme not in {'https', 'http'} or not parsed.netloc:
                issues.append('web evidence requires an explicit URL; this command never opens it')
        else:
            issues.append('unsupported answer evidence kind')
    for inference in record.get('inferences', []):
        premises = inference.get('premiseEvidenceIds') or []
        if not inference.get('statement') or not premises or any(p not in seen for p in premises):
            issues.append('inference must cite available evidence; reasoning cannot fill missing facts')
    if record.get('assessment') not in {'passed', 'failed', 'incomplete'}:
        incomplete.append('an explicit answer assessment is required')
    if issues:
        state = 'invalid'
    elif incomplete:
        state = 'inconclusive'
    elif mode == 'mixed':
        state = 'mixed-usage-recorded'
    else:
        state = record['assessment']
    return {'schemaVersion': 'harness.queryEvaluationAudit.v1', 'state': state, 'mode': mode,
            'answerAssessment': record.get('assessment'),
            'knowledgeOnlyAcceptance': state == 'passed' and mode == 'knowledge-only',
            'externalEvents': external, 'blockingIssues': issues, 'incompleteEvidence': incomplete,
            'coverageAssurance': 'supplied-record-validation-not-runtime-attestation',
            'semanticAssurance': 'reviewer-assessed-not-proven-by-citation-checks',
            'boundary': 'no-network-no-promotion-no-knowledge-write'}


def run_audit_query_evaluation(args) -> dict:
    root = Path(args.root).resolve()
    record_path = under(root, args.evaluation_record, root/'var')
    result = audit_record(root, json.loads(read_text(record_path)))
    run = safe_run_id(args.run_id)
    report = under(root, args.report, root/'var') if args.report else root/'var/rag'/run/'query-evaluation-audit.json'
    if report.resolve() == record_path.resolve():
        raise ValueError('audit report must not overwrite the evaluation input record')
    result.update(record=rel(root, record_path), recordHashSha256=sha256_file(record_path), report=rel(root,report))
    write_text(report, json.dumps(result, ensure_ascii=False, indent=2))
    print_json(result)
    if result['state'] not in {'passed', 'mixed-usage-recorded'}:
        raise ValueError('query evaluation audit did not pass; inspect the preserved report state')
    return result
