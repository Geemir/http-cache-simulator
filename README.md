# ICS HTTP Cache Simulator

[简体中文](README.zh-CN.md)

This Python command-line simulator replays chronological requests from multiple clients against a shared HTTP cache. It supports FIFO, LRU, and LFU with LRU tie-breaking. It reports JSON metrics for the full trace and for each client.

## Quick start

Use Python 3.10 or newer from the repository root. The simulator has no third-party dependencies.

```shell
python -m cache_sim --resources examples/resources.csv --requests examples/requests.csv --capacity-bytes 10 --policy fifo
python -m unittest discover -s tests -v
```

The included trace has seven requests, two cache hits, and 35 bytes of origin traffic. The CLI defaults to 102,400 bytes of cache capacity and 5 ms per hit. A miss uses the latency in the resource table. Resources larger than the capacity leave cache contents intact.

## Course reference trace

Place the course `resources.csv` and `requests_reference.csv` in the repository root. These files identify resources by `scheme`, `host`, and `path`. The simulator uses the resulting URLs as cache keys and processes rows in file order. HTTP metadata such as status and Cache-Control has no effect under the course simulation assumptions.

```shell
python -m cache_sim --resources resources.csv --requests requests_reference.csv --policy lfu --events-csv lfu-events.csv
```

Use `--policy fifo`, `--policy lru`, or `--policy lfu` to select the rule. The optional events CSV records each request's outcome, evictions, cache contents in oldest-insertion order, cache occupancy in bytes, response time, and running totals for origin bytes and hits. The eviction and cache contents columns contain JSON arrays of resource IDs.

With the course `expected_fifo.csv`, `expected_lru.csv`, and `expected_lfu.csv` also in the root, the test suite compares every request against the reference output.

## Input and output

- The synthetic example uses `resource_id` in both CSVs in place of the three URL columns. The resource CSV needs `size_bytes` and `origin_latency_ms`. The requests CSV needs `client_id`. Named extra columns are ignored.
- The JSON output includes request and byte hit ratios as fractions between zero and one, mean response time in milliseconds, and origin traffic in bytes.

[Team roadmap](docs/roadmap.md)
