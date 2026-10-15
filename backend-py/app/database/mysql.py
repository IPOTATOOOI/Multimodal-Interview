import mysql.connector
from mysql.connector import Error
from datetime import datetime
from loguru import logger
import os

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv()

# MySQL数据库配置
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'swcup'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'swcup'),
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_mysql_connection():
    """
    获取MySQL数据库连接
    """
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            logger.info("MySQL数据库连接成功")
            return connection
    except Error as e:
        logger.error(f"MySQL数据库连接失败: {e}")
        raise e

def execute_query(query, params=None):
    """
    执行查询语句
    """
    connection = None
    cursor = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        result = cursor.fetchall()
        return result
    except Error as e:
        logger.error(f"查询执行失败: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def execute_insert(query, params=None):
    """
    执行插入语句，返回插入的ID
    """
    connection = None
    cursor = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        inserted_id = cursor.lastrowid
        connection.commit()
        return inserted_id
    except Error as e:
        logger.error(f"插入执行失败: {e}")
        if connection:
            connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def execute_update(query, params=None):
    """
    执行更新语句
    """
    connection = None
    cursor = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        affected_rows = cursor.rowcount
        connection.commit()
        return affected_rows
    except Error as e:
        logger.error(f"更新执行失败: {e}")
        if connection:
            connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
