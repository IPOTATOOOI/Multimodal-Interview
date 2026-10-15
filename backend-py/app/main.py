from app.core.redis_cache import build_cache_key, delete_cache_sync
import sys
import httpx
import pymysql
import subprocess
import threading
import uvicorn
from app.database.mysql import execute_query
import multiprocessing
from loguru import logger
# from sentence_transformers import SentenceTransformer
import chromadb
from neo4j import GraphDatabase, basic_auth

from chromadb.utils import embedding_functions
from neo4j import GraphDatabase, basic_auth
import os
from pathlib import Path


from fastapi import FastAPI, UploadFile, File, Form, Depends, APIRouter, HTTPException
from fastapi.params import Path as APIPath
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from LogDatabase import get_db
from app.database.mysql import execute_query
from app.routers import auth
from typing import Optional,List
from app.routers.ask.getQuestion import router as get_question_router
from app.routers.ask.history import router as history_router
from app.routers.ask.initiate import router as initiate_router
from app.routers.ask.question import router as question_router
from app.routers.audio.voice import router as voice_router
from app.routers.interview.interview_end import router as interview_end_router
from app.routers.prepare.position_info import router as position_info_router
from app.routers.questionBank.topic import router as questionbank_router
from app.routers.resume.resume import router as resume_router
from app.routers.written_test.written_test import router as written_test_router

