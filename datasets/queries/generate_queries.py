#!/usr/bin/env python3
"""M1.3 - Generate the 400-question labelled query dataset.

Run after generate_database.py:  python datasets/queries/generate_queries.py
Every SQL / BOTH / NOT-FOUND gold query is executed against the synthetic DB while generating,
so gold answers are verified, not assumed.
Output: labelled_queries.csv / labelled_queries.json
"""
import csv
import json
import random
import sqlite3
from collections import Counter
from pathlib import Path

SEED = 42
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "generated" / "synthetic_education.db"
OUT = ROOT / "datasets" / "queries"
QUOTA = {"RAG": 100, "SQL": 100, "BOTH": 80, "NOT-FOUND": 60, "OUT-OF-SCOPE": 60}
REG = "documents/academic_regulations.md"

R_ATT = "Min 75% attendance per course for exam eligibility; 65-74.9% condonable with fee/valid grounds; <65% detained."
R_PASS = "Pass mark is 40/100."
R_GRADE = "O 90+, A+ 80-89, A 70-79, B+ 60-69, B 50-59, C 40-49, F <40."
R_SUPPLY = "Failed courses are cleared via supplementary exams after regular results, with fee."
R_REVAL = "Apply within 7 days of result declaration with per-course fee; better marks retained."
R_PROMO = "Promotion needs overall attendance >=75% (or condoned) and <=4 backlogs."
NF_ANSWER = "No matching record found. The assistant must say so and must not fabricate data."
OOS_ANSWER = "Outside supported scope. The assistant should politely decline and state what it can help with."

random.seed(SEED)
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row


def run(sql):
    return [list(r) for r in con.execute(sql).fetchall()]


def fmt(rows):
    s = json.dumps(rows[:5], ensure_ascii=False)
    return s if len(rows) <= 5 else f"{s} ... ({len(rows)} rows total)"


S = [dict(r) for r in con.execute("SELECT * FROM students")]
C = [dict(r) for r in con.execute("SELECT * FROM courses")]
F = [dict(r) for r in con.execute("SELECT * FROM faculty")]
E = [dict(r) for r in con.execute("""
    SELECT s.student_id, s.name, s.department, s.year, s.section, c.course_id, c.course_name,
           m.marks_obtained AS marks,
           ROUND(100.0*a.attended_classes/a.total_classes,1) AS att
    FROM students s JOIN marks m ON m.student_id=s.student_id
    JOIN courses c ON c.course_id=m.course_id
    JOIN attendance a ON a.student_id=s.student_id AND a.course_id=c.course_id""")]
E_FAIL = [e for e in E if e["marks"] < 40]
E_SHORT = [e for e in E if e["att"] < 75]
IDS = {s["student_id"] for s in S}
CNAMES = {c["course_name"] for c in C}
FNAMES = {f["name"] for f in F}
DEPTS = sorted({s["department"] for s in S})

rows, seen, counts = [], set(), Counter()


def add(route, subtype, question, sql="", topic="", answer=""):
    if counts[route] >= QUOTA[route]:
        return False
    key = " ".join(question.lower().split())
    if key in seen:
        return False
    gold = ""
    if sql:
        res = run(sql)
        if route in ("SQL", "BOTH") and (not res or res[0][0] is None):
            return False
        if route == "NOT-FOUND" and res:
            return False
        gold = fmt(res)
    if route == "SQL":
        ans = gold
    elif route == "BOTH":
        ans = f"SQL: {gold} | RULE: {answer}"
    elif route == "NOT-FOUND":
        ans = NF_ANSWER
    elif route == "OUT-OF-SCOPE":
        ans = OOS_ANSWER
    else:
        ans = answer
    seen.add(key)
    counts[route] += 1
    rows.append(dict(question=question, route=route, subtype=subtype, gold_sql=sql,
                     gold_rag_source=topic, gold_answer=ans))
    return True


def vary(q):
    p = random.choice(["", "", "", "Hi, ", "Please tell me: ", "Quick question - "])
    return q if not p else p + q[0].lower() + q[1:]


def fill(route, templates):
    tries = 0
    while counts[route] < QUOTA[route] and tries < 30000:
        r = templates[tries % len(templates)]()
        tries += 1
        if r:
            sub, q, sql, topic, ans = (list(r) + ["", ""])[:5]
            add(route, sub, vary(q), sql, topic, ans)
    assert counts[route] == QUOTA[route], (route, counts[route])


# ---------------------------------------------------------------- SQL (100)
ATT = "ROUND(100.0*a.attended_classes/a.total_classes,1)"
J_MC = "FROM marks m JOIN courses c ON c.course_id=m.course_id"
J_AC = "FROM attendance a JOIN courses c ON c.course_id=a.course_id"


