import unittest

from semantic_drift.protocol import (
    Condition,
    MediatedRewrite,
    HumanEdit,
    ParticipantResponse,
    advance_chain,
    start_chain,
    FailedEditorAttempt,
    SHARED_EDITOR_INSTRUCTION_SHA256,
    editor_request_sha256,
    normalized_token_edit_distance,
)

WORD = "mavren"
T0 = '{"seed": null, "temperature": 0}'


def source_of(state):
    return state.seed_text if not state.records else state.records[-1].human_produced_text


def response(generation: int, *, text: str = "Someone practiced mavren carefully."):
    return ParticipantResponse(
        participant_code=f"anon-{generation}",
        valence_rating=0,
        meaning_paraphrase="Pauses before responding to a request.",
        confidence=80,
        human_produced_text=text,
        passage_tone_rating=0,
    )


def rewrite(state, output: str | None = None, *, params: str = T0, model_version: str = "test-only"):
    """A rewrite correctly bound to the chain's current source text."""
    source = source_of(state)
    return MediatedRewrite(
        output_text="Rewritten: " + source if output is None else output,
        model_id="mock-identity",
        model_version=model_version,
        prompt_sha256=SHARED_EDITOR_INSTRUCTION_SHA256,
        run_id=f"test-run-{state.completed_generation + 1}",
        decoding_parameters_json=params,
        request_sha256=editor_request_sha256(state.nonce_form, source),
    )


def human_edit(state, output: str | None = None):
    source = source_of(state)
    g = state.completed_generation + 1
    return HumanEdit(
        "Edited: " + source if output is None else output, f"editor-{g}",
        SHARED_EDITOR_INSTRUCTION_SHA256, f"edit-{g}",
        editor_request_sha256(state.nonce_form, source),
    )


