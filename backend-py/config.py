import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

VECTOR_DB_NAME = os.getenv('VECTOR_DB_NAME', 'SW_vector_db-4')