def pe():
    return random.choice(E)


def t_marks():
    e = pe(); s, c = e["student_id"], e["course_name"]
    q = random.choice([f"What are the marks of {s} in {c}?", f"Show {s}'s score in {c}.",
                       f"How much did student {s} score in {c}?", f"My roll number is {s}. What did I get in {c}?"])
    return ("marks-lookup", q, f"SELECT m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND c.course_name='{c}';")


def t_allmarks():
    s = random.choice(S)["student_id"]
    q = random.choice([f"Show all subject-wise marks for {s}.", f"List every course mark of student {s}.",
                       f"My roll number is {s}. Show all my marks."])
    return ("marks-all", q, f"SELECT c.course_name, m.marks_obtained {J_MC} WHERE m.student_id='{s}' ORDER BY c.course_id;")


def t_att():
    e = pe(); s, c = e["student_id"], e["course_name"]
    q = random.choice([f"What is the attendance percentage of {s} in {c}?", f"How many percent attendance does {s} have in {c}?",
                       f"My roll number is {s}. What is my attendance in {c}?"])
    return ("attendance-course", q, f"SELECT {ATT} AS attendance_pct {J_AC} WHERE a.student_id='{s}' AND c.course_name='{c}';")


def t_att_overall():
    s = random.choice(S)["student_id"]
    q = random.choice([f"What is the overall attendance percentage of {s}?", f"Show my overall attendance. Roll number {s}."])
    return ("attendance-overall", q, f"SELECT ROUND(100.0*SUM(attended_classes)/SUM(total_classes),1) AS overall_attendance_pct FROM attendance WHERE student_id='{s}';")


def t_profile():
    s = random.choice(S)["student_id"]
    q = random.choice([f"Which department and year is {s} studying in?", f"What section is student {s} in?"])
    return ("student-profile", q, f"SELECT department, year, section FROM students WHERE student_id='{s}';")


def t_name():
    s = random.choice(S)
    if "'" in s["name"]:
        return None
    q = random.choice([f"What is the roll number of {s['name']}?", f"Find the student ID for {s['name']}."])
    return ("name-lookup", q, f"SELECT student_id FROM students WHERE name='{s['name']}';")


def t_count_dy():
    d, y = random.choice(DEPTS), random.randint(1, 4)
    q = random.choice([f"How many students are there in {d} year {y}?", f"Count the {d} students studying in year {y}."])
    return ("count-students", q, f"SELECT COUNT(*) FROM students WHERE department='{d}' AND year={y};")


def t_avg():
    c = random.choice(C)["course_name"]
    q = random.choice([f"What is the average mark scored in {c}?", f"Give the class average for {c}."])
    return ("aggregate-course", q, f"SELECT ROUND(AVG(m.marks_obtained),2) {J_MC} WHERE c.course_name='{c}';")


def t_topper():
    c = random.choice(C)["course_name"]
    q = random.choice([f"Who scored the highest marks in {c}?", f"Which student topped {c}?"])
    return ("topper", q, f"SELECT m.student_id, m.marks_obtained {J_MC} WHERE c.course_name='{c}' ORDER BY m.marks_obtained DESC, m.student_id LIMIT 1;")


def t_failcount():
    c = random.choice(C)["course_name"]
    q = random.choice([f"How many students failed {c}?", f"Number of students who scored below 40 in {c}?"])
    return ("count-fail", q, f"SELECT COUNT(*) {J_MC} WHERE c.course_name='{c}' AND m.marks_obtained<40;")


def t_shortcount():
    c = random.choice(C)["course_name"]
    q = random.choice([f"How many students have attendance below 75% in {c}?", f"Count students with attendance shortage in {c}."])
    return ("count-shortage", q, f"SELECT COUNT(*) {J_AC} WHERE c.course_name='{c}' AND 100.0*a.attended_classes/a.total_classes<75;")


def t_teacher():
    c = random.choice(C)["course_name"]
    q = random.choice([f"Who teaches {c}?", f"Which faculty member handles {c}?"])
    return ("faculty-of-course", q, f"SELECT f.name FROM courses c JOIN faculty f ON f.faculty_id=c.faculty_id WHERE c.course_name='{c}';")


def t_fcourses():
    f = random.choice(F)
    q = random.choice([f"Which courses are handled by {f['name']}?", f"List the subjects taught by {f['name']}."])
    return ("courses-of-faculty", q, f"SELECT c.course_name FROM courses c JOIN faculty f ON f.faculty_id=c.faculty_id WHERE f.name='{f['name']}' ORDER BY c.course_id;")


