import unittest

from norming.preview import render_preview
from norming.summary import summarise


class PreviewAndSummaryTests(unittest.TestCase):
    def test_preview_is_pilot_only_and_contains_ten_items(self):
        html = render_preview(3)
        self.assertEqual(html.count('class="item"'), 10)
        self.assertIn("NOT hosted", html)
        self.assertIn("valence_1", html)
        self.assertIn("valence_10", html)
        self.assertIn("meaning_paraphrase", html)
        self.assertNotIn("PROLIFIC_PID", html)

    def test_invalid_preview_slot_fails(self):
        for slot in (0, 41, True):
            with self.subTest(slot=slot), self.assertRaises(ValueError):
                render_preview(slot)

    def test_summary_does_not_invent_data(self):
        with self.assertRaisesRegex(ValueError, "No participant"):
            summarise([])

    def test_summary_of_explicit_synthetic_fixture(self):
        rows = [
            dict(participant_slot="1", concept_id="C01", presented_nonce_form="mavren",
                 valence_rating="-2", meaning_paraphrase="An invented practice", confidence="80"),
            dict(participant_slot="2", concept_id="C01", presented_nonce_form="solven",
                 valence_rating="2", meaning_paraphrase="The same invented practice", confidence="90"),
        ]
        result = summarise(rows)
        self.assertEqual(result[0]["n"], 2)
        self.assertEqual(result[0]["mean_valence"], 0)
        self.assertEqual(result[0]["negative_fraction"], 0.5)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            summarise(rows + [rows[0]])
        with self.assertRaisesRegex(ValueError, "Out-of-range"):
            summarise([dict(rows[0], valence_rating="5")])


if __name__ == "__main__":
    unittest.main()
