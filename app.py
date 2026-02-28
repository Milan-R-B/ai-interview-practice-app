import streamlit as st
import ollama
import pandas as pd
import os
import re
from datetime import datetime

st.set_page_config(page_title="AI Interview Practice", page_icon="🎯")

st.title("🎯 AI Interview Practice App (Ollama Powered)")
st.write("Local LLM-based mock interview system.")

DATA_FILE = "interview_progress.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Date", "Role", "Question", "Score"])
    df.to_csv(DATA_FILE, index=False)

role = st.selectbox("Select Role", [
    "Software Engineer",
    "Data Analyst",
    "HR"
])

def generate_question(role):
    prompt = f"Generate one professional interview question for a {role}. Only return the question."
    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()

if st.button("Generate Question"):
    with st.spinner("Generating question..."):
        st.session_state.question = generate_question(role)

if "question" in st.session_state:
    st.subheader("Interview Question")
    st.info(st.session_state.question)

    user_answer = st.text_area("Your Answer", height=200)

    if st.button("Get AI Feedback"):
        if user_answer.strip() == "":
            st.error("Please write your answer first.")
        else:
            with st.spinner("Evaluating..."):

                feedback_prompt = f"""
You are a professional interview coach.

Question: {st.session_state.question}
Answer: {user_answer}

Provide:
1. Score out of 10 (e.g., 7/10)
2. Strengths
3. Weaknesses
4. Improvement Suggestions
"""

                response = ollama.chat(
                    model="llama3",
                    messages=[{"role": "user", "content": feedback_prompt}]
                )

                feedback_text = response["message"]["content"]

                score_match = re.search(r'(\d+)/10', feedback_text)
                score = int(score_match.group(1)) if score_match else 5

                new_entry = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Role": role,
                    "Question": st.session_state.question,
                    "Score": score
                }])

                new_entry.to_csv(DATA_FILE, mode="a", header=False, index=False)

                st.success("AI Feedback")
                st.write(feedback_text)

st.divider()
st.header("📈 Progress Dashboard")

df = pd.read_csv(DATA_FILE)

if not df.empty:
    st.dataframe(df)
    st.metric("Average Confidence Score", f"{df['Score'].mean():.2f} / 10")
    st.line_chart(df["Score"])
else:
    st.info("No practice data yet.")