"""MCP tool response compression middleware.

Provides transparent compression/decompression for MCP tool call responses
using the caveman protocol to reduce token usage while preserving technical content.

This middleware is designed to be integrated into the MCP adapter boundary.
It operates on MCP response structures, compressing textual content fields
while preserving code blocks, file paths, and other structured data.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta
from typing import Any

from opencontext_core.compression.caveman import CavemanCompressor
from opencontext_core.config import OpenContextConfig


class MCPCompressionConfig:
    """Helper for MCP compression settings."""

    def __init__(self, config: OpenContextConfig) -> None:
        self.config = config
        mcp_config = config.cache.mcp
        self.enabled = mcp_config.enabled and mcp_config.compression_enabled
        self.compression_ratio = mcp_config.compression_ratio
        self.preserve_code_blocks = mcp_config.preserve_code_blocks
        self.cache_ttl = timedelta(seconds=mcp_config.cache_ttl_seconds)
        self._cache: dict[str, CachedResponse] = {}

    def should_compress(self, content_type: str) -> bool:
        """Determine if a content type should be compressed."""
        # Compress text/*, application/json (if large), etc.
        return content_type.startswith("text/") or content_type == "application/json"

    def compute_hash(self, request_key: str, response: dict[str, Any]) -> str:
        """Compute deterministic hash for cache lookup."""
        combined = f"{request_key}:{response!s}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]


class CachedResponse:
    """Cache entry for compressed MCP responses."""

    def __init__(self, response: dict[str, Any], compressed: bool, expires_at: datetime) -> None:
        self.response = response
        self.compressed = compressed
        self.expires_at = expires_at

    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at


class MCPCompressionMiddleware:
    """Middleware for compressing MCP tool responses.

    Usage:
        middleware = MCPCompressionMiddleware(config)
        compressed = await middleware.handle(request_id, original_response)
    """

    def __init__(self, config: OpenContextConfig) -> None:
        self.config = MCPCompressionConfig(config)
        self.compressor = CavemanCompressor(intensity="full")

    async def handle(
        self,
        request_id: str,
        response: dict[str, Any],
        *,
        compute: Callable[[], Coroutine[Any, Any, dict[str, Any]]] | None = None,
    ) -> dict[str, Any]:
        """Process an MCP response with optional compression and caching.

        Args:
            request_id: Unique identifier for the request (for cache key)
            response: The raw response from the MCP tool
            compute: Optional async callable to compute response if not cached

        Returns:
            Processed (possibly compressed) response
        """
        if not self.config.enabled:
            return response

        # Check cache first
        cache_key = self.config.compute_hash(request_id, response)
        cached = self.config._cache.get(cache_key)
        if cached and cached.is_valid():
            return cached.response

        # Apply compression to textual fields
        compressed = self._compress_response(response)

        # Cache result
        expires = datetime.now() + self.config.cache_ttl
        self.config._cache[cache_key] = CachedResponse(compressed, compressed != response, expires)

        return compressed

    def _compress_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Recursively compress string values in response dict."""
        if not response:
            return response

        compressed: dict[str, Any] = {}
        for key, value in response.items():
            if isinstance(value, str):
                compressed[key] = self._compress_string(value)
            elif isinstance(value, dict):
                compressed[key] = self._compress_response(value)
            elif isinstance(value, list):
                compressed[key] = self._compress_list(value)
            else:
                compressed[key] = value

        return compressed

    def _compress_list(self, items: list[Any]) -> list[Any]:
        """Compress strings within a list."""
        compressed: list[Any] = []
        for item in items:
            if isinstance(item, str):
                compressed.append(self._compress_string(item))
            elif isinstance(item, dict):
                compressed.append(self._compress_response(item))
            elif isinstance(item, list):
                compressed.append(self._compress_list(item))
            else:
                compressed.append(item)
        return compressed

    def _compress_string(self, text: str) -> str:
        """Compress a single string if beneficial."""
        if not text.strip():
            return text
        # Quick check if compression likely helpful (> 200 chars)
        if len(text) < 200:
            return text
        compressed = self.compressor.compress(text)
        # Only use compression if we actually saved tokens (>10% reduction)
        savings = (len(text) - len(compressed)) / len(text)
        if savings > 0.1:
            return compressed
        return text


def create_mcp_middleware(config: OpenContextConfig) -> MCPCompressionMiddleware:
    """Factory to create MCP compression middleware from config."""
    return MCPCompressionMiddleware(config)


# Convenience function for direct compression without middleware overhead
def compress_mcp_response(response: dict[str, Any], config: OpenContextConfig) -> dict[str, Any]:
    """Compress an MCP response using caveman protocol."""
    middleware = MCPCompressionMiddleware(config)
    return middleware._compress_response(response)
