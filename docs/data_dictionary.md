# Data model, privacy and provenance (proposed)

**This is a schema proposal; no human data is present.** The Python module models a single concept within a chain. An eventual persistent storage layer must join all concepts within the same participant/generation and coordinate assignments across chains.

| Field | Type / meaning |
|---|---|
| `chain_id` | pseudonymous chain-level randomisation ID |
| `condition` | `human_only`, `human_edited`, or `llm_mediated` |
| `concept_id` | stable seeded referent ID |
| `nonce_form` | 4–16-letter lower-case form, counterbalanced across concepts |
| `generation` | human generation 1–6; g0 is seed, not a participant |
| `participant_code` | random code, not name/email/IP address |
| `transmission_source_text` | g0 seed or immediately preceding human output |
| `received_text` | exact vignette shown to the human |
| `valence_rating` | finite 0–100, 50 = neutral |
| `meaning_paraphrase` | participant's interpretation |
| `confidence` | finite 0–100 |
| `human_produced_text` | next-generation candidate text |
| `mediated_rewrite` | LLM rewrite on g1–g4 in arm C only |
| `human_edit` | human-editor output, pseudonymous editor ID, instruction SHA-256 and run ID on g1–g4 in arm B only |
| `mediated_rewrite.output_text` | exact model rewrite shown to current participant |
| `mediated_rewrite.model_id` | vendor or model identifier |
| `mediated_rewrite.model_version` | pinned model revision/snapshot |
| `mediated_rewrite.prompt_sha256` | SHA-256 of frozen prompt; complete prompt must be stored separately in version control |
| `mediated_rewrite.run_id` | immutable reference to external request+response log |
| `mediated_rewrite.decoding_parameters_json` | canonical full generation-parameter JSON |

Additional linked tables (not implemented): instrument/stimulus pretests, blinded independent denotation and context-valence ratings, rater IDs, participant-to-chain enrolment constraint, randomisation manifest, provider failures/retries, ethics and withdrawal ledger.

## Operational constraints

- Store timestamped API request/response events (including errors) and signed model/config snapshots in secured systems. Log all attempts, but do not expose them to participants.
- Preserve the exact text before and after each model step. Do not silently regenerate or cleanse a "failed" trial.
- Human participants should receive only their current `received_text`, an anonymous response form and the relevant word; never send complete `ChainState` to browsers.
- Use isolated access-controlled identifiers for contact information, recruitment payments or withdrawal links. Do not commit PII, IP addresses, raw participant exports or secrets.
- Set and document storage location, encryption, retention, deletion and consent handling before recruitment. Data anonymisation requires assessing reidentification risks in free text, not just dropping participant IDs.
- Separate deterministic/synthetic examples from real data releases and label all figures with provenance.

## Limits of the current code

The three-arm prototype enforces local state-transition invariants but **does not** provide authentication, a persistent database, concurrent access control, participant-session randomisation, LLM API integration, blinded annotation, sample-size determination or a preregistered analysis model. Those components must be added and tested before recruitment.
