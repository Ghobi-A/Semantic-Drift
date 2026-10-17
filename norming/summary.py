"""Descriptive-only human-data norming summaries; never synthesise outcomes.

Required CSV columns:
participant_slot,concept_id,presented_nonce_form,valence_rating,meaning_paraphrase,confidence

No inferential claims or automatic final stimulus selection are made.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
import statistics


REQUIRED = frozenset({
    "participant_slot", "concept_id", "presented_nonce_form",
    "valence_rating", "meaning_paraphrase", "confidence",
})


def summarise(rows: list[dict[str, str]]) -> list[dict[str, float | int | str]]:
    if not rows:
        raise ValueError("No participant observations were supplied")
    groups: dict[str, list[int]] = defaultdict(list)
    seen = set()
    for row in rows:
        if not REQUIRED.issubset(row):
            raise ValueError(f"Missing fields: {sorted(REQUIRED - row.keys())}")
        try:
            slot = int(row["participant_slot"])
            valence = int(row["valence_rating"])
            confidence = float(row["confidence"])
        except (TypeError, ValueError) as err:
            raise ValueError("Invalid participant slot, integer valence or confidence") from err
        if slot < 1 or valence < -3 or valence > 3 or not (0 <= confidence <= 100):
            raise ValueError("Out-of-range slot, valence or confidence")
        concept = row["concept_id"].strip()
        if not concept or not row["presented_nonce_form"].strip() or not row["meaning_paraphrase"].strip():
            raise ValueError("Missing concept, nonce form or comprehension paraphrase")
        key = (slot, concept)
        if key in seen:
            raise ValueError(f"Duplicate concept for participant slot: {key}")
        seen.add(key)
        groups[concept].append(valence)
    result = []
    for concept, ratings in sorted(groups.items()):
        result.append({
            "concept_id": concept,
            "n": len(ratings),
            "mean_valence": round(statistics.mean(ratings), 3),
            "sd_valence": round(statistics.stdev(ratings), 3) if len(ratings) > 1 else float("nan"),
            "negative_fraction": round(sum(x < 0 for x in ratings) / len(ratings), 3),
            "positive_fraction": round(sum(x > 0 for x in ratings) / len(ratings), 3),
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path, help="Human response CSV supplied by a real approved survey")
    args = parser.parse_args()
    with args.responses.open("r", newline="", encoding="utf-8") as stream:
        result = summarise(list(csv.DictReader(stream)))
    writer = csv.DictWriter(
        __import__("sys").stdout, fieldnames=list(result[0]), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(result)
    print("DESCRIPTIVE PILOT STATISTICS ONLY: denotation coding and independent validation still required.",
          file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
