from flask import Flask, render_template
from dotenv import load_dotenv
import mariadb
import sys
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)


def get_db_connection():
    try:
        conn = mariadb.connect(
            user=os.getenv('MARIADB_USER'),
            password=os.getenv('MARIADB_PASSWORD'),
            host=os.getenv('MARIADB_HOST', 'localhost'),
            port=int(os.getenv('MARIADB_PORT')),
            database=os.getenv('MARIADB_DATABASE'),
        )
        return conn
    except mariadb.Error as e:
        print(f"Error de conexión a MariaDB: {e}")
        sys.exit(1)


def get_all_tables(cursor):
    cursor.execute("SHOW TABLES")
    return [table[0] for table in cursor.fetchall()]


def get_table_data(cursor, table_name, limit=100):
    cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))

    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    return {
        'columns': columns,
        'rows': rows
    }


def get_all_data(cursor, tables, limit=100):
    data = {}
    for table in tables:
        data[table] = get_table_data(cursor, table, limit)
    return data


@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        db_name = conn.database
        tables = get_all_tables(cursor)
        data = get_all_data(cursor, tables, limit=100)

        return render_template(
            'index.html',
            data=data,
            db_name=db_name
        )
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)