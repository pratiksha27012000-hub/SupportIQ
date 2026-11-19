
from backend.app.core.database import get_db_connection


connection = get_db_connection()

try:
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_name = 'tickets'
        ORDER BY ordinal_position;
    """)

    columns = cursor.fetchall()

    print("SUPPORTIQ TICKET TABLE")
    print("----------------------")

    for column in columns:
        print(f"{column[0]} : {column[1]}")

    cursor.close()

finally:
    connection.close()
