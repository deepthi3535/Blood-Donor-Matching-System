"""Create MySQL database and user for Blood Need."""

import os
import sys

import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'blood_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'blood_password')
DB_NAME = os.getenv('DB_NAME', 'blood_need_db')

ROOT_USER = os.getenv('MYSQL_ROOT_USER', 'root')
ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD', '')


def main():
    print("Setting up Blood Need database...")
    print(f"Host: {DB_HOST}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")

    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        connection.close()
        print("\nDatabase already configured and accessible.")
        print("Start the backend with: python run.py")
        return
    except pymysql.Error:
        print("App user cannot connect yet. Attempting setup with MySQL root...")

    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=ROOT_USER,
            password=ROOT_PASSWORD,
            charset='utf8mb4'
        )
    except pymysql.Error as exc:
        print(f"\nFailed to connect as MySQL root user: {exc}")
        print("Set MYSQL_ROOT_USER and MYSQL_ROOT_PASSWORD in .env if needed.")
        sys.exit(1)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(
                f"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' "
                f"IDENTIFIED BY '{DB_PASSWORD}'"
            )
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON `{DB_NAME}`.* TO '{DB_USER}'@'localhost'"
            )
            cursor.execute("FLUSH PRIVILEGES")
        connection.commit()
        print("\nDatabase setup complete.")
        print("Start the backend with: python run.py")
    finally:
        connection.close()


if __name__ == '__main__':
    main()
