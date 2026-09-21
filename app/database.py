import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "education.db"


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        section TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY,
        subject_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS marks (
        mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        marks INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(subject_id) REFERENCES subjects(subject_id)
    );

    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        percentage REAL,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(subject_id) REFERENCES subjects(subject_id)
    );

    CREATE TABLE IF NOT EXISTS faculty (
        faculty_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL
    );
    """)

    # Students
    cursor.executemany("""
        INSERT OR IGNORE INTO students
        VALUES (?, ?, ?, ?, ?)
    """, [
        (101, "Yasaswini", "CSE-AIML", 4, "A"),
        (102, "Sirisha", "CSE-AIML", 4, "A"),
        (103, "Harika", "CSE-AIML", 4, "A"),
        (104, "Baji Vali", "CSE-AIML", 4, "A"),
        (105, "Beni", "CSE-AIML", 4, "A"),
        (106, "Suresh", "CSE-AIML", 4, "A")
    ])

    # Subjects
    cursor.executemany("""
        INSERT OR IGNORE INTO subjects
        VALUES (?, ?)
    """, [
        (1, "DBMS"),
        (2, "Artificial Intelligence"),
        (3, "Machine Learning"),
        (4, "Operating Systems"),
        (5, "Java")
    ])

    # Marks
    cursor.executemany("""
        INSERT INTO marks (student_id, subject_id, marks)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM marks
            WHERE student_id = ? AND subject_id = ?
        )
    """, [
        (101, 1, 86, 101, 1),
        (101, 2, 91, 101, 2),
        (101, 3, 88, 101, 3),
        (102, 1, 78, 102, 1),
        (102, 2, 84, 102, 2),
        (103, 1, 82, 103, 1),
        (103, 2, 88, 103, 2),
        (104, 1, 75, 104, 1),
        (105, 1, 90, 105, 1),
        (106, 1, 81, 106, 1)
    ])

    # Attendance
    cursor.executemany("""
        INSERT INTO attendance
        (student_id, subject_id, percentage)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM attendance
            WHERE student_id = ? AND subject_id = ?
        )
    """, [
        (101, 1, 87.5, 101, 1),
        (101, 2, 92.0, 101, 2),
        (101, 3, 89.0, 101, 3),
        (102, 1, 81.0, 102, 1),
        (102, 2, 86.0, 102, 2),
        (103, 1, 90.0, 103, 1),
        (104, 1, 76.0, 104, 1),
        (105, 1, 94.0, 105, 1),
        (106, 1, 83.0, 106, 1)
    ])

    # Faculty
    cursor.executemany("""
        INSERT OR IGNORE INTO faculty
        VALUES (?, ?, ?)
    """, [
        (201, "Dr. Anil Kumar", "CSE-AIML"),
        (202, "Dr. Priya Sharma", "CSE-AIML"),
        (203, "Dr. Ravi Teja", "CSE-AIML")
    ])

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("Education database created successfully!")