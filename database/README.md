# Education Database (M1.1 and M1.2)

Project: AI-LLM RAG Education System

This module has two parts:

1. **M1.1 Schema**: creates the empty database tables.
2. **M1.2 Data generator**: fills the tables with 2,000 fake (synthetic) students.

Database type: **SQLite**

---

## Folder Structure

```
database/
├── data/
│   └── synthetic_education.db     # generated database
├── schema/
│   ├── schema.sql                 # creates the 5 tables
│   ├── test_schema.py             # tests the schema
│   ├── er_diagram.md / .png       # table relationship diagram
│   └── schema_documentation.md    # column details
├── scripts/
│   └── generate_data.py           # generates synthetic data
└── README.md
```

---

## M1.1 Schema

`schema.sql` creates 5 tables:

| Table | Purpose | Main Columns |
|---|---|---|
| students | Student details | student_id, name, department, year, section |
| faculty | Teacher details | faculty_id, faculty_name, department, designation |
| courses | Subjects taught | course_id, course_name, faculty_id, semester |
| marks | Marks per student per course | mark_id, student_id, course_id, marks_obtained, max_marks |
| attendance | Attendance per student per course | attendance_id, student_id, course_id, total_classes, attended_classes |

### Relationships

```
faculty ──► courses ◄── marks ──► students
               ▲                     ▲
               └──── attendance ─────┘
```

- One faculty member teaches many courses.
- One student has many marks and attendance records.
- Each course has many marks and attendance records.

### Rules enforced by the schema

- Year must be between 1 and 4.
- Semester must be between 1 and 8.
- Marks obtained cannot be negative or greater than max marks.
- Attended classes cannot be greater than total classes.
- Each student has only one attendance record per course.
- Foreign keys are enabled, so no record can point to a missing student, course or faculty.
- Indexes on student_id, course_id and faculty_id make queries faster.

Attendance percentage is **not stored**. It is calculated as `attended_classes * 100.0 / total_classes`.

---

## M1.2 Synthetic Data Generator

`generate_data.py` creates the database from `schema.sql` and fills it with random but realistic data using the Faker library.

### Records generated (default)

| Table | Rows | How |
|---|---|---|
| students | 2,000 | 200 per department |
| faculty | 50 | 5 per department |
| courses | 320 | 10 departments × 8 semesters × 4 courses |
| marks | 8,000 | 4 per student (one per course) |
| attendance | 8,000 | 4 per student (one per course) |

Departments: CSE, CSM, AIML, AIDS, EEE, MECH, CIVIL, ECE, CIC, CSO

### Data details

- Student years are 1 to 4, and sections are A to D.
- Each student's semester matches their year (year 3 means semester 5 or 6).
- Marks follow a bell curve around 72 out of 100, limited to 20 to 100.
- Total classes per course are 35 to 50, with attendance between 60% and 99%.
- A fixed seed (default 42) gives the same data every run.

---

## How to Run

Run all commands from the repository root.

```powershell
# 1. Create and activate the virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install requirements
pip install -r requirements.txt

# 3. Generate the database (2,000 students)
python database/scripts/generate_data.py

# Replace an existing database
python database/scripts/generate_data.py --overwrite

# Custom number of students
python database/scripts/generate_data.py --students 500 --overwrite

# Test the schema
python database/schema/test_schema.py
```

### Options

| Option | Default | Meaning |
|---|---|---|
| --students | 2000 | Number of students |
| --seed | 42 | Random seed for repeatable data |
| --db-path | database/data/synthetic_education.db | Output file |
| --overwrite | off | Replace an existing database |

### Validation

After generating, the script checks row counts, foreign keys, 4 marks and 4 attendance records per student, all 10 departments, and SQLite integrity. It prints `SUCCESS!` if everything passes.

---

## Sample Queries

```sql
-- Attendance percentage for one student
SELECT course_id,
       ROUND(attended_classes * 100.0 / total_classes, 1) AS attendance_pct
FROM attendance
WHERE student_id = 'STU000001';

-- Students below 75% attendance
SELECT student_id, course_id
FROM attendance
WHERE attended_classes * 100.0 / total_classes < 75;

-- Average marks per department
SELECT s.department, ROUND(AVG(m.marks_obtained), 2) AS avg_marks
FROM marks m
JOIN students s ON m.student_id = s.student_id
GROUP BY s.department;
```

---

## Requirements

- Python 3.9+
- faker (`pip install faker`)
- sqlite3 (built into Python)