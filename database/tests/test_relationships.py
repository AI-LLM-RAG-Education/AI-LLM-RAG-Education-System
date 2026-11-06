"""
test(M1): validate student and course relationships
Project: AI-LLM RAG Education System

Run from repository root:
python database/tests/test_relationships.py
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = (
    Path(__file__).resolve().parents[1]
    / "data" / "synthetic_education.db"
)

# course_id looks like CSE-S06-C01, so the text before the first "-" is the department
DEPT_OF_COURSE = "substr(c.course_id, 1, instr(c.course_id, '-') - 1)"

CHECKS = [
    ("No orphan marks (missing student)",
     """SELECT m.mark_id FROM marks m
        LEFT JOIN students s ON m.student_id = s.student_id
        WHERE s.student_id IS NULL"""),

    ("No orphan marks (missing course)",
     """SELECT m.mark_id FROM marks m
        LEFT JOIN courses c ON m.course_id = c.course_id
        WHERE c.course_id IS NULL"""),

    ("No orphan attendance (missing student)",
     """SELECT a.attendance_id FROM attendance a
        LEFT JOIN students s ON a.student_id = s.student_id
        WHERE s.student_id IS NULL"""),

    ("No orphan attendance (missing course)",
     """SELECT a.attendance_id FROM attendance a
        LEFT JOIN courses c ON a.course_id = c.course_id
        WHERE c.course_id IS NULL"""),

    ("Every course has an existing faculty",
     """SELECT c.course_id FROM courses c
        LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
        WHERE f.faculty_id IS NULL"""),

    ("Every student has exactly 4 marks",
     """SELECT s.student_id FROM students s
        LEFT JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id HAVING COUNT(m.mark_id) != 4"""),

    ("Every student has exactly 4 attendance records",
     """SELECT s.student_id FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id HAVING COUNT(a.attendance_id) != 4"""),

    ("Marks and attendance cover the same student-course pairs",
     """SELECT student_id, course_id FROM marks
        EXCEPT SELECT student_id, course_id FROM attendance
        UNION
        SELECT student_id, course_id FROM attendance
        EXCEPT SELECT student_id, course_id FROM marks"""),

    ("Student courses belong to the student's department",
     f"""SELECT m.student_id, m.course_id FROM marks m
         JOIN students s ON m.student_id = s.student_id
         JOIN courses c ON m.course_id = c.course_id
         WHERE {DEPT_OF_COURSE} != s.department"""),

    ("Course semester matches student's year",
     """SELECT m.student_id, m.course_id FROM marks m
        JOIN students s ON m.student_id = s.student_id
        JOIN courses c ON m.course_id = c.course_id
        WHERE c.semester NOT IN (s.year * 2 - 1, s.year * 2)"""),

    ("All 4 courses of a student are in one semester",
     """SELECT m.student_id FROM marks m
        JOIN courses c ON m.course_id = c.course_id
        GROUP BY m.student_id HAVING COUNT(DISTINCT c.semester) != 1"""),

    ("Course faculty belongs to the same department",
     f"""SELECT c.course_id FROM courses c
         JOIN faculty f ON c.faculty_id = f.faculty_id
         WHERE {DEPT_OF_COURSE} != f.department"""),

    ("No duplicate student-course pairs in marks",
     """SELECT student_id, course_id FROM marks
        GROUP BY student_id, course_id HAVING COUNT(*) > 1"""),
]


def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        print("Run: python database/scripts/generate_data.py")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")

    failed = 0
    print("\n===== RELATIONSHIP VALIDATION =====")

    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    status = "PASSED" if not fk_errors else "FAILED"
    print(f"{status}  Foreign key check")
    failed += bool(fk_errors)

    for name, sql in CHECKS:
        bad_rows = conn.execute(sql).fetchall()
        status = "PASSED" if not bad_rows else "FAILED"
        print(f"{status}  {name}")
        if bad_rows:
            failed += 1
            print(f"        {len(bad_rows)} bad rows, e.g. {bad_rows[:3]}")

    unused = conn.execute(
        """SELECT COUNT(*) FROM courses c
           WHERE c.course_id NOT IN (SELECT course_id FROM marks)"""
    ).fetchone()[0]
    print(f"INFO    Courses with no students: {unused}")

    print("===================================")
    conn.close()

    if failed:
        print(f"{failed} check(s) FAILED")
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()