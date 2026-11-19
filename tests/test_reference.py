import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
POLICIES = ("fifo", "lru", "lfu")
REFERENCE_IDS = {
    "https://learn.university.edu/courses/ics/index.html": "A",
    "https://learn.university.edu/static/main.css": "B",
    "https://learn.university.edu/static/logo.svg": "C",
    "https://cdn.university.edu/images/avatar-default.png": "D",
    "https://pypi.org/static/css/warehouse.css": "E",
}


class ReferenceTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        paths = [
            PROJECT / "resources.csv",
            PROJECT / "requests_reference.csv",
            *(PROJECT / f"expected_{policy}.csv" for policy in POLICIES),
        ]
        if not any(path.is_file() for path in paths):
            raise unittest.SkipTest("Place the five course reference CSVs in the repository root")
        missing = [path.name for path in paths if not path.is_file()]
        if missing:
            raise AssertionError(f"Incomplete reference files: {', '.join(missing)}")

    def test_policies_match_all_reference_rows(self):
        for policy in POLICIES:
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "events.csv"
                run = subprocess.run(
                    [
                        sys.executable, "-m", "cache_sim",
                        "--resources", "resources.csv",
                        "--requests", "requests_reference.csv",
                        "--policy", policy,
                        "--events-csv", str(output),
                    ],
                    cwd=PROJECT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                with output.open(newline="", encoding="utf-8") as stream:
                    actual = list(csv.DictReader(stream))
                with (PROJECT / f"expected_{policy}.csv").open(newline="", encoding="utf-8-sig") as stream:
                    expected = list(csv.DictReader(stream))

                self.assertEqual(len(actual), len(expected))
                for event, target in zip(actual, expected, strict=True):
                    with self.subTest(step=target["step"]):
                        self.assertEqual(event["step"], target["step"])
                        self.assertEqual(REFERENCE_IDS[event["resource_id"]], target["resource_id"])
                        self.assertEqual(event["client_id"], target["client_id"])
                        self.assertEqual(event["result"], target["result"])
                        evicted = [REFERENCE_IDS[url] for url in json.loads(event["evicted"])]
                        contents = [REFERENCE_IDS[url] for url in json.loads(event["cache_contents_oldest_first"])]
                        self.assertEqual(",".join(evicted) or "-", target["evicted"])
                        self.assertEqual(",".join(contents), target["cache_contents_oldest_first"])
                        self.assertEqual(int(event["cache_used_bytes"]), 1024 * int(target["cache_used_KiB"]))
                        self.assertEqual(float(event["response_ms"]), float(target["response_ms"]))
                        self.assertEqual(event["cumulative_origin_bytes"], target["cumulative_origin_bytes"])
                        self.assertEqual(event["cumulative_hits"], target["cumulative_hits"])

                metrics = json.loads(run.stdout)
                overall = metrics["overall"]
                self.assertEqual(overall["requests"], len(expected))
                self.assertEqual(overall["hits"], int(expected[-1]["cumulative_hits"]))
                self.assertEqual(overall["origin_bytes"], int(expected[-1]["cumulative_origin_bytes"]))
                self.assertAlmostEqual(
                    overall["mean_response_ms"],
                    sum(float(row["response_ms"]) for row in expected) / len(expected),
                )
                self.assertEqual(sum(client["requests"] for client in metrics["clients"].values()), len(expected))
                self.assertEqual(sum(client["origin_bytes"] for client in metrics["clients"].values()), overall["origin_bytes"])
