import csv
import io
import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from norming.allocation import Candidate, allocate_norming, load_candidates


FIXTURE = Path(__file__).resolve().parents[1] / "norming" / "candidates.csv"


class NormingTests(unittest.TestCase):
    def test_candidate_inventory_has_twenty_distinct_entries(self):
        candidates = load_candidates(FIXTURE)
        self.assertEqual(len(candidates), 20)
        self.assertEqual(len({x.definition for x in candidates}), 20)

    def test_balanced_concepts_and_forms(self):
        candidates = load_candidates(FIXTURE)
        assignments = allocate_norming(candidates)
        self.assertEqual(len(assignments), 40)
        self.assertEqual(assignments, allocate_norming(candidates))
        all_items = [item for assignment in assignments for item in assignment.items]
        self.assertEqual(len(all_items), 400)
        counts = Counter(item.concept_id for item in all_items)
        form_counts = Counter(item.presented_nonce_form for item in all_items)
        self.assertEqual(set(counts.values()), {20})
        self.assertEqual(set(form_counts.values()), {20})
        for a in assignments:
            self.assertEqual(len(a.items), 10)
            self.assertEqual(len({x.concept_id for x in a.items}), 10)

    def test_invalid_configuration_is_rejected(self):
        candidates = load_candidates(FIXTURE)
        for opts in ({"participants": 39}, {"items_per_participant": 0}, {"items_per_participant": 21}):
            with self.subTest(opts=opts), self.assertRaises(ValueError):
                allocate_norming(candidates, **opts)

    def test_duplicate_form_is_rejected(self):
        with TemporaryDirectory() as directory:
            p = Path(directory) / "items.csv"
            p.write_text(
                "concept_id,candidate_nonce_form,definition\n"
                "C1,mavren,One concept\n"
                "C2,mavren,Another concept\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_candidates(p)


if __name__ == "__main__":
    unittest.main()
