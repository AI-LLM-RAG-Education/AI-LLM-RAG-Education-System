import csv, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.router.router import route_query

split = sys.argv[1] if len(sys.argv) > 1 else "development"
src = {"development": "datasets/development/dev.csv",
       "test": "datasets/test/test.csv"}[split]
out = ROOT / "preds.csv"

rows = list(csv.DictReader(open(ROOT / src, encoding="utf-8")))

# Resume: skip questions already predicted
done = set()
if out.exists():
    done = {r["query_id"] for r in csv.DictReader(open(out, encoding="utf-8"))}

new_file = not out.exists()
with open(out, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if new_file:
        w.writerow(["query_id", "predicted_route"])
    for i, r in enumerate(rows, 1):
        if r["query_id"] in done:
            continue
        try:
            pred = route_query(r["question"])
        except Exception as e:
            pred = "ERROR"
            print("error on", r["query_id"], e)
        w.writerow([r["query_id"], pred])
        f.flush()
        print(f"{i}/{len(rows)} {r['query_id']} -> {pred}")