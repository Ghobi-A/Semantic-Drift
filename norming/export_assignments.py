"""Export a deterministic participant-slot manifest; contains no real participant data."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from .allocation import allocate_norming, load_candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=Path(__file__).with_name("candidates.csv"))
    parser.add_argument("--out", type=Path, default=Path("norming_assignments.csv"))
    parser.add_argument("--participants", type=int, default=40)
    parser.add_argument("--items", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20261017)
    args = parser.parse_args()
    plans = allocate_norming(load_candidates(args.candidates), participants=args.participants, items_per_participant=args.items, seed=args.seed)
    with args.out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("participant_slot", "item_order", "concept_id", "nonce_form", "definition"))
        for plan in plans:
            for order, item in enumerate(plan.items, start=1):
                writer.writerow((plan.participant_slot, order, item.concept_id, item.presented_nonce_form, item.definition))
    print(f"Exported {sum(len(p.items) for p in plans)} stimulus presentations across {len(plans)} slots to {args.out}")


if __name__ == "__main__":
    main()
