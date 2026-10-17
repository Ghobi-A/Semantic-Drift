"""Audit-only dry run with made-up responses and mock identity rewrites.

This is NOT a participant experiment or evidence of connotational drift.
Run: python -m examples.dry_run
"""

import json

from semantic_drift.protocol import (
    Condition, MediatedRewrite, ParticipantResponse, advance_chain, start_chain,
)


def main() -> None:
    state = start_chain(
        "example-synthetic-chain", Condition.LLM_MEDIATED, "pause-practice",
        "mavren", "Mavren means pausing before responding to someone's request.",
    )
    for generation in range(1, 7):
        previous_text = state.seed_text if not state.records else state.records[-1].human_produced_text
        fake_rewrite = None
        if generation <= 4:
            fake_rewrite = MediatedRewrite(
                output_text=previous_text,  # Identity operator; no external LLM
                model_id="test-only-identity-operator",
                model_version="not-an-llm",
                prompt_sha256="0" * 64,
                run_id=f"synthetic-{generation}",
                decoding_parameters_json="{}",
            )
        state = advance_chain(
            state,
            ParticipantResponse(
                participant_code=f"synthetic-p{generation}",
                valence_rating=50,  # made up; never use as real data
                meaning_paraphrase="Pausing before responding",
                confidence=80,
                human_produced_text=previous_text,
            ),
            rewrite=fake_rewrite,
        )
    print(json.dumps({
        "warning": "SYNTHETIC EXAMPLE — no humans or LLM were used",
        "generations": state.completed_generation,
        "mediated": [r.generation for r in state.records if r.mediated_rewrite],
        "washout": [r.generation for r in state.records if not r.mediated_rewrite],
        "all_nonce_forms_preserved": all("mavren" in r.received_text for r in state.records),
    }, indent=2))


if __name__ == "__main__":
    main()
