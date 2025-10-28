import sqlite3
import psycopg2
import os
from django.conf import settings


def migrate_sqlite_to_postgres():
    """Миграция данных из SQLite в PostgreSQL"""

    # Подключение к SQLite
    sqlite_conn = sqlite3.connect('db.sqlite3')
    sqlite_cursor = sqlite_conn.cursor()

    # Подключение к PostgreSQL
    postgres_conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    postgres_cursor = postgres_conn.cursor()

    try:
        # Получаем список таблиц
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sqlite_cursor.fetchall()

        for table in tables:
            table_name = table[0]
            if table_name.startswith('sqlite_'):
                continue

            print(f"Migrating table: {table_name}")

            # Получаем данные из SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()

            # Получаем названия колонок
            sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in sqlite_cursor.fetchall()]

            if rows:
                # Создаем плейсхолдеры для INSERT
                placeholders = ', '.join(['%s'] * len(columns))
                columns_str = ', '.join(columns)

                # Вставляем данные в PostgreSQL
                insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                postgres_cursor.executemany(insert_query, rows)

        postgres_conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        postgres_conn.rollback()
    finally:
        sqlite_conn.close()
        postgres_conn.close()


if __name__ == "__main__":
    migrate_sqlite_to_postgres()