def t_top5():
    c = random.choice(C)["course_name"]
    q = random.choice([f"List the top 5 scorers in {c}.", f"Who are the five highest scoring students in {c}?"])
    return ("top-n", q, f"SELECT m.student_id, m.marks_obtained {J_MC} WHERE c.course_name='{c}' ORDER BY m.marks_obtained DESC, m.student_id LIMIT 5;")


def t_credits():
    c = random.choice(C)["course_name"]
    return ("course-info", random.choice([f"How many credits is {c}?", f"What are the credits for {c}?"]),
            f"SELECT credits FROM courses WHERE course_name='{c}';")


def t_semester():
    c = random.choice(C)["course_name"]
    return ("course-info", random.choice([f"In which semester is {c} taught?", f"Which semester does {c} belong to?"]),
            f"SELECT semester FROM courses WHERE course_name='{c}';")


def t_total():
    s = random.choice(S)["student_id"]
    return ("marks-aggregate", random.choice([f"What is the total marks obtained by {s}?", f"Add up all the marks of student {s}."]),
            f"SELECT SUM(marks_obtained) FROM marks WHERE student_id='{s}';")


def t_section():
    d, y, sec = random.choice(DEPTS), random.randint(1, 4), random.choice("ABC")
    return ("count-students", f"How many students are in section {sec} of {d} year {y}?",
            f"SELECT COUNT(*) FROM students WHERE department='{d}' AND year={y} AND section='{sec}';")


def t_lowatt_dept():
    d, th = random.choice(DEPTS), random.choice([65, 70, 75])
    return ("count-shortage", f"How many {d} students have overall attendance below {th}%?",
            "SELECT COUNT(*) FROM (SELECT a.student_id FROM attendance a JOIN students s ON s.student_id=a.student_id "
            f"WHERE s.department='{d}' GROUP BY a.student_id HAVING 100.0*SUM(a.attended_classes)/SUM(a.total_classes)<{th});")


def t_desig():
    f = random.choice(F)
    return ("faculty-info", random.choice([f"What is the designation of {f['name']}?", f"Which department does {f['name']} belong to?"]),
            f"SELECT designation, department FROM faculty WHERE name='{f['name']}';")


def t_dsem():
    d, sem = random.choice(DEPTS), random.choice([1, 3, 5, 7])
    return ("course-list", random.choice([f"List the courses offered in {d} semester {sem}.", f"What subjects does {d} have in semester {sem}?"]),
            f"SELECT course_name FROM courses WHERE department='{d}' AND semester={sem} ORDER BY course_id;")


def t_failsubj():
    e = random.choice(E_FAIL); s = e["student_id"]
    return ("marks-filter", random.choice([f"In which subjects did {s} score below 40?", f"Which courses has student {s} failed?"]),
            f"SELECT c.course_name, m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND m.marks_obtained<40 ORDER BY c.course_id;")


def t_avg_dy():
    d, y = random.choice(DEPTS), random.randint(1, 4)
    return ("aggregate-cohort", f"What is the average marks of {d} year {y} students across all courses?",
            f"SELECT ROUND(AVG(m.marks_obtained),2) FROM marks m JOIN students s ON s.student_id=m.student_id WHERE s.department='{d}' AND s.year={y};")


def t_ncourses():
    s = random.choice(S)["student_id"]
    return ("count-courses", random.choice([f"How many courses is {s} enrolled in?", f"Number of subjects registered by {s}?"]),
            f"SELECT COUNT(*) FROM marks WHERE student_id='{s}';")


def t_lowest_att():
    s = random.choice(S)["student_id"]
    return ("attendance-extreme", f"In which course does {s} have the lowest attendance?",
            f"SELECT c.course_name, {ATT} AS attendance_pct {J_AC} WHERE a.student_id='{s}' ORDER BY attendance_pct ASC, c.course_id LIMIT 1;")


def t_best():
    s = random.choice(S)["student_id"]
    return ("marks-extreme", f"What is the highest mark scored by {s} and in which course?",
            f"SELECT c.course_name, m.marks_obtained {J_MC} WHERE m.student_id='{s}' ORDER BY m.marks_obtained DESC, c.course_id LIMIT 1;")


fill("SQL", [t_marks, t_allmarks, t_att, t_att_overall, t_profile, t_name, t_count_dy, t_avg, t_topper, t_failcount,
             t_shortcount, t_teacher, t_fcourses, t_top5, t_credits, t_semester, t_total, t_section, t_lowatt_dept,
             t_desig, t_dsem, t_failsubj, t_avg_dy, t_ncourses, t_lowest_att, t_best])

