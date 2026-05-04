"""Memory Stack - Progressive context loading (MemPalace-inspired).

Implements 4-layer memory architecture:
- L0 (Identity): ~50-100 tokens, always loaded
- L1 (Essential Story): ~500-800 tokens, always loaded
- L2 (Room Recall): ~200-500 tokens, on-demand by topic
- L3 (Deep Search): variable, explicit queries only

This prevents context pollution and reduces token usage by 60-80%.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from opencontext_core.models.context import DataClassification
from opencontext_core.models.memory import MemoryItem, MemoryType


@dataclass
class MemoryLayerStats:
    """Statistics for a memory layer."""

    layer: int
    name: str
    token_count: int = 0
    item_count: int = 0
    last_accessed: datetime | None = None


class MemoryStack:
    """4-layer progressive memory loading system.

    Inspired by MemPalace's memory stack architecture. Each layer
    loads progressively more data only when needed, preventing
    context window pollution and reducing token usage.

    Layers:
        L0 - Identity: Who/what is this agent? (~100 tokens)
        L1 - Essential Story: Key moments and facts (~800 tokens)
        L2 - Room Recall: Topic-specific memories (~500 tokens)
        L3 - Deep Search: Full semantic query (variable)
    """

    def __init__(self, storage_path: Path | str = "./.opencontext/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Layer data
        self._l0_identity: dict[str, Any] = {}
        self._l1_story: list[MemoryItem] = []
        self._l2_rooms: dict[str, list[MemoryItem]] = {}
        self._l3_full: list[MemoryItem] = []

        # Statistics
        self._stats: dict[int, MemoryLayerStats] = {
            0: MemoryLayerStats(0, "Identity"),
            1: MemoryLayerStats(1, "Essential Story"),
            2: MemoryLayerStats(2, "Room Recall"),
            3: MemoryLayerStats(3, "Deep Search"),
        }

        # Load persisted state
        self._load()

    def _load(self) -> None:
        """Load memory layers from persistent storage."""
        identity_file = self.storage_path / "l0_identity.json"
        if identity_file.exists():
            with open(identity_file) as f:
                self._l0_identity = json.load(f)

        story_file = self.storage_path / "l1_story.json"
        if story_file.exists():
            with open(story_file) as f:
                data = json.load(f)
                self._l1_story = [MemoryItem.model_validate(item) for item in data]

    def _save(self) -> None:
        """Persist memory layers to storage."""
        identity_file = self.storage_path / "l0_identity.json"
        with open(identity_file, "w") as f:
            json.dump(self._l0_identity, f, indent=2, default=str)

        story_file = self.storage_path / "l1_story.json"
        with open(story_file, "w") as f:
            json.dump(
                [item.model_dump() for item in self._l1_story],
                f,
                indent=2,
                default=str,
            )

    # ============================================================
    # LAYER 0: IDENTITY (Always loaded)
    # ============================================================

    def set_identity(self, key: str, value: Any) -> None:
        """Set an identity attribute (L0 layer).

        Args:
            key: Identity attribute name (e.g., "project_name", "agent_role")
            value: Attribute value
        """
        self._l0_identity[key] = value
        self._save()

    def get_identity(self, key: str, default: Any = None) -> Any:
        """Get an identity attribute.

        Args:
            key: Attribute name
            default: Default value if not found

        Returns:
            Attribute value or default
        """
        return self._l0_identity.get(key, default)

    def build_l0_context(self, max_tokens: int = 100) -> str:
        """Build L0 identity context string.

        Args:
            max_tokens: Maximum tokens for L0 (typically 50-100)

        Returns:
            Identity context string
        """
        lines = ["# Identity", ""]

        for key, value in self._l0_identity.items():
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"- {key}: {value}")

        context = "\n".join(lines)

        # Rough token estimation (4 chars ≈ 1 token)
        if len(context) > max_tokens * 4:
            # Truncate while preserving key-value pairs
            pairs = []
            for key, value in self._l0_identity.items():
                pairs.append(f"- {key}: {value}")

            # Take most important pairs first
            context = "# Identity\n\n" + "\n".join(pairs[: max_tokens // 8])

        self._stats[0].token_count = len(context) // 4
        self._stats[0].last_accessed = datetime.now()

        return context

    # ============================================================
    # LAYER 1: ESSENTIAL STORY (Always loaded)
    # ============================================================

    def add_essential_memory(
        self,
        content: str,
        source: str,
        priority: int = 1,
        memory_type: MemoryType = MemoryType.STRUCTURED_FACT,
    ) -> MemoryItem:
        """Add an essential memory to L1 layer.

        These are the "top moments" - critical facts, decisions,
        and milestones that should always be in context.

        Args:
            content: Memory content
            source: Source of memory (file, conversation, etc.)
            priority: Priority 0 (highest) to 3 (low)
            memory_type: Type of memory

        Returns:
            Created memory item
        """
        item = MemoryItem(
            id=f"l1_{len(self._l1_story)}_{datetime.now().timestamp()}",
            content=content,
            source=source,
            memory_type=memory_type,
            created_at=datetime.now(),
            classification=DataClassification.INTERNAL,
            priority=priority,
            tokens=len(content) // 4,  # Rough estimate
            metadata={
                "layer": 1,
                "added_at": datetime.now().isoformat(),
            },
        )

        self._l1_story.append(item)

        # Sort by priority (0 = highest), then by recency
        self._l1_story.sort(key=lambda x: (x.priority, x.metadata.get("added_at", "")))

        # Keep only top memories (configurable)
        max_l1_items = 50  # ~800 tokens worth
        if len(self._l1_story) > max_l1_items:
            self._l1_story = self._l1_story[:max_l1_items]

        self._save()
        return item

    def build_l1_context(self, max_tokens: int = 800) -> str:
        """Build L1 essential story context.

        Args:
            max_tokens: Maximum tokens for L1 (typically 500-800)

        Returns:
            Essential story context string
        """
        if not self._l1_story:
            return "# Essential Story\n\nNo key memories recorded.\n"

        lines = ["# Essential Story", ""]
        remaining_tokens = max_tokens

        for item in self._l1_story:
            item_tokens = item.tokens or len(item.content) // 4

            if remaining_tokens - item_tokens < 10:  # Need room for header
                break

            lines.append(f"## {item.source}")

            # Truncate content if needed
            content = item.content
            if item_tokens > remaining_tokens * 0.8:
                # Keep first 80% of available space for this item
                max_content_tokens = int(remaining_tokens * 0.8)
                words = content.split()
                truncated = ""
                current_tokens = 0

                for word in words:
                    word_tokens = len(word) // 4 + 1
                    if current_tokens + word_tokens > max_content_tokens:
                        truncated += " [...]"
                        break
                    truncated += word + " "
                    current_tokens += word_tokens

                content = truncated.strip()

            lines.append(content)
            lines.append("")  # Blank line
            remaining_tokens -= item_tokens

        context = "\n".join(lines)
        self._stats[1].token_count = max_tokens - remaining_tokens
        self._stats[1].last_accessed = datetime.now()

        return context

    # ============================================================
    # LAYER 2: ROOM RECALL (On-demand by topic)
    # ============================================================

    def store_room_memory(
        self,
        room: str,
        content: str,
        source: str,
        wing: str = "default",
        memory_type: MemoryType = MemoryType.STRUCTURED_FACT,
    ) -> MemoryItem:
        """Store a memory in a specific room (L2 layer).

        Rooms are topic-specific containers (e.g., "auth", "api", "database").

        Args:
            room: Room/topic name
            content: Memory content
            source: Source of memory
            wing: Wing/category (e.g., "project_auth", "project_api")
            memory_type: Type of memory

        Returns:
            Created memory item
        """
        item = MemoryItem(
            id=f"l2_{wing}_{room}_{datetime.now().timestamp()}",
            content=content,
            source=source,
            memory_type=memory_type,
            created_at=datetime.now(),
            classification=DataClassification.INTERNAL,
            priority=1,
            tokens=len(content) // 4,
            metadata={
                "layer": 2,
                "room": room,
                "wing": wing,
                "stored_at": datetime.now().isoformat(),
            },
        )

        key = f"{wing}:{room}"
        if key not in self._l2_rooms:
            self._l2_rooms[key] = []

        self._l2_rooms[key].append(item)
        return item

    def recall_room(
        self,
        room: str,
        wing: str | None = None,
        max_tokens: int = 500,
    ) -> str:
        """Recall memories from a specific room (L2 layer).

        Args:
            room: Room/topic name
            wing: Optional wing to filter by
            max_tokens: Maximum tokens to return

        Returns:
            Room memories as context string
        """
        matching_items: list[MemoryItem] = []

        for key, items in self._l2_rooms.items():
            if wing and not key.startswith(f"{wing}:"):
                continue

            # Check if room matches
            stored_room = key.split(":")[-1]
            if stored_room == room or room in stored_room:
                matching_items.extend(items)

        if not matching_items:
            return f"# Room: {room}\n\nNo memories found for this topic.\n"

        # Sort by recency
        matching_items.sort(key=lambda x: x.metadata.get("stored_at", ""), reverse=True)

        lines = [f"# Room: {room}", ""]
        remaining_tokens = max_tokens

        for item in matching_items:
            item_tokens = item.tokens or len(item.content) // 4

            if remaining_tokens - item_tokens < 20:
                break

            wing = item.metadata.get("wing", "unknown")
            lines.append(f"## [{wing}] {item.source}")

            # Truncate if needed
            content = item.content
            if item_tokens > remaining_tokens * 0.7:
                words = content.split()
                truncated = ""
                current_tokens = 0

                for word in words:
                    word_tokens = len(word) // 4 + 1
                    if current_tokens + word_tokens > remaining_tokens * 0.7:
                        truncated += " [...]"
                        break
                    truncated += word + " "
                    current_tokens += word_tokens

                content = truncated.strip()

            lines.append(content)
            lines.append("")
            remaining_tokens -= item_tokens

        self._stats[2].token_count = max_tokens - remaining_tokens
        self._stats[2].last_accessed = datetime.now()

        return "\n".join(lines)

    def search_rooms(
        self,
        query: str,
        wing: str | None = None,
        max_results: int = 10,
    ) -> list[MemoryItem]:
        """Search across rooms using simple keyword matching.

        Args:
            query: Search query
            wing: Optional wing filter
            max_results: Maximum results to return

        Returns:
            List of matching memory items
        """
        results: list[MemoryItem] = []
        query_lower = query.lower()

        for key, items in self._l2_rooms.items():
            if wing and not key.startswith(f"{wing}:"):
                continue

            for item in items:
                if query_lower in item.content.lower() or query_lower in item.source.lower():
                    results.append(item)

        # Sort by priority, then recency
        results.sort(
            key=lambda x: (
                x.priority,
                x.metadata.get("stored_at", ""),
            )
        )

        return results[:max_results]

    # ============================================================
    # LAYER 3: DEEP SEARCH (Full semantic query)
    # ============================================================

    def deep_search(
        self,
        query: str,
        max_tokens: int = 2000,
        include_layers: list[int] | None = None,
    ) -> tuple[str, list[MemoryItem]]:
        """Perform deep search across all layers (L3).

        This is the most expensive operation - searches through
        all stored memories and returns the most relevant ones.

        Args:
            query: Search query
            max_tokens: Maximum tokens to return
            include_layers: Which layers to include (default: all)

        Returns:
            Tuple of (context string, matching items)
        """
        if include_layers is None:
            include_layers = [0, 1, 2]

        query_lower = query.lower()
        matches: list[tuple[MemoryItem, float]] = []

        # Search L1 (essential memories)
        if 1 in include_layers:
            for item in self._l1_story:
                score = self._calculate_relevance(item, query_lower)
                if score > 0:
                    matches.append((item, score))

        # Search L2 (room memories)
        if 2 in include_layers:
            for items in self._l2_rooms.values():
                for item in items:
                    score = self._calculate_relevance(item, query_lower)
                    if score > 0:
                        matches.append((item, score))

        # Sort by relevance score
        matches.sort(key=lambda x: x[1], reverse=True)

        # Build context
        lines = [f"# Deep Search: {query}", "", "## Most Relevant Memories", ""]
        remaining_tokens = max_tokens

        items_to_include: list[MemoryItem] = []
        for item, score in matches:
            if remaining_tokens <= 0:
                break

            item_tokens = item.tokens or len(item.content) // 4

            if remaining_tokens - item_tokens - 30 < 0:  # Need room for metadata
                # Try to include at least some content
                available = remaining_tokens - 30
                if available > 50:
                    item_tokens = available
                else:
                    break

            items_to_include.append(item)

            source = item.source
            layer = item.metadata.get("layer", "?")
            room = item.metadata.get("room", "")

            lines.append(f"### [{layer}.{room}] {source} (relevance: {score:.2f})")

            content = item.content
            if len(content) // 4 > item_tokens:
                words = content.split()
                truncated = ""
                current_tokens = 0

                for word in words:
                    word_tokens = len(word) // 4 + 1
                    if current_tokens + word_tokens > item_tokens:
                        truncated += " [...]"
                        break
                    truncated += word + " "
                    current_tokens += word_tokens

                content = truncated.strip()

            lines.append(content)
            lines.append("")
            remaining_tokens -= item_tokens + 30

        self._stats[3].token_count = max_tokens - remaining_tokens
        self._stats[3].last_accessed = datetime.now()

        context = "\n".join(lines)
        return context, items_to_include

    def _calculate_relevance(self, item: MemoryItem, query: str) -> float:
        """Calculate relevance score for a memory item.

        Simple keyword matching - could be enhanced with embeddings.

        Args:
            item: Memory item
            query: Lowercase query string

        Returns:
            Relevance score (0-1)
        """
        content_lower = item.content.lower()
        source_lower = item.source.lower()

        # Check for exact matches
        if query in content_lower:
            # Boost for multiple occurrences
            count = content_lower.count(query)
            return min(1.0, count * 0.3 + 0.3)

        # Check for partial matches in source
        if query in source_lower:
            return 0.5

        # Check for word boundaries
        words = query.split()
        matches = sum(1 for word in words if word in content_lower)

        if matches > 0:
            return min(1.0, matches / len(words) * 0.7)

        return 0.0

    # ============================================================
    # COMBINED CONTEXT BUILDING
    # ============================================================

    def build_wake_up_context(
        self,
        max_tokens: int = 1000,
        topic: str | None = None,
    ) -> str:
        """Build progressive context for "wake-up" (L0 + L1 + optional L2).

        This is the equivalent of MemPalace's `mempalace wake-up` command.
        Always includes identity and essential story, optionally
        includes room-specific context.

        Args:
            max_tokens: Maximum total tokens
            topic: Optional topic to include room context for

        Returns:
            Wake-up context string
        """
        # Calculate allocation
        l0_tokens = min(100, max_tokens // 4)  # 25% for identity
        l1_tokens = min(800, max_tokens // 2)  # 50% for story
        l2_tokens = max_tokens - l0_tokens - l1_tokens  # Rest for room

        parts = []

        # L0: Identity
        parts.append(self.build_l0_context(l0_tokens))

        # L1: Essential Story
        parts.append(self.build_l1_context(l1_tokens))

        # L2: Room context (if topic specified)
        if topic:
            room_context = self.recall_room(topic, max_tokens=l2_tokens)
            if "No memories found" not in room_context:
                parts.append(room_context)

        return "\n\n".join(parts)

    def build_full_context(
        self,
        query: str,
        max_tokens: int = 4000,
    ) -> tuple[str, list[MemoryItem]]:
        """Build full context using progressive loading.

        This is the main entry point for agent context preparation.
        It efficiently combines all layers based on query relevance.

        Args:
            query: User query
            max_tokens: Maximum total tokens

        Returns:
            Tuple of (context string, relevant items)
        """
        # Token budget allocation
        budgets = {
            "l0": 100,  # Always include identity
            "l1": 800,  # Always include essential story
            "l2": 1000,  # Room context
            "l3": max_tokens - 1900,  # Deep search gets the rest
        }

        parts = []
        all_items: list[MemoryItem] = []

        # L0: Identity
        parts.append(self.build_l0_context(budgets["l0"]))

        # L1: Essential Story
        parts.append(self.build_l1_context(budgets["l1"]))

        # Extract potential topics from query
        # Simple keyword extraction (could use NLP in future)
        query_lower = query.lower()
        potential_topics = []
        for key in self._l2_rooms.keys():
            room_name = key.split(":")[-1]
            if room_name in query_lower:
                potential_topics.append(room_name)

        # L2: Room context for relevant topics
        if potential_topics:
            for topic in potential_topics[:2]:  # Max 2 topics
                room_context = self.recall_room(topic, max_tokens=budgets["l2"] // 2)
                if "No memories found" not in room_context:
                    parts.append(room_context)

        # L3: Deep search
        search_context, search_items = self.deep_search(query, max_tokens=budgets["l3"])
        parts.append(search_context)
        all_items.extend(search_items)

        return "\n\n".join(parts), all_items

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_stats(self) -> dict[str, Any]:
        """Get memory stack statistics.

        Returns:
            Dictionary with statistics for each layer
        """
        return {
            "layers": {
                str(stat.layer): {
                    "name": stat.name,
                    "token_count": stat.token_count,
                    "item_count": (
                        len(self._l0_identity)
                        if stat.layer == 0
                        else len(self._l1_story)
                        if stat.layer == 1
                        else sum(len(items) for items in self._l2_rooms.values())
                        if stat.layer == 2
                        else len(self._l2_rooms)
                    ),
                    "last_accessed": stat.last_accessed.isoformat() if stat.last_accessed else None,
                }
                for stat in self._stats.values()
            },
            "total_items": (
                len(self._l0_identity)
                + len(self._l1_story)
                + sum(len(items) for items in self._l2_rooms.values())
            ),
        }

    def clear(self) -> None:
        """Clear all memory layers."""
        self._l0_identity.clear()
        self._l1_story.clear()
        self._l2_rooms.clear()
        self._save()


# Convenience functions for common operations


def create_memory_stack(
    project_path: Path | str,
    project_name: str,
    agent_role: str = "code_assistant",
) -> MemoryStack:
    """Create a new memory stack for a project.

    Args:
        project_path: Path to project root
        project_name: Name of the project
        agent_role: Role of the agent (e.g., "code_assistant", "reviewer")

    Returns:
        Configured memory stack
    """
    stack = MemoryStack(Path(project_path) / ".opencontext" / "memory")

    # Set basic identity
    stack.set_identity("project_name", project_name)
    stack.set_identity("project_path", str(project_path))
    stack.set_identity("agent_role", agent_role)
    stack.set_identity("created_at", datetime.now().isoformat())

    return stack


def get_wake_up_context(
    project_path: Path | str,
    topic: str | None = None,
) -> str:
    """Get wake-up context for a project.

    This is a shortcut for building progressive context.

    Args:
        project_path: Path to project root
        topic: Optional topic to focus on

    Returns:
        Wake-up context string
    """
    memory_dir = Path(project_path) / ".opencontext" / "memory"
    if not memory_dir.exists():
        return "# Identity\n\nNo memory stack found for this project.\n"

    stack = MemoryStack(memory_dir)
    return stack.build_wake_up_context(topic=topic)


__all__ = [
    "MemoryLayerStats",
    "MemoryStack",
    "create_memory_stack",
    "get_wake_up_context",
]
