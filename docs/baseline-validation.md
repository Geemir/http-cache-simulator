# Baseline validation

## Issue #2 — Replacement policy checks

FIFO, LRU, and LFU are selectable through `--policy`. The focused tests in
`tests/test_policies.py` cover the distinct eviction orders, repeated evictions,
exact capacity, oversized misses that leave the cache intact, and hits across
clients. They also check LFU's least-recently-used tie-break and that an evicted
resource starts with a fresh frequency when it is reinserted.

```text
python -m unittest discover -s tests -v
```

Expected on this branch: **10 tests pass**, including the three reference runs
inside `test_policies_match_all_reference_rows`. Verified with Python 3.12.14.

## Issue #5 — Course reference replay

Each run used an empty shared cache with a capacity of 102,400 B (100 KiB),
a 5 ms hit latency, and the resource's origin latency on a miss. Requests were
processed in input order.

| Policy | Hits, expected / actual | Misses, expected / actual | Request hit rate, expected / actual | Origin traffic (KiB), expected / actual | Mean response (ms), expected / actual | Matching events |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FIFO | 3 / 3 | 12 / 12 | 20.00% / 20.00% | 412 / 412 | 95.33 / 95.33 | 15 / 15 |
| LRU | 3 / 3 | 12 / 12 | 20.00% / 20.00% | 394 / 394 | 92.33 / 92.33 | 15 / 15 |
| LFU | 4 / 4 | 11 / 11 | 26.67% / 26.67% | 362 / 362 | 84.33 / 84.33 | 15 / 15 |

All 45 events matched the corresponding `expected_*.csv` rows, including the
hit/miss, eviction order, cache contents and occupancy, latency, and cumulative
hits and origin bytes. The reference test maps simulator URLs to the A–E IDs in
the answer key. Counts, byte totals, and per-request latencies matched exactly.
The summary displays hit rates and mean latencies rounded to two decimal places
to match `reference_trace_answer_key.md`. One KiB is 1,024 B.

Run from the repository root. Each command writes the event CSV and prints
the summary JSON.

```text
python -m cache_sim --resources resources.csv --requests requests_reference.csv --capacity-bytes 102400 --hit-latency-ms 5 --policy fifo --events-csv fifo-events.csv
python -m cache_sim --resources resources.csv --requests requests_reference.csv --capacity-bytes 102400 --hit-latency-ms 5 --policy lru --events-csv lru-events.csv
python -m cache_sim --resources resources.csv --requests requests_reference.csv --capacity-bytes 102400 --hit-latency-ms 5 --policy lfu --events-csv lfu-events.csv
```