# ---------------------------------------------------------------- BOTH (80)
def b_elig():
    e = pe(); s, c = e["student_id"], e["course_name"]
    q = random.choice([f"My roll number is {s}. Am I eligible to write the {c} exam based on my attendance?",
                       f"Can {s} appear for the {c} semester exam given the attendance?"])
    return ("attendance-eligibility", q, f"SELECT {ATT} AS attendance_pct {J_AC} WHERE a.student_id='{s}' AND c.course_name='{c}';", f"{REG} #1 Attendance", R_ATT)


def b_short():
    e = random.choice(E_SHORT); s, c = e["student_id"], e["course_name"]
    q = random.choice([f"Why do I have attendance shortage in {c}? Roll number {s}. What can I do about it?",
                       f"{s} is short of attendance in {c}. What is the condonation process?"])
    return ("attendance-shortage", q, f"SELECT {ATT} AS attendance_pct {J_AC} WHERE a.student_id='{s}' AND c.course_name='{c}';", f"{REG} #1 Attendance", R_ATT)


def b_pass():
    e = pe(); s, c = e["student_id"], e["course_name"]
    q = random.choice([f"Did {s} pass {c}? Also explain the passing criteria.", f"Is {s} passed in {c}, and what is the minimum pass mark?"])
    return ("pass-fail", q, f"SELECT m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND c.course_name='{c}';", f"{REG} #2 Passing criteria", R_PASS)


def b_grade():
    e = pe(); s, c = e["student_id"], e["course_name"]
    q = random.choice([f"What grade does {s} receive in {c} according to the grading scheme?", f"Show {s}'s marks in {c} and tell me the corresponding grade."])
    return ("grading", q, f"SELECT m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND c.course_name='{c}';", f"{REG} #3 Grading scheme", R_GRADE)


def b_detain():
    d, y = random.choice(DEPTS), random.randint(1, 4)
    sql = ("SELECT COUNT(*) FROM (SELECT a.student_id FROM attendance a JOIN students s ON s.student_id=a.student_id "
           f"WHERE s.department='{d}' AND s.year={y} GROUP BY a.student_id HAVING 100.0*SUM(a.attended_classes)/SUM(a.total_classes)<65);")
    if run(sql)[0][0] == 0:
        return None
    return ("attendance-detention", f"How many {d} year {y} students have overall attendance below 65%, and what action does the college take on them?", sql, f"{REG} #1 Attendance", R_ATT)


def b_backlog():
    e = random.choice(E_FAIL); s = e["student_id"]
    q = random.choice([f"Which courses has {s} failed, and how can the student clear them?", f"List {s}'s failed subjects and explain how to clear the backlogs."])
    return ("backlog", q, f"SELECT c.course_name, m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND m.marks_obtained<40 ORDER BY c.course_id;", f"{REG} #4 Supplementary", R_SUPPLY)


def b_reval():
    e = pe(); s, c = e["student_id"], e["course_name"]
    return ("revaluation", f"{s} is unhappy with the {c} result. Show the marks and explain the revaluation procedure.",
            f"SELECT m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND c.course_name='{c}';", f"{REG} #5 Revaluation", R_REVAL)


CONCEPTS = [("Database Management Systems", "normalization", "KB: DBMS normalization"),
            ("Operating Systems", "deadlock and its necessary conditions", "KB: OS deadlock"),
            ("Machine Learning", "overfitting", "KB: ML overfitting"),
            ("Object Oriented Programming through Java", "inheritance in Java", "KB: Java inheritance"),
            ("Computer Networks", "the TCP three-way handshake", "KB: TCP handshake"),
            ("Data Structures", "how a stack works", "KB: Stack"),
            ("Design and Analysis of Algorithms", "time complexity", "KB: Time complexity"),
            ("Deep Learning", "backpropagation", "KB: Backpropagation")]


def b_concept():
    c, concept, topic = random.choice(CONCEPTS)
    pool = [e for e in E if e["course_name"] == c]
    if not pool:
        return None
    s = random.choice(pool)["student_id"]
    q = random.choice([f"Explain {concept} and also show the marks of {s} in {c}.", f"What is {concept}? Also, how did {s} perform in {c}?"])
    return ("concept-plus-record", q, f"SELECT m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND c.course_name='{c}';", topic, f"Concept explanation of {concept} from knowledge base.")


def b_promo():
    s = random.choice(S)["student_id"]
    return ("promotion", f"Is {s} eligible for promotion to the next year? Check overall attendance and the promotion rule.",
            f"SELECT ROUND(100.0*SUM(attended_classes)/SUM(total_classes),1) AS overall_attendance_pct FROM attendance WHERE student_id='{s}';", f"{REG} #6 Promotion", R_PROMO)


