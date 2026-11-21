import unittest

from cache_sim.models import Request, Resource
from cache_sim.policies import POLICIES, lfu_victim
from cache_sim.simulator import simulate


class BaselinePolicyTests(unittest.TestCase):
    def test_each_policy_evicts_in_its_own_order_until_there_is_space(self):
        resources = {
            "a": Resource("a", 4, 20),
            "b": Resource("b", 4, 20),
            "c": Resource("c", 4, 20),
            "d": Resource("d", 8, 20),
        }
        requests = [Request("p", name) for name in "abcbbbaacd"]
        expected = {
            "fifo": (("a", "b"), ("c", "d")),
            "lru": (("b", "a"), ("c", "d")),
            "lfu": (("c", "a"), ("b", "d")),
        }
        for name, (evicted, remaining) in expected.items():
            with self.subTest(policy=name):
                events = []
                simulate(
                    resources,
                    requests,
                    capacity_bytes=12,
                    choose_victim=POLICIES[name],
                    on_event=events.append,
                )
                self.assertEqual(events[-1].evicted, evicted)
                self.assertEqual(events[-1].cache_contents_oldest_first, remaining)
                self.assertEqual(events[-1].cache_used_bytes, 12)

    def test_exact_fit_oversized_resource_and_shared_cache(self):
        resources = {
            "a": Resource("a", 4, 20),
            "b": Resource("b", 6, 30),
            "large": Resource("large", 11, 40),
        }
        requests = [
            Request("p", "a"),
            Request("q", "b"),
            Request("q", "a"),
            Request("p", "large"),
            Request("q", "large"),
            Request("p", "b"),
        ]
        for name, choose_victim in POLICIES.items():
            with self.subTest(policy=name):
                events = []
                result = simulate(
                    resources,
                    requests,
                    capacity_bytes=10,
                    choose_victim=choose_victim,
                    on_event=events.append,
                )
                self.assertEqual([event.hit for event in events], [False, False, True, False, False, True])
                self.assertEqual([event.evicted for event in events], [()] * len(requests))
                self.assertEqual(events[1].cache_used_bytes, 10)
                for oversized in events[3:5]:
                    self.assertEqual(oversized.cache_used_bytes, 10)
                    self.assertEqual(oversized.cache_contents_oldest_first, ("a", "b"))
                    self.assertEqual(oversized.origin_bytes, 11)
                    self.assertEqual(oversized.response_ms, 40)
                self.assertEqual(result.clients["p"].hits, 1)
                self.assertEqual(result.clients["q"].hits, 1)

    def test_lfu_breaks_frequency_ties_by_last_access(self):
        resources = {name: Resource(name, 4, 20) for name in "abc"}
        requests = [Request("p", name) for name in "abbac"]
        events = []
        simulate(
            resources,
            requests,
            capacity_bytes=8,
            choose_victim=lfu_victim,
            on_event=events.append,
        )
        self.assertEqual(events[-1].evicted, ("b",))

    def test_lfu_reinsertion_resets_frequency(self):
        resources = {
            "a": Resource("a", 4, 20),
            "b": Resource("b", 4, 20),
            "c": Resource("c", 4, 20),
            "full": Resource("full", 8, 20),
        }
        requests = [Request("p", name) for name in ("a", "a", "a", "full", "b", "a", "b", "c")]
        events = []
        simulate(
            resources,
            requests,
            capacity_bytes=8,
            choose_victim=lfu_victim,
            on_event=events.append,
        )
        self.assertEqual(events[3].evicted, ("a",))
        self.assertFalse(events[5].hit)
        self.assertEqual(events[5].cache_contents_oldest_first, ("b", "a"))
        self.assertEqual(events[7].evicted, ("a",))
