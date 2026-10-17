import unittest
from collections import Counter

from semantic_drift.protocol import Condition
from semantic_drift.randomization import allocate_chains


CONCEPTS = ("wait", "share", "reflect", "pause")
FORMS = ("mavren", "solven", "kalora", "tumari")


class RandomizationTests(unittest.TestCase):
    def allocations(self, n=4, seed=281):
        return allocate_chains(
            chains_per_condition=n,
            concept_ids=CONCEPTS,
            nonce_forms=FORMS,
            seed=seed,
        )

    def test_deterministic_and_balanced(self):
        assignments = self.allocations(8)
        self.assertEqual(assignments, self.allocations(8))
        self.assertEqual(len(assignments), 24)
        self.assertEqual(Counter(a.condition for a in assignments), {
            Condition.HUMAN_ONLY: 8, Condition.HUMAN_EDITED: 8, Condition.LLM_MEDIATED: 8,
        })
        self.assertEqual(len({a.chain_id for a in assignments}), 24)

    def test_complete_latin_square_counterbalance(self):
        for condition in Condition:
            subset = [a for a in self.allocations(4) if a.condition is condition]
            for concept in CONCEPTS:
                self.assertEqual(
                    {dict(a.concept_to_nonce_form)[concept] for a in subset}, set(FORMS)
                )
            for assignment in subset:
                self.assertEqual(set(dict(assignment.concept_to_nonce_form)), set(CONCEPTS))
                self.assertEqual(set(dict(assignment.concept_to_nonce_form).values()), set(FORMS))

    def test_non_multiple_has_at_most_one_count_difference(self):
        for condition in Condition:
            subset = [a for a in self.allocations(7) if a.condition is condition]
            for concept in CONCEPTS:
                counts = Counter(dict(a.concept_to_nonce_form)[concept] for a in subset)
                self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            self.allocations(0)
        with self.assertRaises(ValueError):
            allocate_chains(chains_per_condition=2, concept_ids=("x",), nonce_forms=("x", "y"), seed=1)
        with self.assertRaises(ValueError):
            allocate_chains(chains_per_condition=2, concept_ids=("x", "x"), nonce_forms=("mavren", "solven"), seed=1)


if __name__ == "__main__":
    unittest.main()
