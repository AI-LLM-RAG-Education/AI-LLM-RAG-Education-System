import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.router.router import route_query

rows = list(csv.DictReader(open(ROOT / "datasets/custom/custom_queries.csv", encoding="utf-8")))
ok = 0
for r in rows:
    got = route_query(r["question"])
    good = got == r["route"]
    ok += good
    print(f"[{'OK ' if good else 'BAD'}] expected={r['route']:<13} got={got:<13} | {r['question']}")
print(f"\n{ok}/{len(rows)} correct ({100*ok/len(rows):.1f}%)")