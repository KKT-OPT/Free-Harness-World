# Structured Ingestion Manifest Template

Status: template
Version: v0.1.0-p9-preflight

```yaml
manifestId: <generated-id>
sourceRef: <source-path-or-uri>
sourceType: pdf | office | html | image | audio | video | other
profileRef: rag/manifests/offline-markitdown-rapidocr-whisper.profile.example.yaml
network: disabled
llmApiRequired: false
outputState: extracted
outputs:
  markdown: <path>
  metadataManifest: <path>
  extractionReport: <path>
  chunksJsonl: <path>
provenance:
  inputHash: <sha256>
  outputHash: <sha256>
  toolVersions: []
review:
  reviewedKnowledge: false
  reviewer: null
```
