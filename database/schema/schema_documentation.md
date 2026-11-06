# M1.1 – Database Schema Design

## 1. Introduction

The objective of M1.1 is to design a relational database schema for the AI-LLM RAG Education System. The database stores structured academic information about students, faculty, courses, marks and attendance.

The schema establishes relationships between these entities using primary keys and foreign keys.

## 2. Database Entities

### 2.1 Students Table

Stores student academic and identification details.

| Column | Data Type | Constraint |
|---|---|---|
| student_id | TEXT | Primary Key |
| name | TEXT | NOT NULL |
| department | TEXT | NOT NULL |
| year | INTEGER | NOT NULL, CHECK |
| section | TEXT | NOT NULL |

### 2.2 Faculty Table

Stores faculty information.

| Column | Data Type | Constraint |
|---|---|---|
| faculty_id | TEXT | Primary Key |
| faculty_name | TEXT | NOT NULL |
| department | TEXT | NOT NULL |
| designation | TEXT | NOT NULL |

### 2.3 Courses Table

Stores course information and the faculty member assigned to each course.

| Column | Data Type | Constraint |
|---|---|---|
| course_id | TEXT | Primary Key |
| course_name | TEXT | NOT NULL |
| faculty_id | TEXT | Foreign Key |
| semester | INTEGER | NOT NULL, CHECK |

### 2.4 Marks Table

Stores student assessment marks for different courses.

| Column | Data Type | Constraint |
|---|---|---|
| mark_id | TEXT | Primary Key |
| student_id | TEXT | Foreign Key |
| course_id | TEXT | Foreign Key |
| marks_obtained | REAL | NOT NULL, CHECK |
| max_marks | REAL | NOT NULL, CHECK |

### 2.5 Attendance Table

Stores the aggregate attendance information of students for each course.

| Column | Data Type | Constraint |
|---|---|---|
| attendance_id | TEXT | Primary Key |
| student_id | TEXT | Foreign Key |
| course_id | TEXT | Foreign Key |
| total_classes | INTEGER | NOT NULL, CHECK |
| attended_classes | INTEGER | NOT NULL, CHECK |

Attendance percentage is calculated using:

Attendance Percentage = (Attended Classes / Total Classes) × 100

## 3. Primary Keys and Foreign Keys

Primary keys uniquely identify records in each table.

Foreign keys establish relationships between related tables:

- `courses.faculty_id` references `faculty.faculty_id`.
- `marks.student_id` references `students.student_id`.
- `marks.course_id` references `courses.course_id`.
- `attendance.student_id` references `students.student_id`.
- `attendance.course_id` references `courses.course_id`.

## 4. Entity Relationships

1. Faculty to Courses: One-to-Many.
2. Students to Marks: One-to-Many.
3. Courses to Marks: One-to-Many.
4. Students to Attendance: One-to-Many.
5. Courses to Attendance: One-to-Many.

## 5. Integrity Constraints

The database uses:

- PRIMARY KEY to uniquely identify records.
- FOREIGN KEY to maintain referential integrity.
- NOT NULL to ensure mandatory fields are populated.
- UNIQUE to prevent duplicate student-course attendance summaries.
- CHECK to validate year, semester, marks and attendance values.
- INDEX to improve frequently used lookup operations.

## 6. Implementation and Testing

The schema is implemented using SQLite.

A Python test script (`test_schema.py`) validates:

1. Table creation.
2. Sample data insertion.
3. Attendance percentage calculation.
4. Foreign-key enforcement.
5. Marks validation.
6. Existence of all five required tables.

All schema tests passed successfully using a temporary SQLite database.

## 7. Future Enhancements

- Introduce a faculty-course assignment table if multiple faculty members teach the same course.
- Extend attendance to session-level records if required.
- Integrate the finalized schema with synthetic academic data.
- Migrate to PostgreSQL for later application and access-control modules.

## 8. Deliverables

- Relational database schema (`schema.sql`).
- Entity Relationship Diagram (`er_diagram.md`).
- Schema testing script (`test_schema.py`).
- Database schema documentation (`schema_documentation.md`).