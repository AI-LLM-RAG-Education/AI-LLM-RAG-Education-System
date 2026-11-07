# M1 - Development/Test Split & Evaluation Plan

## Split (M1.4)
- Script: `datasets/queries/split_dataset.py` (seed 42, stratified)
- Development: **320** questions -> `datasets/development/dev.csv` (tune prompts, router, SQL agent)
- Test: **80** questions -> `datasets/test/test.csv` (run ONCE for final numbers; never tune on it)

| Route | Dev | Test |
|---|---|---|
| RAG | 80 | 20 |
| SQL | 80 | 20 |
| BOTH | 64 | 16 |
| NOT-FOUND | 48 | 12 |
| OUT-OF-SCOPE | 48 | 12 |

80:20 is a recommended starting ratio, not a value fixed by the module plan. Stratification is by route, and by
subtype within route (55 of 61 subtypes appear in the test set).

## Metrics
| Component | Metric |
|---|---|
| Decision Router | Accuracy, per-class precision/recall/F1, macro-F1, confusion matrix (`scripts/evaluate_router.py`) |
| SQL branch | Execution accuracy: generated SQL result == gold SQL result |
| RAG branch | Recall@K / precision on `gold_rag_source`; faithfulness of the answer |
| NOT-FOUND | Rate of correct "no record" replies (no fabricated values) |
| OUT-OF-SCOPE | Correct refusal rate, esp. `unsafe-write-or-admin` |

## Usage
```bash
python database/scripts/generate_database.py
python datasets/queries/generate_queries.py
python datasets/queries/split_dataset.py
pytest tests/M1
python scripts/evaluate_router.py --pred preds.csv --split development --map-general
```
`--map-general` maps the prototype router's legacy `GENERAL` label to `OUT-OF-SCOPE`.
