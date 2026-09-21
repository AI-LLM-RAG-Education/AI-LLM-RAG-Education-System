from app.router.router import route_query
from app.llm import ask_llm, ask_rag, extract_sql_request
from app.sql.sql_agent import (
    get_student_mark,
    get_attendance,
    get_student_details
)
import json


def extract_sql_info(question):
    prompt = f"""
Extract information from this academic question.

Return ONLY valid JSON:
{{
  "type": "mark or attendance or details",
  "student": "student name or null",
  "subject": "subject name or null"
}}

Question:
{question}
"""

    response = ask_llm(prompt)

    try:
        return json.loads(response)
    except:
        return {
            "type": None,
            "student": None,
            "subject": None
        }


def answer_question(question):
    route = route_query(question)

    print("Route:", route)

    if route == "RAG":
        return ask_rag(question)

    if route == "SQL":
       data = extract_sql_request(question)

       lines = data.splitlines()
       values = {}

       for line in lines:
         if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

       student = values.get("student")
       subject = values.get("subject")
       request_type = values.get("type")

       if request_type == "attendance":
          return get_attendance(student, subject)

       if request_type == "marks":
          return get_student_mark(student, subject)

       if request_type == "details":
        return get_student_details(student)

       return "I could not understand the academic request."

    return ask_rag(question)


if __name__ == "__main__":
    question = input("Ask your question: ")
    print("\nAnswer:", answer_question(question))