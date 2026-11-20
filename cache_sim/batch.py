"""Replay every registered policy for each workload and capacity in a JSON plan."""

import argparse
import csv
import json
import math
import subprocess
import sys
from dataclasses import fields
from pathlib import Path

from .io import atomic_csv_output
from .models import Metrics
from .policies import POLICIES


def read_plan(plan_path: Path, output: Path) -> tuple[dict[str, tuple[Path, Path]], list[int], float]:
    plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    if not isinstance(plan, dict):
        raise ValueError("The plan must be a JSON object")
    capacities = plan.get("capacities_bytes")
    if not isinstance(capacities, list) or not capacities or any(
        type(size) is not int or size < 0 for size in capacities
    ):
        raise ValueError("capacities_bytes must be a nonempty list of nonnegative integers")
    if len(set(capacities)) != len(capacities):
        raise ValueError("capacities_bytes contains a duplicate capacity")
    latency = plan.get("hit_latency_ms", 5)
    if type(latency) not in (int, float) or not math.isfinite(latency) or latency < 0:
        raise ValueError("hit_latency_ms must be finite and nonnegative")

    workloads = plan.get("workloads")
    if not isinstance(workloads, dict) or not workloads:
        raise ValueError("workloads must map workload names to their input files")
    destination = output.resolve()
    if destination == plan_path.resolve():
        raise ValueError("Output CSV would overwrite the experiment plan")
    inputs = {}
    for name, files in workloads.items():
        if not name.strip() or not isinstance(files, dict) or not all(
            isinstance(files.get(key), str) and files[key].strip() for key in ("resources", "requests")
        ):
            raise ValueError(f"Workload {name!r} needs a name, resources path and requests path")
        resources = plan_path.parent / files["resources"]
        requests = plan_path.parent / files["requests"]
        if destination in (resources.resolve(), requests.resolve()):
            raise ValueError(f"Output CSV would overwrite an input of workload {name!r}")
        inputs[name] = (resources, requests)
    return inputs, capacities, latency


def run_batch(plan_path: Path, output: Path) -> None:
    inputs, capacities, latency = read_plan(plan_path, output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with atomic_csv_output(output) as stream:
        writer = csv.DictWriter(stream, lineterminator="\n", quoting=csv.QUOTE_NONNUMERIC, fieldnames=[
            "workload", "capacity_bytes", "policy", "hit_latency_ms", "scope", "client_id",
            *(field.name for field in fields(Metrics)),
        ])
        writer.writeheader()
        for name, (resources, requests) in inputs.items():
            for size in capacities:
                for policy in POLICIES:
                    run = subprocess.run([
                        sys.executable, "-m", "cache_sim", "--resources", str(resources),
                        "--requests", str(requests), "--capacity-bytes", str(size),
                        "--policy", policy, "--hit-latency-ms", str(latency),
                    ], capture_output=True, text=True)
                    if run.returncode:
                        raise ValueError(f"{name} / {size} bytes / {policy}: {run.stderr.strip()}")
                    summary = json.loads(run.stdout)
                    case = dict(workload=name, capacity_bytes=size, policy=policy, hit_latency_ms=latency)
                    writer.writerow(dict(case, scope="overall", client_id="", **summary["overall"]))
                    for client_id, metrics in summary["clients"].items():
                        writer.writerow(dict(case, scope="client", client_id=client_id, **metrics))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True, help="JSON plan with input paths relative to the plan")
    parser.add_argument("--output", type=Path, required=True, help="Destination results CSV")
    args = parser.parse_args()
    try:
        run_batch(args.plan, args.output)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")


if __name__ == "__main__":
    main()
