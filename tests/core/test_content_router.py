from __future__ import annotations

from opencontext_core.memory_usability import ContentRouter, ContentType, SerializationFormat


def test_code_routes_to_code_strategy() -> None:
    route = ContentRouter().route("def login(): pass", path="src/auth.py")

    assert route.content_type is ContentType.CODE
    assert route.compression_strategy == "code_aware_symbol_selection"


def test_json_and_yaml_route_to_structured_serializers() -> None:
    json_route = ContentRouter().route('{"a": 1}')
    yaml_route = ContentRouter().route("a: 1", path="opencontext.yaml")

    assert json_route.serialization_format is SerializationFormat.JSON
    assert yaml_route.serialization_format is SerializationFormat.TOON


def test_tool_output_is_untrusted_and_unknown_falls_back_safely() -> None:
    router = ContentRouter()
    tool_route = router.route("ran tests", declared_type=ContentType.TOOL_OUTPUT)
    unknown_route = router.route("")

    assert tool_route.untrusted is True
    assert unknown_route.content_type is ContentType.UNKNOWN
    assert unknown_route.security_policy == "redact"
