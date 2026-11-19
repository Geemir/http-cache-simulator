import csv
import json
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile

from .models import Request, RequestEvent, Resource


def _read_rows(
    path: Path, required_columns: tuple[str, ...],
) -> Iterator[tuple[int, dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        headers = set(reader.fieldnames or ())
        identity = ("resource_id",) if "resource_id" in headers else ("scheme", "host", "path")
        columns = required_columns + identity
        missing = set(columns) - headers
        if missing:
            raise ValueError(f"{path} missing CSV headers {', '.join(sorted(missing))}")

        for row in reader:
            values = {column: (row[column] or "").strip() for column in columns}
            if not all(values.values()):
                raise ValueError(f"{path}:{reader.line_num} has a blank required value")
            yield reader.line_num, values


def _resource_id(row: dict[str, str]) -> str:
    if "resource_id" in row:
        return row["resource_id"]
    scheme = row["scheme"].lower()
    host = row["host"].lower()
    return f"{scheme}://{host}{row['path']}"


def load_resources(path: Path) -> dict[str, Resource]:
    resources = {}
    for line, row in _read_rows(path, ("size_bytes", "origin_latency_ms")):
        resource_id = _resource_id(row)
        if resource_id in resources:
            raise ValueError(f"{path}:{line} has duplicate resource ID {resource_id!r}")
        try:
            resources[resource_id] = Resource(
                resource_id, int(row["size_bytes"]), float(row["origin_latency_ms"]),
            )
        except ValueError as error:
            raise ValueError(f"{path}:{line} has an invalid size or latency. {error}") from error
    return resources


def iter_requests(path: Path) -> Iterator[Request]:
    for _, row in _read_rows(path, ("client_id",)):
        yield Request(row["client_id"], _resource_id(row))


@contextmanager
def event_csv_writer(path: Path) -> Iterator[Callable[[RequestEvent], None]]:
    """Stream events to a sibling file and publish it after a successful run."""
    stream = NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False)
    temporary_path = Path(stream.name)
    try:
        with stream:
            writer = csv.writer(stream)
            writer.writerow([
                "step", "resource_id", "client_id", "result", "evicted",
                "cache_contents_oldest_first", "cache_used_bytes", "response_ms",
                "cumulative_origin_bytes", "cumulative_hits",
            ])

            def record(event: RequestEvent) -> None:
                writer.writerow([
                    event.request_number, event.request.resource_id, event.request.client_id,
                    "HIT" if event.hit else "MISS", json.dumps(event.evicted),
                    json.dumps(event.cache_contents_oldest_first), event.cache_used_bytes,
                    event.response_ms, event.cumulative_origin_bytes, event.cumulative_hits,
                ])

            yield record
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)
