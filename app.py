import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from agent.agent import run_agent
from utils.file_parser import parse_pdf, parse_ppt
from utils.database import init_db, save_score, get_scores
from utils.calendar import export_calendar
from utils.rag import SimpleRAG

# ---------- CONFIG ----------
st.set_page_config(page_title="Study Assistant", layout="wide")
init_db()
rag = SimpleRAG()

# ---------- UI ----------
st.markdown("""
<style>
.stApp {
    background: #0f172a;
    color: #e2e8f0;
}
section[data-testid="stSidebar"] {
    background: #020617;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
.stButton>button {
    background: #3b82f6;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------- NAV ----------
page = st.sidebar.radio("Navigation", ["Dashboard", "Quiz", "Progress"])
st.title("Smart Study Assistant")

# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    subject = st.text_input("Subject")
    exam_date = st.date_input("Exam Date")
    hours = st.slider("Hours/Day", 1, 10, 3)

    uploaded_file = st.file_uploader("Upload Notes", type=["pdf", "pptx"])

    notes_text = ""

    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            notes_text = parse_pdf(uploaded_file)
        else:
            notes_text = parse_ppt(uploaded_file)

        rag.add_documents(notes_text)
        st.success("Notes indexed")

    if st.button("Generate Study Plan"):
        context = rag.query(f"{subject} important topics")

        if not context.strip():
            context = f"General knowledge about {subject}"

        result = run_agent(subject, exam_date, hours, context)
        st.write(result)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# QUIZ
# =========================================================
elif page == "Quiz":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    subject = st.text_input("Subject for Quiz")

    if st.button("Generate Quiz"):
        context = rag.query(f"{subject} key topics concepts")

        if not context.strip():
            context = f"General knowledge about {subject}"

        quiz = run_agent(subject, None, None, context, mode="quiz")

        if quiz:
            st.session_state["quiz"] = quiz
            st.session_state["answers"] = {}
        else:
            st.error("Quiz failed. Try again.")

    if "quiz" in st.session_state:
        quiz = st.session_state["quiz"]

        for i, q in enumerate(quiz):
            st.markdown(f"### Q{i+1}")

            ans = st.radio(q["question"], q["options"], key=i)
            st.session_state["answers"][i] = ans

        if st.button("Submit Quiz"):
            score = 0

            for i, q in enumerate(quiz):
                user_ans = st.session_state["answers"][i]

                st.markdown(f"**{q['question']}**")

                if user_ans.strip().lower() == q["answer"].strip().lower():
                    st.success("Correct")
                    score += 1
                else:
                    st.error(f"Wrong. Correct: {q['answer']}")

                st.info(q["explanation"])

            st.success(f"Score: {score}/{len(quiz)}")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PROGRESS
# =========================================================
elif page == "Progress":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    subject = st.text_input("Subject")

    scores = get_scores(subject)

    if scores:
        df = pd.DataFrame(scores, columns=["Score"])
        fig, ax = plt.subplots()
        ax.plot(df["Score"], marker='o')
        st.pyplot(fig)

    score = st.number_input("Enter Score", 0, 100)

    if st.button("Save Score"):
        save_score(subject, score)
        st.success("Saved")

    if st.button("Export Calendar"):
        export_calendar(subject, st.date_input("Date"))
        st.success("Calendar created")

    st.markdown('</div>', unsafe_allow_html=True)