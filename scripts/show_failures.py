import csv, sys
gold = {r["query_id"]: r for r in csv.DictReader(open("datasets/development/dev.csv", encoding="utf-8"))}
pred = {r["query_id"]: r["predicted_route"].upper() for r in csv.DictReader(open("preds.csv", encoding="utf-8"))}
want, got = sys.argv[1], sys.argv[2]
n = 0
for q, r in gold.items():
    if r["route"] == want and got in pred.get(q, ""):
        print(r["question"]); n += 1
        if n == 10: break