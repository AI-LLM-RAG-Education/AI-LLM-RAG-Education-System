-- M1.1 Education database schema (SQLite). Synthetic data only.
PRAGMA foreign_keys = ON;

CREATE TABLE faculty (
    faculty_id  TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    department  TEXT NOT NULL,
    designation TEXT NOT NULL
);

CREATE TABLE courses (
    course_id   TEXT PRIMARY KEY,
    course_name TEXT NOT NULL UNIQUE,
    department  TEXT NOT NULL,
    semester    INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    credits     INTEGER NOT NULL,
    faculty_id  TEXT NOT NULL REFERENCES faculty(faculty_id)
);

CREATE TABLE students (
    student_id     TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    department     TEXT NOT NULL,
    year           INTEGER NOT NULL CHECK (year BETWEEN 1 AND 4),
    section        TEXT NOT NULL,
    admission_year INTEGER NOT NULL,
    email          TEXT UNIQUE
);

CREATE TABLE marks (
    mark_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id     TEXT NOT NULL REFERENCES students(student_id),
    course_id      TEXT NOT NULL REFERENCES courses(course_id),
    marks_obtained INTEGER NOT NULL CHECK (marks_obtained BETWEEN 0 AND 100),
    max_marks      INTEGER NOT NULL DEFAULT 100,
    UNIQUE (student_id, course_id)
);

CREATE TABLE attendance (
    attendance_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id       TEXT NOT NULL REFERENCES students(student_id),
    course_id        TEXT NOT NULL REFERENCES courses(course_id),
    total_classes    INTEGER NOT NULL,
    attended_classes INTEGER NOT NULL,
    CHECK (attended_classes <= total_classes),
    UNIQUE (student_id, course_id)
);

CREATE INDEX idx_marks_student      ON marks(student_id);
CREATE INDEX idx_marks_course       ON marks(course_id);
CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_students_dept_year ON students(department, year);
