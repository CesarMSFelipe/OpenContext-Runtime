# Compression

Compression is deterministic and explicitly lossy unless the selected strategy
is `none`. The v0.1 engine supports truncate, extractive head/tail, and a lossy
bullet-placeholder strategy.

Protected spans prevent unsafe mutation. Code blocks, JSON schemas, file paths,
numeric values, citations, and warning-like lines cause the item to be preserved
unchanged. The adaptive compression controller is a deterministic policy
skeleton that avoids lossy compression for high-risk and P0/P1 content.