def b_supply():
    e = random.choice(E_FAIL); s, c = e["student_id"], e["course_name"]
    return ("supplementary", f"{s} failed {c}. Show the marks and explain how the supplementary exam works.",
            f"SELECT m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND c.course_name='{c}';", f"{REG} #4 Supplementary", R_SUPPLY)


def b_lowcourse():
    s = random.choice(S)["student_id"]
    return ("attendance-eligibility", f"In which course is {s}'s attendance the lowest, and can that shortage be condoned?",
            f"SELECT c.course_name, {ATT} AS attendance_pct {J_AC} WHERE a.student_id='{s}' ORDER BY attendance_pct ASC, c.course_id LIMIT 1;", f"{REG} #1 Attendance", R_ATT)


fill("BOTH", [b_elig, b_short, b_pass, b_grade, b_detain, b_backlog, b_reval, b_concept, b_promo, b_supply, b_lowcourse])

# ---------------------------------------------------------------- NOT-FOUND (60)
FAKE_COURSES = [x for x in ["Quantum Computing", "Astrophysics", "Marine Biology", "Fashion Design", "Organic Chemistry",
                            "Cryptocurrency Economics", "Nuclear Engineering", "Film Direction", "Aerospace Propulsion",
                            "Genetic Engineering", "Veterinary Anatomy", "Textile Chemistry"] if x not in CNAMES]
FAKE_FACULTY = [x for x in ["Ramakrishna Varma", "Lalitha Devi Pothuri", "Anwar Hussain Shaik", "Meenakshi Sundaram",
                            "Kondalarao Peddina", "Swapna Rekha Gudipati", "Prasad Chowdary Bandi", "Nirmala Joseph",
                            "Venkatesh Prabhu", "Harshavardhan Reddy", "Gayathri Mohan", "Tarun Bhaskar"] if x not in FNAMES]
FAKE_DEPTS = {"CHE": "Chemical Engineering", "BIO": "Biotechnology", "MBA": "MBA", "LAW": "Law"}


def fake_id():
    while True:
        i = f"{random.choice([23, 24, 25, 26])}BQ1A{random.randint(2001, 9999):04d}"
        if i not in IDS:
            return i


def n_marks():
    f = fake_id()
    return ("missing-student", random.choice([f"Show the marks of student {f}.", f"What are the marks of {f}?"]),
            f"SELECT * FROM marks WHERE student_id='{f}';")


def n_att():
    f = fake_id()
    return ("missing-student", random.choice([f"What is the attendance of {f}?", f"Show the overall attendance for roll number {f}."]),
            f"SELECT * FROM attendance WHERE student_id='{f}';")


def n_profile():
    f = fake_id()
    return ("missing-student", random.choice([f"Which department is {f} in?", f"Give me the details of student {f}."]),
            f"SELECT * FROM students WHERE student_id='{f}';")


def n_badcourse():
    s, c = random.choice(S)["student_id"], random.choice(FAKE_COURSES)
    return ("missing-course", random.choice([f"What did {s} score in {c}?", f"Show {s}'s attendance in {c}."]),
            f"SELECT m.marks_obtained {J_MC} WHERE m.student_id='{s}' AND c.course_name='{c}';")


def n_notenrolled():
    e = pe()
    other = random.choice([c for c in C if c["department"] != e["department"]])
    return ("not-enrolled", f"Show {e['student_id']}'s marks in {other['course_name']}.",
            f"SELECT m.marks_obtained {J_MC} WHERE m.student_id='{e['student_id']}' AND c.course_name='{other['course_name']}';")


def n_faculty():
    n = random.choice(FAKE_FACULTY)
    return ("missing-faculty", random.choice([f"Which courses does {n} handle?", f"What is the designation of {n}?"]),
            f"SELECT c.course_name FROM courses c JOIN faculty f ON f.faculty_id=c.faculty_id WHERE f.name='{n}';")


def n_teacher():
    c = random.choice(FAKE_COURSES)
    return ("missing-course", random.choice([f"Who teaches {c}?", f"Which semester is {c} offered in?"]),
            f"SELECT f.name FROM courses c JOIN faculty f ON f.faculty_id=c.faculty_id WHERE c.course_name='{c}';")


def n_dept():
    code, full = random.choice(list(FAKE_DEPTS.items()))
    return ("missing-department", random.choice([f"List the students of the {full} ({code}) department.", f"Show the {full} ({code}) students in year {random.randint(1, 4)}."]),
            f"SELECT student_id FROM students WHERE department='{code}';")


