"""Pure, auditable state transitions for a six-generation human transmission chain.

A human-subject interface must only show StepRecord.received_text to participants,
not the whole state/history. This package neither calls an LLM nor stores PII.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import math
import re


GENERATIONS = 6
MEDIATED_GENERATIONS = frozenset({1, 2, 3, 4})


class Condition(str, Enum):
    HUMAN_ONLY = "human_only"
    LLM_MEDIATED = "llm_mediated"


def _nonblank(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")


def _contains_word(text: str, word: str) -> bool:
    return bool(re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text))


def _rating(value: int | float, label: str) -> None:
    if type(value) not in (int, float) or not math.isfinite(value) or not (0 <= value <= 100):
        raise ValueError(f"{label} must be a finite number in [0, 100]")


@dataclass(frozen=True)
class ParticipantResponse:
    """One human response. Valence 0=negative, 50=neutral, 100=positive."""

    participant_code: str  # random, non-identifying code; never contact details
    valence_rating: float
    meaning_paraphrase: str
    confidence: float  # 0 to 100
    human_produced_text: str

    def __post_init__(self) -> None:
        _nonblank(self.participant_code, "participant_code")
        _rating(self.valence_rating, "valence_rating")
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
    decoding_parameters_json: str

    def __post_init__(self) -> None:
        for name in ("output_text", "model_id", "model_version", "run_id", "decoding_parameters_json"):
            _nonblank(getattr(self, name), name)
        if not re.fullmatch(r"[0-9a-f]{64}", self.prompt_sha256):
            raise ValueError("prompt_sha256 must contain 64 lowercase hex characters")


@dataclass(frozen=True)
class StepRecord:
    generation: int
    participant_code: str
    transmission_source_text: str  # g0 seed or preceding human's output
    received_text: str  # only text the current human sees
    mediated_rewrite: MediatedRewrite | None
    valence_rating: float
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
) -> ChainState:
    """Append one human generation after enforcing the preregistered schedule.

    The external orchestration layer must generate and save the rewrite *before*
    submitting a response. A failed or absent rewrite raises an error; there is
    no automatic fallback to human-only transmission.
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
    if any(r.participant_code == response.participant_code for r in state.records):
        raise ValueError("the same participant cannot return in a later generation of a chain")

    source_text = state.seed_text if not state.records else state.records[-1].human_produced_text
    received_text = rewrite.output_text if should_mediate else source_text
    if not _contains_word(received_text, state.nonce_form):
        raise ValueError("transmitted text must preserve the exact nonce_form")
    if not _contains_word(response.human_produced_text, state.nonce_form):
        raise ValueError("human-produced text must preserve the exact nonce_form")

    record = StepRecord(
        generation=generation,
        participant_code=response.participant_code,
        transmission_source_text=source_text,
        received_text=received_text,
        mediated_rewrite=rewrite,
        valence_rating=response.valence_rating,
        meaning_paraphrase=response.meaning_paraphrase,
        confidence=response.confidence,
        human_produced_text=response.human_produced_text,
    )
    return replace(state, records=state.records + (record,))
