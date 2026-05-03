from groq import Groq
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.1-8b-instant"


# ---------- CLEAN JSON ----------
def clean_json(text):
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return match.group()
    return text


# ---------- VALIDATE QUIZ ----------
def validate_quiz(data):
    if not isinstance(data, list):
        return False

    for q in data:
        if not all(k in q for k in ["question", "options", "answer", "explanation"]):
            return False
        if len(q["options"]) != 4:
            return False

    return True


# ---------- MAIN FUNCTION ----------
def run_agent(subject, exam_date, hours, context, mode="plan"):

    if mode == "quiz":

        prompt = f"""
You are generating a quiz for a student.

Subject: {subject}

Context:
{context}

IMPORTANT RULES:
- Questions MUST be strictly about {subject}
- Focus on concepts, definitions, and applications
- NO general knowledge questions
- Answer MUST be EXACTLY one of the options

Return EXACTLY this JSON:

[
  {{
    "question": "Question here",
    "options": ["Option1", "Option2", "Option3", "Option4"],
    "answer": "Option1",
    "explanation": "Explanation"
  }}
]
"""

        # 🔁 retry loop
        for _ in range(3):
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )

            output = response.choices[0].message.content

            try:
                cleaned = clean_json(output)
                data = json.loads(cleaned)

                if validate_quiz(data):
                    return data
            except:
                continue

        return None

    else:
        prompt = f"""
You are a smart study assistant.

Subject: {subject}
Exam Date: {exam_date}
Study Hours: {hours}

Context:
{context}

Tasks:
1. Create a study plan
2. Identify weak areas
3. Suggest revision strategy
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content