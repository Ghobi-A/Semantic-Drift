"""Pure, auditable state transitions for a six-generation human transmission chain.

A human-subject interface must only show StepRecord.received_text to participants,
not the whole state/history. This package neither calls an LLM nor stores PII.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import json
import math
import re
from hashlib import sha256


GENERATIONS = 6
MEDIATED_GENERATIONS = frozenset({1, 2, 3, 4})

# Static editor instruction. Both human and model editors receive this same text,
# alongside the same word and current vignette as separate task inputs.
SHARED_EDITOR_INSTRUCTION = (
    "Improve the clarity and fluency of this passage while preserving its "
    "intended meaning. Keep the target word exactly unchanged. "
    "Do not add information not present in the passage."
)
SHARED_EDITOR_INSTRUCTION_SHA256 = sha256(
    SHARED_EDITOR_INSTRUCTION.encode("utf-8")
).hexdigest()

# One valence scale for norming and the main study: integers -3..+3, 0 = neither.
VALENCE_MIN, VALENCE_MAX = -3, 3
# Primary outcome probe: the word is rated in this constant neutral frame (the
# same frame as the norming survey), not as the tone of the received vignette.
NEUTRAL_PROBE_TEMPLATE = "Someone used {word} yesterday."
# An editing step may be attempted at most this many times in total. Every
# failed attempt is logged on the step; exhausting the budget ends the chain.
MAX_EDITOR_ATTEMPTS = 3


def editor_request_sha256(nonce_form: str, passage: str) -> str:
    """Hash of the complete, canonical editor request for one edge.

    The request is exactly three things: the shared instruction, the target
    word and the passage being edited. An adapter must hash what it actually
    sends; chain history, concept definitions, arm labels or earlier rewrites
    in the request change the hash and the transition is rejected.
    """
    if not isinstance(nonce_form, str) or not isinstance(passage, str):
        raise TypeError("nonce_form and passage must be strings")
    payload = json.dumps(
        {"instruction": SHARED_EDITOR_INSTRUCTION, "passage": passage, "target_word": nonce_form},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def normalized_token_edit_distance(source: str, edited: str) -> float:
    """Token-level Levenshtein / max token count; zero means identical.

    A descriptive post-intervention measure; conditioning on this in the
    primary C-vs-B contrast would generally be post-treatment adjustment.
    """
    if not isinstance(source, str) or not isinstance(edited, str):
        raise TypeError("source and edited must be strings")
    left, right = source.split(), edited.split()
    if not left and not right:
        return 0.0
    if len(right) > len(left):
        left, right = right, left
    row = list(range(len(right) + 1))
    for i, token in enumerate(left, start=1):
        next_row = [i]
        for j, other in enumerate(right, start=1):
            next_row.append(min(
                row[j] + 1, next_row[j-1] + 1,
                row[j-1] + (token != other),
            ))
        row = next_row
    return row[-1] / max(len(left), len(right))



class Condition(str, Enum):
    HUMAN_ONLY = "human_only"
    HUMAN_EDITED = "human_edited"
    LLM_MEDIATED = "llm_mediated"


def _nonblank(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")


def _contains_word(text: str, word: str, *, allow_capitalised: bool = False) -> bool:
    """Whole-word match. Seeds need the exact lower-case form; transmitted and
    produced text may also use the initial-capital form (e.g. sentence-initial
    "Mavren"), so ordinary fluent editing is not an arm-dependent abort."""
    forms = {word, word.capitalize()} if allow_capitalised else {word}
    return any(re.search(r"(?<!\w)" + re.escape(f) + r"(?!\w)", text) for f in forms)


def _valence(value: int, label: str) -> None:
    if type(value) is not int or not (VALENCE_MIN <= value <= VALENCE_MAX):
        raise ValueError(f"{label} must be an integer in [{VALENCE_MIN}, {VALENCE_MAX}]")


def _sha256_hex(value: str, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError(f"{label} must be a lower-case SHA-256 hex digest")


def _decoding_parameters(raw: str) -> dict:
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("decoding_parameters_json must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("decoding_parameters_json must be a JSON object")
    temperature = parsed.get("temperature")
    if type(temperature) not in (int, float) or not math.isfinite(temperature) or temperature < 0:
        raise ValueError("decoding parameters must state a finite temperature >= 0")
    if "seed" not in parsed or (parsed["seed"] is not None and type(parsed["seed"]) is not int):
        raise ValueError("decoding parameters must state an integer seed, or null if the provider has none")
    return parsed


def _rating(value: int | float, label: str) -> None:
    if type(value) not in (int, float) or not math.isfinite(value) or not (0 <= value <= 100):
        raise ValueError(f"{label} must be a finite number in [0, 100]")


@dataclass(frozen=True)
class ParticipantResponse:
    """One human response. Both valence items are integers -3..+3, 0 = neither.

    valence_rating is the primary outcome: the word rated in
    NEUTRAL_PROBE_TEMPLATE. passage_tone_rating is the tone of the received
    vignette, kept separate so passage tone cannot stand in for word valence.
    """

    participant_code: str  # random, non-identifying code; never contact details
    valence_rating: int
    meaning_paraphrase: str
    confidence: float  # 0 to 100
    human_produced_text: str
    passage_tone_rating: int

    def __post_init__(self) -> None:
        _nonblank(self.participant_code, "participant_code")
        _valence(self.valence_rating, "valence_rating")
        _valence(self.passage_tone_rating, "passage_tone_rating")
        _rating(self.confidence, "confidence")
        _nonblank(self.meaning_paraphrase, "meaning_paraphrase")
        _nonblank(self.human_produced_text, "human_produced_text")


@dataclass(frozen=True)
class MediatedRewrite:
    """Externally generated rewrite plus minimal immutable audit provenance."""

    output_text: str
    model_id: str
    model_version: str
    prompt_sha256: str
    run_id: str
    decoding_parameters_json: str  # JSON object with "temperature" and "seed"
    request_sha256: str  # editor_request_sha256 of what was actually sent

    def __post_init__(self) -> None:
        for name in ("output_text", "model_id", "model_version", "run_id", "decoding_parameters_json"):
            _nonblank(getattr(self, name), name)
        if self.prompt_sha256 != SHARED_EDITOR_INSTRUCTION_SHA256:
            raise ValueError("prompt_sha256 must match the pinned shared editor instruction")
        _sha256_hex(self.request_sha256, "request_sha256")
        _decoding_parameters(self.decoding_parameters_json)

    def operator_signature(self) -> str:
        """Model, version and decoding settings; the per-call seed is excluded."""
        settings = _decoding_parameters(self.decoding_parameters_json)
        settings.pop("seed")
        return json.dumps([self.model_id, self.model_version, settings], sort_keys=True)


@dataclass(frozen=True)
class HumanEdit:
    """Human-editor intervention with pseudonymous provenance."""
    output_text: str
    editor_code: str
    instruction_sha256: str
    edit_run_id: str
    request_sha256: str  # editor_request_sha256 of what the editor was shown

    def __post_init__(self) -> None:
        for name in ("output_text", "editor_code", "edit_run_id"):
            _nonblank(getattr(self, name), name)
        if self.instruction_sha256 != SHARED_EDITOR_INSTRUCTION_SHA256:
            raise ValueError("instruction_sha256 must match the pinned shared editor instruction")
        _sha256_hex(self.request_sha256, "request_sha256")


@dataclass(frozen=True)
class FailedEditorAttempt:
    """An editor attempt (either arm) that produced no usable output."""
    run_id: str  # reference to the archived request/response or edit session
    reason: str  # e.g. "provider_error", "target_word_missing", "empty_output"

    def __post_init__(self) -> None:
        _nonblank(self.run_id, "run_id")
        _nonblank(self.reason, "reason")


@dataclass(frozen=True)
class StepRecord:
    generation: int
    participant_code: str
    transmission_source_text: str  # g0 seed or preceding human's output
    received_text: str  # only text the current human sees
    normalized_edit_distance: float  # edited input vs previous human/seed
    mediated_rewrite: MediatedRewrite | None
    human_edit: HumanEdit | None
    failed_editor_attempts: tuple[FailedEditorAttempt, ...]
    valence_rating: int  # primary: word in the neutral probe frame
    passage_tone_rating: int  # diagnostic: tone of received_text
    meaning_paraphrase: str
    confidence: float
    human_produced_text: str


@dataclass(frozen=True)
class ChainState:
    chain_id: str
    condition: Condition
    concept_id: str
    nonce_form: str
    seed_text: str
    records: tuple[StepRecord, ...] = ()

    @property
    def completed_generation(self) -> int:
        return len(self.records)


def start_chain(
    chain_id: str,
    condition: Condition,
    concept_id: str,
    nonce_form: str,
    seed_text: str,
) -> ChainState:
    for label, value in (("chain_id", chain_id), ("concept_id", concept_id), ("seed_text", seed_text)):
        _nonblank(value, label)
    if not isinstance(condition, Condition):
        raise ValueError("condition must be a Condition enum")
    if not isinstance(nonce_form, str) or not re.fullmatch(r"[a-z]{4,16}", nonce_form):
        raise ValueError("nonce_form must be 4–16 lowercase ASCII letters")
    if not _contains_word(seed_text, nonce_form):
        raise ValueError("seed_text must contain the exact nonce_form as a whole word")
    return ChainState(chain_id, condition, concept_id, nonce_form, seed_text)


def advance_chain(
    state: ChainState,
    response: ParticipantResponse,
    rewrite: MediatedRewrite | None = None,
    human_edit: HumanEdit | None = None,
    failed_editor_attempts: tuple[FailedEditorAttempt, ...] = (),
) -> ChainState:
    """Append one human generation after enforcing the preregistered schedule.

    The external orchestration layer must generate and save the intervention
    *before* submitting a response. Missing or mismatched editor output fails
    closed; it must never silently become human-only transmission.
    """
    if not isinstance(state, ChainState) or not isinstance(response, ParticipantResponse):
        raise TypeError("expected ChainState and ParticipantResponse")
    if state.completed_generation >= GENERATIONS:
        raise ValueError("chain already completed six generations")

    generation = state.completed_generation + 1
    should_mediate = state.condition is Condition.LLM_MEDIATED and generation in MEDIATED_GENERATIONS
    if should_mediate and not isinstance(rewrite, MediatedRewrite):
        raise ValueError(f"generation {generation} requires a versioned LLM rewrite")
    if not should_mediate and rewrite is not None:
        raise ValueError(f"generation {generation} prohibits LLM mediation")
    should_human_edit = state.condition is Condition.HUMAN_EDITED and generation in MEDIATED_GENERATIONS
    if should_human_edit and not isinstance(human_edit, HumanEdit):
        raise ValueError(f"generation {generation} requires a versioned human edit")
    if not should_human_edit and human_edit is not None:
        raise ValueError(f"generation {generation} prohibits human editing")
    if should_human_edit and any(
        r.human_edit is not None and r.human_edit.editor_code == human_edit.editor_code
        for r in state.records
    ):
        raise ValueError("same editor cannot edit multiple generations in a chain")
    if any(r.participant_code == response.participant_code for r in state.records):
        raise ValueError("the same participant cannot return in a later generation of a chain")

    source_text = state.seed_text if not state.records else state.records[-1].human_produced_text
    expected_request = editor_request_sha256(state.nonce_form, source_text)
    if should_mediate:
        if rewrite.request_sha256 != expected_request:
            raise ValueError("rewrite request_sha256 does not match this edge's instruction, word and source text")
        earlier = [r.mediated_rewrite for r in state.records if r.mediated_rewrite is not None]
        if any(e.operator_signature() != rewrite.operator_signature() for e in earlier):
            raise ValueError("model, version and decoding parameters must stay constant within a chain")
    if should_human_edit and human_edit.request_sha256 != expected_request:
        raise ValueError("human edit request_sha256 does not match this edge's instruction, word and source text")

    failed_editor_attempts = tuple(failed_editor_attempts)
    if any(not isinstance(a, FailedEditorAttempt) for a in failed_editor_attempts):
        raise TypeError("failed_editor_attempts must be FailedEditorAttempt records")
    if failed_editor_attempts and not (should_mediate or should_human_edit):
        raise ValueError(f"generation {generation} has no editor step to fail")
    if len(failed_editor_attempts) > MAX_EDITOR_ATTEMPTS - 1:
        raise ValueError(f"at most {MAX_EDITOR_ATTEMPTS} editor attempts are allowed per edge")
    accepted_run_id = rewrite.run_id if should_mediate else (human_edit.edit_run_id if should_human_edit else None)
    run_ids = [a.run_id for a in failed_editor_attempts] + ([accepted_run_id] if accepted_run_id else [])
    if len(set(run_ids)) != len(run_ids):
        raise ValueError("every editor attempt needs its own run_id")

    received_text = rewrite.output_text if should_mediate else (human_edit.output_text if should_human_edit else source_text)
    if not _contains_word(received_text, state.nonce_form, allow_capitalised=True):
        raise ValueError("transmitted text must preserve the exact nonce_form")
    if not _contains_word(response.human_produced_text, state.nonce_form, allow_capitalised=True):
        raise ValueError("human-produced text must preserve the exact nonce_form")

    record = StepRecord(
        generation=generation,
        participant_code=response.participant_code,
        transmission_source_text=source_text,
        received_text=received_text,
        normalized_edit_distance=normalized_token_edit_distance(source_text, received_text),
        mediated_rewrite=rewrite,
        human_edit=human_edit,
        failed_editor_attempts=failed_editor_attempts,
        valence_rating=response.valence_rating,
        passage_tone_rating=response.passage_tone_rating,
        meaning_paraphrase=response.meaning_paraphrase,
        confidence=response.confidence,
        human_produced_text=response.human_produced_text,
    )
    return replace(state, records=state.records + (record,))
