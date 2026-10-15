import datetime
import bcrypt
import os
from fastapi import HTTPException
from LogDatabase import get_db, UserRepository
from uuid import uuid4


class AdminService:
    @staticmethod
    def register_admin(admin_data: dict):
        db = next(get_db())
        cursor = None
        try:
            # 检查连接是否有效
            if not db.open:
                db.ping(reconnect=True)

            cursor = db.cursor()  # 修改为使用字典游标
            # 检查用户名是否存在
            cursor.execute("SELECT id FROM admin WHERE username = %s", (admin_data["username"],))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="用户名已存在")

            # 密码加密
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(admin_data["password"].encode('utf-8'), salt)
            hashed_password_str = hashed_password.decode('utf-8')

            # 如果有 face_bytes，保存为唯一文件名到 uploads/facephoto
            face_filename = None
            face_bytes = admin_data.get("face_bytes")
            face_original_filename = admin_data.get("face_original_filename")
            
            if face_bytes is not None and face_original_filename:
                _, ext = os.path.splitext(face_original_filename)
                # 保持扩展名（若无则默认 .jpg）
                if not ext:
                    ext = '.jpg'
                unique_name = f"{uuid4().hex}{ext}"
                uploads_dir = os.path.join(os.getcwd(), 'uploads', 'admin_facephoto')
                try:
                    os.makedirs(uploads_dir, exist_ok=True)
                    file_path = os.path.join(uploads_dir, unique_name)
                    with open(file_path, 'wb') as f:
                        f.write(face_bytes)
                    face_filename = unique_name
                except Exception as e:
                    # 保存失败，不阻塞注册，但记录异常并继续（也可改为抛出）
                    print(f"保存管理员人脸图片失败: {e}")

            # 插入数据库
            sql = """
                INSERT INTO admin (username, password, email, create_time, status, face_filename) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            create_time = datetime.datetime.now()
            cursor.execute(sql, (
                admin_data["username"],
                hashed_password_str,
                admin_data["email"],
                create_time,
                1,  # 默认状态为1表示正常
                face_filename  # 人脸图片文件名
            ))
            db.commit()

            # 获取刚插入的管理员ID
            admin_id = cursor.lastrowid

            # 查询刚创建的管理员详细信息
            cursor.execute("SELECT * FROM admin WHERE id = %s", (admin_id,))
            new_admin = cursor.fetchone()

            # 格式化返回数据
            result = {
                "id": new_admin["id"],
                "username": new_admin["username"],
                "email": new_admin["email"],
                "createTime": new_admin["create_time"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(new_admin["create_time"], datetime.datetime) else new_admin["create_time"],
                "status": new_admin["status"]
            }

            # 如果保存了 face 文件，则尝试提取 embedding 并入库（自动 enroll）
            try:
                if face_filename:
                    # 延迟导入以避免在没有 dlib 环境下导入失败导致注册失败
                    try:
                        from app.face_recognition.face_utils import get_embedding_from_bytes
                        from app.face_recognition.vector_db import add_embedding, delete_user_embeddings
                        # 读取文件字节
                        uploads_path = os.path.join(os.getcwd(), 'uploads', 'admin_facephoto', face_filename)
                        if os.path.isfile(uploads_path):
                            with open(uploads_path, 'rb') as f:
                                fb = f.read()
                            emb = get_embedding_from_bytes(fb)
                            if emb is not None:
                                try:
                                    # 先删除该管理员的所有旧向量数据（如果有的话）
                                    delete_user_embeddings(f"admin_{new_admin['id']}")
                                    # 为管理员添加特殊前缀以区分
                                    add_embedding(f"admin_{new_admin['id']}", face_filename, emb)
                                except Exception as e:
                                    print(f"添加管理员 embedding 到向量库失败: {e}")
                            else:
                                print("无法从管理员注册图片中提取 embedding")
                        else:
                            print(f"注册时未找到保存的管理员人脸文件: {uploads_path}")
                    except Exception as e:
                        # 如果 face_recognition 不可用（dlib 未安装等），记录并继续
                        print(f"管理员自动 enroll 失败（可能缺少 dlib/依赖）: {e}")
            except Exception:
                # 自动 enroll 不应阻塞注册流程
                pass

            return result

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            # 这里不关闭数据库连接，因为连接可能来自连接池

    @staticmethod
    def authenticate_admin(username: str, password: str):
        db = next(get_db())
        cursor = None
        try:
            # 检查连接是否有效
            if not db.open:
                db.ping(reconnect=True)

            cursor = db.cursor()  # 使用字典游标
            cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
            admin = cursor.fetchone()

            if not admin:
                raise HTTPException(status_code=401, detail="用户名或密码错误")

            # 验证密码
            if not bcrypt.checkpw(password.encode('utf-8'), admin["password"].encode('utf-8')):
                raise HTTPException(status_code=401, detail="用户名或密码错误")

            return admin

        except HTTPException as he:
            # 已知的 HTTP 异常（例如 401）应原样抛出，以便保持正确的状态码
            raise he
        except Exception as e:
            # 未知异常统一返回 500
            raise HTTPException(status_code=500, detail=f"认证失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            # 这里不关闭数据库连接，因为连接可能来自连接池

    @staticmethod
    def create_user(user_data: dict):
        db = next(get_db())
        cursor = None
        try:
            if not db.open:
                db.ping(reconnect=True)

            cursor = db.cursor()
            username = user_data["username"].strip()
            password = user_data["password"]
            email = user_data.get("email")
            email = email.strip() if isinstance(email, str) and email.strip() else None

            if not username:
                raise HTTPException(status_code=400, detail="用户名不能为空")

            if len(password) < 6:
                raise HTTPException(status_code=400, detail="密码长度至少为6位")

            if UserRepository.get_user_by_username(db, username):
                raise HTTPException(status_code=400, detail="用户名已存在")

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_id = UserRepository.create_user(db, username, hashed_password, email)

            cursor.execute(
                """
                SELECT
                    user_id,
                    username,
                    COALESCE(name, '') AS name,
                    COALESCE(email, '') AS email,
                    COALESCE(university, '') AS university,
                    COALESCE(major, '') AS major,
                    created_at
                FROM user
                WHERE user_id = %s
                """,
                (user_id,)
            )
            new_user = cursor.fetchone()

            try:
                from app.database.neo4j import graph
                if graph is not None:
                    from py2neo import Node
                    tx = graph.begin()
                    tx.merge(Node("User", id=user_id), "User", "id")
                    tx.commit()
            except Exception:
                pass

            return {
                "user_id": new_user["user_id"],
                "username": new_user["username"],
                "name": new_user["name"],
                "email": new_user["email"],
                "university": new_user["university"],
                "major": new_user["major"],
                "created_at": new_user["created_at"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(new_user["created_at"], datetime.datetime) else new_user["created_at"],
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"新增用户失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def list_users(username: str = None, page: int = 1, page_size: int = 20):
        db = next(get_db())
        cursor = None
        try:
            if not db.open:
                db.ping(reconnect=True)

            cursor = db.cursor()
            
            # 先查询总数
            count_sql = "SELECT COUNT(*) AS total FROM user"
            count_params = []
            if username:
                count_sql += " WHERE username LIKE %s"
                count_params.append(f"%{username}%")
            
            cursor.execute(count_sql, tuple(count_params))
            count_result = cursor.fetchone()
            total = count_result["total"] if count_result else 0
            
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 查询分页数据
            sql = """
                SELECT
                    user_id,
                    username,
                    COALESCE(name, '') AS name,
                    COALESCE(email, '') AS email,
                    COALESCE(gender, 0) AS gender,
                    COALESCE(age, 0) AS age,
                    COALESCE(university, '') AS university,
                    COALESCE(major, '') AS major,
                    created_at,
                    updated_at
                FROM user
            """
            params = []

            if username:
                sql += " WHERE username LIKE %s"
                params.append(f"%{username}%")

            sql += " ORDER BY user_id DESC LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            cursor.execute(sql, tuple(params))
            users = cursor.fetchall()

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [
                    {
                        "user_id": user["user_id"],
                        "username": user["username"],
                        "name": user["name"],
                        "email": user["email"],
                        "gender": user["gender"],
                        "age": user["age"],
                        "university": user["university"],
                        "major": user["major"],
                        "created_at": user["created_at"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(user["created_at"], datetime.datetime) else user["created_at"],
                        "updated_at": user["updated_at"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(user["updated_at"], datetime.datetime) else user["updated_at"],
                    }
                    for user in users
                ]
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询用户失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def get_dashboard_stats():
        """
        获取大屏展示所需的统计数据，通过一次联合查询减少数据库请求开销
        """
        db = next(get_db())
        cursor = None
        try:
            if not db.open:
                db.ping(reconnect=True)

            cursor = db.cursor()

            # 使用 UNION ALL 将多个统计查询合并为一次请求
            sql = """
                SELECT 'total_users' AS stat_type, COUNT(*) AS value FROM user
                UNION ALL
                SELECT 'total_interviews' AS stat_type, COUNT(*) AS value FROM interview_history
                UNION ALL
                SELECT 'total_qa' AS stat_type, COUNT(*) AS value FROM qa
                UNION ALL
                SELECT 'avg_professional_knowledge' AS stat_type,
                    COALESCE(AVG(professional_knowledge), 0) AS value
                FROM interview_history
                WHERE professional_knowledge IS NOT NULL
                UNION ALL
                SELECT 'avg_language_expression' AS stat_type,
                    COALESCE(AVG(language_expression), 0) AS value
                FROM interview_history
                WHERE language_expression IS NOT NULL
                UNION ALL
                SELECT 'today_users' AS stat_type, COUNT(*) AS value
                FROM user
                WHERE DATE(created_at) = CURDATE()
                UNION ALL
                SELECT 'today_interviews' AS stat_type, COUNT(*) AS value
                FROM interview_history
                WHERE DATE(interview_time) = CURDATE()
            """

            cursor.execute(sql)
            results = cursor.fetchall()

            # 将结果转换为字典
            stats = {}
            for row in results:
                stats[row["stat_type"]] = float(row["value"]) if isinstance(row["value"], (float, int)) else row["value"]

            return {
                "total_users": int(stats.get("total_users", 0)),
                "total_interviews": int(stats.get("total_interviews", 0)),
                "total_qa": int(stats.get("total_qa", 0)),
                "avg_professional_knowledge": round(stats.get("avg_professional_knowledge", 0), 2),
                "avg_language_expression": round(stats.get("avg_language_expression", 0), 2),
                "today_users": int(stats.get("today_users", 0)),
                "today_interviews": int(stats.get("today_interviews", 0)),
                "update_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def get_all_interviews_for_dashboard():
        """
        获取大屏展示所需的所有面试数据（一次性查询，避免逐个用户请求）

        返回格式：
        {
            "users": [{"id": "1", "username": "...", "university": "..."}],
            "interviews": [
                {
                    "id": "1",
                    "user_id": "1",
                    "username": "...",
                    "field": "...",
                    "position": "...",
                    "score": 85,
                    "interview_time": "2024-01-01",
                    "professional_knowledge": 4,
                    "skill_match": 4,
                    "language_expression": 3,
                    "logical_thinking": 4,
                    "innovation_ability": 3,
                    "stress_resistance": 4
                },
                ...
            ]
        }
        """
        db = next(get_db())
        cursor = None
        try:
            if not db.open:
                db.ping(reconnect=True)

            cursor = db.cursor()

            # 一次性查询所有面试数据，关联用户信息
            sql = """
                SELECT
                    ih.history_id AS id,
                    ih.user_id,
                    u.username,
                    COALESCE(u.university, '') AS university,
                    ih.field,
                    ih.position,
                    COALESCE(ih.score, 0) AS score,
                    ih.interview_time,
                    COALESCE(ih.professional_knowledge, 0) AS professional_knowledge,
                    COALESCE(ih.skill_match, 0) AS skill_match,
                    COALESCE(ih.language_expression, 0) AS language_expression,
                    COALESCE(ih.logical_thinking, 0) AS logical_thinking,
                    COALESCE(ih.innovation_ability, 0) AS innovation_ability,
                    COALESCE(ih.stress_resistance, 0) AS stress_resistance
                FROM interview_history ih
                LEFT JOIN user u ON ih.user_id = u.user_id
                ORDER BY ih.interview_time DESC
            """

            cursor.execute(sql)
            interviews = cursor.fetchall()

            # 获取所有唯一用户（用于前端下拉选择）
            users_query = """
                SELECT
                    user_id AS id,
                    username,
                    username AS name,
                    COALESCE(university, '') AS university
                FROM user
                ORDER BY user_id DESC
            """
            cursor.execute(users_query)
            users = cursor.fetchall()

            return {
                "users": [
                    {
                        "id": str(u["id"]),
                        "name": u["name"],
                        "username": u["username"],
                        "school": u["university"],
                        "province": ""  # 需要前端从学校信息推断
                    }
                    for u in users
                ],
                "interviews": [
                    {
                        "id": str(i["id"]),
                        "user_id": str(i["user_id"]),
                        "username": i["username"],
                        "domain": i["field"],
                        "position": i["position"],
                        "date": i["interview_time"].strftime('%Y-%m-%d') if i["interview_time"] else '',
                        "interview_time": i["interview_time"],
                        "interviewTimestamp": i["interview_time"].timestamp() if i["interview_time"] else 0,
                        "totalScore": int(i["score"]),
                        "dimensionScores": [
                            {"name": "专业知识", "score": int(i["professional_knowledge"] * 20)},
                            {"name": "技能匹配", "score": int(i["skill_match"] * 20)},
                            {"name": "语言表达", "score": int(i["language_expression"] * 20)},
                            {"name": "逻辑思维", "score": int(i["logical_thinking"] * 20)},
                            {"name": "创新能力", "score": int(i["innovation_ability"] * 20)},
                            {"name": "抗压能力", "score": int(i["stress_resistance"] * 20)},
                        ]
                    }
                    for i in interviews
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取面试数据失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def get_user_by_username(username: str):
        db = next(get_db())
        cursor = None
        try:
            if not db.open:
                db.ping(reconnect=True)

            normalized_username = username.strip()
            if not normalized_username:
                raise HTTPException(status_code=400, detail="用户名不能为空")

            cursor = db.cursor()
            cursor.execute(
                """
                SELECT
                    user_id,
                    username,
                    COALESCE(name, '') AS name,
                    COALESCE(email, '') AS email,
                    COALESCE(gender, 0) AS gender,
                    COALESCE(age, 0) AS age,
                    COALESCE(university, '') AS university,
                    COALESCE(major, '') AS major,
                    created_at,
                    updated_at
                FROM user
                WHERE username = %s
                LIMIT 1
                """,
                (normalized_username,)
            )
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")

            return {
                "user_id": user["user_id"],
                "username": user["username"],
                "name": user["name"],
                "email": user["email"],
                "gender": user["gender"],
                "age": user["age"],
                "university": user["university"],
                "major": user["major"],
                "created_at": user["created_at"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(user["created_at"], datetime.datetime) else user["created_at"],
                "updated_at": user["updated_at"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(user["updated_at"], datetime.datetime) else user["updated_at"],
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"根据用户名查询用户失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def delete_user(user_id: int):
        db = next(get_db())
        cursor = None
        try:
            if not db.open:
                db.ping(reconnect=True)

            cursor = db.cursor()
            cursor.execute("SELECT user_id, username FROM user WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")

            cursor.execute("DELETE FROM user WHERE user_id = %s", (user_id,))
            db.commit()

            return {
                "user_id": user["user_id"],
                "username": user["username"]
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()
