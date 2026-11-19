from collections.abc import Callable, Mapping

from .models import CacheEntry


ReplacementPolicy = Callable[[Mapping[str, CacheEntry]], str]


def fifo_victim(entries: Mapping[str, CacheEntry]) -> str:
    return min(entries, key=lambda resource_id: entries[resource_id].inserted_at)


def lru_victim(entries: Mapping[str, CacheEntry]) -> str:
    return min(entries, key=lambda resource_id: entries[resource_id].last_accessed_at)


def lfu_victim(entries: Mapping[str, CacheEntry]) -> str:
    def priority(resource_id: str) -> tuple[int, int]:
        entry = entries[resource_id]
        return entry.accesses, entry.last_accessed_at

    return min(entries, key=priority)


POLICIES: dict[str, ReplacementPolicy] = {
    "fifo": fifo_victim,
    "lru": lru_victim,
    "lfu": lfu_victim,
}
