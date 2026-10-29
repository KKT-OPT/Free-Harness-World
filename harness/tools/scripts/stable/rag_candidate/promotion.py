"""Source-bound promotion: validate the reviewed bytes, then write and seal those bytes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from pathlib import Path

from .common import read_text, write_text, rel, sha256_file, sha256_text, today, update_status, print_json, safe_run_id
from .metadata import frontmatter, metadata, list_values, dump_mapping
from .pdf_normalize import under


REQUIRED_SECTIONS = ("Statement", "Source Overview", "Core Framework", "Applicability", "Non-Applicability",
                     "Key Concepts", "Source Trace", "Staleness", "Governance Notes")


def source_issues(root: Path, manifest: dict) -> list[str]:
    issues = []
    ids = [source.get("id") for source in manifest.get("sources", [])]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        issues.append("manifest source IDs must be present and unique")
    if manifest.get("blockedSources"):
        issues.append("manifest contains blocked inputs; resolve or explicitly scope a separate corpus")
    for source in manifest.get("sources", []):
        for ref_key, hash_key in (("sourceRef", "sourceHashSha256"), ("normalizedMarkdown", "normalizedHashSha256"),
                                  ("normalizationManifest", "normalizationManifestHashSha256")):
            value = source.get(ref_key)
            if not value:
                continue
            try:
                path = under(root, value)
                if not path.is_file():
                    issues.append(f"missing {ref_key}: {value}")
                elif source.get(hash_key) and sha256_file(path) != source[hash_key]:
                    issues.append(f"changed {ref_key}: {value}")
            except ValueError:
                issues.append(f"source reference escapes root: {value}")
        if not source.get("sourceRef") or not source.get("sourceHashSha256"):
            issues.append("source must have a path and hash")
        if source.get("candidatePage"):
            candidate = under(root, source["candidatePage"])
            if candidate.is_file():
                fm = frontmatter(read_text(candidate))
                if fm.get("source_file") != source.get("sourceRef"):
                    issues.append("candidate source does not match manifest: " + source["id"])
                if fm.get("extracted_file") != source.get("extractedMarkdown"):
                    issues.append("candidate normalized reference does not match manifest: " + source["id"])
            else:
                issues.append("candidate source page missing: " + source["id"])
    return issues


def bindings_from_args(root: Path, manifest: dict, args) -> list[dict]:
    mapping = getattr(args, "promotion_map", None)
    if mapping:
        value = json.loads(read_text(under(root, mapping)))
        bindings = value.get("items", []) if isinstance(value, dict) else value
        if not isinstance(bindings, list) or not bindings:
            raise ValueError("promotion map requires a nonempty items list")
    elif getattr(args, "reviewed_draft", None):
        sources = manifest.get("sources", [])
        source_id = getattr(args, "source_id", None)
        if not source_id and len(sources) != 1:
            raise ValueError("a reviewed draft for multiple sources requires --source-id")
        source_id = source_id or sources[0]["id"]
        draft = under(root, args.reviewed_draft, root / "user/knowledge/candidate")
        target = getattr(args, "target", None) or frontmatter(read_text(draft)).get("documentName")
        bindings = [{"sourceId": source_id, "draft": rel(root, draft), "target": target}]
    else:
        return []
    source_ids = {source["id"] for source in manifest.get("sources", [])}
    seen_sources, seen_targets = set(), set()
    clean = []
    for item in bindings:
        source_id = item.get("sourceId")
        if source_id not in source_ids or source_id in seen_sources:
            raise ValueError("unknown or duplicate promotion source id")
        draft = under(root, item["draft"], root / "user/knowledge/candidate")
        target = under(root, item["target"], root / "user/knowledge/reviewed")
        if target.suffix.lower() != ".md" or str(target).casefold() in seen_targets:
            raise ValueError("duplicate or invalid promotion target")
        if not draft.is_file():
            raise ValueError("reviewed draft missing")
        seen_sources.add(source_id)
        seen_targets.add(str(target).casefold())
        clean.append({"sourceId": source_id, "draft": rel(root, draft), "target": rel(root, target)})
    return clean


def review_snapshot(root: Path, manifest_path: Path, wiki: Path, bindings: list[dict]) -> str:
    manifest = json.loads(read_text(manifest_path))
    files = {manifest_path, *wiki.rglob("*.md")}
    for source in manifest.get("sources", []):
        for key in ("sourceRef", "normalizedMarkdown", "normalizationManifest"):
            if source.get(key):
                files.add(under(root, source[key]))
    for item in bindings:
        draft = under(root, item["draft"])
        files.add(draft)
        # Secondary copies are review inputs too, not just documentary links.
        for ref in list_values(metadata(read_text(draft)).get('sourceRefs')):
            files.add(under(root, ref))
    material = {"bindings": bindings, "files": sorted((rel(root, path), sha256_file(path) if path.is_file() else "missing") for path in files)}
    return sha256_text(json.dumps(material, sort_keys=True, ensure_ascii=False))


def _section(text: str, title: str) -> str:
    match = re.search(r"(?ms)^## " + re.escape(title) + r"\s*\n(.*?)(?=^## |\Z)", text)
    return match[1].strip() if match else ""


def format_reviewed(root, manifest, wiki, target, scope, reviewer, approval_note, review_after, **_) -> str:
    """Generic content comes exclusively from the selected candidate, never its topic name."""
    if len(manifest.get("sources", [])) != 1:
        raise ValueError("formatting requires exactly one selected source")
    source = manifest["sources"][0]
    candidate = read_text(under(root, source["candidatePage"]))
    title = frontmatter(candidate).get("title") or source["id"]
    statement = _section(candidate, "Candidate Summary")
    overview = _section(candidate, "Source Overview") or statement
    framework = _section(candidate, "Core Framework") or _section(candidate, "Key Claims")
    if not statement or not framework or "Agent review required" in statement:
        raise ValueError("candidate lacks a source-grounded summary/framework; provide an enriched candidate or reviewed draft")
    domain = target.relative_to(root / "user/knowledge/reviewed").parts[0]
    refs = [source["sourceRef"], source.get("normalizedMarkdown") or source.get("extractedMarkdown")]
    refs = list(dict.fromkeys(ref for ref in refs if ref))
    fm = {"documentName": rel(root, target), "version": "v1.0.0-reviewed", "updatedAt": today(), "status": "active",
          "knowledgeRole": "authoritative", "authoritative": True, "tags": list_values(frontmatter(candidate).get("tags")),
          "purpose": f"整理{title}的来源知识、方法与适用边界。", "scope": ["reviewed-knowledge", scope, domain],
          "prerequisites": ["harness/governance/KnowledgePromotionPolicy.md"], "relatedDocuments": ["harness/rag/RAGIndex.md"],
          "outputTo": [rel(root, target)], "owner": "user", "reviewAfter": review_after, "supersededBy": None, "dependsOn": refs,
          "review": {"reviewedBy": reviewer, "reviewedAt": today(), "decision": "user-authorized-promotion"}}
    meta = {"knowledgeId": target.stem, "domain": domain, "scope": scope, "projectId": None,
            "sourceRefs": refs, "reviewedBy": reviewer, "reviewedAt": today(), "reviewAfter": review_after,
            "approvalNote": approval_note, "sensitiveRisk": "low", "storageBoundary": f"user/knowledge/reviewed/{domain}"}
    parts = ["---\n" + dump_mapping(fm) + "\n---", "# " + str(title), "## 元数据\n\n```yaml\n" + dump_mapping(meta) + "\n```"]
    sections = {"Statement": statement, "Source Overview": overview, "Core Framework": framework,
                "Applicability": _section(candidate, "Applicability"), "Non-Applicability": _section(candidate, "Non-Applicability"),
                "Key Concepts": _section(candidate, "Key Concepts") or _section(candidate, "Core Concepts") or _section(candidate, "Key Claims"),
                "Source Trace": "\n".join("- `" + ref + "`" for ref in refs),
                "Staleness": f"原件更新、发生冲突或到 `{review_after}` 时重新审核。",
                "Governance Notes": "本页由已补全候选按明确授权晋升。候选、图和运行态报告仍属证据；不推断公开再分发许可。"}
    for name, content in sections.items():
        if not content:
            raise ValueError(f"candidate missing substantive section: {name}")
        parts.append(f"## {name}\n\n{content}")
    if Path(source['sourceRef']).suffix.lower() == '.pdf':
        from .reviewed_content import rendered_content
        block, coverage = rendered_content(root, source, target)
        fm['contentCoverage'] = coverage
        fm['sourceSha256'] = source['sourceHashSha256']
        parts[0] = '---\n' + dump_mapping(fm) + '\n---'
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def validate_draft(root: Path, source: dict, target: Path, text: str) -> None:
    fm, meta = frontmatter(text), metadata(text)
    if fm.get("documentName") != rel(root, target) or fm.get("knowledgeRole") != "authoritative" or fm.get("authoritative") is not True:
        raise ValueError("draft identity/authoritative metadata does not match target")
    if fm.get("status") != "active" or not list_values(fm.get("tags")):
        raise ValueError("draft requires active status and tags")
    for key in ("version", "updatedAt", "purpose", "scope", "prerequisites", "relatedDocuments", "outputTo", "owner", "reviewAfter", "supersededBy", "dependsOn", "review"):
        if key not in fm:
            raise ValueError(f"draft frontmatter missing {key}")
    for section in REQUIRED_SECTIONS:
        if len(_section(text, section)) < 15:
            raise ValueError("draft missing or empty section: " + section)
    if "\ufffd" in text or "Agent review required" in text:
        raise ValueError("draft contains replacement characters or scaffold text")
    refs = list_values(meta.get("sourceRefs"))
    expected = {source["sourceRef"], source.get("normalizedMarkdown") or source.get("extractedMarkdown")}
    if not expected.issubset(set(refs)):
        raise ValueError("draft does not trace to the selected raw and normalized source")
    for ref in refs:
        if ref.startswith("var/"):
            raise ValueError("runtime paths cannot be reviewed sourceRefs")
        path = under(root, ref)
        if not path.exists():
            raise ValueError("draft sourceRef missing: " + ref)
    secondary = fm.get('secondarySources') or []
    if not isinstance(secondary, list):
        raise ValueError('secondarySources must be a list')
    seen = set()
    for item in secondary:
        ref = item.get('sourceRef')
        if not ref or ref == source['sourceRef'] or ref in seen or ref not in refs:
            raise ValueError('secondary source must be unique and included in sourceRefs')
        path = under(root, ref, root/'user/knowledge/raw')
        if not item.get('sourceHashSha256') or sha256_file(path) != item['sourceHashSha256']:
            raise ValueError('secondary source hash mismatch')
        seen.add(ref)
    if source.get("qualityState") == "needs-review" and not ("## 转换质量" in text or "## Conversion Quality" in text):
        raise ValueError("draft must disclose PDF/OCR conversion quality")
    from .reviewed_content import validate_content
    validate_content(root, source, target, text)


def promote(args) -> dict:
    from .commands import _load_status, _wiki_inventory, _review_gates
    root = Path(args.root).resolve()
    manifest_path, wiki = under(root, args.manifest), under(root, args.wiki)
    manifest = json.loads(read_text(manifest_path))
    run_id = safe_run_id(args.run_id or manifest["manifestId"])
    if not args.reviewer.strip() or not args.approval_note.strip() or not args.review_after.strip():
        raise ValueError("reviewer, approval note and review-after are required")
    status = _load_status(root, run_id)
    gates = _review_gates(manifest, status, _wiki_inventory(root, wiki))
    issues = gates["blockingIssues"] + source_issues(root, manifest)
    if issues:
        raise ValueError("promotion blocked: " + "; ".join(issues))
    package = status.get("reviewPackage", {})
    bindings = bindings_from_args(root, manifest, args)
    if package.get("state") != "ready-for-human-review" or package.get("reviewInputHashSha256") != review_snapshot(root, manifest_path, wiki, bindings):
        raise ValueError("review inputs changed or have no bound snapshot; rerun review-package for these exact inputs")
    sources = {source["id"]: source for source in manifest["sources"]}
    if getattr(args, "promotion_map", None):
        if set(item["sourceId"] for item in bindings) != set(sources):
            raise ValueError("batch map must cover every source exactly once; use a separately scoped manifest for a subset")
    elif not bindings:
        selected = getattr(args, "source_id", None)
        if selected is None and len(sources) != 1:
            raise ValueError("multiple sources require --source-id or --promotion-map; no implicit first-source promotion")
        selected = selected or next(iter(sources))
        if selected not in sources:
            raise ValueError("unknown source id")
        bindings = [{"sourceId": selected, "target": rel(root, under(root, args.target, root / "user/knowledge/reviewed"))}]
    plans = []
    for item in bindings:
        source = sources[item["sourceId"]]
        target = under(root, item["target"], root / "user/knowledge/reviewed")
        if item.get("draft"):
            draft = under(root, item["draft"])
            content = draft.read_bytes()
        else:
            content = format_reviewed(root, {**manifest, "sources": [source]}, wiki, target, args.scope, args.reviewer, args.approval_note, args.review_after).encode("utf-8")
        try:
            validate_draft(root, source, target, content.decode("utf-8-sig"))
        except ValueError as exc:
            raise ValueError(f"draft {source['id']}: {exc}") from exc
        before = target.read_bytes() if target.exists() else None
        if before is not None and before != content and not args.overwrite:
            raise FileExistsError("reviewed target already exists: " + rel(root, target))
        plans.append({"item": item, "source": source, "target": target, "content": content, "before": before})
    transaction = uuid.uuid4().hex
    evidence = root / "var/rag" / run_id / "promotions" / transaction
    evidence.mkdir(parents=True, exist_ok=False)
    write_text(evidence / "transaction-plan.json", json.dumps([
        {"target": rel(root, plan["target"]), "sourceId": plan["source"]["id"], "backup": f"{index:04d}.before",
         "previousHashSha256": hashlib.sha256(plan["before"]).hexdigest() if plan["before"] is not None else None,
         "contentHashSha256": hashlib.sha256(plan["content"]).hexdigest()} for index, plan in enumerate(plans)
    ], ensure_ascii=False, indent=2))
    committed, staged = [], []
    try:
        for index, plan in enumerate(plans):
            if plan["before"] is not None:
                (evidence / f"{index:04d}.before").write_bytes(plan["before"])
            if (plan["target"].read_bytes() if plan["target"].exists() else None) != plan["before"]:
                raise RuntimeError("target changed concurrently before commit")
            if plan["before"] == plan["content"]:
                continue
            plan["target"].parent.mkdir(parents=True, exist_ok=True)
            stage = plan["target"].with_name(plan["target"].name + "." + transaction + ".tmp")
            staged.append(stage)
            stage.write_bytes(plan["content"])
            os.replace(stage, plan["target"])
            committed.append(plan)
    except Exception as exc:
        rollback = []
        for plan in reversed(committed):
            if not plan["target"].exists() or plan["target"].read_bytes() != plan["content"]:
                rollback.append({"target": rel(root, plan["target"]), "state": "concurrent-change-preserved"})
                continue  # Never overwrite a third party's concurrent edit during rollback.
            if plan["before"] is None:
                plan["target"].unlink()
            else:
                plan["target"].write_bytes(plan["before"])
            rollback.append({"target": rel(root, plan["target"]), "state": "restored"})
        write_text(evidence / "rollback-result.json", json.dumps(rollback, ensure_ascii=False, indent=2))
        raise RuntimeError(f"promotion failed ({exc}); recovery evidence: {rel(root, evidence)}") from exc
    finally:
        for path in staged:
            path.unlink(missing_ok=True)
    entries = [{"sourceId": plan["source"]["id"], "sourceRef": plan["source"]["sourceRef"],
                "sourceHashSha256": plan["source"]["sourceHashSha256"],
                "normalizedMarkdown": plan["source"].get("normalizedMarkdown"),
                "normalizedHashSha256": plan["source"].get("normalizedHashSha256"),
                "target": rel(root, plan["target"]), "contentHashSha256": hashlib.sha256(plan["content"]).hexdigest(),
                "draft": plan["item"].get("draft"), "changed": plan in committed} for plan in plans]
    result = {"state": "promoted", "runId": run_id, "transactionId": transaction, "scope": args.scope,
              "target": entries[0]["target"] if len(entries) == 1 else None, "entries": entries,
              "promotedCount": len(entries), "changedCount": len(committed), "reviewer": args.reviewer,
              "reviewedAt": today(), "approvalNote": args.approval_note, "reviewAfter": args.review_after,
              "sourceManifest": rel(root, manifest_path), "candidateWiki": rel(root, wiki),
              "reviewInputHashSha256": package["reviewInputHashSha256"], "promotionHandledByThisTool": True,
              "reviewedKnowledgeWritten": bool(committed), "record": rel(root, evidence / "result.json")}
    write_text(evidence / "result.json", json.dumps(result, ensure_ascii=False, indent=2))
    latest = root / "var/rag" / run_id / "promotion-ledger.json"
    ledger = json.loads(read_text(latest)) if latest.exists() else {"entries": {}}
    for entry in entries:
        ledger["entries"][entry["target"]] = {**entry, "record": result["record"], "reviewedAt": today()}
    write_text(latest, json.dumps(ledger, ensure_ascii=False, indent=2))
    report = under(root, args.report) if args.report else evidence / "promotion-result.md"
    result["report"] = rel(root, report)
    write_text(report, "# 知识晋升结果\n\n" + f"- 来源数：{len(entries)}；实际更新：{len(committed)}。\n- 审核人：{args.reviewer}；日期：{today()}。\n- 最终内容哈希与源文件哈希见 `{result['record']}`。\n")
    update_status(root, run_id, {"state": "promoted", "promotionResult": result})
    print_json(result)
    return result
