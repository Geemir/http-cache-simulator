# ICS HTTP Cache Simulator

This Python command-line simulator replays chronological requests from multiple clients against a shared HTTP cache. The starter includes FIFO, byte capacity accounting, and JSON metrics for the full trace and for each client.

## Quick start

Use Python 3.10 or newer from the repository root. The starter has no third-party dependencies.

```shell
python -m cache_sim --resources examples/resources.csv --requests examples/requests.csv --capacity-bytes 10 --policy fifo
python -m unittest discover -s tests -v
```

The included trace has seven requests, two cache hits, and 35 bytes of origin traffic. The CLI defaults to 102,400 bytes of cache capacity and 5 ms per hit. A miss uses the latency in the resource table. Resources larger than the capacity leave cache contents intact.

## Starter input and output

- The example resource CSV uses `resource_id,size_bytes,origin_latency_ms`.
- The example request CSV uses `client_id,resource_id`. Put the rows in chronological order. Named extra columns are ignored.
- The JSON output includes request and byte hit ratios as fractions between zero and one, mean response time in milliseconds, and origin traffic in bytes.

The sample CSVs are synthetic fixtures. The course CSV format and published reference outputs still need validation. [Team roadmap](docs/roadmap.md)
