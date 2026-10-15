import logging
from typing import Dict, Any
import json
from app.database.mysql import execute_insert, execute_query, execute_update

# 配置日志记录器
logger = logging.getLogger(__name__)

class ResumeDatabaseService:
    @staticmethod
    def _ensure_string_list(items, field_name: str) -> list:
        """确保列表项都是字符串类型"""
        if items is None:
            return []

        if not isinstance(items, list):
            logger.warning(f"{field_name}不是列表类型: {items}")
            return [str(items)]
        
        result = []
        for item in items:
            if item is None:
                continue
            if isinstance(item, dict):
                logger.warning(f"{field_name}中包含字典项: {item}")
                # 尝试从字典中提取有意义的字符串表示
                item = str(item.get('name', '')) or str(item)
            result.append(str(item))
        return result

    @staticmethod
    def _ensure_string(value, field_name: str):
        """将模型返回的标量字段规范化为数据库可绑定的字符串"""
        if value is None:
            return None
        if isinstance(value, list):
            logger.warning(f"{field_name}是列表类型，已合并为字符串: {value}")
            return ",".join(str(item) for item in value if item is not None)
        if isinstance(value, dict):
            logger.warning(f"{field_name}是字典类型，已转换为字符串: {value}")
            return str(value.get("name", "")) or json.dumps(value, ensure_ascii=False)
        return str(value)

    @staticmethod
    def save_structured_data(data: dict, user_id: str, domain: str, position: str):
        """
        将结构化数据存储到MySQL数据库中
        :param data: 包含简历信息的字典
        :param user_id: 用户ID
        :param domain: 技术领域
        :param position: 岗位
        """
        logger.info(f"接收到的原始数据: {data}")
        
        if not data or "姓名" not in data:
            logger.error(f"数据验证失败: {data}")
            raise ValueError("数据无效或缺少必要字段")

        try:
            # 预处理数据
            school = ResumeDatabaseService._ensure_string(data.get("学校"), "学校")
            skills = ResumeDatabaseService._ensure_string_list(data.get("技能列表", []), "技能列表")
            projects = ResumeDatabaseService._ensure_string_list(data.get("项目经历", []), "项目经历")
            internships = ResumeDatabaseService._ensure_string_list(data.get("实习经历", []), "实习经历")
            
            logger.info(f"处理后的学校: {school}")
            logger.info(f"处理后的技能列表: {skills}")
            logger.info(f"处理后的项目经历: {projects}")
            logger.info(f"处理后的实习经历: {internships}")

            # 插入数据
            insert_query = """
            INSERT INTO resume (user_id, name, age, school, major, graduation_year, skills, project_experiences, internship_experiences)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                user_id,
                ResumeDatabaseService._ensure_string(data.get("姓名"), "姓名"),
                ResumeDatabaseService._ensure_string(data.get("年龄"), "年龄"),
                school,
                ResumeDatabaseService._ensure_string(data.get("专业"), "专业"),
                ResumeDatabaseService._ensure_string(data.get("毕业年份"), "毕业年份"),
                ",".join(skills),
                "\n".join(projects),
                "\n".join(internships)
            )
            
            logger.info(f"准备执行SQL插入，values: {values}")
            resume_id = execute_insert(insert_query, values)
            return {"success": "数据已成功存储到数据库", "resume_id": resume_id}
            
        except Exception as e:
            error_msg = f"数据库操作失败: {str(e)}"
            logger.error(f"{error_msg}, 原始数据: {data}")
            return {"error": error_msg}

    @staticmethod
    def get_resume_by_user_id(user_id: str):
        """
        根据用户ID获取简历信息
        :param user_id: 用户ID
        :return: 简历信息字典
        """
        try:
            query = """
            SELECT * FROM resume 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
            """
            
            result = execute_query(query, (user_id,))
            
            if result:
                return result[0]
            else:
                return None
                
        except Exception as e:
            print(f"获取简历信息失败: {e}")
            return None

    @staticmethod
    def update_resume_data(resume_id: int, data: dict):
        """
        更新简历信息
        :param resume_id: 简历ID
        :param data: 更新的数据字典
        :return: 更新结果
        """
        try:
            skills = ResumeDatabaseService._ensure_string_list(data.get("技能列表", []), "技能列表")
            projects = ResumeDatabaseService._ensure_string_list(data.get("项目经历", []), "项目经历")
            internships = ResumeDatabaseService._ensure_string_list(data.get("实习经历", []), "实习经历")

            update_query = """
            UPDATE resume 
            SET name = %s, age = %s, school = %s, major = %s, graduation_year = %s, 
                skills = %s, project_experiences = %s, internship_experiences = %s
            WHERE resume_id = %s
            """
            
            values = (
                ResumeDatabaseService._ensure_string(data.get("姓名"), "姓名"),
                ResumeDatabaseService._ensure_string(data.get("年龄"), "年龄"),
                ResumeDatabaseService._ensure_string(data.get("学校"), "学校"),
                ResumeDatabaseService._ensure_string(data.get("专业"), "专业"),
                ResumeDatabaseService._ensure_string(data.get("毕业年份"), "毕业年份"),
                ",".join(skills),
                "\n".join(projects),
                "\n".join(internships),
                resume_id
            )
            
            affected_rows = execute_update(update_query, values)
            
            if affected_rows > 0:
                return {"success": "简历信息更新成功"}
            else:
                return {"error": "未找到对应的简历记录"}
                
        except Exception as e:
            return {"error": f"更新简历信息失败: {str(e)}"}
