"""Lightweight PHP and Python symbol extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass

from opencontext_core.models.project import Symbol

PY_CLASS_RE = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)")
PY_DEF_RE = re.compile(r"^\s*(async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)")
PHP_TYPE_RE = re.compile(r"\b(class|interface|trait|enum)\s+([A-Za-z_][A-Za-z0-9_]*)")
PHP_FUNCTION_RE = re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)")


@dataclass(frozen=True)
class ExtractableFile:
    """Minimal scanned-file contract needed by the symbol extractor."""

    relative_path: str
    language: str
    content: str


class SymbolExtractor:
    """Extracts simple symbols without language parser dependencies."""

    def extract(self, file: ExtractableFile) -> list[Symbol]:
        """Extract symbols from a supported file."""

        if file.language == "python":
            return self._extract_python(file)
        if file.language == "php":
            return self._extract_php(file)
        return []

    def _extract_python(self, file: ExtractableFile) -> list[Symbol]:
        symbols: list[Symbol] = []
        current_class: tuple[str, int] | None = None
        for line_number, line in enumerate(file.content.splitlines(), start=1):
            indent = len(line) - len(line.lstrip(" "))
            class_match = PY_CLASS_RE.match(line)
            if class_match:
                current_class = (class_match.group(1), indent)
                symbols.append(
                    _symbol(
                        file.relative_path,
                        class_match.group(1),
                        "class",
                        line_number,
                        "python",
                    )
                )
                continue
            def_match = PY_DEF_RE.match(line)
            if def_match:
                name = def_match.group(2)
                container = (
                    current_class[0]
                    if current_class is not None and indent > current_class[1]
                    else None
                )
                kind = "method" if container else "function"
                symbols.append(
                    _symbol(file.relative_path, name, kind, line_number, "python", container)
                )
        return symbols

    def _extract_php(self, file: ExtractableFile) -> list[Symbol]:
        symbols: list[Symbol] = []
        current_type: str | None = None
        for line_number, line in enumerate(file.content.splitlines(), start=1):
            type_match = PHP_TYPE_RE.search(line)
            if type_match:
                current_type = type_match.group(2)
                symbols.append(
                    _symbol(
                        file.relative_path,
                        current_type,
                        type_match.group(1),
                        line_number,
                        "php",
                    )
                )
            function_match = PHP_FUNCTION_RE.search(line)
            if function_match:
                name = function_match.group(1)
                container = current_type if current_type is not None else None
                kind = "method" if container else "function"
                symbols.append(
                    _symbol(file.relative_path, name, kind, line_number, "php", container)
                )
        return symbols


def _symbol(
    path: str,
    name: str,
    kind: str,
    line: int,
    language: str,
    container: str | None = None,
) -> Symbol:
    return Symbol(
        id=f"{path}:{name}:{line}",
        name=name,
        kind=kind,
        path=path,
        line=line,
        language=language,
        container=container,
        metadata={},
    )