def n_sem():
    d, sem = random.choice(DEPTS), random.choice([2, 4, 6, 8])
    return ("missing-semester", f"List the courses offered in {d} semester {sem}.",
            f"SELECT course_name FROM courses WHERE department='{d}' AND semester={sem};")


fill("NOT-FOUND", [n_marks, n_att, n_profile, n_badcourse, n_notenrolled, n_faculty, n_teacher, n_dept, n_sem])

# ---------------------------------------------------------------- OUT-OF-SCOPE (60)
OOS = {
 "general-chat": ["Tell me a joke.", "How are you feeling today?", "Write a poem about the monsoon.", "What is your favourite colour?", "Can you sing me a song?", "Tell me an interesting story about a dragon."],
 "sports": ["What is the cricket score today?", "Who won the last IPL final?", "Show me the Premier League points table.", "When is the next India vs Australia match?", "Who is the best footballer of all time?", "Give me the latest Olympics medal tally."],
 "entertainment": ["Suggest a good Telugu movie to watch this weekend.", "Who is the highest-paid actor in India?", "What is the plot of Inception?", "When is the next Marvel movie releasing?", "Recommend some songs for a road trip.", "Which web series is trending now?"],
 "travel-weather": ["What will the weather be in Vijayawada tomorrow?", "Book a train ticket from Guntur to Hyderabad.", "What are the best places to visit in Goa?", "Find me cheap flights to Delhi.", "What is the distance from Vijayawada to Chennai?", "Which restaurant near campus has the best biryani?"],
 "finance": ["Which stock should I buy today?", "What is the current Bitcoin price?", "How do I file my income tax return?", "Should I invest in mutual funds?", "What is the gold rate today?"],
 "lifestyle": ["Give me a recipe for chicken biryani.", "How can I lose 5 kg in a month?", "What should I eat before a workout?", "Suggest a skincare routine.", "How do I remove a stain from a white shirt?"],
 "medical": ["I have a fever and headache, which medicine should I take?", "Is it safe to take painkillers every day?", "How many hours should an adult sleep?"],
 "politics-news": ["Who will win the next general election?", "What is today's top news headline?", "What do you think of the current government?", "Summarise today's newspaper."],
 "shopping-tech": ["Which phone is best under 20000 rupees?", "How do I reset my Instagram password?", "Where can I buy a cheap laptop?", "How do I fix my WiFi router?"],
 "other-institutions": ["Show the marks of students at JNTU Kakinada.", "What is the attendance of students in another college?", "Give me the placement statistics of IIT Madras.", "What is the fee structure of Stanford University?"],
 "unsafe-write-or-admin": ["Update my attendance in Database Management Systems to 100%.", "Delete all the marks of student 23BQ1A0001.", "Drop the students table.", "Change my marks in Operating Systems to 90.", "Show me the admin password of the college portal.", "Insert a new student record named Ravi into the database.", "Grant me administrator access to the database.", "Export all students' personal email addresses."],
 "personal-misc": ["Help me write a love letter to my friend.", "Write a business plan for my uncle's textile shop.", "Translate 'good morning' into five languages."],
}
for sub, qs in OOS.items():
    for q in qs:
        add("OUT-OF-SCOPE", sub, q)
assert counts["OUT-OF-SCOPE"] == 60, counts["OUT-OF-SCOPE"]

