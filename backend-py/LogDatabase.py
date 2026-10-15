import os
import pymysql
from pymysql.err import Error
from contextlib import contextmanager
from fastapi import Depends, HTTPException, status


class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', 'swcup')


@contextmanager
def get_db_connection():
    config = DatabaseConfig()
    try:
        connection = pymysql.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            database=config.database,
            cursorclass=pymysql.cursors.DictCursor  # 指定游标类为 DictCursor
        )
        yield connection
    except Error as e:
        raise RuntimeError(f"数据库连接失败: {e}") from e
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()


def get_db():
    with get_db_connection() as conn:
        yield conn


class UserRepository:
    @staticmethod
    def get_user_by_username(conn, username: str):
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            return cursor.fetchone()

    @staticmethod
    def get_user_by_id(conn, user_id: int):
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
            return cursor.fetchone()

    @staticmethod
    def create_user(conn, username: str, hashed_password: str, email: str = None, face_filename: str = None):
        try:
            with conn.cursor() as cursor:
                if face_filename and email:
                    sql = "INSERT INTO user (username, password, email, face) VALUES (%s, %s, %s, %s)"
                    params = (username, hashed_password, email, face_filename)
                elif face_filename:
                    sql = "INSERT INTO user (username, password, face) VALUES (%s, %s, %s)"
                    params = (username, hashed_password, face_filename)
                elif email:
                    sql = "INSERT INTO user (username, password, email) VALUES (%s, %s, %s)"
                    params = (username, hashed_password, email)
                else:
                    sql = "INSERT INTO user (username, password) VALUES (%s, %s)"
                    params = (username, hashed_password)
                cursor.execute(sql, params)
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            conn.rollback()
            raise

    @staticmethod
    def update_user_face(conn, user_id: int, face_filename: str):
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE user SET face = %s WHERE user_id = %s"
                cursor.execute(sql, (face_filename, user_id))
                conn.commit()
                return cursor.rowcount
        except Error:
            conn.rollback()
            raise
