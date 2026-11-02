"""Inspect staged Python literals without mistaking expressions for credentials."""
import argparse
import ast
import json
import re
from pathlib import Path

PATH = re.compile(r'(?<![A-Za-z0-9_])[A-Za-z]:[\\/]+(?=[A-Za-z0-9_. $(){}\[\]-])')
SECRET_NAME = re.compile(r'.*(?:password|passwd|token|secret|api[_-]?key)', re.I)
TOKEN_FORMAT = re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bAKIA[A-Z0-9]{16}\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')


def scan_source(text):
    findings = []
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [{'code': 'python-syntax-error', 'line': exc.lineno}]
    def literal(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr) and all(isinstance(n, ast.Constant) and isinstance(n.value, str) for n in node.values):
            return ''.join(n.value for n in node.values)
        return None
    def credential(name, node):
        value = literal(node)
        if (SECRET_NAME.fullmatch(str(name)) and value and not value.strip().startswith('<')):
            findings.append({'code': 'credential-like-literal', 'line': node.lineno})
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if PATH.search(node.value):
                findings.append({'code': 'concrete-local-path', 'line': node.lineno})
            if TOKEN_FORMAT.search(node.value):
                findings.append({'code': 'credential-format', 'line': node.lineno})
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                if isinstance(target, ast.Name):
                    credential(target.id, node.value)
                elif isinstance(target, ast.Attribute):
                    credential(target.attr, node.value)
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                credential(literal(key), value)
        elif isinstance(node, ast.keyword):
            credential(node.arg, node.value)
    return findings


def main():
    parser = argparse.ArgumentParser(description='Read-only staged Python literal scan; never prints detected values')
    parser.add_argument('--path', required=True)
    args = parser.parse_args()
    findings = scan_source(Path(args.path).read_text(encoding='utf-8-sig'))
    print(json.dumps({'state': 'failed' if findings else 'passed', 'findings': findings}))
    return bool(findings)


if __name__ == '__main__':
    raise SystemExit(main())
