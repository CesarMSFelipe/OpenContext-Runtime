# Project Intelligence Layer

The project intelligence layer scans a software project before an LLM run. It
respects ignore patterns, detects languages by extension, classifies file types,
estimates tokens, extracts lightweight symbols, applies optional technology
profiles, and persists a `ProjectManifest`.

The layer also marks files with potential secrets and records safety warnings in
manifest metadata. Repo maps are derived from the manifest and symbol index so
they can summarize project shape without exposing raw file content.

## Implemented Outputs

- `ProjectManifest`: persisted project name, root, technology profiles, files, symbols, dependency
  graph, generated timestamp, and indexing metadata.
- `ProjectFile`: path, language, file type, token estimate, size, summary, and safety metadata.
- `Symbol`: lightweight name/kind/path/line metadata extracted from source files.
- `DependencyGraph`: deterministic import/include edges for supported language patterns.
- Repo-map entries: compact path and symbol summaries rendered under a token budget.
- Local deterministic embedding records: optional asynchronous records behind core interfaces, not a
  dependency on an external vector database.
- Graph tunnels: persisted links between indexed projects for cross-project recall, disabled unless
  configured.

## Technology Profiles

Technology profiles add stack-specific knowledge without replacing the core.
The core knows the `TechnologyProfile` protocol and a generic fallback profile;
first-party profile implementations live outside `opencontext_core`.

```python
class TechnologyProfile(Protocol):
    name: str

    def detect(self, project_root: Path) -> ProfileDetectionResult: ...
    def classify_file(self, path: Path) -> FileClassificationResult | None: ...
    def extract_symbols(self, file: ProjectFile) -> list[Symbol]: ...
    def build_context_providers(self) -> list[ContextProviderReference]: ...
    def suggest_workflows(self) -> list[WorkflowPackReference]: ...
    def suggest_validation_commands(self) -> list[SafeCommand]: ...
```

First-party profiles in v0.1 include a broad catalog across frontend, backend,
mobile, PHP/CMS, Python/data, JVM/.NET, native systems languages, DevOps/IaC,
monorepos, static sites, databases, and platform projects. See
[Technology Profiles](technology-profiles.md).

Hard rule: no framework-specific logic in `opencontext_core`.
