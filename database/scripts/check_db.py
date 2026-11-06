import sqlite3
conn = sqlite3.connect("database/data/synthetic_education.db")

print("Student:")
print(conn.execute("SELECT * FROM students LIMIT 1").fetchall())

sid = conn.execute("SELECT student_id FROM students LIMIT 1").fetchone()[0]

print("\nHer marks (4 rows):")
for row in conn.execute("SELECT * FROM marks WHERE student_id=?", (sid,)):
    print(row)

print("\nHer attendance (4 rows):")
for row in conn.execute("SELECT * FROM attendance WHERE student_id=?", (sid,)):
    print(row)