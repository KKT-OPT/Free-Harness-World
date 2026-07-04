---
documentName: harness/templates/knowledge/StructuredIngestionManifestTemplate.md
version: v1.2.0-normalized-source-output
updatedAt: 2026-07-04 00:00:00.000 +08:00
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
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
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
  decision: normalized-source-output-field-added
---
# Structured Ingestion Manifest 模板

```yaml
manifestId: <generated-id>
sourceRef: <source-path-or-uri>
sourceType: pdf | office | html | image | audio | video | other
profileRef: harness/rag/manifests/offline-markitdown-rapidocr-whisper.profile.example.yaml
network: disabled
llmApiRequired: false
sourceGate:
  compatible: true
  blockedReason: null
  bodyHash: <normalized-body-hash>
  sourceFingerprint: <path-fingerprint>
  duplicateBodyHashOf: null
schema:
  domain: <domain>
  schemaRef: user/knowledge/reviewed/<domain>/schema.md
  injectedSections: []
extraction:
  extractionGranularity: fine | standard | coarse | minimal | custom
  entityCap: <number>
  conceptCap: <number>
  batchStrategy: <strategy>
tagVocabulary:
  mode: default | custom
  allowedTags: []
outputState: extracted
outputs:
  normalizedMarkdown: user/knowledge/raw/<domain>/normalized/<source>.md
  runtimeExtractedMarkdown: var/rag/<run-id>/extracted/<source>.md
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
