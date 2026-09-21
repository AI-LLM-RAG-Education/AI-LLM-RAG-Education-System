from app.llm import ask_llm
import json
import re


def route_query(question):
    prompt = f"""
You are the routing controller for an Education AI Assistant.

Choose exactly ONE route:

SQL:
- student marks
- student attendance
- student details
- academic records

RAG:
- educational concepts
- study material
- questions about subjects or documents

GENERAL:
- greetings
- casual conversation
- questions unrelated to education or academic records

Return ONLY JSON:
{{"route":"SQL"}}
or
{{"route":"RAG"}}
or
{{"route":"GENERAL"}}

Question:
{question}
"""

    response = ask_llm(prompt).strip()

    # Try normal JSON
    try:
        result = json.loads(response)
        route = result.get("route", "").upper()

        if route in ["SQL", "RAG", "GENERAL"]:
            return route
    except:
        pass

    # Try to find route inside unexpected LLM output
    match = re.search(r'"route"\s*:\s*"(SQL|RAG|GENERAL)"', response.upper())

    if match:
        return match.group(1)

    # Safe fallback
    q = question.lower()

    sql_words = [
        "mark", "marks", "attendance",
        "student id", "student details",
        "academic record"
    ]

    general_words = [
        "hello", "hi", "hey",
        "good morning", "good afternoon",
        "good evening", "thanks", "thank you"
    ]

    if any(word in q for word in sql_words):
        return "SQL"

    if any(word in q for word in general_words):
        return "GENERAL"

    return "RAG"


if __name__ == "__main__":
    questions = [
        "What are the features of Java?",
        "What is Yasaswini's DBMS mark?",
        "What is Sirisha's attendance?",
        "What is artificial intelligence?",
        "Hello"
    ]

    for question in questions:
        print(question, "->", route_query(question))