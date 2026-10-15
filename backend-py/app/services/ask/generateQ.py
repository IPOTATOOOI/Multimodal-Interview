import json
from loguru import logger
from app.services.AI.spark_API import call_spark_api
from app.database.neo4j import graph

def get_all_tags_from_neo4j() -> list:
    """
    从Neo4j图数据库中查询"软件开发"->"专项练习"下所有Topic下的Tag节点
    """
    try:
        if graph is None:
            logger.error("Neo4j数据库未连接")
            return []
        # Cypher查询：先定位根分类和专项练习二级分类，再查所有Topic下的Tag
        query = (
            "MATCH (r:RootCategory {name: '软件开发'})-[:HAS_SUB]->(s:SubCategory {name: '专项练习'})-[:CONTAINS_TOPIC]->(t:Topic) "
            "MATCH (t)-[:INCLUDES]->(q:Question)-[:MARKED_AS]->(tag:Tag) "
            "RETURN DISTINCT tag.id AS id, tag.name AS name ORDER BY rand()"
        )
        result = graph.run(query).data()
        tags = [{"id": row["id"], "name": row["name"]} for row in result]
        logger.info(f"从Neo4j查询到{len(tags)}个Tag节点（软件开发-专项练习）")
        return tags
    except Exception as e:
        logger.error(f"查询Neo4j Tag节点失败: {str(e)}")
        return []

def select_tags_for_written_test(career_domain: str, job_role: str, all_tags: list) -> list:
    """
    使用大模型从所有Tag中筛选出适合笔试测试的30个Tag
    """
    try:
        # 只取前50个Tag，避免prompt过长
        limited_tags = all_tags[:50]
        tags_str = "\n".join([f"- {tag['name']} (ID: {tag['id']})" for tag in limited_tags])
        
        prompt = f"""
你是笔试出题专家。从以下Tag中选择30个最适合{career_domain}领域{job_role}岗位的Tag：

{tags_str}

只返回JSON数组：["tag-id-1", "tag-id-2", ..., "tag-id-30"]
不要任何解释，只要JSON。
"""
        
        result = call_spark_api(prompt)
        logger.info(f"大模型返回的Tag筛选结果: {result}")
        
        # 检查返回结果是否为空
        if not result or result.strip() == "":
            logger.warning("大模型返回空结果，使用默认Tag")
            # 使用一些通用的重要Tag作为默认值
            default_tags = [
                "tag-algorithm-complexity", "tag-data-structure", "tag-sort-algorithm",
                "tag-search-algorithm", "tag-class", "tag-inheritance", "tag-thread",
                "tag-concurrency", "tag-tree-structure", "tag-graph-structure",
                "tag-func-lib", "tag-exception", "tag-test-case", "tag-oop", "tag-memory"
            ]
            return default_tags[:30]
        
        # 清理JSON字符串
        cleaned_result = result.strip()
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.startswith("```"):
            cleaned_result = cleaned_result[3:]
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]
        cleaned_result = cleaned_result.strip()
        
        try:
            selected_tag_ids = json.loads(cleaned_result)
            logger.info(f"筛选出的Tag ID列表: {selected_tag_ids}")
            return selected_tag_ids
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON解析失败: {str(json_error)}, 原始内容: {cleaned_result}")
            # 使用默认Tag
            default_tags = [
                "tag-algorithm-complexity", "tag-data-structure", "tag-sort-algorithm",
                "tag-search-algorithm", "tag-class", "tag-inheritance", "tag-thread",
                "tag-concurrency", "tag-tree-structure", "tag-graph-structure",
                "tag-func-lib", "tag-exception", "tag-test-case", "tag-oop", "tag-memory"
            ]
            return default_tags[:30]
        
    except Exception as e:
        logger.error(f"筛选Tag失败: {str(e)}")
        # 使用默认Tag
        default_tags = [
            "tag-algorithm-complexity", "tag-data-structure", "tag-sort-algorithm",
            "tag-search-algorithm", "tag-class", "tag-inheritance", "tag-thread",
            "tag-concurrency", "tag-tree-structure", "tag-graph-structure",
            "tag-func-lib", "tag-exception", "tag-test-case", "tag-oop", "tag-memory"
        ]
        return default_tags[:30]

def get_questions_by_tags(tag_ids: list) -> list:
    """
    根据Tag ID列表从Neo4j中查询对应的题目，每个Tag随机选择一道题
    """
    try:
        if graph is None:
            logger.error("Neo4j数据库未连接")
            return []
            
        questions = []
        for tag_id in tag_ids:
            # 为每个Tag随机查询一道题
            query = """
            MATCH (t:Tag {id: $tag_id})-[:MARKED_AS]-(q:Question)
            OPTIONAL MATCH (q)-[:TESTS]->(kp:KnowledgePoint)
            WITH q, t, collect(DISTINCT kp.name) AS knowledge_points
            RETURN q.id AS id, q.title AS title, q.content AS content, 
                   q.choice AS choice, q.type AS type, q.difficulty AS difficulty, 
                   q.answer AS answer, t.name AS tag_name,
                   knowledge_points[0] AS knowledgepoint_name
            ORDER BY rand() LIMIT 1
            """
            result = graph.run(query, tag_id=tag_id).data()
            
            if result:
                question = result[0]
                questions.append({
                    "question_id": question["id"],
                    "title": question["title"],
                    "content": question["content"],
                    "choice": question["choice"] or " ",
                    "question_type": question["type"],
                    "difficulty": question["difficulty"],
                    "standard_answer": question["answer"],
                    "tag_name": question["tag_name"],
                    "knowledgepoint_name": question["knowledgepoint_name"] or "",
                    "question_score": 5.0
                })
                logger.info(f"为Tag {tag_id} 查询到题目: {question['title']}")
            else:
                logger.warning(f"为Tag {tag_id} 未查询到题目")
        
        logger.info(f"总共查询到{len(questions)}道题目")
        return questions[:20]
        
    except Exception as e:
        logger.error(f"根据Tag查询题目失败: {str(e)}")
        return []

def generate_first_question(career_domain: str, job_role: str, user_id: str = None) -> dict:
    """
    生成面试的第一道问题及初始话题（交互式面试模式专用）。
    同时复用 Neo4j + LLM 流程生成笔试题并返回。

    Returns:
        dict: {
            "question": str,
            "topic": str,
            "difficulty": str,
            "written_test_questions": list
        }
    """
    logger.info(f"初始化面试首问，领域: {career_domain}，岗位: {job_role}，user_id: {user_id}")

    # 生成笔试题（Neo4j Tag 筛选 + LLM 选题，逻辑不变）
    written_test_questions = []
    all_tags = get_all_tags_from_neo4j()
    if all_tags:
        selected_tag_ids = select_tags_for_written_test(career_domain, job_role, all_tags)
        if selected_tag_ids:
            written_test_questions = get_questions_by_tags(selected_tag_ids)

    # 第一道题固定为开场自我介绍，不调用 LLM
    OPENING_QUESTION = (
        "你好！欢迎参加面工坊的面试，我是AI面试官。"
        "我们将针对您应聘的职位进行面试。"
        "请先简单介绍一下自己，不超过3分钟。"
    )

    logger.info("首问已设置为固定开场白")
    return {
        "question": OPENING_QUESTION,
        "topic": "自我介绍",
        "difficulty": "基础",
        "written_test_questions": written_test_questions,
    }
