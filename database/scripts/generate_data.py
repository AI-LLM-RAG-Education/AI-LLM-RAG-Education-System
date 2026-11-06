
"""
M1.2 - Synthetic Educational Data Generator
Project: AI-LLM RAG Education System

Uses the exact five-table schema created in M1.1.
Default: 2,000 students across 10 departments.

Run from repository root:
python database/scripts/generate_data.py
"""

import argparse
import random
import sqlite3
from pathlib import Path

from faker import Faker


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

DEPARTMENTS = [
    "CSE", "CSM", "AIML", "AIDS", "EEE",
    "MECH", "CIVIL", "ECE", "CIC", "CSO"
]

SECTIONS = ["A", "B", "C", "D"]

DESIGNATIONS = [
    "Assistant Professor",
    "Associate Professor",
    "Professor",
    "Senior Lecturer"
]

# Department-specific subject pools.
# Four subjects are selected for each semester.

SUBJECTS = {
    "CSE": [
        "Programming Fundamentals", "Data Structures",
        "Database Management Systems", "Operating Systems",
        "Computer Networks", "Software Engineering",
        "Artificial Intelligence", "Machine Learning"
    ],
    "CSM": [
        "Programming for AI", "Data Structures",
        "Database Management Systems", "Machine Learning",
        "Deep Learning", "Natural Language Processing",
        "Computer Vision", "Data Analytics"
    ],
    "AIML": [
        "Artificial Intelligence", "Machine Learning",
        "Deep Learning", "Python Programming",
        "Data Structures", "Neural Networks",
        "Natural Language Processing", "Computer Vision"
    ],
    "AIDS": [
        "Statistics for Data Science", "Python Programming",
        "Data Analytics", "Database Management Systems",
        "Machine Learning", "Big Data Analytics",
        "Data Visualization", "Deep Learning"
    ],
    "EEE": [
        "Electrical Circuit Analysis", "Electrical Machines",
        "Power Systems", "Control Systems",
        "Power Electronics", "Electrical Measurements",
        "Digital Electronics", "Renewable Energy Systems"
    ],
    "MECH": [
        "Engineering Mechanics", "Thermodynamics",
        "Fluid Mechanics", "Manufacturing Technology",
        "Machine Design", "Heat Transfer",
        "CAD and CAM", "Industrial Engineering"
    ],
    "CIVIL": [
        "Building Materials", "Surveying",
        "Structural Analysis", "Geotechnical Engineering",
        "Fluid Mechanics", "Transportation Engineering",
        "Environmental Engineering", "Concrete Technology"
    ],
    "ECE": [
        "Electronic Devices", "Digital Electronics",
        "Signals and Systems", "Communication Systems",
        "Microprocessors", "VLSI Design",
        "Control Systems", "Embedded Systems"
    ],
    "CIC": [
        "Internet of Things", "Python Programming",
        "Computer Networks", "Cloud Computing",
        "Embedded Systems", "Database Management Systems",
        "Cyber Security", "Machine Learning"
    ],
    "CSO": [
        "Computer Programming", "Data Structures",
        "Operating Systems", "Database Management Systems",
        "Computer Networks", "Software Engineering",
        "Web Technologies", "Cloud Computing"
    ]
}


# --------------------------------------------------
# 2. PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

SCHEMA_FILE = BASE_DIR / "schema" / "schema.sql"

DEFAULT_DB_PATH = (
    BASE_DIR / "data" / "synthetic_education.db"
)


# --------------------------------------------------
# 3. INITIALIZE DATABASE
# --------------------------------------------------

def initialize_database(db_path):

    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_FILE}"
        )

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    schema = SCHEMA_FILE.read_text(
        encoding="utf-8"
    )

    conn = sqlite3.connect(str(db_path))

    conn.execute("PRAGMA foreign_keys = ON")

    conn.executescript(schema)

    return conn


# --------------------------------------------------
# 4. GENERATE FACULTY
# --------------------------------------------------

def generate_faculty(fake):

    faculty_records = []

    for department in DEPARTMENTS:

        for number in range(1, 6):

            faculty_id = (
                f"F-{department}-{number:03d}"
            )

            faculty_name = fake.name()

            designation = random.choice(
                DESIGNATIONS
            )

            faculty_records.append((
                faculty_id,
                faculty_name,
                department,
                designation
            ))

    return faculty_records


# --------------------------------------------------
# 5. GENERATE COURSES
# --------------------------------------------------

