import sqlite3

def init_db():
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS scores (subject TEXT, score INT)")
    conn.commit()
    conn.close()

def save_score(subject, score):
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("INSERT INTO scores VALUES (?, ?)", (subject, score))
    conn.commit()
    conn.close()

def get_scores(subject):
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("SELECT score FROM scores WHERE subject=?", (subject,))
    data = c.fetchall()
    conn.close()
    return data