import unittest

import numpy as np

from splatneuron import (
    BranchingReceiver,
    ReceiverAnchor,
    SplatWorld,
    geometry_distance,
    make_default_bank,
    route_receiver,
    wait_same_receiver,
)


class CoreTests(unittest.TestCase):
    def test_bank_is_normalized_and_gram_diagonal_is_one(self):
        geoms, templates, gram = make_default_bank(size=20)
        self.assertEqual(len(geoms), 300)
        self.assertTrue(np.allclose(np.linalg.norm(templates, axis=1), 1.0, atol=1e-10))
        self.assertTrue(np.allclose(np.real(np.diag(gram)), 1.0, atol=1e-10))

    def test_geometry_distance_is_symmetric(self):
        geoms, _, _ = make_default_bank(size=16)
        self.assertAlmostEqual(geometry_distance(geoms[0], geoms[-1]), geometry_distance(geoms[-1], geoms[0]))

    def test_consolidation_moves_anchor_toward_destination(self):
        geoms, _, _ = make_default_bank(size=16)
        anchor = ReceiverAnchor(geoms[0], plasticity_rate=0.25)
        before = geometry_distance(anchor.geometry, geoms[-1])
        anchor.consolidate(geoms[-1], evidence=1.0)
        after = geometry_distance(anchor.geometry, geoms[-1])
        self.assertLess(after, before)

    def test_route_can_change_observation_map_while_wait_cannot(self):
        geoms, _, gram = make_default_bank(size=20)
        target = len(geoms) - 1
        rng1 = np.random.default_rng(7)
        rng2 = np.random.default_rng(7)
        ep_wait = SplatWorld(gram, target, rng1, distractors=0, noise_sd=0.01).episode(1)
        ep_route = SplatWorld(gram, target, rng2, distractors=0, noise_sd=0.01).episode(1)
        wait = wait_same_receiver(ep_wait, 0, 300)
        route = route_receiver(ep_route, geoms, geoms[0])
        self.assertGreater(abs(route.response), abs(wait.response))
        self.assertLessEqual(route.work, len(geoms))

    def test_branching_receiver_can_grow_after_repeated_far_routes(self):
        geoms, _, gram = make_default_bank(size=20)
        target = len(geoms) - 1
        br = BranchingReceiver(geoms[0], max_branches=2, growth_patience=2, far_threshold=1.0)
        grew = False
        for k in range(3):
            ep = SplatWorld(gram, target, np.random.default_rng(100 + k), distractors=0, noise_sd=0.0).episode(1)
            _, did_grow = br.observe(ep, geoms)
            grew = grew or did_grow
        self.assertTrue(grew)
        self.assertEqual(len(br.branches), 2)


if __name__ == "__main__":
    unittest.main()
