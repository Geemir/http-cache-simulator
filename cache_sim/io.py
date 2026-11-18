import csv
from collections.abc import Iterator
from pathlib import Path

from .models import Request, Resource


def _read_rows(path: Path, columns: tuple[str, ...]) -> Iterator[tuple[int, list[str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        missing = set(columns) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path} missing CSV headers {', '.join(sorted(missing))}")

        for row in reader:
            values = [(row[column] or "").strip() for column in columns]
            if not all(values):
                raise ValueError(f"{path}:{reader.line_num} has a blank required value")
            yield reader.line_num, values


def load_resources(path: Path) -> dict[str, Resource]:
    resources = {}
    columns = ("resource_id", "size_bytes", "origin_latency_ms")
    for line, (resource_id, raw_size, raw_latency) in _read_rows(path, columns):
        if resource_id in resources:
            raise ValueError(f"{path}:{line} has duplicate resource ID {resource_id!r}")
        try:
            resources[resource_id] = Resource(resource_id, int(raw_size), float(raw_latency))
        except ValueError as error:
            raise ValueError(f"{path}:{line} has an invalid size or latency. {error}") from error
    return resources


def iter_requests(path: Path) -> Iterator[Request]:
    for _, (client_id, resource_id) in _read_rows(path, ("client_id", "resource_id")):
        yield Request(client_id, resource_id)
