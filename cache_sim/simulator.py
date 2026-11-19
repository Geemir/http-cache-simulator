import math
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from .models import CacheEntry, Metrics, Request, RequestEvent, Resource, SimulationResult
from .policies import ReplacementPolicy, fifo_victim


@dataclass
class _Totals:
    requests: int = 0
    hits: int = 0
    requested_bytes: int = 0
    hit_bytes: int = 0
    response_ms: float = 0.0

    def record(self, size_bytes: int, hit: bool, response_ms: float) -> None:
        self.requests += 1
        self.requested_bytes += size_bytes
        self.response_ms += response_ms
        if hit:
            self.hits += 1
            self.hit_bytes += size_bytes

    def metrics(self) -> Metrics:
        return Metrics(
            requests=self.requests,
            hits=self.hits,
            requested_bytes=self.requested_bytes,
            hit_bytes=self.hit_bytes,
            origin_bytes=self.requested_bytes - self.hit_bytes,
            request_hit_ratio=self.hits / self.requests if self.requests else 0.0,
            byte_hit_ratio=self.hit_bytes / self.requested_bytes if self.requested_bytes else 0.0,
            mean_response_ms=self.response_ms / self.requests if self.requests else 0.0,
        )


def simulate(
    resources: Mapping[str, Resource],
    requests: Iterable[Request],
    *,
    capacity_bytes: int = 102_400,
    hit_latency_ms: float = 5.0,
    choose_victim: ReplacementPolicy = fifo_victim,
    on_event: Callable[[RequestEvent], None] | None = None,
) -> SimulationResult:
    """Process requests in input order against a fresh shared cache."""
    if capacity_bytes < 0:
        raise ValueError("Cache capacity must be nonnegative")
    if not math.isfinite(hit_latency_ms) or hit_latency_ms < 0:
        raise ValueError("Cache hit latency must be finite and nonnegative")

    entries: dict[str, CacheEntry] = {}
    used_bytes = 0
    overall = _Totals()
    clients: dict[str, _Totals] = defaultdict(_Totals)

    for request_number, request in enumerate(requests, start=1):
        resource_id = request.resource_id
        resource = resources.get(resource_id)
        if resource is None:
            raise ValueError(f"Request {request_number} refers to unknown resource {resource_id!r}")

        entry = entries.get(resource_id)
        hit = entry is not None
        evicted: list[str] = []
        if entry is not None:
            entry.accesses += 1
            entry.last_accessed_at = request_number
        elif resource.size_bytes <= capacity_bytes:
            while used_bytes + resource.size_bytes > capacity_bytes:
                victim = choose_victim(entries)
                used_bytes -= entries.pop(victim).resource.size_bytes
                evicted.append(victim)
            entries[resource_id] = CacheEntry(resource, request_number, request_number)
            used_bytes += resource.size_bytes

        response_ms = hit_latency_ms if hit else resource.origin_latency_ms
        overall.record(resource.size_bytes, hit, response_ms)
        clients[request.client_id].record(resource.size_bytes, hit, response_ms)
        if on_event is not None:
            on_event(
                RequestEvent(
                    request_number=request_number,
                    request=request,
                    hit=hit,
                    evicted=tuple(evicted),
                    response_ms=response_ms,
                    origin_bytes=0 if hit else resource.size_bytes,
                    cache_contents_oldest_first=tuple(entries),
                    cache_used_bytes=used_bytes,
                    cumulative_origin_bytes=overall.requested_bytes - overall.hit_bytes,
                    cumulative_hits=overall.hits,
                )
            )

    return SimulationResult(
        overall=overall.metrics(),
        clients={client_id: totals.metrics() for client_id, totals in clients.items()},
    )
