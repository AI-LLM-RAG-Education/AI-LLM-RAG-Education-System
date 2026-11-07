#!/usr/bin/env python3
"""Evaluate a Decision Router against the labelled query set (pure Python, no dependencies).

Usage:
  python scripts/evaluate_router.py --pred preds.csv --split test
preds.csv needs columns: query_id,predicted_route
Valid routes: RAG, SQL, BOTH, NOT-FOUND, OUT-OF-SCOPE.
Use --map-general to treat the prototype's legacy GENERAL label as OUT-OF-SCOPE.
Reports accuracy, per-class precision/recall/F1, macro-F1 and the confusion matrix.
"""
import argparse
import csv
from pathlib import Path

ROUTES = ["RAG", "SQL", "BOTH", "NOT-FOUND", "OUT-OF-SCOPE"]
ROOT = Path(__file__).resolve().parents[1]
FILES = {"development": "datasets/development/dev.csv", "test": "datasets/test/test.csv",
         "all": "datasets/queries/labelled_queries.csv"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--split", choices=FILES, default="development")
    ap.add_argument("--map-general", action="store_true")
    a = ap.parse_args()
    gold = {r["query_id"]: r["route"] for r in csv.DictReader(open(ROOT / FILES[a.split], encoding="utf-8"))}
    pred = {r["query_id"]: r["predicted_route"].strip().upper() for r in csv.DictReader(open(a.pred, encoding="utf-8"))}
    if a.map_general:
        pred = {k: ("OUT-OF-SCOPE" if v == "GENERAL" else v) for k, v in pred.items()}
    missing = [q for q in gold if q not in pred]
    if missing:
        print(f"WARNING: {len(missing)} queries have no prediction (counted wrong).")
    cm = {g: {p: 0 for p in ROUTES + ["OTHER"]} for g in ROUTES}
    for q, g in gold.items():
        p = pred.get(q, "OTHER")
        cm[g][p if p in ROUTES else "OTHER"] += 1
    correct = sum(cm[r][r] for r in ROUTES)
    print(f"Split: {a.split}   Queries: {len(gold)}   Routing accuracy: {correct / len(gold):.3f}\n")
    print(f"{'route':<14}{'precision':>10}{'recall':>8}{'f1':>8}{'support':>9}")
    f1s = []
    for r in ROUTES:
        tp = cm[r][r]
        fp = sum(cm[g][r] for g in ROUTES if g != r)
        fn = sum(cm[r].values()) - tp
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
        f1s.append(f1)
        print(f"{r:<14}{pr:>10.3f}{rc:>8.3f}{f1:>8.3f}{tp + fn:>9}")
    print(f"\nMacro-F1: {sum(f1s) / len(f1s):.3f}\n\nConfusion matrix (rows=gold, cols=predicted)")
    print(f"{'':<14}" + "".join(f"{p:>14}" for p in ROUTES + ["OTHER"]))
    for g in ROUTES:
        print(f"{g:<14}" + "".join(f"{cm[g][p]:>14}" for p in ROUTES + ["OTHER"]))


if __name__ == "__main__":
    main()
