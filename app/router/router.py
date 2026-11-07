import json
import re
from app.llm import ask_llm

VALID_ROUTES = {"SQL", "RAG", "BOTH", "OUT-OF-SCOPE"}

def route_query(question: str) -> str:
    """Classify the user's intent. NOT-FOUND is decided after source lookup."""
    prompt = f"""
You are a router for an education assistant with two knowledge sources:
1) a SQLite database containing student details, marks, attendance, subjects and faculty
2) educational PDFs, currently Java notes.

Choose exactly one route:
- SQL: the question needs only structured student/academic database information.
- RAG: the question needs only information explained in the educational PDFs.
- BOTH: the question explicitly needs BOTH a database fact and a PDF/document fact.
- OUT-OF-SCOPE: the question is unrelated to student academic records or educational study material.

Important:
- A question asking about a missing student/record is still SQL; the application will check and return NOT-FOUND if absent.
- A question about a topic not present in the PDF is still RAG; the application will check and return NOT-FOUND if unsupported.
- Do not use NOT-FOUND as a route. It is a result after searching.
- Greetings and unrelated requests are OUT-OF-SCOPE.
Return only JSON such as {{"route":"SQL"}}.

Question: {question}
"""
    try:
        response = ask_llm(prompt).strip()
        match = re.search(r'\{.*?\}', response, re.S)
        if match:
            route = json.loads(match.group(0)).get("route", "").upper()
            if route in VALID_ROUTES:
                return route
    except Exception:
        pass

    # Conservative keyword fallback if the model is unavailable or returns invalid output.
    q = question.lower()
    if any(x in q for x in ["weather", "flight", "recipe", "cricket score", "stock price", "hotel", "birthday poem"]):
        return "OUT-OF-SCOPE"
    if any(x in q for x in [" and explain", " and what", "along with", "also tell me"]):
        if any(x in q for x in ["mark", "attendance", "student", "faculty", "department"]):
            return "BOTH"
    if any(x in q for x in ["mark", "marks", "attendance", "student id", "student details",
                            "student record", "faculty", "department", "section"]):
        return "SQL"
    if any(x in q for x in ["java", "inheritance", "polymorphism", "jvm", "class", "object",
                            "loop", "variable", "programming", "method", "interface"]):
        return "RAG"
    return "OUT-OF-SCOPE"
