"""Compression layer — deterministic and structural compression backends."""

from opencontext_core.compression.cache_aligner import AlignedPrompt, CacheAligner
from opencontext_core.compression.ccr_cache import (
    CCRCacheBackend,
    CCRStats,
    MemoryCCRBackend,
    SQLiteCCRBackend,
    ccr_stats,
    compress_with_ccr,
    retrieve_original,
    store_original,
)
from opencontext_core.compression.code_compressor import CodeCompressionMode, CodeCompressor
from opencontext_core.compression.output_reducer import OutputReducer, OutputReductionPlan
from opencontext_core.compression.smart_crusher import compress as smart_crusher_compress
from opencontext_core.compression.smart_crusher import expand as smart_crusher_expand
from opencontext_core.compression.terse import TerseCompressor, compress, expand, token_savings

__all__ = [
    "AlignedPrompt",
    "CCRCacheBackend",
    "CCRStats",
    "CacheAligner",
    "CodeCompressionMode",
    "CodeCompressor",
    "MemoryCCRBackend",
    "OutputReducer",
    "OutputReductionPlan",
    "SQLiteCCRBackend",
    "TerseCompressor",
    "ccr_stats",
    "compress",
    "compress_with_ccr",
    "expand",
    "retrieve_original",
    "smart_crusher_compress",
    "smart_crusher_expand",
    "store_original",
    "token_savings",
]