from app.routers.graph.graph import router as graph_router
from app.routers.recommend import router as recommend_router
from app.routers.user_portrait import router as portrait_router
from app.routers.study_path import router as study_path_router
from app.routers.graph.upload import router as graph_upload_router
from app.routers.graphRAG_keyword.keyword_graph import router as graph_rag_keyword_router
#文本回答保存
from app.routers.text_input.text_input import router as text_input_router
# 改进后的graphRAG
from app.routers.graphRAG_enhanced.graph_rag_routes import  graph_rag_router
from app.routers.rag_router import router as rag_router
from app.routers.admin.admin import router as admin_router
#
# from app.graphRAG_enhanced.index_manager import index_manager
# from app.graphRAG_enhanced.graph_operations import Neo4jGraphOperations
# from app.graphRAG.embedding_utils import EmbeddingUtils
# from typing import List, Dict, Any, Union
#
# from app.graphRAG_enhanced.index_manager import index_manager
# from app.graphRAG_enhanced.graph_operations import Neo4jGraphOperations
# from app.graphRAG.embedding_utils import EmbeddingUtils
from typing import List, Dict, Any, Union

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from datetime import datetime
from app.speech_analyzer import start_monitoring, stop_monitoring
from contextlib import asynccontextmanager
from app.commentary_er import run_monitor
from app.image_analysis import analyze_expression_and_gesture
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(title="AI Interview API", version="2.0.0")
router = APIRouter()

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(initiate_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(question_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(interview_end_router, prefix="/api")
app.include_router(get_question_router, prefix="/api")
app.include_router(written_test_router, prefix="/api")
app.include_router(questionbank_router, prefix="/api")
app.include_router(position_info_router, prefix="/api")
app.include_router(recommend_router, prefix="/api")
app.include_router(graph_router, prefix="/api")
app.include_router(graph_upload_router, prefix="/api")
app.include_router(graph_rag_keyword_router, prefix="/api")
app.include_router(text_input_router, prefix="/api")
app.include_router(portrait_router)
app.include_router(study_path_router)
# 改进后的graphRAG
app.include_router(graph_rag_router)

#
# # graphRAG_enhanced 社区检测
# embedding_model = SentenceTransformer('')
# import os
# from dotenv import load_dotenv
#
# # 加载环境变量
# load_dotenv()
#
# chroma_client = chromadb.PersistentClient(path=os.getenv('CHROMA_DB_PATH', 'D:/fcproject/SWCUP-backend/chroma_db'))
# chroma_collection = chroma_client.get_or_create_collection(name="learning_community_embeddings")

#graphRAG_enhanced 局部子图检索



'''音频分析：'''
AUDIO_DIR = BASE_DIR / "uploads" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
async def start_audio_monitor():
    if os.getenv("AUDIO_MONITOR_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        logger.info("Audio monitor is disabled")
        return

    # 后台线程启动监控，不阻塞 FastAPI 主线程
    threading.Thread(
        target=start_monitoring,
        args=(str(AUDIO_DIR), "small"),
        daemon=True
    ).start()

@app.on_event("shutdown")
async def shutdown_event():
    stop_monitoring()
'''音频分析END'''





# Neo4j配置（局部子图检索用）
NEO4J_URI = settings.NEO4J_URI
NEO4J_USER = settings.NEO4J_USER
NEO4J_PASSWORD = settings.NEO4J_PASSWORD
# 定义Neo4j连接函数
def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD)
        )
        driver.verify_connectivity()
        return driver
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j连接失败：{str(e)}")
# graphRAG_enhanced 社区检测
# embedding_model = SentenceTransformer(os.getenv('EMBEDDING_MODEL_PATH', 'D:/fcproject/SWCUP-backend/vecDB/paraphrase-multilingual-MiniLM-L12-v2'))
# chroma_client = chromadb.PersistentClient(path=os.getenv('CHROMA_DB_PATH', 'D:/fcproject/SWCUP-backend/chroma_db'))
# chroma_collection = chroma_client.get_or_create_collection(name="learning_community_embeddings")

# app.include_router(rag_router)



@app.get("/")
async def root():
    return {"message": "Welcome to SWCUP Backend API"}


@app.post("/api/save-audio")
async def save_audio(
    file: UploadFile = File(...),
    historyId: Optional[str] = Form(None),
    history_id: Optional[str] = Form(None),
    question_qa_id: Optional[str] = Form(None)
):
    try:
        # 确保上传目录存在
        save_dir = os.getenv('UPLOAD_DIR', 'uploads/audio')
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file.filename)

        # 保存原始文件
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # 兼容两种字段命名：historyId / history_id
        incoming_history_id = historyId if historyId is not None else history_id
        if incoming_history_id is None:
            return {
                "success": False,
                "error": "缺少historyId或history_id参数"
            }

        # 将历史记录ID转换为整数类型
        try:
            history_id_int = int(incoming_history_id)
        except ValueError:
            return {
                "success": False,
                "error": f"无效的历史记录ID: {incoming_history_id}，应为整数类型"
            }

        logger.info(
            f"save-audio收到请求: history_id={history_id_int}, filename={file.filename}, question_qa_id={question_qa_id}"
        )

        # 构建转发接口的请求
        from dotenv import load_dotenv
        
        # 加载环境变量
        load_dotenv()
        
        transcribe_url = os.getenv('TRANSCRIBE_URL', 'http://127.0.0.1:8000/api/voice/transcribe')

        # 重置文件指针以便重新读取
        file.file.seek(0)

        async with httpx.AsyncClient() as client:
            # 构建multipart请求 - 使用原始文件对象
            files = {"file": (file.filename, file.file, file.content_type)}
            data = {
                "history_id": history_id_int,
            }
            if question_qa_id is not None:
                data["question_qa_id"] = question_qa_id

            # 发送请求。转写接口可能耗时较长，避免30秒超时导致仅保存不转写。
            response = await client.post(
                transcribe_url,
                files=files,
                data=data,
                timeout=300.0
            )

            # 检查响应状态
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"转写服务错误: {response.status_code} - {response.text}",
                    "transcribe_response": response.json() if response.text else None
                }

            transcribe_response = response.json()

        # 返回合并的结果
        return {
            "save_status": {
                "success": True,
                "message": "录音保存成功",
                "filepath": file_path,
                "historyId": incoming_history_id
            },
            "answer_index": transcribe_response.get("answer_index"),
            "transcribe_status": transcribe_response
        }

    except Exception as e:
        logger.exception("save-audio failed")
        return {
            "success": False,
            "error": str(e)
        }


# 全局计数器
image_counters = {}
counters_lock = {}


# 构建目标路径：项目根目录/facial_landmarks/img
IMAGE_SAVE_DIR = BASE_DIR / 'facial_landmarks' / 'img'
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)


@app.post("/api/save-image")
async def save_image(
        image: UploadFile = File(...),
        history_id: int = Form(...)
):
    """保存摄像头图片接口"""
    # 初始化计数器
    if history_id not in image_counters:
        image_counters[history_id] = 0
        counters_lock[history_id] = False

    # 等待计数器释放
    while counters_lock.get(history_id):
        pass

    # 锁定计数器
    counters_lock[history_id] = True
    image_counters[history_id] += 1
    counter = image_counters[history_id]

    # 生成文件名
    filename = f"his-{history_id}-img-{counter}.jpg"
    file_path = os.path.join(IMAGE_SAVE_DIR, filename)

    try:
        # 保存图片
        contents = await image.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # 更新计数器状态
        counters_lock[history_id] = False

        return {
            "success": True,
            "filename": filename,
            "history_id": history_id,
            "counter": counter
        }
    except Exception as e:
        # 出错时回滚计数器
        image_counters[history_id] -= 1
        counters_lock[history_id] = False
        return {
            "success": False,
            "error": str(e)
        }

