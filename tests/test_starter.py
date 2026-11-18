import json
import subprocess
import sys
import unittest
from pathlib import Path

from cache_sim.models import Request, Resource
from cache_sim.simulator import simulate


PROJECT = Path(__file__).resolve().parents[1]
EXAMPLES = PROJECT / "examples"


class ResourceTests(unittest.TestCase):
    def test_resource_rejects_values_that_would_corrupt_metrics(self):
        for size_bytes, origin_latency_ms in [(-1, 1), (1, -1), (1, float("nan"))]:
            with self.subTest(size_bytes=size_bytes, origin_latency_ms=origin_latency_ms):
                with self.assertRaises(ValueError):
                    Resource("invalid", size_bytes, origin_latency_ms)


class SimulatorTests(unittest.TestCase):
    def test_fifo_hits_preserve_insertion_order_and_one_miss_can_evict_twice(self):
        resources = {
            "a": Resource("a", 4, 20),
            "b": Resource("b", 6, 40),
            "c": Resource("c", 4, 60),
            "d": Resource("d", 11, 80),
            "e": Resource("e", 10, 100),
        }
        requests = [
            Request("p", "a"),
            Request("q", "b"),
            Request("q", "a"),
            Request("p", "c"),
            Request("p", "d"),
            Request("q", "b"),
            Request("p", "e"),
        ]
        events = []

        result = simulate(resources, iter(requests), capacity_bytes=10, on_event=events.append)

        self.assertEqual([event.hit for event in events], [False, False, True, False, False, True, False])
        self.assertEqual(events[3].evicted, ("a",))
        self.assertEqual(events[4].evicted, ())
        self.assertEqual(events[6].evicted, ("b", "c"))
        self.assertEqual(result.overall.origin_bytes, 35)
        self.assertAlmostEqual(result.overall.request_hit_ratio, 2 / 7)
        self.assertAlmostEqual(result.overall.byte_hit_ratio, 10 / 45)
        self.assertAlmostEqual(result.overall.mean_response_ms, 310 / 7)
        self.assertEqual(result.clients["p"].origin_bytes, 29)
        self.assertAlmostEqual(result.clients["q"].request_hit_ratio, 2 / 3)
        self.assertAlmostEqual(result.clients["q"].mean_response_ms, 50 / 3)

    def test_empty_trace_yields_zero_totals_and_no_clients(self):
        result = simulate({}, [], capacity_bytes=0)

        self.assertEqual(result.overall.requests, 0)
        self.assertEqual(result.overall.mean_response_ms, 0)
        self.assertEqual(result.clients, {})

    def test_unknown_resource_reports_the_request_number(self):
        with self.assertRaisesRegex(ValueError, "Request 1.*unknown resource 'missing'"):
            simulate({}, [Request("p", "missing")])


class CommandLineTests(unittest.TestCase):
    def test_example_csvs_produce_json_statistics(self):
        result = subprocess.run(
            [
                sys.executable, "-m", "cache_sim",
                "--resources", str(EXAMPLES / "resources.csv"),
                "--requests", str(EXAMPLES / "requests.csv"),
                "--capacity-bytes", "10",
                "--hit-latency-ms", "2",
                "--policy", "fifo",
            ],
            cwd=PROJECT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(result.stdout)

        self.assertEqual(report["overall"]["requests"], 7)
        self.assertEqual(report["overall"]["origin_bytes"], 35)
        self.assertAlmostEqual(report["overall"]["mean_response_ms"], 304 / 7)
        self.assertEqual(set(report["clients"]), {"p", "q"})
