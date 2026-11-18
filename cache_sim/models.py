import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Resource:
    resource_id: str
    size_bytes: int
    origin_latency_ms: float

    def __post_init__(self) -> None:
        if not isinstance(self.size_bytes, int) or self.size_bytes < 0:
            raise ValueError("Resource size must be a nonnegative integer")
        if not math.isfinite(self.origin_latency_ms) or self.origin_latency_ms < 0:
            raise ValueError("Origin latency must be finite and nonnegative")


@dataclass(frozen=True, slots=True)
class Request:
    client_id: str
    resource_id: str


@dataclass(slots=True)
class CacheEntry:
    resource: Resource
    inserted_at: int
    last_accessed_at: int
    accesses: int = 1


@dataclass(frozen=True, slots=True)
class RequestEvent:
    request_number: int
    request: Request
    hit: bool
    evicted: tuple[str, ...]
    response_ms: float
    origin_bytes: int


@dataclass(frozen=True, slots=True)
class Metrics:
    requests: int
    hits: int
    requested_bytes: int
    hit_bytes: int
    origin_bytes: int
    request_hit_ratio: float
    byte_hit_ratio: float
    mean_response_ms: float


@dataclass(frozen=True, slots=True)
class SimulationResult:
    overall: Metrics
    clients: dict[str, Metrics]
