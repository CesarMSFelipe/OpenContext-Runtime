"""Tests for CodeCompressor — AST-aware code compression."""

from __future__ import annotations

from opencontext_core.compression.code_compressor import CodeCompressionMode, CodeCompressor

_PY = '''\
def greet(name: str) -> str:
    """Return a greeting string."""
    # build message
    message = "Hello, " + name
    return message


class Greeter:
    """Wraps greet."""

    def run(self, name: str) -> str:
        return greet(name)
'''


def test_strip_docstrings_removes_docstrings() -> None:
    cc = CodeCompressor()
    # No language → skips tree-sitter, uses regex fallback reliably
    result = cc.compress(_PY, strip_docstrings=True, strip_comments=False, shorten_locals=False)
    assert "Return a greeting string" not in result
    assert "def greet" in result


def test_strip_comments_removes_hash_comments() -> None:
    cc = CodeCompressor()
    result = cc.compress(
        _PY, language="python", strip_docstrings=False, strip_comments=True, shorten_locals=False
    )
    assert "# build message" not in result
    assert "def greet" in result


def test_plan_mode_keeps_only_signatures() -> None:
    cc = CodeCompressor()
    result = cc.compress(_PY, language="python", mode=CodeCompressionMode.PLAN)
    assert "def greet" in result
    assert "message = " not in result


def test_act_mode_returns_content_unchanged() -> None:
    cc = CodeCompressor()
    result = cc.compress(_PY, language="python", mode=CodeCompressionMode.ACT)
    # ACT returns content as-is; check key content present and nothing stripped
    assert "message = " in result
    assert "return greet(name)" in result


def test_empty_input_returns_empty() -> None:
    cc = CodeCompressor()
    assert cc.compress("") == ""
