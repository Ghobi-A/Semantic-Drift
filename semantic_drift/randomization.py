"""Reproducible, condition-balanced chain allocation and Latin-square form rotation.

Randomisation is for independent *chains*, not individual word ratings.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import re
from .protocol import Condition


@dataclass(frozen=True)
class ChainAssignment:
    chain_id: str
    condition: Condition
    concept_to_nonce_form: tuple[tuple[str, str], ...]


def allocate_chains(
    *,
    chains_per_condition: int,
    concept_ids: tuple[str, ...],
    nonce_forms: tuple[str, ...],
    seed: int,
) -> tuple[ChainAssignment, ...]:
    """Balance treatment arms and rotate all form-to-concept mappings within each arm.

    Complete form counterbalancing requires chains_per_condition to be a multiple
    of the number of concepts; otherwise counts differ by at most one per concept.
    This is a reproducible *allocation plan*, not a participant recruitment tool.
    """
    if type(chains_per_condition) is not int or chains_per_condition < 1:
        raise ValueError("chains_per_condition must be a positive integer")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if not concept_ids or len(concept_ids) != len(nonce_forms):
        raise ValueError("need equal, nonzero numbers of concepts and nonce forms")
    if len(set(concept_ids)) != len(concept_ids) or len(set(nonce_forms)) != len(nonce_forms):
        raise ValueError("concept IDs and nonce forms must each be unique")
    if any(not isinstance(s, str) or not s.strip() for s in concept_ids):
        raise ValueError("concept IDs must be nonblank strings")
    if any(not isinstance(s, str) or not re.fullmatch(r"[a-z]{4,16}", s) for s in nonce_forms):
        raise ValueError("nonce forms must be 4–16 lowercase ASCII letters")

    rng = random.Random(seed)
    forms = list(nonce_forms)
    concepts = list(concept_ids)
    rng.shuffle(forms)
    rng.shuffle(concepts)
    k = len(concepts)
    assignments: list[ChainAssignment] = []

    for condition in (Condition.HUMAN_ONLY, Condition.HUMAN_EDITED, Condition.LLM_MEDIATED):
        offsets = [index % k for index in range(chains_per_condition)]
        rng.shuffle(offsets)
        for index, offset in enumerate(offsets, start=1):
            mapping = tuple(
                (concept, forms[(position + offset) % k])
                for position, concept in enumerate(concepts)
            )
            assignments.append(
                ChainAssignment(f"{condition.value}-{index:03d}", condition, mapping)
            )
    rng.shuffle(assignments)
    return tuple(assignments)