class ProtocolTests(unittest.TestCase):
    def make_chain(self, condition):
        return start_chain(
            "chain-1", condition, "pause-before-reply", "mavren",
            "Mavren is a practice of pausing before replying to a request. mavren.",
        )

    def test_edit_magnitude_measured_at_each_incoming_edge(self):
        self.assertEqual(normalized_token_edit_distance("a b", "a c"), 0.5)
        self.assertEqual(normalized_token_edit_distance("a", "a b"), 0.5)
        self.assertEqual(normalized_token_edit_distance("", ""), 0)
        self.assertEqual(normalized_token_edit_distance("a", "b"), 1)
        start = self.make_chain(Condition.LLM_MEDIATED)
        state = advance_chain(start, response(1), rewrite(start, "mavren is more concise."))
        record = state.records[-1]
        self.assertGreater(record.normalized_edit_distance, 0)
        self.assertLessEqual(record.normalized_edit_distance, 1)
        control = advance_chain(self.make_chain(Condition.HUMAN_ONLY), response(1))
        self.assertEqual(control.records[-1].normalized_edit_distance, 0)

    def test_non_matching_pinned_editor_instruction_fails(self):
        with self.assertRaisesRegex(ValueError, "pinned shared editor instruction"):
            MediatedRewrite("mavren", "test", "v1", "f"*64, "r", T0, "a"*64)
        with self.assertRaisesRegex(ValueError, "pinned shared editor instruction"):
            HumanEdit("mavren", "anon", "f"*64, "edit", "a"*64)

    def test_exactly_four_rewrites_then_two_washout_steps(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        initial = state
        for generation in range(1, 7):
            source = source_of(state)
            media = rewrite(state) if generation <= 4 else None
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
            previous = source_of(state)
            edit = human_edit(state) if g <= 4 else None
            state = advance_chain(state, response(g), human_edit=edit)
            self.assertEqual(state.records[-1].received_text, edit.output_text if edit else previous)
            self.assertEqual(state.records[-1].human_edit is not None, g <= 4)
            self.assertIsNone(state.records[-1].mediated_rewrite)

    def test_human_edit_missing_or_misplaced_fails(self):
        with self.assertRaisesRegex(ValueError, "requires a versioned human edit"):
            advance_chain(self.make_chain(Condition.HUMAN_EDITED), response(1))
        with self.assertRaisesRegex(ValueError, "prohibits human editing"):
            control = self.make_chain(Condition.HUMAN_ONLY)
            advance_chain(control, response(1), human_edit=human_edit(control))
        state = self.make_chain(Condition.HUMAN_EDITED)
        for g in range(1, 5):
            state = advance_chain(state, response(g), human_edit=human_edit(state))
        with self.assertRaisesRegex(ValueError, "prohibits human editing"):
            advance_chain(state, response(5), human_edit=human_edit(state))

    def test_human_editor_provenance_and_word_preservation(self):
        with self.assertRaises(ValueError):
            HumanEdit("mavren", "editor", "bad-hash", "run", "a"*64)
        with self.assertRaisesRegex(ValueError, "exact nonce_form"):
            start = self.make_chain(Condition.HUMAN_EDITED)
            advance_chain(start, response(1), human_edit=human_edit(start, "no target"))

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
            control = self.make_chain(Condition.HUMAN_ONLY)
            advance_chain(control, response(1), rewrite(control))

    def test_rewrite_rejected_during_washout(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        for generation in range(1, 5):
            state = advance_chain(state, response(generation), rewrite(state))
        with self.assertRaisesRegex(ValueError, "prohibits"):
            advance_chain(state, response(5), rewrite(state))

    def test_target_word_must_survive_rewrite_and_human_output(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        with self.assertRaisesRegex(ValueError, "exact nonce_form"):
            advance_chain(state, response(1), rewrite(state, "the word was removed"))
        with self.assertRaisesRegex(ValueError, "exact nonce_form"):
            advance_chain(state, response(1, text="no target word"), rewrite(state))

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
        for value in (float("nan"), float("inf"), -4, 4, 1.5, 50, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ParticipantResponse("anon", value, "paraphrase", 90, "mavren", 0)
                with self.assertRaises(ValueError):
                    ParticipantResponse("anon", 0, "paraphrase", 90, "mavren", value)
        for value in (-3, 0, 3):
            ParticipantResponse("anon", value, "paraphrase", 90, "mavren", value)
        with self.assertRaises(ValueError):
            MediatedRewrite("mavren", "model", "v1", "not-a-hash", "run-1", T0, "a"*64)

    def test_probe_valence_and_passage_tone_are_recorded_separately(self):
        state = self.make_chain(Condition.HUMAN_ONLY)
        state = advance_chain(state, ParticipantResponse("anon", -2, "paraphrase", 90, "mavren again", 3))
        self.assertEqual(state.records[0].valence_rating, -2)
        self.assertEqual(state.records[0].passage_tone_rating, 3)

    def test_decoding_parameters_must_state_temperature_and_seed(self):
        for bad in ("{}", "not json", "[]", '{"temperature": 0}', '{"seed": 1}',
                    '{"seed": 1, "temperature": -1}', '{"seed": "x", "temperature": 0}',
                    '{"seed": null, "temperature": true}'):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "decoding"):
                    MediatedRewrite("mavren", "m", "v", SHARED_EDITOR_INSTRUCTION_SHA256, "r", bad, "a"*64)
        MediatedRewrite("mavren", "m", "v", SHARED_EDITOR_INSTRUCTION_SHA256, "r",
                        '{"seed": 7, "temperature": 0.7}', "a"*64)

    def test_rewrite_must_be_bound_to_this_edge(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        good = rewrite(state)
        for wrong in (editor_request_sha256(WORD, "Some other passage about mavren."),
                      editor_request_sha256("solven", state.seed_text),
                      editor_request_sha256(WORD, state.seed_text + " Earlier: history.")):
            stale = MediatedRewrite(good.output_text, good.model_id, good.model_version,
                                    good.prompt_sha256, good.run_id, T0, wrong)
            with self.assertRaisesRegex(ValueError, "request_sha256"):
                advance_chain(state, response(1), stale)
        edited = self.make_chain(Condition.HUMAN_EDITED)
        stale_edit = HumanEdit("Edited mavren.", "editor-1", SHARED_EDITOR_INSTRUCTION_SHA256, "edit-1",
                               editor_request_sha256(WORD, "Something else about mavren."))
        with self.assertRaisesRegex(ValueError, "request_sha256"):
            advance_chain(edited, response(1), human_edit=stale_edit)

    def test_operator_must_stay_constant_within_chain(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        state = advance_chain(state, response(1), rewrite(state, params='{"seed": 1, "temperature": 0.7}'))
        # A different per-call seed is allowed; anything else is not.
        advance_chain(state, response(2), rewrite(state, params='{"seed": 2, "temperature": 0.7}'))
        with self.assertRaisesRegex(ValueError, "constant within a chain"):
            advance_chain(state, response(2), rewrite(state, params='{"seed": 2, "temperature": 0}'))
        with self.assertRaisesRegex(ValueError, "constant within a chain"):
            advance_chain(state, response(2), rewrite(
                state, params='{"seed": 2, "temperature": 0.7}', model_version="silently-updated"))

    def test_sentence_initial_capital_is_the_same_word(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        state = advance_chain(state, response(1, text="Mavren helped me."), rewrite(state, "Mavren is a pause."))
        self.assertEqual(state.completed_generation, 1)
        for variant in ("MAVREN is a pause.", "mavrens are pauses.", "Mavrenish pauses."):
            with self.subTest(variant=variant):
                with self.assertRaisesRegex(ValueError, "exact nonce_form"):
                    advance_chain(state, response(2), rewrite(state, variant))

    def test_failed_editor_attempts_are_logged_and_bounded(self):
        state = self.make_chain(Condition.LLM_MEDIATED)
        fails = (FailedEditorAttempt("try-1", "provider_error"), FailedEditorAttempt("try-2", "target_word_missing"))
        done = advance_chain(state, response(1), rewrite(state), failed_editor_attempts=fails)
        self.assertEqual(done.records[0].failed_editor_attempts, fails)
        with self.assertRaisesRegex(ValueError, "at most 3"):
            advance_chain(state, response(1), rewrite(state),
                          failed_editor_attempts=fails + (FailedEditorAttempt("try-3", "empty_output"),))
        with self.assertRaisesRegex(ValueError, "own run_id"):
            advance_chain(state, response(1), rewrite(state),
                          failed_editor_attempts=(FailedEditorAttempt("test-run-1", "provider_error"),))
        with self.assertRaisesRegex(ValueError, "no editor step"):
            advance_chain(self.make_chain(Condition.HUMAN_ONLY), response(1),
                          failed_editor_attempts=fails[:1])
        self.assertEqual(advance_chain(self.make_chain(Condition.HUMAN_ONLY), response(1))
                         .records[0].failed_editor_attempts, ())

    def test_response_does_not_accept_non_enum_condition(self):
        with self.assertRaises(ValueError):
            start_chain("one", "llm_mediated", "concept", "mavren", "mavren")


if __name__ == "__main__":
    unittest.main()
