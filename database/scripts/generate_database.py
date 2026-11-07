#!/usr/bin/env python3
"""M1.2 - Generate the synthetic education database (2,000 fictional students).

Run from the repo root:  python database/scripts/generate_database.py
Deterministic: the same SEED always produces the same database.
"""
import random
import sqlite3
from pathlib import Path

from faker import Faker

SEED = 42
N_STUDENTS = 2000
ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "database" / "schema" / "education_schema.sql"
DB = ROOT / "data" / "generated" / "synthetic_education.db"

# 20 unique courses per department = 4 odd semesters (1,3,5,7) x 5 courses
CATALOG = {
    "CSM": ["Mathematics for Machine Learning", "Programming in Python", "Digital Logic Design",
            "Data Structures", "Discrete Mathematics", "Database Management Systems",
            "Object Oriented Programming through Java", "Operating Systems", "Computer Organization",
            "Probability and Statistics", "Machine Learning", "Computer Networks",
            "Software Engineering", "Design and Analysis of Algorithms",
            "Formal Languages and Automata Theory", "Deep Learning", "Natural Language Processing",
            "Big Data Analytics", "Computer Vision", "Reinforcement Learning"],
    "CSE": ["Engineering Mathematics", "C Programming", "Engineering Physics",
            "Basic Electrical Engineering", "Engineering Graphics", "Data Structures using C++",
            "Digital Electronics", "Java Programming", "Discrete Structures", "Computer Architecture",
            "Web Technologies", "Compiler Design", "Information Security", "Cloud Computing",
            "Mobile Application Development", "Distributed Systems", "Software Testing",
            "Internet of Things", "Blockchain Technology", "Cyber Forensics"],
    "ECE": ["Linear Algebra and Calculus", "Engineering Chemistry", "Network Analysis",
            "Electronic Devices and Circuits", "Signals and Systems", "Analog Circuits",
            "Digital Signal Processing", "Electromagnetic Theory", "Control Systems", "Microprocessors",
            "VLSI Design", "Digital Communications", "Antennas and Wave Propagation",
            "Embedded Systems", "Microwave Engineering", "Optical Communications",
            "Wireless Communications", "Radar Systems", "Satellite Communications", "Image Processing"],
}
DEPT_WEIGHTS = {"CSM": 0.40, "CSE": 0.35, "ECE": 0.25}
DESIGNATIONS = ["Assistant Professor", "Associate Professor", "Professor"]


def clip(x, lo, hi):
    return max(lo, min(hi, x))


def main():
    random.seed(SEED)
    Faker.seed(SEED)
    fake = Faker("en_IN")
    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA.read_text())

    used_names = set()

    def unique_name():
        while True:
            n = f"{fake.first_name()} {fake.last_name()}"
            if n not in used_names and "'" not in n:
                used_names.add(n)
                return n

    faculty, fid = {}, 1
    for dept in CATALOG:
        faculty[dept] = []
        for _ in range(10):
            f_id = f"F{fid:03d}"
            fid += 1
            faculty[dept].append(f_id)
            con.execute("INSERT INTO faculty VALUES (?,?,?,?)",
                        (f_id, unique_name(), dept, random.choice(DESIGNATIONS)))

    course_ids = {}
    for dept, names in CATALOG.items():
        for i, cname in enumerate(names):
            sem = [1, 3, 5, 7][i // 5]
            cid = f"{dept}{sem}{i % 5 + 1:02d}"
            course_ids.setdefault((dept, sem), []).append(cid)
            con.execute("INSERT INTO courses VALUES (?,?,?,?,?,?)",
                        (cid, cname, dept, sem, random.choice([3, 3, 4]), random.choice(faculty[dept])))

    depts, weights = list(DEPT_WEIGHTS), list(DEPT_WEIGHTS.values())
    for idx in range(1, N_STUDENTS + 1):
        dept = random.choices(depts, weights)[0]
        year = random.randint(1, 4)
        adm = 2027 - year
        sid = f"{adm % 100}BQ1A{idx:04d}"
        con.execute("INSERT INTO students VALUES (?,?,?,?,?,?,?)",
                    (sid, unique_name(), dept, year, random.choice("ABC"), adm,
                     f"{sid.lower()}@example.edu"))
        ability = random.gauss(0, 1)
        for cid in course_ids[(dept, 2 * year - 1)]:
            marks = int(clip(round(62 + 13 * ability + random.gauss(0, 9)), 8, 100))
            total = random.randint(38, 60)
            pct = clip(80 + 9 * ability + random.gauss(0, 9), 35, 100)
            con.execute("INSERT INTO marks (student_id,course_id,marks_obtained) VALUES (?,?,?)",
                        (sid, cid, marks))
            con.execute("INSERT INTO attendance (student_id,course_id,total_classes,attended_classes) "
                        "VALUES (?,?,?,?)", (sid, cid, total, round(pct * total / 100)))
    con.commit()
    for t in ("students", "faculty", "courses", "marks", "attendance"):
        print(f"{t:<11}{con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>7}")
    con.close()


if __name__ == "__main__":
    main()