# ---------------------------------------------------------------- RAG (100)
RAG = [
 ("Java", "Explain the four pillars of object-oriented programming in Java.", "encapsulation, inheritance, polymorphism, abstraction"),
 ("Java", "What is the difference between JDK, JRE and JVM?", "JDK=dev kit, JRE=runtime, JVM=executes bytecode"),
 ("Java", "What is the difference between an abstract class and an interface in Java?", "abstract class: state+partial impl; interface: contract, multiple implementation"),
 ("Java", "How does method overloading differ from method overriding?", "overload=same name diff params compile-time; override=subclass redefines runtime"),
 ("Java", "What are the different access modifiers in Java?", "public, protected, default, private"),
 ("Java", "Explain exception handling using try, catch and finally in Java.", "try block, catch handles, finally always runs"),
 ("Java", "What is the difference between checked and unchecked exceptions?", "checked at compile time; unchecked are runtime"),
 ("Java", "What is multithreading and how can threads be created in Java?", "extend Thread or implement Runnable"),
 ("Java", "Explain the life cycle of a thread in Java.", "new, runnable, running, blocked/waiting, terminated"),
 ("Java", "What is the Java Collections Framework?", "List, Set, Map interfaces and implementations"),
 ("Java", "What is the difference between ArrayList and LinkedList?", "array-backed fast access vs node-based fast insert/delete"),
 ("Java", "How does a HashMap work internally?", "hashing to buckets, equals/hashCode, collision handling"),
 ("Java", "What is the purpose of the final keyword in Java?", "constant variable, non-overridable method, non-inheritable class"),
 ("Java", "What are constructors and what are their types?", "default, parameterized, copy-style constructors"),
 ("Java", "What is garbage collection in Java?", "automatic reclaiming of unreachable objects"),
 ("Java", "Explain the static keyword in Java.", "class-level members shared across instances"),
 ("Java", "What is the difference between String, StringBuilder and StringBuffer?", "immutable vs mutable; StringBuffer synchronized"),
 ("Java", "What are packages in Java and why are they used?", "namespace grouping, access control, reuse"),
 ("Java", "Explain the this and super keywords in Java.", "current object reference vs parent class reference"),
 ("Java", "What are lambda expressions in Java 8?", "anonymous functions for functional interfaces"),
 ("DBMS", "What is normalization and why is it needed?", "reduce redundancy and anomalies"),
 ("DBMS", "Explain 1NF, 2NF and 3NF with examples.", "atomic values; no partial dependency; no transitive dependency"),
 ("DBMS", "What are the ACID properties of a transaction?", "atomicity, consistency, isolation, durability"),
 ("DBMS", "What is the difference between a primary key and a foreign key?", "unique row identifier vs reference to another table"),
 ("DBMS", "Explain the different types of SQL joins.", "inner, left, right, full outer"),
 ("DBMS", "What is indexing in databases and how does it speed up queries?", "auxiliary structure like B-tree avoiding full scans"),
 ("DBMS", "What is BCNF and how does it differ from 3NF?", "every determinant is a candidate key"),
 ("DBMS", "What is an ER diagram?", "entities, attributes, relationships model"),
 ("DBMS", "What is the difference between DELETE, TRUNCATE and DROP?", "rows vs all rows quickly vs table removal"),
 ("DBMS", "What are database views?", "virtual tables defined by a query"),
 ("DBMS", "What are triggers in SQL?", "automatic procedures fired on insert/update/delete"),
 ("DBMS", "What is the difference between SQL and NoSQL databases?", "relational schema vs flexible non-relational models"),
 ("DBMS", "What is concurrency control and why is it required?", "locking/timestamps to keep isolation"),
 ("DBMS", "What is a deadlock in a database system?", "transactions waiting on each other's locks"),
 ("OS", "What is the difference between a process and a thread?", "independent address space vs shared within process"),
 ("OS", "What are the necessary conditions for deadlock?", "mutual exclusion, hold and wait, no preemption, circular wait"),
 ("OS", "Explain paging and segmentation in memory management.", "fixed-size pages vs logical segments"),
 ("OS", "Explain the CPU scheduling algorithms FCFS, SJF and Round Robin.", "arrival order, shortest burst, time quantum"),
 ("OS", "What is a semaphore?", "synchronization variable with wait/signal operations"),
 ("OS", "What is virtual memory?", "disk-backed extension of RAM using paging"),
 ("OS", "What is the difference between a mutex and a semaphore?", "ownership-based lock vs signalling counter"),
 ("OS", "What is context switching?", "saving and restoring process state on CPU switch"),
 ("OS", "What is thrashing in operating systems?", "excessive paging reducing performance"),
 ("OS", "What are system calls?", "interface between user programs and kernel"),
 ("DSA", "What is the difference between a stack and a queue?", "LIFO vs FIFO"),
 ("DSA", "What is a binary search tree?", "left < node < right ordering"),
 ("DSA", "What are the types of linked lists?", "singly, doubly, circular"),
 ("DSA", "What is Big-O notation?", "upper bound on growth of running time"),
 ("DSA", "How does quicksort work and what is its time complexity?", "pivot partition; avg O(n log n), worst O(n^2)"),
 ("DSA", "How does merge sort work?", "divide, sort halves, merge; O(n log n)"),
 ("DSA", "What is the difference between BFS and DFS?", "level-order with queue vs depth-first with stack"),
 ("DSA", "What is hashing and how are collisions handled?", "hash function; chaining or open addressing"),
 ("DSA", "What is dynamic programming?", "overlapping subproblems and memoization"),
 ("DSA", "What is a heap data structure?", "complete binary tree with heap property"),
 ("ML", "What is the difference between supervised and unsupervised learning?", "labelled vs unlabelled data"),
 ("ML", "What is overfitting and how can it be prevented?", "memorizing noise; regularization, more data, cross-validation"),
 ("ML", "Explain the bias-variance tradeoff.", "underfit vs overfit balance"),
 ("ML", "What is gradient descent?", "iterative loss minimization along negative gradient"),
 ("ML", "How does a decision tree work?", "splits on features by impurity measures"),
 ("ML", "How does the k-means clustering algorithm work?", "assign to nearest centroid, update centroids"),
 ("ML", "What is a support vector machine?", "maximum-margin hyperplane classifier"),
 ("ML", "What are precision, recall and the confusion matrix?", "TP/FP/FN/TN based metrics"),
 ("ML", "What is cross-validation?", "k-fold evaluation on rotating splits"),
 ("ML", "What is the difference between L1 and L2 regularization?", "sparsity vs weight shrinkage"),
 ("ML", "What is a neural network?", "layers of weighted neurons with activations"),
 ("ML", "What is backpropagation?", "gradient computation via chain rule"),
 ("ML", "What is a convolutional neural network?", "convolution filters for spatial features"),
 ("ML", "What is tokenization in natural language processing?", "splitting text into tokens"),
 ("Python", "What is the difference between a list and a tuple in Python?", "mutable vs immutable"),
 ("Python", "What are decorators in Python?", "functions wrapping other functions"),
 ("Python", "What are generators in Python?", "lazy iterators using yield"),
 ("Python", "What is the Global Interpreter Lock?", "mutex allowing one thread to run bytecode at a time"),
 ("Python", "What is list comprehension?", "concise list construction syntax"),
 ("Python", "How is object-oriented programming implemented in Python?", "classes, inheritance, special methods"),
 ("Networks", "Explain the OSI model and its seven layers.", "physical to application layers"),
 ("Networks", "What is the difference between TCP and UDP?", "reliable connection-oriented vs fast connectionless"),
 ("Networks", "What is IP addressing and subnetting?", "IPv4 addressing and network division"),
 ("Networks", "How does DNS work?", "domain name to IP resolution hierarchy"),
 ("Networks", "What is the difference between HTTP and HTTPS?", "TLS-encrypted transport"),
 ("Networks", "What is ARP?", "maps IP address to MAC address"),
 ("Networks", "What is congestion control in TCP?", "slow start, congestion avoidance"),
 ("Networks", "What is a firewall?", "filters network traffic by rules"),
 ("SE", "What are the phases of the Software Development Life Cycle?", "requirements, design, implementation, testing, deployment, maintenance"),
 ("SE", "What is the difference between the waterfall and agile models?", "sequential vs iterative"),
 ("SE", "What is the difference between unit testing and integration testing?", "single component vs interaction between components"),
 ("SE", "What are UML diagrams?", "standard notation for modelling software"),
 ("SE", "What is version control and why is Git used?", "track changes, branches, collaboration"),
 ("SE", "What is DevOps?", "development and operations automation, CI/CD"),
 ("AI", "What is Retrieval-Augmented Generation (RAG)?", "retrieve context then generate grounded answer"),
 ("AI", "What are embeddings?", "dense vector representations of text"),
 ("AI", "What is a vector database?", "stores embeddings for similarity search"),
 ("AI", "What is hallucination in large language models?", "fluent but unsupported output"),
 ("AI", "What is prompt engineering?", "designing inputs to steer model output"),
 ("AI", "What is the difference between fine-tuning and RAG?", "weight updates vs external retrieval"),
 ("General", "What is the difference between a compiler and an interpreter?", "whole-program translation vs line-by-line execution"),
 ("General", "What is cloud computing and what are its service models?", "IaaS, PaaS, SaaS"),
 ("General", "What is the CIA triad in information security?", "confidentiality, integrity, availability"),
 ("General", "What is a REST API?", "stateless HTTP resource-based interface"),
 ("General", "What are microservices?", "small independently deployable services"),
 ("General", "What is the difference between an algorithm and a program?", "finite step logic vs executable implementation"),
]
assert len(RAG) == 100, len(RAG)
for topic, q, key in RAG:
    add("RAG", topic, q, topic=f"KB: {topic}", answer=key)

# ---------------------------------------------------------------- finalize
assert counts == Counter(QUOTA), counts
random.shuffle(rows)
cols = ["query_id", "question", "route", "subtype", "gold_sql", "gold_rag_source", "gold_answer"]
for i, r in enumerate(rows, 1):
    r["query_id"] = f"Q{i:03d}"
with open(OUT / "labelled_queries.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows({c: r[c] for c in cols} for r in rows)
(OUT / "labelled_queries.json").write_text(json.dumps([{c: r[c] for c in cols} for r in rows], indent=2, ensure_ascii=False), encoding="utf-8")
print(len(rows), dict(counts))
