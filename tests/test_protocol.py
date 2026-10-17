import unittest

from semantic_drift.protocol import (
    Condition,
    MediatedRewrite,
    HumanEdit,
    ParticipantResponse,
    advance_chain,
    start_chain,
)


def response(generation: int, *, text: str = "Someone practiced mavren carefully."):
    return ParticipantResponse(
        participant_code=f"anon-{generation}",
        valence_rating=50,
        meaning_paraphrase="Pauses before responding to a request.",
        confidence=80,
        human_produced_text=text,
    )


def rewrite(text: str, generation: int):
    return MediatedRewrite(
        output_text="Rewritten: " + text,
        model_id="mock-identity",
        model_version="test-only",
        prompt_sha256="a" * 64,
        run_id=f"test-run-{generation}",
        decoding_parameters_json='{"temperature":0}',
    )


def human_edit(text: str, generation: int):
    return HumanEdit("Edited: " + text, f"editor-{generation}", "b" * 64, f"edit-{generation}")


class ProtocolTests(unittest.TestCase):
    def make_chain(self, condition):
        return start_chain(
            "chain-1", condition, "pause-before-reply", "mavren",
            "Mavren is a practice of pausing before replying to a request. mavren.",
        )

    def test_exactly_four_rewrites_then_two_washout_steps(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        initial = state
        for generation in range(1, 7):
            source = state.seed_text if not state.records else state.records[-1].human_produced_text
            media = rewrite(source, generation) if generation <= 4 else None
            state = advance_chain(state, response(generation), media)
            record = state.records[-1]
            self.assertEqual(record.generation, generation)
            self.assertEqual(record.transmission_source_text, source)
            self.assertEqual(record.mediated_rewrite is not None, generation <= 4)
            self.assertEqual(record.received_text, media.output_text if media else source)
        self.assertEqual(len(initial.records), 0, "append must not mutate prior states")
        self.assertEqual(state.completed_generation, 6)
        self.assertEqual(sum(r.mediated_rewrite is not None for r in state.records), 4)
        with self.assertRaises(ValueError):
            advance_chain(state, response(7))

    def test_human_editor_four_steps_and_two_washout_steps(self):
        state = self.make_chain(Condition.HUMAN_EDITED)
        for g in range(1, 7):
            previous = state.seed_text if not state.records else state.records[-1].human_produced_text
            edit = human_edit(previous, g) if g <= 4 else None
            state = advance_chain(state, response(g), human_edit=edit)
            self.assertEqual(state.records[-1].received_text, edit.output_text if edit else previous)
            self.assertEqual(state.records[-1].human_edit is not None, g <= 4)
            self.assertIsNone(state.records[-1].mediated_rewrite)

    def test_human_edit_missing_or_misplaced_fails(self):
        with self.assertRaisesRegex(ValueError, "requires a versioned human edit"):
            advance_chain(self.make_chain(Condition.HUMAN_EDITED), response(1))
        with self.assertRaisesRegex(ValueError, "prohibits human editing"):
            advance_chain(self.make_chain(Condition.HUMAN_ONLY), response(1), human_edit=human_edit("mavren", 1))
        state = self.make_chain(Condition.HUMAN_EDITED)
        for g in range(1, 5):
            state = advance_chain(state, response(g), human_edit=human_edit("mavren", g))
        with self.assertRaisesRegex(ValueError, "prohibits human editing"):
            advance_chain(state, response(5), human_edit=human_edit("mavren", 5))

    def test_human_editor_provenance_and_word_preservation(self):
        with self.assertRaises(ValueError):
            HumanEdit("mavren", "editor", "bad-hash", "run")
        with self.assertRaisesRegex(ValueError, "exact nonce_form"):
            advance_chain(self.make_chain(Condition.HUMAN_EDITED), response(1), human_edit=human_edit("no target", 1))

    def test_human_only_never_rewrites(self):
        state = self.make_chain(Condition.HUMAN_ONLY)
        for generation in range(1, 7):
            state = advance_chain(state, response(generation))
            self.assertIsNone(state.records[-1].mediated_rewrite)
        self.assertEqual(state.records[0].received_text, state.seed_text)

    def test_missing_rewrite_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "requires"):
            advance_chain(self.make_chain(Condition.LLM_MEDIATED), response(1))

    def test_control_rewrite_rejected(self):
        with self.assertRaisesRegex(ValueError, "prohibits"):
            advance_chain(self.make_chain(Condition.HUMAN_ONLY), response(1), rewrite("mavren", 1))

    def test_rewrite_rejected_during_washout(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        for generation in range(1, 5):
            state = advance_chain(state, response(generation), rewrite("mavren", generation))
        with self.assertRaisesRegex(ValueError, "prohibits"):
            advance_chain(state, response(5), rewrite("mavren", 5))

    def test_target_word_must_survive_rewrite_and_human_output(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        with self.assertRaisesRegex(ValueError, "exact nonce_form"):
            advance_chain(state, response(1), rewrite("the word was removed", 1))
        with self.assertRaisesRegex(ValueError, "exact nonce_form"):
            advance_chain(state, response(1, text="no target word"), rewrite("mavren", 1))

    def test_whole_word_not_substring(self):
        with self.assertRaises(ValueError):
            start_chain("one", Condition.HUMAN_ONLY, "concept", "mavren", "Only mavrens appears.")

    def test_nonce_forms_are_case_sensitive(self):
        with self.assertRaisesRegex(ValueError, "seed_text"):
            start_chain(
                "case-check", Condition.HUMAN_ONLY, "concept", "mavren",
                "Mavren is not the lowercase form.",
            )

    def test_reused_participant_rejected(self):
        state = self.make_chain(Condition.HUMAN_ONLY)
        state = advance_chain(state, response(1))
        with self.assertRaisesRegex(ValueError, "same participant"):
            advance_chain(state, response(1))

    def test_invalid_ratings_and_provenance_rejected(self):
        for value in (float("nan"), float("inf"), -1, 101, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ParticipantResponse("anon", value, "paraphrase", 90, "mavren")
        with self.assertRaises(ValueError):
            MediatedRewrite("mavren", "model", "v1", "not-a-hash", "run-1", "{}")

    def test_response_does_not_accept_non_enum_condition(self):
        with self.assertRaises(ValueError):
            start_chain("one", "llm_mediated", "concept", "mavren", "mavren")


if __name__ == "__main__":
    unittest.main()
