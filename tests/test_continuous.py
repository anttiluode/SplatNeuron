import unittest

import numpy as np

from splatneuron.continuous import ContinuousDomain, ContinuousFieldEpisode, FixedCapacityTracker


class ContinuousTests(unittest.TestCase):
    def test_query_is_truly_off_grid_and_budget_is_exact(self):
        domain = ContinuousDomain()
        target = np.array([0.333, 0.417, 0.371, 0.219])
        ep = ContinuousFieldEpisode(
            target,
            1,
            np.random.default_rng(1),
            domain=domain,
            distractors=0,
            noise_sd=0.0,
        )
        tracker = FixedCapacityTracker(
            [[0.28, 0.30, 0.28, 0.12], [0.70, 0.68, 0.73, 0.61]],
            domain=domain,
        )
        res = tracker.observe(ep, budget=8, mode="hybrid", plastic=True)
        self.assertEqual(res.work, 8)
        self.assertEqual(ep.observations, 8)
        self.assertEqual(res.coordinate.shape, (4,))

    def test_cache_waits_and_hybrid_can_route(self):
        anchors = [[0.28, 0.30, 0.28, 0.12], [0.70, 0.68, 0.73, 0.61]]
        near = np.array(anchors[0], dtype=float)
        far = np.array([0.50, 0.50, 0.50, 0.40])

        cache = FixedCapacityTracker(anchors)
        ep1 = ContinuousFieldEpisode(near, 1, np.random.default_rng(2), distractors=0, noise_sd=0.0)
        self.assertEqual(cache.observe(ep1, budget=8, mode="cache", plastic=False).action, "WAIT")

        route = FixedCapacityTracker(anchors, admission_threshold=0.99)
        ep2 = ContinuousFieldEpisode(far, 1, np.random.default_rng(3), distractors=0, noise_sd=0.0)
        self.assertEqual(route.observe(ep2, budget=8, mode="hybrid", plastic=False).action, "ROUTE")

    def test_plastic_route_keeps_capacity_fixed(self):
        anchors = [[0.28, 0.30, 0.28, 0.12], [0.70, 0.68, 0.73, 0.61]]
        tracker = FixedCapacityTracker(anchors, admission_threshold=0.99)
        before = [a.copy() for a in tracker.anchors]
        ep = ContinuousFieldEpisode(
            [0.35, 0.36, 0.35, 0.18],
            1,
            np.random.default_rng(4),
            distractors=0,
            noise_sd=0.0,
        )
        tracker.observe(ep, budget=8, mode="hybrid", plastic=True)
        self.assertEqual(len(tracker.anchors), 2)
        self.assertTrue(any(np.linalg.norm(a - b) > 1e-12 for a, b in zip(tracker.anchors, before)))


if __name__ == "__main__":
    unittest.main()
