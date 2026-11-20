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

The six files from Oscar’s course handoff are already in the repository root. The resource table identifies each URL by `scheme`, `host`, and `path` and gives its `size_bytes` and `origin_latency_ms`. The request table uses the same URL columns plus `timestamp`, `client_id`, and `method`. Its 15 GET requests from three clients are in chronological order. The simulator replays the rows in file order. HTTP status and Cache-Control have no effect under the course assumptions.

```shell
mkdir -p results
for policy in fifo lru lfu; do
  python -m cache_sim --resources resources.csv --requests requests_reference.csv \
    --capacity-bytes 102400 --hit-latency-ms 5 --policy "$policy" \
    --events-csv "results/$policy-events.csv" > "results/$policy-summary.json"
done
python -m unittest discover -s tests -p test_reference.py -v
```

Use `--policy fifo`, `--policy lru`, or `--policy lfu` to select the rule. The optional events CSV records each request's outcome, evictions, cache contents in oldest-insertion order, cache occupancy in bytes, response time, and running totals for origin bytes and hits. The eviction and cache contents columns contain JSON arrays of resource IDs.

The reference test maps logged URLs to the A–E aliases in the answer key, converts expected KiB to bytes (1 KiB = 1,024 bytes), and checks every event against the three `expected_*.csv` files. For a quick check of `overall`, FIFO, LRU and LFU yield 3, 3 and 4 hits and 421,888, 403,456 and 370,688 origin bytes, respectively.

## Oscar’s 10-request demo

```shell
python -m cache_sim --resources examples/oscar/demo/resources.csv \
  --requests examples/oscar/demo/requests.csv --capacity-bytes 102400 \
  --hit-latency-ms 5 --policy fifo --events-csv oscar-fifo-events.csv
```

Change the policy to `lru` or `lfu` to compare step 7. FIFO evicts A, LRU evicts B and LFU evicts C. At step 8 the 120 KiB resource misses and leaves each cache intact. [Oscar’s hand calculation](docs/oscar_hand_calculation.md)

## Input and output

- The synthetic example uses `resource_id` in both CSVs in place of the three URL columns. The resource CSV needs `size_bytes` and `origin_latency_ms`. The requests CSV needs `client_id`. Named extra columns are ignored.
- The JSON output includes request and byte hit ratios as fractions between zero and one, mean response time in milliseconds, and origin traffic in bytes.

[Team roadmap](docs/roadmap.md)
