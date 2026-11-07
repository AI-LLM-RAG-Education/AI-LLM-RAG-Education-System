
-- ============================================
-- M1.1: EDUCATION DATABASE SCHEMA
-- Project: AI-LLM RAG Application
-- Database: SQLite
-- ============================================

PRAGMA foreign_keys = ON;

-- 1. STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 4),
    section TEXT NOT NULL
);

-- 2. FACULTY TABLE
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id TEXT PRIMARY KEY,
    faculty_name TEXT NOT NULL,
    department TEXT NOT NULL,
    designation TEXT NOT NULL
);

-- 3. COURSES TABLE
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    faculty_id TEXT NOT NULL,
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),

    FOREIGN KEY (faculty_id)
        REFERENCES faculty(faculty_id)
);

-- 4. MARKS TABLE
CREATE TABLE IF NOT EXISTS marks (
    mark_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    marks_obtained REAL NOT NULL CHECK (marks_obtained >= 0),
    max_marks REAL NOT NULL CHECK (max_marks > 0),

    CHECK (marks_obtained <= max_marks),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
);

-- 5. ATTENDANCE TABLE
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    total_classes INTEGER NOT NULL CHECK (total_classes > 0),
    attended_classes INTEGER NOT NULL CHECK (attended_classes >= 0),

    CHECK (attended_classes <= total_classes),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id),

    UNIQUE (student_id, course_id)
);

-- INDEXES FOR FASTER QUERY EXECUTION

CREATE INDEX IF NOT EXISTS idx_marks_student
ON marks(student_id);

CREATE INDEX IF NOT EXISTS idx_marks_course
ON marks(course_id);

CREATE INDEX IF NOT EXISTS idx_attendance_student
ON attendance(student_id);

CREATE INDEX IF NOT EXISTS idx_courses_faculty
ON courses(faculty_id);
