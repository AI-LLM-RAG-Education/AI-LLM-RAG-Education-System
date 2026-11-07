
# M1.1 – Education Database ER Diagram

## Entity Relationships

```mermaid
erDiagram

    FACULTY ||--o{ COURSES : teaches

    STUDENTS ||--o{ MARKS : receives
    COURSES ||--o{ MARKS : contains

    STUDENTS ||--o{ ATTENDANCE : has
    COURSES ||--o{ ATTENDANCE : tracks

    STUDENTS {
        TEXT student_id PK
        TEXT name
        TEXT department
        INTEGER year
        TEXT section
    }

    FACULTY {
        TEXT faculty_id PK
        TEXT faculty_name
        TEXT department
        TEXT designation
    }

    COURSES {
        TEXT course_id PK
        TEXT course_name
        TEXT faculty_id FK
        INTEGER semester
    }

    MARKS {
        TEXT mark_id PK
        TEXT student_id FK
        TEXT course_id FK
        REAL marks_obtained
        REAL max_marks
    }

    ATTENDANCE {
        TEXT attendance_id PK
        TEXT student_id FK
        TEXT course_id FK
        INTEGER total_classes
        INTEGER attended_classes
    }
```

## Relationship Explanation

1. One faculty member can teach multiple courses.
2. One student can have multiple marks records.
3. One course can have multiple marks records.
4. One student can have one attendance summary per course.
5. One course can have attendance records for multiple students.
