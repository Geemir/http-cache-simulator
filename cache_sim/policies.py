from collections.abc import Callable, Mapping

from .models import CacheEntry


ReplacementPolicy = Callable[[Mapping[str, CacheEntry]], str]


def fifo_victim(entries: Mapping[str, CacheEntry]) -> str:
    return min(entries, key=lambda resource_id: entries[resource_id].inserted_at)


POLICIES: dict[str, ReplacementPolicy] = {"fifo": fifo_victim}
