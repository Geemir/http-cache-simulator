import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cache_sim.policies import POLICIES


PROJECT = Path(__file__).resolve().parents[1]
SAMPLE_PLAN = PROJECT / "examples" / "batch-plan.json"


def run_batch(plan, output):
    return subprocess.run(
        [sys.executable, "-m", "cache_sim.batch", "--plan", str(plan), "--output", str(output)],
        cwd=PROJECT, capture_output=True, text=True,
    )


class BatchTests(unittest.TestCase):
    def test_sample_matrix_matches_independent_cli_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new" / "results.csv"
            batch = run_batch(SAMPLE_PLAN, output)
            self.assertEqual(batch.returncode, 0, batch.stderr)
            with output.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))

        actual = {
            (row["workload"], int(row["capacity_bytes"]), row["policy"], row["scope"], row["client_id"]): row
            for row in rows
        }
        self.assertEqual(len(actual), len(rows), "duplicate matrix rows")
        plan = json.loads(SAMPLE_PLAN.read_text())
        for name, paths in plan["workloads"].items():
            for size in plan["capacities_bytes"]:
                for policy in POLICIES:
                    with self.subTest(workload=name, size=size, policy=policy):
                        report = json.loads(subprocess.check_output([
                            sys.executable, "-m", "cache_sim",
                            "--resources", str(SAMPLE_PLAN.parent / paths["resources"]),
                            "--requests", str(SAMPLE_PLAN.parent / paths["requests"]),
                            "--policy", policy, "--capacity-bytes", str(size),
                            "--hit-latency-ms", str(plan["hit_latency_ms"]),
                        ], cwd=PROJECT))
                        scopes = [("overall", "", report["overall"])]
                        scopes.extend(("client", client, metrics) for client, metrics in report["clients"].items())
                        for scope, client, metrics in scopes:
                            row = actual.pop((name, size, policy, scope, client))
                            self.assertEqual(float(row["hit_latency_ms"]), plan["hit_latency_ms"])
                            for field, value in metrics.items():
                                self.assertEqual(row[field], str(value), field)
        self.assertEqual(actual, {})

    def test_failed_later_workload_preserves_existing_table_and_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resources = root / "resources.csv"
            resources.write_bytes((PROJECT / "examples" / "resources.csv").read_bytes())
            requests = str(PROJECT / "examples" / "requests.csv")
            plan = root / "plan.json"
            plan.write_text(json.dumps({
                "capacities_bytes": [10],
                "workloads": {
                    "valid": {"resources": "resources.csv", "requests": requests},
                    "broken": {"resources": "resources.csv", "requests": "missing.csv"},
                },
            }))
            for destination in (resources, plan):
                original = destination.read_bytes()
                run = run_batch(plan, destination)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("overwrite", run.stderr)
                self.assertEqual(destination.read_bytes(), original)

            output = root / "results.csv"
            output.write_text("previous completed run\n")
            run = run_batch(plan, output)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("broken", run.stderr)
            self.assertIn("missing.csv", run.stderr)
            self.assertEqual(output.read_text(), "previous completed run\n")