def generate_courses(faculty_records):

    faculty_by_department = {}

    for faculty in faculty_records:

        department = faculty[2]

        faculty_by_department.setdefault(
            department, []
        ).append(faculty[0])

    course_records = []

    courses_by_department_semester = {}

    for department in DEPARTMENTS:

        subject_pool = SUBJECTS[department]

        for semester in range(1, 9):

            course_list = []

            for number in range(1, 5):

                course_id = (
                    f"{department}-S{semester:02d}"
                    f"-C{number:02d}"
                )

                subject_index = (
                    (semester - 1) * 4 + number - 1
                ) % len(subject_pool)

                course_name = (
                    f"Semester {semester} - "
                    f"{subject_pool[subject_index]}"
                )

                faculty_id = random.choice(
                    faculty_by_department[department]
                )

                course_records.append((
                    course_id,
                    course_name,
                    faculty_id,
                    semester
                ))

                course_list.append(course_id)

            courses_by_department_semester[
                (department, semester)
            ] = course_list

    return course_records, courses_by_department_semester


# --------------------------------------------------
# 6. GENERATE STUDENTS
# --------------------------------------------------

def generate_students(fake, student_count):

    student_records = []
    student_details = {}

    base_count, remainder = divmod(
        student_count, len(DEPARTMENTS)
    )

    student_number = 1

    for dept_index, department in enumerate(DEPARTMENTS):

        department_count = (
            base_count +
            (1 if dept_index < remainder else 0)
        )

        for _ in range(department_count):

            student_id = (
                f"STU{student_number:06d}"
            )

            name = fake.name()

            year = random.randint(1, 4)

            section = random.choice(SECTIONS)

            # Each academic year has two semesters.
            semester = random.choice([
                (year * 2) - 1,
                year * 2
            ])

            student_records.append((
                student_id,
                name,
                department,
                year,
                section
            ))

            student_details[student_id] = {
                "department": department,
                "semester": semester
            }

            student_number += 1

    return student_records, student_details


# --------------------------------------------------
# 7. GENERATE MARKS
# --------------------------------------------------

def generate_marks(
    student_details,
    courses_by_department_semester
):

    marks_records = []

    mark_number = 1

    for student_id, details in student_details.items():

        department = details["department"]
        semester = details["semester"]

        course_ids = courses_by_department_semester[
            (department, semester)
        ]

        for course_id in course_ids:

            # Varied, plausible academic marks.
            marks_obtained = round(
                max(
                    20,
                    min(
                        100,
                        random.gauss(72, 14)
                    )
                ),
                2
            )

            max_marks = 100.0

            mark_id = f"M{mark_number:08d}"

            marks_records.append((
                mark_id,
                student_id,
                course_id,
                marks_obtained,
                max_marks
            ))

            mark_number += 1

    return marks_records


# --------------------------------------------------
# 8. GENERATE ATTENDANCE
# --------------------------------------------------

def generate_attendance(
    student_details,
    courses_by_department_semester
):

    attendance_records = []

    attendance_number = 1

    for student_id, details in student_details.items():

        department = details["department"]
        semester = details["semester"]

        course_ids = courses_by_department_semester[
            (department, semester)
        ]

        for course_id in course_ids:

            total_classes = random.randint(35, 50)

            attendance_rate = random.uniform(
                0.60, 0.99
            )

            attended_classes = round(
                total_classes * attendance_rate
            )

            attendance_id = (
                f"A{attendance_number:08d}"
            )

            attendance_records.append((
                attendance_id,
                student_id,
                course_id,
                total_classes,
                attended_classes
            ))

            attendance_number += 1

    return attendance_records


# --------------------------------------------------
# 9. INSERT DATA INTO SQLITE
# --------------------------------------------------

def insert_records(
    conn,
    faculty,
    courses,
    students,
    marks,
    attendance
):

    with conn:

        conn.executemany("""
            INSERT INTO faculty (
                faculty_id,
                faculty_name,
                department,
                designation
            )
            VALUES (?, ?, ?, ?)
        """, faculty)

        conn.executemany("""
            INSERT INTO courses (
                course_id,
                course_name,
                faculty_id,
                semester
            )
            VALUES (?, ?, ?, ?)
        """, courses)

        conn.executemany("""
            INSERT INTO students (
                student_id,
                name,
                department,
                year,
                section
            )
            VALUES (?, ?, ?, ?, ?)
        """, students)

        conn.executemany("""
            INSERT INTO marks (
                mark_id,
                student_id,
                course_id,
                marks_obtained,
                max_marks
            )
            VALUES (?, ?, ?, ?, ?)
        """, marks)

        conn.executemany("""
            INSERT INTO attendance (
                attendance_id,
                student_id,
                course_id,
                total_classes,
                attended_classes
            )
            VALUES (?, ?, ?, ?, ?)
        """, attendance)


