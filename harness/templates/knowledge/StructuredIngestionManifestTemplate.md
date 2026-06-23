---
documentName: harness/templates/knowledge/StructuredIngestionManifestTemplate.md
version: v1.0.0-h6-rag-boundary
updatedAt: 2026-06-22 23:41:15.773 +08:00
status: active
purpose: 提供 structured ingestion manifest 模板，记录 raw-to-candidate workflow 的来源、输出和审查状态。
scope:
  - knowledge-template
  - structured-ingestion
  - rag-manifest
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/manifests/README.md
  - harness/governance/KnowledgePromotionPolicy.md
outputTo:
  - harness/templates/knowledge/StructuredIngestionManifestTemplate.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-22
  decision: h6-complete
---
# Structured Ingestion Manifest 模板

```yaml
manifestId: <generated-id>
sourceRef: <source-path-or-uri>
sourceType: pdf | office | html | image | audio | video | other
profileRef: harness/rag/manifests/offline-markitdown-rapidocr-whisper.profile.example.yaml
network: disabled
llmApiRequired: false
outputState: extracted
outputs:
  extractedMarkdown: var/rag/<run-id>/extracted/<source>.md
  metadataManifest: var/rag/<run-id>/extracted/metadata-manifest.json
  extractionReport: var/rag/<run-id>/extracted/extraction-report.md
  chunksJsonl: var/rag/<run-id>/extracted/chunks.jsonl
  candidateWiki: user/knowledge/candidate/<run-id>/wiki
  evalReports: var/rag/<run-id>/evals/
  graphRuntime: var/rag/<run-id>/graph/
provenance:
  inputHash: <sha256>
  outputHash: <sha256>
  toolVersions: []
review:
  reviewedKnowledge: false
  promotionHandledByThisTool: false
  reviewer: null
```
