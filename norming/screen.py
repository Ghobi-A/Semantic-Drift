"""Predeclared pilot exclusion rules; no participant data bundled.

This program NEVER labels an item 'neutral', only retained for independent
validation, rejected by a fixed criterion, or insufficient for screening.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from math import sqrt
import json


REQUIRED_N = 20
VALENCE_MEAN_LIMIT = 0.5
T_CRITICAL_DF19_TWO_SIDED_95 = 2.093024054
MIN_ADJUDICATED_CORRECT = 18
MIN_INITIAL_RATER_AGREEMENT = 17


def _code(value: str) -> bool:
    if value not in {"0", "1"}:
        raise ValueError("Blinded rater and adjudication codes must be 0 or 1")
    return value == "1"


def screen(
    response_rows: list[dict[str, str]],
    denotation_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    """Join by (participant_slot, concept_id); fail on duplicates/broken links."""
    if not response_rows or not denotation_rows:
        raise ValueError("Both actual participant responses and blinded codes are required")
    response_keys: set[tuple[str, str]] = set()
    valences: dict[str, list[int]] = defaultdict(list)
    for row in response_rows:
        if not {"participant_slot", "concept_id", "valence_rating"} <= row.keys():
            raise ValueError("Responses lack required screening fields")
        key = (str(row["participant_slot"]).strip(), str(row["concept_id"]).strip())
        if not all(key) or key in response_keys:
            raise ValueError("Missing or duplicate response slot/concept")
        response_keys.add(key)
        try:
            raw = row["valence_rating"]
            if raw not in {str(x) for x in range(-3, 4)}:
                raise ValueError("Valence must be an integer on -3..3")
            valences[key[1]].append(int(raw))
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid valence score") from exc

    codes: dict[str, list[tuple[bool, bool, bool]]] = defaultdict(list)
    coded_keys: set[tuple[str, str]] = set()
    for row in denotation_rows:
        if not {"participant_slot", "concept_id", "rater_a_correct", "rater_b_correct",
                "adjudicated_correct"} <= row.keys():
            raise ValueError("Denotation coding lacks required screening fields")
        key = (str(row["participant_slot"]).strip(), str(row["concept_id"]).strip())
        if not all(key) or key in coded_keys or key not in response_keys:
            raise ValueError("Missing, duplicate or unlinked denotation code")
        coded_keys.add(key)
        codes[key[1]].append(tuple(_code(row[c]) for c in
                                    ("rater_a_correct", "rater_b_correct", "adjudicated_correct")))
    results: list[dict[str, object]] = []
    for concept, values in sorted(valences.items()):
        rows = codes.get(concept, [])
        record: dict[str, object] = {
            "concept_id": concept, "n_ratings": len(values), "n_coded": len(rows),
            "status": "insufficient", "reasons": [], "mean_valence": None,
            "ci95_lower": None, "ci95_upper": None,
            "adjudicated_correct": None, "rater_agreement": None,
        }
        if len(values) != REQUIRED_N or len(rows) != REQUIRED_N:
            record["reasons"] = ["requires exactly 20 unique ratings and 20 linked denotation codes"]
            results.append(record)
            continue
        center = mean(values)
        sem = stdev(values) / sqrt(REQUIRED_N)
        lower = center - T_CRITICAL_DF19_TWO_SIDED_95 * sem
        upper = center + T_CRITICAL_DF19_TWO_SIDED_95 * sem
        correct = sum(adjudicated for _, _, adjudicated in rows)
        agreement = sum(a == b for a, b, _ in rows)
        reasons = []
        if abs(center) > VALENCE_MEAN_LIMIT:
            reasons.append("absolute mean valence exceeds 0.5")
        if lower > 0 or upper < 0:
            reasons.append("95% t confidence interval excludes 0")
        if correct < MIN_ADJUDICATED_CORRECT:
            reasons.append("fewer than 18/20 denotation paraphrases adjudicated correct")
        if agreement < MIN_INITIAL_RATER_AGREEMENT:
            reasons.append("fewer than 17/20 initial rater codes agree")
        record.update({
            "status": "reject" if reasons else "retain_for_validation",
            "reasons": reasons, "mean_valence": round(center, 6),
            "ci95_lower": round(lower, 6), "ci95_upper": round(upper, 6),
            "adjudicated_correct": correct, "rater_agreement": agreement,
        })
        results.append(record)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path)
    parser.add_argument("denotation_codes", type=Path)
    args = parser.parse_args()
    with args.responses.open(encoding="utf-8", newline="") as f:
        responses = list(csv.DictReader(f))
    with args.denotation_codes.open(encoding="utf-8", newline="") as f:
        codes = list(csv.DictReader(f))
    print(json.dumps({"warning": "exploratory screening; not equivalence or proof of neutrality",
                      "screen": screen(responses, codes)}, indent=2))


if __name__ == "__main__":
    main()
