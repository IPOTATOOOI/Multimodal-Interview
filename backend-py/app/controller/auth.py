from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from LogDatabase import get_db_connection, UserRepository
import bcrypt
import pymysql
from py2neo import Node
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def _require_secret_key() -> None:
    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SECRET_KEY is not configured",
        )


class AuthService:
    @staticmethod
    def register_user(username: str = None, password: str = None, email: str = None, face_original_filename: str = None, face_bytes: bytes = None):
        # 接受 username, password, email, 可选的 face 文件名和字节
        with get_db_connection() as conn:
            if UserRepository.get_user_by_username(conn, username):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="用户名已经注册"
                )
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            # 如果有 face_bytes，保存为唯一文件名到 uploads/facephoto
            face_filename = None
            if face_bytes is not None and face_original_filename:
                import os
                from uuid import uuid4
                _, ext = os.path.splitext(face_original_filename)
                # 保持扩展名（若无则默认 .jpg）
                if not ext:
                    ext = '.jpg'
                unique_name = f"{uuid4().hex}{ext}"
                uploads_dir = os.path.join(os.getcwd(), 'uploads', 'facephoto')
                try:
                    os.makedirs(uploads_dir, exist_ok=True)
                    file_path = os.path.join(uploads_dir, unique_name)
                    with open(file_path, 'wb') as f:
                        f.write(face_bytes)
                    face_filename = unique_name
                except Exception as e:
                    # 保存失败，不阻塞注册，但记录异常并继续（也可改为抛出）
                    print(f"保存人脸图片失败: {e}")
            try:
                new_user_id = UserRepository.create_user(conn, username, hashed_password, email, face_filename)
                # 在 Neo4j 中创建用户节点（以 user_id 为唯一标识）
                try:
                    from app.database.neo4j import graph
                    if graph is not None:
                        tx = graph.begin()
                        node = Node("User", id=new_user_id)
                        tx.merge(node, "User", "id")
                        tx.commit()
                except Exception:
                    # 创建图节点失败不影响注册流程
                    pass

                # 如果保存了 face 文件，则尝试提取 embedding 并入库（自动 enroll）
                try:
                    if face_filename:
                        # 延迟导入以避免在没有 dlib 环境下导入失败导致注册失败
                        try:
                            from app.face_recognition.face_utils import get_embedding_from_bytes
                            from app.face_recognition.vector_db import add_embedding
                            # 读取文件字节
                            import os
                            uploads_path = os.path.join(os.getcwd(), 'uploads', 'facephoto', face_filename)
                            if os.path.isfile(uploads_path):
                                with open(uploads_path, 'rb') as f:
                                    fb = f.read()
                                emb = get_embedding_from_bytes(fb)
                                if emb is not None:
                                    try:
                                        add_embedding(new_user_id, face_filename, emb)
                                    except Exception as e:
                                        print(f"添加 embedding 到向量库失败: {e}")
                                else:
                                    print("无法从注册图片中提取 embedding")
                            else:
                                print(f"注册时未找到保存的人脸文件: {uploads_path}")
                        except Exception as e:
                            # 如果 face_recognition 不可用（dlib 未安装等），记录并继续
                            print(f"自动 enroll 失败（可能缺少 dlib/依赖）: {e}")
                except Exception:
                    # 自动 enroll 不应阻塞注册流程
                    pass
                return new_user_id
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"数据库错误: {e}"
                )

    @staticmethod 
    def authenticate_user(login_data):
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)  # 使用 DictCursor
                sql = "SELECT user_id, username, password FROM user WHERE username = %s"
                cursor.execute(sql, (login_data.username,))
                user = cursor.fetchone()
                
                if not user or not bcrypt.checkpw(
                    login_data.password.encode('utf-8'),
                    user['password'].encode('utf-8')
                ):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="用户名或密码错误"
                    )
                # 确认图数据库中存在该用户的 User 节点
                try:
                    from app.database.neo4j import graph
                    if graph is not None and user.get('user_id') is not None:
                        uid = user.get('user_id')
                        try:
                            uid = int(uid)
                        except Exception:
                            pass
                        tx = graph.begin()
                        from py2neo import Node
                        tx.merge(Node("User", id=uid), "User", "id")
                        tx.commit()
                except Exception:
                    # Neo4j 不可用或写入失败不影响登录
                    pass
                return user  # 返回包含 user_id 的完整用户信息
                
            finally:
                cursor.close()


def create_access_token(data: dict, expires_delta: timedelta = None):
    _require_secret_key()
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    _require_secret_key()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    with get_db_connection() as conn:
        user = UserRepository.get_user_by_username(conn, username)
        if not user:
            raise credentials_exception
        return user


async def get_current_admin(token: str = Depends(oauth2_scheme)):
    _require_secret_key()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证管理员凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if not username or not is_admin:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, status, create_time FROM admin WHERE username = %s",
                (username,)
            )
            admin = cursor.fetchone()

        if not admin:
            raise credentials_exception

        return admin
