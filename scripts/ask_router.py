import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.router.router import route_query

print("Type a question (or 'quit' to stop)")
while True:
    q = input("\nQuestion: ").strip()
    if q.lower() in ("quit", "exit", ""):
        break
    print("Route  :", route_query(q))