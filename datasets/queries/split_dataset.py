#!/usr/bin/env python3
"""M1.4 - Stratified 80/20 development/test split.

Run:  python datasets/queries/split_dataset.py
Stratified by route, and by subtype inside each route (every 5th item of a seeded,
subtype-sorted shuffle goes to test), so all five routes and nearly all subtypes
appear in BOTH sets. Fixed SEED => reproducible.
"""
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

SEED = 42
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "datasets" / "queries" / "labelled_queries.csv"


def main():
    random.seed(SEED)
    with open(SRC, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    cols = list(rows[0].keys())
    by_route = defaultdict(list)
    for r in rows:
        by_route[r["route"]].append(r)
    dev, test = [], []
    for route in sorted(by_route):
        items = by_route[route][:]
        random.shuffle(items)
        items.sort(key=lambda r: r["subtype"])  # stable: keeps shuffled order within subtype
        for i, r in enumerate(items):
            (test if i % 5 == 0 else dev).append(r)
    for name, data in (("development/dev.csv", dev), ("test/test.csv", test)):
        with open(ROOT / "datasets" / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(sorted(data, key=lambda r: r["query_id"]))
    summary = {
        "seed": SEED, "total": len(rows), "development": len(dev), "test": len(test),
        "development_by_route": dict(Counter(r["route"] for r in dev)),
        "test_by_route": dict(Counter(r["route"] for r in test)),
        "test_subtypes_covered": len({r["subtype"] for r in test}),
        "total_subtypes": len({r["subtype"] for r in rows}),
    }
    (ROOT / "datasets" / "split_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
