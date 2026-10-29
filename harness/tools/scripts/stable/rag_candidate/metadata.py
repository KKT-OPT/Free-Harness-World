"""Shared Markdown metadata parsing; no dependence on list indentation or YAML wrapping."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from copy import deepcopy
from datetime import date, datetime

import yaml


class _UniqueLoader(yaml.SafeLoader):
    pass


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def load_mapping(text: str) -> dict:
    value = yaml.load(text, Loader=_UniqueLoader)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("Markdown metadata must be a YAML mapping")
    return value


@lru_cache(maxsize=512)
def _frontmatter(text: str) -> dict:
    match = re.match(r"\A\ufeff?---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    return load_mapping(match[1]) if match else {}


def frontmatter(text: str) -> dict:
    return deepcopy(_frontmatter(text))


@lru_cache(maxsize=512)
def _metadata(text: str) -> dict:
    """Fenced knowledge metadata overrides display frontmatter (e.g. scalar scope)."""
    result = dict(_frontmatter(text))
    for match in re.finditer(r"(?ms)^```ya?ml[ \t]*\r?\n(.*?)^```[ \t]*\r?$", text):
        block = load_mapping(match[1])
        if any(key in block for key in ("knowledgeId", "sourceRefs", "reviewedBy")):
            result.update(block)
    return result


def metadata(text: str) -> dict:
    return deepcopy(_metadata(text))


def scalar(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value).strip() or None


def list_values(value) -> list[str]:
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    return list(dict.fromkeys(str(item).strip() for item in values if item is not None and str(item).strip()))


class _IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def dump_mapping(value: dict) -> str:
    return yaml.dump(value, Dumper=_IndentedDumper, allow_unicode=True, sort_keys=False, width=20000).strip()
