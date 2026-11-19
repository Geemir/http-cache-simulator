import argparse
import csv
import json
from contextlib import ExitStack
from dataclasses import asdict
from pathlib import Path

from .io import event_csv_writer, iter_requests, load_resources
from .policies import POLICIES
from .simulator import simulate


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate a shared HTTP cache.")
    parser.add_argument("--resources", type=Path, required=True, help="Resource metadata CSV")
    parser.add_argument("--requests", type=Path, required=True, help="Chronological request CSV")
    parser.add_argument("--capacity-bytes", type=int, default=102_400)
    parser.add_argument("--hit-latency-ms", type=float, default=5.0)
    parser.add_argument("--policy", choices=POLICIES, default="fifo")
    parser.add_argument("--events-csv", type=Path, help="Write per-request events to this CSV")
    args = parser.parse_args()

    try:
        with ExitStack() as stack:
            on_event = None
            if args.events_csv is not None:
                if args.events_csv.resolve() in (args.resources.resolve(), args.requests.resolve()):
                    parser.error("--events-csv must be separate from the input files")
                on_event = stack.enter_context(event_csv_writer(args.events_csv))
            result = simulate(
                load_resources(args.resources),
                iter_requests(args.requests),
                capacity_bytes=args.capacity_bytes,
                hit_latency_ms=args.hit_latency_ms,
                choose_victim=POLICIES[args.policy],
                on_event=on_event,
            )
    except (OSError, ValueError, csv.Error) as error:
        parser.error(str(error))

    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
