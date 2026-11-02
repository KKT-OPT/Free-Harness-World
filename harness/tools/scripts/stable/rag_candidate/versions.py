"""Read-only metadata inventory and review signals; never decide legal precedence."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from .common import read_text, rel, write_text, sha256_file, safe_run_id
from .metadata import frontmatter
from .pdf_normalize import under


def audit_versions(root, reviewed, as_of):
    date.fromisoformat(as_of)
    rows, issues, groups = [], [], defaultdict(list)
    for page in sorted(reviewed.rglob('*.md')):
        text = read_text(page)
        fm = frontmatter(text)
        if fm.get('knowledgeRole') != 'authoritative' or fm.get('authoritative') is not True or not fm.get('sourceSha256'):
            continue
        ref, value, errors, warnings = rel(root,page), fm.get('sourceVersion'), [], []
        if not isinstance(value, dict) or not value:
            value = {}
            errors.append('missing-sourceVersion')
        for key in ['publishedOn', 'effectiveOn', 'officialStatus', 'sourceDocumentState']:
            if key not in value:
                errors.append('missing-version-field:'+key)
        for key in ['issuedOn', 'publishedOn', 'effectiveOn', 'statusVerifiedOn']:
            raw = value.get(key)
            if raw is not None:
                try:
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(raw)):
                        raise ValueError('invalid ISO date')
                    date.fromisoformat(str(raw))
                except ValueError:
                    errors.append('invalid-date:'+key)
        if value.get('officialStatus') in {'current', 'upcoming'} and not value.get('statusVerifiedOn'):
            errors.append('official-status-without-verification-date')
        if value.get('statusVerifiedOn') and str(value['statusVerifiedOn']) > as_of:
            errors.append('verification-date-after-as-of')
        if not value.get('publishedOn'):
            warnings.append('publication-date-unknown-do-not-infer-from-filename')
        state = str(value.get('sourceDocumentState') or '')
        if 'draft' in state:
            warnings.append('draft-not-a-formal-version')
        if 'translation' in state:
            warnings.append('translation-language-boundary')
        effective = str(value.get('effectiveOn') or '')
        temporal = 'date-unknown'
        if effective and 'invalid-date:effectiveOn' not in errors:
            temporal = 'not-yet-effective' if effective > as_of else 'effective-date-reached-not-current-status-proof'
        if value.get('publishedOn') and 'invalid-date:publishedOn' not in errors and str(value['publishedOn']) > as_of:
            temporal = 'not-yet-published'
        if value.get('publishedOn') and effective and str(value['publishedOn']) > effective:
            warnings.append('effective-before-publication-review-explicit-conditions')
        identifier = str(value.get('standardId') or '')
        match = re.fullmatch(r'([A-Za-z]+(?:/[A-Za-z]+)?\s*\d+(?:\.\d+)*)\s*[—-]\s*(\d{4})', identifier)
        if match:
            groups[re.sub(r'\s+', '', match[1]).upper()].append(ref)
        if errors:
            issues.append({'page': ref, 'issues': errors})
        rows.append({'page': ref, 'sha256': sha256_file(page), 'sourceVersion': value,
                     'temporalState': temporal, 'issues': errors, 'warnings': warnings})
    if not rows:
        issues.append({'issues': ['no-source-pages-with-sourceSha256-in-explicit-scope']})
    return {'state': 'failed' if issues else 'passed', 'scope': 'reviewed-source-version-metadata-audit',
            'asOf': as_of, 'sourceCount': len(rows), 'issues': issues, 'sources': rows,
            'counts': {'publicationDateUnknown': sum(not r['sourceVersion'].get('publishedOn') for r in rows),
                       'states': dict(Counter(r['sourceVersion'].get('sourceDocumentState', 'unknown') for r in rows))},
            'versionReviewGroups': [{'identifierFamily': k, 'pages': v} for k,v in groups.items() if len(v)>1],
            'assurance': 'metadata-and-version-review-signals-only-not-semantic-conflict-or-current-legal-status-proof',
            'selectionBoundary': 'scope-and-subject-before-user-defined-precedence; no-global-law-or-standard-priority-hardcoded'}


def run_audit_versions(args):
    root = Path(args.root).resolve()
    reviewed = under(root, args.reviewed, root/'user/knowledge/reviewed')
    result = audit_versions(root, reviewed, args.as_of)
    output = root/'var/rag'/safe_run_id(args.run_id)/'version-audit.json'
    if output.exists():
        raise FileExistsError('version audit requires a new run id')
    result['report'] = rel(root,output)
    write_text(output, json.dumps(result, ensure_ascii=False, indent=2, default=str))
    if result['issues']:
        from .common import print_json
        print_json(result)
        raise ValueError('version metadata audit failed; preserve report and repair source-bound candidates')
    return result
