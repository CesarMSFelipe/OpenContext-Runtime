from __future__ import annotations

import pytest
from pydantic import ValidationError

from opencontext_core.memory_usability.context_repository import MemoryItem


def test_context_repository_classification_required() -> None:
    with pytest.raises(ValidationError):
        MemoryItem.model_validate(
            {
                "id": "mem-1",
                "kind": "fact",
                "source": "trace:abc",
                "valid_from": "2026-05-02T00:00:00Z",
                "tokens": 1,
                "content": "content",
            }
        )
