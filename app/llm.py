from ollama import chat
from app.rag.rag import search

MODEL = "education-ai"


def ask_llm(prompt):
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        think=False
    )
    return response.message.content


def ask_rag(question):
    results = search(question, k=3)
    context = "\n\n".join(results)

    prompt = f"""
You are an educational assistant.

Answer the question using ONLY the context below.
If the answer is not present in the context, say:
"The information was not found in the provided documents."

Context:
{context}

Question:
{question}

Give a clear and concise answer.
"""

    return ask_llm(prompt)

def extract_sql_request(question):
    prompt = f"""
Extract the student name, subject name, and requested information.

IMPORTANT:
- Student name MUST exactly match one of:
  Yasaswini, Sirisha, Harika, Baji Vali, Beni, Suresh
- Subject MUST exactly match one of:
  DBMS, Artificial Intelligence, Machine Learning, Operating Systems, Java
- Do NOT change, shorten, or correct the spelling of names.
- Preserve the exact capitalization shown above.

Question: {question}

Return ONLY in this format:
student=NAME
subject=SUBJECT
type=TYPE

TYPE must be one of:
attendance
marks
details
"""
    return ask_llm(prompt)

if __name__ == "__main__":
    print(ask_rag("What are the features of Java?"))