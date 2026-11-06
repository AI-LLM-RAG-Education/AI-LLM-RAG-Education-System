
import sqlite3
import tempfile
from pathlib import Path

SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def test_database_schema():

    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:

        db_path = Path(temp_dir) / "test_education.db"

        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")

        try:
            # 1. Execute schema
            conn.executescript(schema)
            print("1. Schema creation: PASSED")

            # 2. Insert faculty
            conn.execute("""
                INSERT INTO faculty
                VALUES ('F001', 'Dr. Kumar', 'CSM', 'Professor')
            """)

            # 3. Insert student
            conn.execute("""
                INSERT INTO students
                VALUES ('23BQ1A42G9', 'Ravi Kumar',
                        'CSM', 3, 'A')
            """)

            # 4. Insert course
            conn.execute("""
                INSERT INTO courses
                VALUES ('CSM301', 'DBMS', 'F001', 5)
            """)

            # 5. Insert marks
            conn.execute("""
                INSERT INTO marks
                VALUES ('M001', '23BQ1A42G9',
                        'CSM301', 85, 100)
            """)

            # 6. Insert attendance
            conn.execute("""
                INSERT INTO attendance
                VALUES ('A001', '23BQ1A42G9',
                        'CSM301', 40, 35)
            """)

            conn.commit()
            print("2. Sample data insertion: PASSED")

            # 7. Check attendance percentage
            result = conn.execute("""
                SELECT ROUND(
                    attended_classes * 100.0 / total_classes, 2
                )
                FROM attendance
            """).fetchone()

            assert result[0] == 87.5
            print("3. Attendance calculation: PASSED")

            # 8. Test foreign key constraint
            try:
                conn.execute("""
                    INSERT INTO courses
                    VALUES ('CSM999', 'Invalid Course',
                            'F999', 5)
                """)
                raise AssertionError(
                    "Invalid faculty reference accepted"
                )

            except sqlite3.IntegrityError:
                print("4. Foreign key validation: PASSED")

            # 9. Test marks constraint
            try:
                conn.execute("""
                    INSERT INTO marks
                    VALUES ('M002', '23BQ1A42G9',
                            'CSM301', 110, 100)
                """)
                raise AssertionError(
                    "Invalid marks accepted"
                )

            except sqlite3.IntegrityError:
                print("5. Marks validation: PASSED")

            # 10. Verify required tables
            tables = conn.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                ORDER BY name
            """).fetchall()

            table_names = {row[0] for row in tables}

            expected = {
                "students",
                "faculty",
                "courses",
                "marks",
                "attendance"
            }

            assert expected.issubset(table_names)

            print("6. Five required tables: PASSED")
            print("\nALL SCHEMA TESTS PASSED!")

        finally:
            conn.close()


if __name__ == "__main__":
    test_database_schema()
