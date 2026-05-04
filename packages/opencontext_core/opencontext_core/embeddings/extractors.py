"""Utilities for creating embedding records from project artifacts."""

from __future__ import annotations

from opencontext_core.embeddings.models import EmbeddedItem
from opencontext_core.models.context import DataClassification
from opencontext_core.models.project import ProjectManifest


def items_from_manifest(
    manifest: ProjectManifest,
    classifier: object | None = None,  # Optional classification predictor
) -> list[EmbeddedItem]:
    """Extract embeddable items from a project manifest.

    Args:
        manifest: The project manifest
        classifier: Optional classifier to determine data classification

    Returns:
        List of embedding records ready for generation
    """
    items: list[EmbeddedItem] = []

    # Classify files
    for file in manifest.files:
        # Use summary as the embeddable content
        content = file.summary or file.path
        classification = DataClassification.INTERNAL
        items.append(
            EmbeddedItem.create(
                item_id=f"file:{file.path}",
                item_type="file",
                project_name=manifest.project_name,
                content=content,
                classification=classification,
                metadata={
                    "source_path": file.path,
                    "language": file.language,
                    "file_type": file.file_type.value,
                    "size_bytes": file.size_bytes,
                },
            )
        )

    # Classify symbols
    for symbol in manifest.symbols:
        # Build content from symbol data
        parts = []
        parts.append(f"{symbol.kind} {symbol.name}")
        signature = getattr(symbol, "signature", None) or symbol.metadata.get("signature")
        docstring = getattr(symbol, "docstring", None) or symbol.metadata.get("docstring")
        if signature:
            parts.append(str(signature))
        if docstring:
            parts.append(str(docstring))

        content = "\n".join(parts).strip()
        classification = DataClassification.INTERNAL

        items.append(
            EmbeddedItem.create(
                item_id=f"symbol:{symbol.id}",
                item_type="symbol",
                project_name=manifest.project_name,
                content=content,
                classification=classification,
                metadata={
                    "source_path": symbol.path,
                    "line": symbol.line,
                    "kind": symbol.kind,
                    "language": symbol.language,
                },
            )
        )

    return items
