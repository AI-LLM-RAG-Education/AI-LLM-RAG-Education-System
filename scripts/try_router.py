import csv, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.router.router import route_query


def predict(q):
    r = route_query(q)
    return "OUT-OF-SCOPE" if r == "GENERAL" else r


def interactive():
    while True:
        q = input("\nAsk (or press Enter to exit): ").strip()
        if not q:
            break
        print("Route:", route_query(q))


def sample(n=5):
    rows = list(csv.DictReader(open(ROOT / "datasets/development/dev.csv", encoding="utf-8")))
    random.seed(1)
    ok = total = 0
    for route in ["RAG", "SQL", "BOTH", "NOT-FOUND", "OUT-OF-SCOPE"]:
        for r in random.sample([x for x in rows if x["route"] == route], n):
            p = predict(r["question"])
            total += 1
            ok += p == route
            print(f"[{'OK ' if p == route else 'BAD'}] expected={route:<12} got={p:<12} | {r['question'][:70]}")
    print(f"\n{ok}/{total} correct")


if __name__ == "__main__":
    sample() if "--sample" in sys.argv else interactive()