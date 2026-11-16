# Data model, privacy and provenance (proposed)

**This is a schema proposal; no human data is present.** The Python module models a single concept within a chain. An eventual persistent storage layer must join all concepts within the same participant/generation and coordinate assignments across chains.

| Field | Type / meaning |
|---|---|
| `chain_id` | opaque chain ID (`chain-NNN`), numbered after the allocation shuffle so it does not reveal the arm; only the allocation manifest links it to `condition` |
| `condition` | `human_only`, `human_edited`, or `llm_mediated` |
| `concept_id` | stable seeded referent ID |
| `nonce_form` | 4–16-letter lower-case form, counterbalanced across concepts |
| `generation` | human generation 1–6; g0 is seed, not a participant |
| `participant_code` | random code, not name/email/IP address |
| `transmission_source_text` | g0 seed or immediately preceding human output |
| `received_text` | exact vignette shown to the human |
| `normalized_edit_distance` | incoming-edge token Levenshtein distance / max token count, measured before participant response; 0 for unedited edges |
| `valence_rating` | **primary outcome**: integer −3..+3 (0 = neither) for the word in the neutral probe sentence `NEUTRAL_PROBE_TEMPLATE`; same scale and wording as norming |
| `passage_tone_rating` | integer −3..+3, tone of `received_text`; diagnostic, kept separate from the primary outcome |
| `meaning_paraphrase` | participant's interpretation |
| `confidence` | finite 0–100 |
| `human_produced_text` | next-generation candidate text |
| `mediated_rewrite` | LLM rewrite on g1–g4 in arm C only |
| `human_edit` | human-editor output, pseudonymous editor ID, instruction SHA-256 and run ID on g1–g4 in arm B only |
| `mediated_rewrite.output_text` | exact model rewrite shown to current participant |
| `mediated_rewrite.model_id` | vendor or model identifier |
| `mediated_rewrite.model_version` | pinned model revision/snapshot |
| `mediated_rewrite.prompt_sha256` | SHA-256 of the **same frozen shared editor instruction** used by human editors; full raw provider messages are separately archived |
| `mediated_rewrite.run_id` | immutable reference to external request+response log |
| `mediated_rewrite.decoding_parameters_json` | JSON object; must state `temperature` and `seed` (`null` if unsupported). Constant within a chain apart from the seed |
| `mediated_rewrite.request_sha256`, `human_edit.request_sha256` | hash of the complete canonical editor request (instruction, target word, source passage); must match the edge's `transmission_source_text` |
| `failed_editor_attempts` | up to two logged failed editor attempts (`run_id`, `reason`) before the accepted one; empty on unedited edges |

Additional linked tables (not implemented): instrument/stimulus pretests, blinded independent denotation and context-valence ratings, rater IDs, participant-to-chain enrolment constraint, randomisation manifest, provider failures/retries, ethics and withdrawal ledger.

## Operational constraints

- Store timestamped API request/response events (including errors) and signed model/config snapshots in secured systems. Log all attempts, but do not expose them to participants.
- Use the identically worded shared editor instruction with both editing arms. Recruit human editors from the same eligible participant pool while prohibiting role collision within a chain. Preserve each incoming-edge edit magnitude as a post-treatment diagnostic.
- Preserve the exact text before and after each model step. Do not silently regenerate or cleanse a "failed" trial.
- Human participants should receive only their current `received_text`, an anonymous response form and the relevant word; never send complete `ChainState` to browsers.
- Use isolated access-controlled identifiers for contact information, recruitment payments or withdrawal links. Do not commit PII, IP addresses, raw participant exports or secrets.
- Set and document storage location, encryption, retention, deletion and consent handling before recruitment. Data anonymisation requires assessing reidentification risks in free text, not just dropping participant IDs.
- Separate deterministic/synthetic examples from real data releases and label all figures with provenance.

## Limits of the current code

The three-arm prototype enforces local state-transition invariants but **does not** provide authentication, a persistent database, concurrent access control, participant-session randomisation, LLM API integration, blinded annotation, sample-size determination or a preregistered analysis model. Those components must be added and tested before recruitment.
