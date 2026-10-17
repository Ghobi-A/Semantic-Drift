"""Balanced incomplete-block assignment for exploratory nonce-word norming.

40 slots x 10 concepts = 400 presentations / 20 concepts = 20 ratings per
concept. Counterbalance word-to-concept assignment to diagnose surface-form
effects. Slots are pseudonymous assignment indices, NOT Prolific identifiers.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import random
import re


@dataclass(frozen=True)
class Candidate:
    concept_id: str
    candidate_nonce_form: str
    definition: str


@dataclass(frozen=True)
class NormingItem:
    concept_id: str
    presented_nonce_form: str
    definition: str


@dataclass(frozen=True)
class Assignment:
    participant_slot: int
    items: tuple[NormingItem, ...]


def load_candidates(path: str | Path) -> tuple[Candidate, ...]:
    with open(path, encoding="utf-8", newline="") as infile:
        rows = tuple(Candidate(**row) for row in csv.DictReader(infile))
    if not rows:
        raise ValueError("candidate inventory cannot be empty")
    if len({r.concept_id for r in rows}) != len(rows):
        raise ValueError("concept IDs must be unique")
    if len({r.candidate_nonce_form for r in rows}) != len(rows):
        raise ValueError("nonce forms must be unique")
    for row in rows:
        if not re.fullmatch(r"[a-z]{4,16}", row.candidate_nonce_form):
            raise ValueError(f"invalid nonce form: {row.candidate_nonce_form!r}")
        if not row.concept_id.strip() or not row.definition.strip():
            raise ValueError("candidate IDs and definitions cannot be blank")
    return rows


def allocate_norming(
    candidates: tuple[Candidate, ...],
    *,
    participants: int = 40,
    items_per_participant: int = 10,
    seed: int = 20261017,
) -> tuple[Assignment, ...]:
    n = len(candidates)
    if type(participants) is not int or participants <= 0 or participants % n:
        raise ValueError("participants must be a positive multiple of number of candidates")
    if type(items_per_participant) is not int or not (1 <= items_per_participant <= n):
        raise ValueError("items_per_participant must be between 1 and candidate count")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if len({c.concept_id for c in candidates}) != n or len({c.candidate_nonce_form for c in candidates}) != n:
        raise ValueError("candidate IDs and forms must be unique")

    rng = random.Random(seed)
    shuffled = list(candidates)
    rng.shuffle(shuffled)
    forms = [c.candidate_nonce_form for c in shuffled]
    rng.shuffle(forms)
    output: list[Assignment] = []
    for slot in range(participants):
        indices = [(slot + j) % n for j in range(items_per_participant)]
        rng.shuffle(indices)  # per-participant display order
        items = tuple(
            NormingItem(
                concept_id=shuffled[i].concept_id,
                presented_nonce_form=forms[(i + slot) % n],
                definition=shuffled[i].definition,
            )
            for i in indices
        )
        output.append(Assignment(slot + 1, items))
    return tuple(output)
