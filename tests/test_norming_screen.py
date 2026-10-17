import unittest

from norming.screen import screen, REQUIRED_N


def fixture(values, correct=20, concordant=20):
    assert len(values) == 20
    obs = [{"participant_slot": str(i+1), "concept_id": "C01",
            "valence_rating": str(v)} for i, v in enumerate(values)]
    codes = [{"participant_slot": str(i+1), "concept_id": "C01",
              "rater_a_correct": "1",
              "rater_b_correct": "1" if i < concordant else "0",
              "adjudicated_correct": "1" if i < correct else "0"}
             for i in range(20)]
    return obs, codes


class PrespecifiedScreenTests(unittest.TestCase):
    def test_provisional_retention_not_neutrality_certification(self):
        rows, coded = fixture([-1, 0, 1, 0] * 5)
        result = screen(rows, coded)[0]
        self.assertEqual(result["status"], "retain_for_validation")
        self.assertEqual(result["mean_valence"], 0)
        self.assertLess(result["ci95_lower"], 0)
        self.assertGreater(result["ci95_upper"], 0)

    def test_excludes_absolute_mean_over_half(self):
        rows, coded = fixture([1] * 12 + [0] * 8)
        result = screen(rows, coded)[0]
        self.assertEqual(result["status"], "reject")
        self.assertIn("absolute mean valence exceeds 0.5", result["reasons"])

    def test_excludes_positive_ci_even_when_mean_does_not_exceed_half(self):
        rows, coded = fixture([1] * 10 + [0] * 10)
        result = screen(rows, coded)[0]
        self.assertEqual(result["mean_valence"], 0.5)
        self.assertGreater(result["ci95_lower"], 0)
        self.assertIn("95% t confidence interval excludes 0", result["reasons"])

    def test_denotation_filter_is_stricter(self):
        rows, coded = fixture([-1, 0, 1, 0] * 5, correct=17)
        self.assertEqual(screen(rows, coded)[0]["status"], "reject")
        rows, coded = fixture([-1, 0, 1, 0] * 5, concordant=16)
        self.assertEqual(screen(rows, coded)[0]["status"], "reject")

    def test_insufficient_instead_of_false_retention(self):
        rows, coded = fixture([-1, 0, 1, 0] * 5)
        self.assertEqual(screen(rows[:-1], coded[:-1])[0]["status"], "insufficient")

    def test_malformed_links_fail_closed(self):
        rows, coded = fixture([-1, 0, 1, 0] * 5)
        with self.assertRaises(ValueError):
            screen(rows, coded + [coded[0]])
        with self.assertRaises(ValueError):
            screen(rows, [dict(coded[0], rater_a_correct="not-coded")] + coded[1:])
        with self.assertRaises(ValueError):
            screen([dict(rows[0], valence_rating="4")] + rows[1:], coded)


if __name__ == "__main__":
    unittest.main()