IMAGE_DIR = "facial_landmarks/img"
PROCESSING_DIR = "facial_landmarks"
PREDICTOR_FILE = "../facial_landmarks/shape_predictor_68_face_landmarks.dat"

class JpgHandler(FileSystemEventHandler):
    """处理新jpg文件创建事件"""

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() in ('.jpg', '.jpeg'):
            print(f"检测到新图片: {file_path.name}")
            # 在独立线程中处理文件避免阻塞监控
            threading.Thread(
                target=process_image,
                args=(file_path.name,),
                daemon=True
            ).start()


def process_image(filename: str):
    """执行人脸关键点检测脚本"""
    command = [
        "python", "face_keypoints.py",
        "--shape-predictor", PREDICTOR_FILE,
        "--image", f"img/{filename}"
    ]

    try:
        # 在指定目录执行命令
        result = subprocess.run(
            command,
            cwd=PROCESSING_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"处理完成: {filename}\n输出: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"处理失败 {filename}:\n{e.stderr}")


@app.on_event("startup")
def start_file_watcher():
    """启动文件监视器"""
    # 确保目录存在
    Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)

    observer = Observer()
    event_handler = JpgHandler()
    observer.schedule(event_handler, IMAGE_DIR, recursive=False)
    observer.start()
    print(f"行为分析启动，开始监控目录: {IMAGE_DIR}")

    # 保存observer实例到app状态
    app.state.observer = observer


@app.on_event("shutdown")
def stop_file_watcher():
    """停止文件监视器"""
    app.state.observer.stop()
    app.state.observer.join()
    print("文件监控已停止")


# 请求数据模型
class ProfileUpdate(BaseModel):
    username: str
    name: str
    gender: int
    age: int
    university: str
    major: str

# 全局检索（社区摘要）请求模型
class CommunityRetrievalRequest(BaseModel):
    user_query: str
    top_k: int = 3  # 默认返回Top-3社区
    user_id: Optional[int] = None  # 添加user_id字段

class SubgraphRetrievalRequest(BaseModel):
    entities: list  # 从用户问题解析出的关键实体列表
    hop_count: int = 2  # 默认多跳次数
    user_id: Optional[int] = None  # 添加user_id字段

class SearchQuestionsRequest(BaseModel):
    intent: str
    key_word: List[str]
    max_count: int = 20
    user_id: Optional[int] = None  # 添加 user_id 字段

class SearchResultResponse(BaseModel):
    intent: str
    context_text: Dict[str, Any]

@router.put("/update-profile")
@router.post("/update-profile") # 增加对 POST 的兼容支持
async def update_profile(
        profile: ProfileUpdate,
        conn=Depends(get_db)
):
    try:
        with conn.cursor() as cursor:
            # 执行更新 (只更新 user 表，因为 admin 表没有这些扩展字段)
            sql = """
            UPDATE user
            SET name = %s,
                gender = %s,
                age = %s,
                university = %s,
                major = %s
            WHERE username = %s
            """
            affected_rows = cursor.execute(sql, (
                profile.name,
                profile.gender,
                profile.age,
                profile.university,
                profile.major,
                profile.username
            ))

            conn.commit()

            if affected_rows == 0:
                # 如果受影响行数为0，可能是该用户不存在，或者传入的是 admin
                raise HTTPException(
                    status_code=404,
                    detail=f"普通用户表中未找到 '{profile.username}' (管理员不支持修改扩展信息)"
                )

            return {
                "status": "success",
                "message": "Profile updated successfully",
                "username": profile.username
            }

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    finally:
        conn.close()

# 响应模型
class UserProfileResponse(BaseModel):
    name: Optional[str] = Field("", description="姓名，可能为空")
    gender: str = Field(..., description="性别")
    age: Optional[int] = Field(0, description="年龄，可能为空")
    university: Optional[str] = Field("", description="大学，可能为空")
    major: Optional[str] = Field("", description="专业，可能为空")


