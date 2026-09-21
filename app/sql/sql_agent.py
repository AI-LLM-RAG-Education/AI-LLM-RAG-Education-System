from app.database import get_connection


def execute_query(query, params=()):
    conn = get_connection()
    result = conn.execute(query, params).fetchall()
    conn.close()
    return result


def get_student_mark(student_name, subject_name):
    query = """
    SELECT s.name, sub.subject_name, m.marks
    FROM marks m
    JOIN students s ON m.student_id = s.student_id
    JOIN subjects sub ON m.subject_id = sub.subject_id
    WHERE LOWER(s.name) = LOWER(?)
    AND LOWER(sub.subject_name) = LOWER(?)
    """

    result = execute_query(query, (student_name, subject_name))

    if result:
        return f"{result[0][0]}'s {result[0][1]} mark is {result[0][2]}."

    return f"No mark record was found for {student_name} in {subject_name}."


def get_attendance(student_name, subject_name):
    query = """
    SELECT s.name, sub.subject_name, a.percentage
    FROM attendance a
    JOIN students s ON a.student_id = s.student_id
    JOIN subjects sub ON a.subject_id = sub.subject_id
    WHERE LOWER(s.name) = LOWER(?)
    AND LOWER(sub.subject_name) = LOWER(?)
    """

    result = execute_query(query, (student_name, subject_name))

    if result:
        return f"{result[0][0]}'s {result[0][1]} attendance is {result[0][2]}%."

    return f"No attendance record was found for {student_name} in {subject_name}."


def get_student_details(student_name):
    query = """
    SELECT student_id, name, department, year, section
    FROM students
    WHERE LOWER(name) = LOWER(?)
    """

    result = execute_query(query, (student_name,))

    if result:
        r = result[0]
        return (
            f"Student ID: {r[0]}, Name: {r[1]}, "
            f"Department: {r[2]}, Year: {r[3]}, Section: {r[4]}"
        )

    return f"No student record was found for {student_name}."


if __name__ == "__main__":
    print(get_student_mark("Yasaswini", "DBMS"))
    print(get_student_mark("Yasaswini", "Python"))
    print(get_attendance("Yasaswini", "DBMS"))
    print(get_attendance("Yasaswini", "Python"))
    print(get_student_details("Yasaswini"))