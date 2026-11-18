import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from .io import iter_requests, load_resources
from .policies import POLICIES
from .simulator import simulate


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate a shared HTTP cache.")
    parser.add_argument("--resources", type=Path, required=True, help="Resource metadata CSV")
    parser.add_argument("--requests", type=Path, required=True, help="Chronological request CSV")
    parser.add_argument("--capacity-bytes", type=int, default=102_400)
    parser.add_argument("--hit-latency-ms", type=float, default=5.0)
    parser.add_argument("--policy", choices=POLICIES, default="fifo")
    args = parser.parse_args()

    try:
        result = simulate(
            load_resources(args.resources),
            iter_requests(args.requests),
            capacity_bytes=args.capacity_bytes,
            hit_latency_ms=args.hit_latency_ms,
            choose_victim=POLICIES[args.policy],
        )
    except (OSError, ValueError, csv.Error) as error:
        parser.error(str(error))

    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