# 添加获取用户资料的路由
@router.get("/user-profile/{username}", response_model=UserProfileResponse)
async def get_user_profile(
        username: str = APIPath(...),
        isAdmin: bool = False,  # 接收前端传来的 isAdmin 参数
        conn=Depends(get_db)
):
    try:
        with conn.cursor() as cursor:
            if isAdmin:
                # 如果是管理员，查 admin 表。因为缺少个人信息字段，返回默认空值
                sql = """
                SELECT 
                    username,
                    '' AS name,
                    0 AS gender,
                    0 AS age,
                    '' AS university,
                    '' AS major
                FROM admin
                WHERE username = %s
                """
            else:
                # 如果是普通用户，查 user 表
                sql = """
                SELECT 
                    username,
                    COALESCE(name, '') AS name,
                    COALESCE(gender, 0) AS gender,
                    COALESCE(age, 0) AS age,
                    COALESCE(university, '') AS university,
                    COALESCE(major, '') AS major
                FROM user
                WHERE username = %s
                """

            cursor.execute(sql, (username,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Username '{username}' not found in database"
                )

            # 修复性别映射逻辑，需要与前端的 genderReverseMap 严格对应
            # 1: '男', 2: '女', 0: '未知'
            if 'gender' in result:
                if result['gender'] == 1:
                    result['gender'] = '男'
                elif result['gender'] == 2:
                    result['gender'] = '女'
                else:
                    result['gender'] = '未知'

            return result

    except pymysql.MySQLError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    finally:
        conn.close()

app.include_router(router, prefix="/api")


@app.on_event("startup")
def startup_event():
    if os.getenv("FACIAL_ANALYSIS_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        logger.info("Facial analysis service is disabled")
        return

    # 启动行为分析服务
    script_path = Path(__file__).resolve().parent.parent / "facial_landmarks" / "face_interviewing.py"

    if not script_path.exists():
        print(f"警告：未找到行为分析服务脚本: {script_path}")
        return

    # 启动子进程
    multiprocessing.Process(
        target=subprocess.run,
        args=([sys.executable, str(script_path)],),
        daemon=True
    ).start()
    print("行为分析服务已启动")


'''回答文本AI批注'''
@app.on_event("startup")
def start_qa_annotation_monitor():
    if os.getenv("QA_ANNOTATION_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        logger.info("QA annotation monitor is disabled")
        return
    import threading
    monitor_thread = threading.Thread(target=run_monitor, daemon=True)
    monitor_thread.start()
    print("QA 批注监视器已启动")
'''回答文本AI批注END'''


# Configuration - 只保留向量数据库目录
# SWCUP_backend_DIR = Path(__file__).resolve().parent.parent  # 指向 SWCUP-backend 目录
VECTOR_DB_DIR = os.getenv('VECTOR_DB_DIR', str(BASE_DIR / "vecDB" / "SW_vector_db"))
os.makedirs(VECTOR_DB_DIR, exist_ok=True)


def process_documents(file_contents: list[tuple[str, str]]):
    """
    直接处理文件内容并更新向量数据库
    file_contents: 元组列表，每个元组包含(文件名, 文件内容)
    """
    if not file_contents:
        raise ValueError("No file content provided")

    print(f"Processing {len(file_contents)} files")

    # 1. 将文件内容拆分为行
    chunks = []
    for file_name, content in file_contents:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped:
                chunks.append(
                    Document(
                        page_content=stripped,
                        metadata={
                            "line_number": i + 1,
                            "source": file_name
                        }
                    )
                )

    print(f"Split into {len(chunks)} chunks")

    # 2. 初始化嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name=os.getenv(
            'EMBEDDING_MODEL_PATH',
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        ),
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # 3. 创建并持久化向量数据库
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    vector_db.persist()

    return {
        "message": "Vector database updated successfully",
        "total_files": len(file_contents),
        "total_chunks": len(chunks),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@app.post("/api/upload/")
# async def upload_files(files: list[UploadFile] = File(...)):
#     """
#     上传文件并更新向量数据库
#     ◦ 只处理TXT文件
#
#     ◦ 直接处理文件内容而不保存到本地
#
#     """
#     file_contents = []
#     skipped_files = []
#     replaced_files = []
#
#     # 读取并处理上传的文件内容
#     for file in files:
#         filename_lower = file.filename.lower()
#
#         if filename_lower.endswith('.docx'):
#             try:
#                 # 读取本地文件内容
#                 with open(frontend_file, 'r', encoding='utf-8') as f:
#                     content = f.read()
#                 file_contents.append((frontend_file, content))
#                 replaced_files.append({
#                     "original": file.filename,
#                     "replaced_with": frontend_file
#                 })
#             except Exception as e:
#                 print(f"Error processing local file {frontend_file}: {str(e)}")
#                 skipped_files.append({
#                     "filename": file.filename,
#                     "reason": f"本地文件处理失败: {str(e)}"
#                 })
#             continue
#
#         if filename_lower.endswith('.pdf'):
#             try:
#                 # 读取本地文件内容
#                 with open(linux_file, 'r', encoding='utf-8') as f:
#                     content = f.read()
#                 file_contents.append((linux_file, content))
#                 replaced_files.append({
#                     "original": file.filename,
#                     "replaced_with": linux_file
#                 })
#             except Exception as e:
#                 print(f"Error processing local file {linux_file}: {str(e)}")
#                 skipped_files.append({
#                     "filename": file.filename,
#                     "reason": f"本地文件处理失败: {str(e)}"
#                 })
#             continue
#
#         # 处理.txt文件
#         if filename_lower.endswith('.txt'):
#             try:
#                 content = await file.read()
#                 decoded_content = content.decode('utf-8')
#                 file_contents.append((file.filename, decoded_content))
#             except Exception as e:
#                 print(f"Error processing {file.filename}: {str(e)}")
#                 skipped_files.append({
#                     "filename": file.filename,
#                     "reason": f"处理失败: {str(e)}"
#                 })
#             continue
#
#         content = await file.read()
#         try:
#             # 解码为UTF-8字符串
#             decoded_content = content.decode('utf-8')
#             file_contents.append((file.filename, decoded_content))
#         except Exception as e:
#             print(f"Error processing {file.filename}: {str(e)}")
#             skipped_files.append(file.filename)
#
#     if not file_contents:
#         return JSONResponse(
#             content={
#                 "message": "No valid TXT files uploaded",
#                 "skipped_files": skipped_files
#             },
#             status_code=400
#         )
#
#     # 处理文件内容并更新向量数据库
#     try:
#         result = process_documents(file_contents)
#         return JSONResponse(
#             content={
#                 "message": f"Processed {len(file_contents)} TXT files",
#                 "processed_files": [name for name, _ in file_contents],
#                 "skipped_files": skipped_files,
#                 "details": result
#             },
#             status_code=200
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to process files: {str(e)}"
#         )
#
# # 不支持的文件类型
#         skipped_files.append({
#             "filename": file.filename,
#             "reason": "不支持的文件类型"
#         })
#
#     # 处理文件内容
#     processed_files = []
#     if file_contents:
#         try:
#             processed_files = process_documents(file_contents)
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"处理文件失败: {str(e)}"
#             )
#
#     # 构建响应
#     response_content = {
#         "processed_files": [name for name, _ in file_contents],
#         "replaced_files": replaced_files,
#         "skipped_files": skipped_files,
#         "details": processed_files
#     }
#
#     return JSONResponse(
#         content={
#             "message": f"处理了 {len(file_contents)} 个文件",
#             "details": response_content
#         },
#         status_code=200
#     )


# def extract_text_from_file(file: UploadFile) -> str:
#     """从不同格式的文件中提取文本内容"""
#     content = ""
#     file_extension = file.filename.split(".")[-1].lower()
#
#     if file_extension == "txt":
#         content = file.file.read().decode("utf-8")
#     elif file_extension == "pdf":
#         pdf_reader = PyPDF2.PdfReader(file.file)
#         for page in pdf_reader.pages:
#             content += page.extract_text() + "\n"
#     elif file_extension in ["doc", "docx"]:
#         doc = docx.Document(file.file)
#         for para in doc.paragraphs:
#             content += para.text + "\n"
#     elif file_extension in ["json", "jsonl"]:
#         # 对于JSON文件，我们只提取文本内容
#         data = json.loads(file.file.read())
#         if isinstance(data, dict):
#             content = json.dumps(data)
#         elif isinstance(data, list):
#             content = "\n".join(json.dumps(item) for item in data)
#
#     return content


# def fixed_size_chunking(text: str, chunk_size: int) -> List[str]:
#     """固定大小分块"""
#     chunks = []
#     for i in range(0, len(text), chunk_size):
#         chunks.append(text[i:i + chunk_size])
#     return chunks


# def sliding_window_chunking(text: str, window_size: int, step_size: int) -> List[str]:
#     """滑动窗口分块"""
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = min(start + window_size, len(text))
#         chunks.append(text[start:end])
#         start += step_size
#     return chunks


# def semantic_chunking(text: str, max_chars: int = 1000) -> List[str]:
#     """简化的语义分块（基于段落和简单句子分割）"""
#     # 首先按段落分割
#     paragraphs = [p for p in text.split('\n') if p.strip()]
#
#     chunks = []
#     current_chunk = ""
#
#     for paragraph in paragraphs:
#         # 如果段落本身就很长，先按句子分割
#         if len(paragraph) > max_chars:
#             # 简单的句子分割：按句号、问号、感叹号分割
#             sentences = re.split(r'[。！？.!?]', paragraph)
#             sentences = [s.strip() for s in sentences if s.strip()]
#
#             for sentence in sentences:
#                 if len(current_chunk) + len(sentence) <= max_chars:
#                     current_chunk += sentence + "。"
#                 else:
#                     if current_chunk:
#                         chunks.append(current_chunk.strip())
#                     current_chunk = sentence + "。"
#         else:
#             # 如果当前块加上新段落不超过最大长度，则添加
#             if len(current_chunk) + len(paragraph) <= max_chars:
#                 current_chunk += paragraph + "\n"
#             else:
#                 # 如果当前块不为空，则添加到结果中
#                 if current_chunk:
#                     chunks.append(current_chunk.strip())
#                 current_chunk = paragraph + "\n"
#
#     # 添加最后一个块
#     if current_chunk:
#         chunks.append(current_chunk.strip())
#
#     # 如果没有任何分块（比如文本很短），则返回整个文本作为一个块
#     if not chunks:
#         chunks = [text]
#
#     return chunks

# @app.post("/upload/fixed/")
# async def upload_fixed_chunk(
#     files: List[UploadFile] = File(...),
#     chunk_size: int = Form(1000)
# ):
#     """固定大小分块接口"""
#     return await process_files(files, "fixed", chunk_size=chunk_size)
#
# @app.post("/upload/semantic/")
# async def upload_semantic_chunk(
#     files: List[UploadFile] = File(...),
#     chunk_size: int = Form(1000)
# ):
#     """语义分块接口"""
#     return await process_files(files, "semantic", chunk_size=chunk_size)
#
# @app.post("/upload/sliding/")
# async def upload_sliding_chunk(
#     files: List[UploadFile] = File(...),
#     window_size: int = Form(1000),
#     step_size: int = Form(500)
# ):
#     """滑动窗口分块接口"""
#     return await process_files(files, "sliding", window_size=window_size, step_size=step_size)
#
#
# async def process_files(
#         files: List[UploadFile],
#         method: str,
#         chunk_size: Optional[int] = None,
#         window_size: Optional[int] = None,
#         step_size: Optional[int] = None
# ):
#     """处理上传的文件并存入向量数据库"""
#     results = []
#
#     # 删除现有的集合（如果存在）
#     try:
#         chroma_client.delete_collection("documents")
#
#     except Exception as e:
#         print(f"删除集合时出错（可能不存在）: {str(e)}")
#
#     # 创建新集合并指定嵌入函数
#     collection = chroma_client.create_collection(
#         name="documents",
#         embedding_function=embedding_func
#     )
#
#     for file in files:
#         try:
#             # 提取文件文本内容
#             text = extract_text_from_file(file)
#
#             # 根据分块方法进行分块
#             if method == "fixed":
#                 chunks = fixed_size_chunking(text, chunk_size or 1000)
#             elif method == "semantic":
#                 chunks = semantic_chunking(text, chunk_size or 1000)
#             elif method == "sliding":
#                 chunks = sliding_window_chunking(
#                     text,
#                     window_size or 1000,
#                     step_size or 500
#                 )
#             else:
#                 return {"error": f"Invalid chunking method: {method}"}
#
#             # 过滤掉空块
#             chunks = [chunk for chunk in chunks if chunk.strip()]
#
#             # 为每个块生成唯一ID
#             chunk_ids = [str(uuid.uuid4()) for _ in chunks]
#
#             # 准备元数据
#             metadatas = [{
#                 "source": file.filename,
#                 "chunk_method": method,
#                 "chunk_index": i,
#                 "chunk_size": len(chunk)
#             } for i, chunk in enumerate(chunks)]
#
#             # 添加到向量数据库
#             collection.add(
#                 documents=chunks,
#                 metadatas=metadatas,
#                 ids=chunk_ids
#             )
#
#             results.append({
#                 "filename": file.filename,
#                 "status": "success",
#                 "chunks_created": len(chunks),
#                 "method": method
#             })
#
#         except Exception as e:
#             results.append({
#                 "filename": file.filename,
#                 "status": "error",
#                 "error": str(e)
#             })
#
#     return {
#         "message": f"文件处理完成，使用{method}分块方法",
#         "results": results
#     }
#
# # 接口1：全局检索（社区摘要）
# @app.post("/retrieve-communities")
# def retrieve_communities(req: CommunityRetrievalRequest):
#     try:
#         # 1. 生成查询嵌入向量
#         query_embedding = embedding_model.encode(req.user_query).tolist()
#
#         # 2. Chroma中检索相似社区
#         results = chroma_collection.query(
#             query_embeddings=[query_embedding],
#             n_results=req.top_k,
#             include=["documents", "metadatas", "distances"]
#         )
#
#         # 3. 整理结果（返回社区ID、摘要、相似度）
#         communities = []
#         for i in range(len(results["ids"][0])):
#             communities.append({
#                 "community_id": results["ids"][0][i],
#                 "summary": results["documents"][0][i],
#                 "similarity": round(1 - results["distances"][0][i], 3)  # 转换为0-1相似度
#             })
#         return {"status": "success", "data": communities}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"全局检索失败：{str(e)}")

# 接口2：局部检索（Neo4j多跳子图）
@app.post("/api/retrieve-subgraph")
def retrieve_subgraph(req: SubgraphRetrievalRequest):
    try:
        # 1. 校验输入（实体列表不能为空）
        if not req.entities:
            raise HTTPException(status_code=400, detail="实体列表不能为空，请先解析用户问题中的实体")
        entities_lower = [entity.lower() for entity in req.entities]
        
        # 2. 构造Cypher多跳查询
        cypher_query = f"""
            MATCH path = (start)-[rels*1..{req.hop_count}]-(end)
            WHERE ANY(node IN nodes(path) WHERE 
                toLower(node.name) IN $entities_lower OR 
                (node.title IS NOT NULL AND toLower(node.title) IN $entities_lower)
            )
            UNWIND rels AS rel
            WITH 
                startNode(rel) AS source_node,
                rel,
                endNode(rel) AS target_node
            WITH DISTINCT
                CASE 
                    WHEN 'Question' IN labels(source_node) THEN source_node.content
                    ELSE source_node.name
                END AS source_entity,
                type(rel) AS relation_type,
                CASE 
                    WHEN 'Question' IN labels(target_node) THEN target_node.content
                    ELSE target_node.name
                END AS target_entity,
                labels(target_node) AS target_entity_labels,
                labels(source_node) AS source_entity_labels
            RETURN 
                source_entity,
                relation_type,
                target_entity,
                target_entity_labels,
                source_entity_labels
            LIMIT 50
            """

        # 3. 添加用户过滤条件
        if req.user_id is not None:
            cypher_query = cypher_query.replace(
                "MATCH path = (start)-[rels*1..{req.hop_count}]-(end)",
                f"MATCH path = (start)-[rels*1..{req.hop_count}]-(end) "
                f"WHERE ALL(n IN nodes(path) WHERE n.user_id = {req.user_id} OR n.user_id = 0)"
            )

        # 4. 执行Neo4j查询
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run(
                cypher_query,
                entities_lower=entities_lower
            )
            # 5. 整理子图结果
            subgraph = [record.data() for record in result]

        # 6. 关闭Neo4j驱动
        driver.close()

        return {"status": "success", "data": subgraph}

    except HTTPException as e:
        raise e  # 抛出已定义的HTTP异常
    except Exception as e:
        raise HTTPException(status_code=504, detail=f"局部检索失败：{str(e)}")
    
# @app.post("/search-questions")
# def search_questions_in_community(req: SearchQuestionsRequest):
#     """
#     根据用户意图进行社区检测，并在最匹配的社区中搜索相关问题
#
#     Args:
#         req: SearchQuestionsRequest 包含intent、key_word、max_count和user_id
#
#     Returns:
#         dict: 包含合并后的context_text
#     """
#     try:
#         # 1. 社区检测（向量匹配）
#         query_embedding = embedding_model.encode(req.intent).tolist()
#
#         # 在Chroma中检索最匹配的社区
#         results = chroma_collection.query(
#             query_embeddings=[query_embedding],
#             n_results=1,  # 只需要最匹配的1个社区
#             include=["documents", "metadatas", "distances"]
#         )
#
#         if not results["ids"][0]:
#             raise HTTPException(status_code=404, detail="未找到匹配的社区")
#
#         # 获取最匹配的社区信息
#         best_match_community = {
#             "community_id": results["ids"][0][0],
#             "summary": results["documents"][0][0],
#             "metadata": results["metadatas"][0][0]
#         }
#
#         # 2. 在该社区中查找Question类型的节点并进行关键词匹配
#         driver = get_neo4j_driver()
#
#         # 构建关键词匹配条件
#         keyword_conditions = []
#         for i, keyword in enumerate(req.key_word):
#             keyword_conditions.append(f"(toLower(q.content) CONTAINS toLower(${f'keyword_{i}'}) OR toLower(q.title) CONTAINS toLower(${f'keyword_{i}'}))")
#
#         # 构建用户过滤条件
#         user_filter = ""
#         params = {"limit": req.max_count}
#         if req.user_id is not None:
#             user_filter = "AND (q.user_id = $user_id OR q.user_id = 0)"
#             params["user_id"] = req.user_id
#
#         cypher_query = f"""
#             MATCH (q:Question)
#             WHERE ({' OR '.join(keyword_conditions)})
#             {user_filter}
#             RETURN q.type AS type, q.title AS title, q.content AS content, q.choice AS choice, q.answer AS answer
#             LIMIT $limit
#         """
#
#         # 准备查询参数
#         for i, keyword in enumerate(req.key_word):
#             params[f"keyword_{i}"] = keyword
#
#         with driver.session() as session:
#             result = session.run(cypher_query, **params)
#             questions = [record.data() for record in result]
#
#         driver.close()
#
#         # 3. 合并社区摘要和问题为context_text
#         # 首先添加社区摘要
#         context_text = f"社区摘要: {best_match_community['summary']}\n\n"
#
#         # 然后添加问题信息
#         if questions:
#             context_text += "相关问题:\n"
#             for i, question in enumerate(questions, 1):
#                 context_text += f"{i}. 问题类型: {question.get('type', 'N/A')}\n"
#                 context_text += f"   标题: {question.get('title', 'N/A')}\n"
#                 context_text += f"   内容: {question.get('content', 'N/A')}\n"
#                 if question.get('choice'):
#                     context_text += f"   选项: {question['choice']}\n"
#                 context_text += f"   答案: {question.get('answer', 'N/A')}\n\n"
#         else:
#             context_text += "未找到相关问题。\n"
#
#         # 4. 返回结果
#         return {
#             "context_text": context_text
#         }
#
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"搜索问题失败：{str(e)}")



@app.get("/api/qa/speech-metrics/{history_id}")
async def get_speech_metrics(history_id: int):
    """
    根据面试历史ID，获取该次面试中所有回答（role=1）的语音指标：
    语速(speech_rate)、清晰度(clarity)、自信度(confidence)
    """
    try:
        sql = """
        SELECT qa_id, speech_rate, clarity, confidence
        FROM qa
        WHERE history_id = %s AND role = 1
        """
        rows = execute_query(sql, (history_id,))
        # 保证返回数值或 null，供前端判断
        return {"data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取语音指标失败: {str(e)}")

@app.get("/api/history/{history_id}/image-evaluation")
async def get_image_evaluation(history_id: int):
    """
    获取并（如果需要）生成该次面试的表情神态评价和肢体动作评价。
    若数据库已有评价则直接返回；否则调用 GLM-4V 进行分析并持久化。
    """
    # 1. 尝试从数据库读取现有评价
    sql_select = """
        SELECT expression_evaluation, gesture_evaluation
        FROM interview_history
        WHERE history_id = %s
    """
    rows = execute_query(sql_select, (history_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    expr = rows[0].get("expression_evaluation", "")
    gest = rows[0].get("gesture_evaluation", "")

    if expr or gest:  # 已有评价，直接返回
        return {
            "history_id": history_id,
            "expression_evaluation": expr or "",
            "gesture_evaluation": gest or "",
        }

    # 2. 无评价时，调用分析函数（图片目录已在环境/配置中定义，这里复用 IMAGE_SAVE_DIR）
    img_dir = str(IMAGE_SAVE_DIR)  # IMAGE_SAVE_DIR 已在 main.py 中定义为 BASE_DIR / 'facial_landmarks' / 'img'
    expr_new, gest_new = analyze_expression_and_gesture(history_id, img_dir)

    # 3. 持久化到数据库
    if expr_new or gest_new:
        sql_update = """
            UPDATE interview_history
            SET expression_evaluation = %s, gesture_evaluation = %s
            WHERE history_id = %s
        """
        execute_query(sql_update, (expr_new, gest_new, history_id))
        delete_cache_sync(build_cache_key("ask", "history", history_id, "detail"))
    else:
        logger.warning(f"Failed to generate evaluation for history_id={history_id}")

    return {
        "history_id": history_id,
        "expression_evaluation": expr_new or "",
        "gesture_evaluation": gest_new or "",
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', '8000')),
        reload=os.getenv('RELOAD', 'false').lower() in {'1', 'true', 'yes'},
    )
