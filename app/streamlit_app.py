import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.main import answer_question
st.set_page_config(
    page_title="Education AI Assistant",
    page_icon="🎓"
)

st.title("🎓 Education AI Assistant")
st.write("Ask questions about educational content or academic records.")

question = st.text_input(
    "Ask your question:",
    placeholder="Example: What is yasaswini's DBMS attendance?"
)

if st.button("Ask"):
    if question.strip():
        with st.spinner("Thinking..."):
            answer = answer_question(question)

        st.success(answer)
    else:
        st.warning("Please enter a question.")