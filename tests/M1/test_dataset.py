"""M1 dataset validation. Run:  pytest tests/M1  (or: python tests/M1/test_dataset.py)"""
import csv
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {"RAG", "SQL", "BOTH", "NOT-FOUND", "OUT-OF-SCOPE"}
EXPECTED = {"RAG": 100, "SQL": 100, "BOTH": 80, "NOT-FOUND": 60, "OUT-OF-SCOPE": 60}


def load(rel):
    with open(ROOT / rel, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


ALL = load("datasets/queries/labelled_queries.csv")
DEV = load("datasets/development/dev.csv")
TEST = load("datasets/test/test.csv")


def test_size_and_label_distribution():
    assert len(ALL) == 400
    assert Counter(r["route"] for r in ALL) == Counter(EXPECTED)


def test_labels_valid_and_no_missing_fields():
    for r in ALL:
        assert r["route"] in ALLOWED
        assert r["question"].strip() and r["gold_answer"].strip() and r["subtype"].strip()


def test_ids_and_questions_unique():
    assert len({r["query_id"] for r in ALL}) == 400
    assert len({" ".join(r["question"].lower().split()) for r in ALL}) == 400


def test_gold_sql_present_exactly_where_required():
    for r in ALL:
        if r["route"] in ("SQL", "BOTH", "NOT-FOUND"):
            assert r["gold_sql"].strip().upper().startswith("SELECT"), r["query_id"]
        else:
            assert not r["gold_sql"], r["query_id"]
        if r["route"] in ("RAG", "BOTH"):
            assert r["gold_rag_source"], r["query_id"]


def test_gold_sql_executes_and_results_match_label():
    db = ROOT / "data" / "generated" / "synthetic_education.db"
    con = sqlite3.connect(db)
    for r in ALL:
        if not r["gold_sql"]:
            continue
        rows = con.execute(r["gold_sql"]).fetchall()
        if r["route"] == "NOT-FOUND":
            assert rows == [], r["query_id"]
        else:
            assert rows and rows[0][0] is not None, r["query_id"]
        assert r["gold_sql"].upper().lstrip().startswith("SELECT")  # read-only


def test_split_is_disjoint_complete_and_stratified():
    d, t = {r["query_id"] for r in DEV}, {r["query_id"] for r in TEST}
    assert not d & t
    assert d | t == {r["query_id"] for r in ALL}
    assert (len(DEV), len(TEST)) == (320, 80)
    assert set(Counter(r["route"] for r in TEST)) == ALLOWED
    assert set(Counter(r["route"] for r in DEV)) == ALLOWED
    for route, n in EXPECTED.items():
        assert sum(r["route"] == route for r in TEST) == n // 5


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