# --------------------------------------------------
# 10. VALIDATE GENERATED DATABASE
# --------------------------------------------------

def validate_database(conn, expected_students):

    print("\n========== VALIDATION ==========")

    expected_counts = {
        "students": expected_students,
        "faculty": len(DEPARTMENTS) * 5,
        "courses": len(DEPARTMENTS) * 8 * 4,
        "marks": expected_students * 4,
        "attendance": expected_students * 4
    }

    all_passed = True

    for table, expected in expected_counts.items():

        actual = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        passed = actual == expected

        print(
            f"{table:15} : {actual:6} "
            f"/ Expected {expected:6} "
            f"{'PASSED' if passed else 'FAILED'}"
        )

        if not passed:
            all_passed = False

    # Foreign key validation
    foreign_key_errors = conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if foreign_key_errors:
        print("Foreign key validation: FAILED")
        all_passed = False
    else:
        print("Foreign key validation: PASSED")

    # Check every student has four marks.
    incorrect_marks = conn.execute("""
        SELECT student_id
        FROM marks
        GROUP BY student_id
        HAVING COUNT(*) != 4
    """).fetchall()

    if incorrect_marks:
        print("Marks distribution: FAILED")
        all_passed = False
    else:
        print("Marks distribution: PASSED")

    # Check every student has four attendance records.
    incorrect_attendance = conn.execute("""
        SELECT student_id
        FROM attendance
        GROUP BY student_id
        HAVING COUNT(*) != 4
    """).fetchall()

    if incorrect_attendance:
        print("Attendance distribution: FAILED")
        all_passed = False
    else:
        print("Attendance distribution: PASSED")

    # Check all ten departments exist.
    actual_departments = {
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT department FROM students"
        ).fetchall()
    }

    if actual_departments == set(DEPARTMENTS):
        print("Department validation: PASSED")
    else:
        print("Department validation: FAILED")
        all_passed = False

    # SQLite integrity validation
    integrity = conn.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    if integrity == "ok":
        print("SQLite integrity: PASSED")
    else:
        print("SQLite integrity: FAILED")
        all_passed = False

    print("================================")

    return all_passed


# --------------------------------------------------
# 11. MAIN EXECUTION
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Generate synthetic education data"
    )

    parser.add_argument(
        "--students",
        type=int,
        default=2000,
        help="Number of students (default: 2000)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Output SQLite database path"
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing output database"
    )

    args = parser.parse_args()

    if args.students < 1:
        parser.error("--students must be at least 1")

    # Reproducible random data.
    random.seed(args.seed)

    fake = Faker("en_IN")
    Faker.seed(args.seed)

    db_path = args.db_path.resolve()

    if db_path.exists():

        if not args.overwrite:
            parser.error(
                f"Database already exists: {db_path}\n"
                "Use --overwrite to replace it."
            )

        db_path.unlink()

    print("\n================================")
    print("M1.2 SYNTHETIC DATA GENERATOR")
    print("================================")

    print(f"Students requested : {args.students}")
    print(f"Departments        : {len(DEPARTMENTS)}")
    print(f"Random seed        : {args.seed}")
    print(f"Output database    : {db_path}")

    conn = None

    try:

        # Generate parent records first.
        faculty = generate_faculty(fake)

        courses, courses_map = generate_courses(
            faculty
        )

        students, student_details = generate_students(
            fake,
            args.students
        )

        marks = generate_marks(
            student_details,
            courses_map
        )

        attendance = generate_attendance(
            student_details,
            courses_map
        )

        # Create database and insert records.
        conn = initialize_database(db_path)

        insert_records(
            conn,
            faculty,
            courses,
            students,
            marks,
            attendance
        )

        # Validate everything.
        passed = validate_database(
            conn,
            args.students
        )

        if not passed:
            raise RuntimeError(
                "Data validation failed. "
                "Please inspect the output."
            )

        print("\nSUCCESS!")
        print("Synthetic education database generated.")
        print(f"Database location: {db_path}")

    except Exception:

        if conn is not None:
            conn.rollback()

        if db_path.exists():
            db_path.unlink()

        raise

    finally:

        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()
