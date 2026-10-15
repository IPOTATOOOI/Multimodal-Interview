
import csv
from py2neo import Graph, Node, Relationship
import os
from dotenv import load_dotenv

# 读取.env配置
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PASS", "")

def import_csv_to_neo4j(csv_file_path, user_id=0):
    """
    将csv数据导入Neo4j，Topic节点id和name根据csv内容动态生成
    
    Args:
        csv_file_path: CSV文件路径
        user_id: 用户ID，默认为0（公共节点）
    """
    graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    # 读取CSV文件
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        if not rows:
            return False
        # 取第一个数据的Topic作为id和name
        topic_id = rows[0]['Topic'].strip()
        topic_name = rows[0]['Topic'].strip()
        # 检查Topic节点是否已存在
        topic_exists = graph.run("MATCH (t:Topic {id: $id}) RETURN t", id=topic_id).data()
        if not topic_exists:
            graph.run("""
                CREATE (t:Topic {
                    id: $id,
                    name: $name,
                    user_id: $user_id
                })
            """, id=topic_id, name=topic_name, user_id=user_id)
            # 可选：连接到SubCategory节点
            graph.run("""
                MATCH (sub:SubCategory {id: $sub_id}),  
                      (topic:Topic {id: $topic_id})
                CREATE (sub)-[:CONTAINS_TOPIC]->(topic)
            """, sub_id="dev-interview", topic_id=topic_id)
        # 添加计数器用于生成Question节点的id
        question_counter = 1
        for row in rows:
            title = row['title'].strip()
            content = row['content'].strip()
            answer = row['answer'].strip()
            tags = row['Tag'].strip()
            topic = row['Topic'].strip()
            # 检查Question节点是否已存在
            question_exists = graph.run("MATCH (q:Question {title: $title}) RETURN q", title=title).data()
            if not question_exists:
                question_id = f"{topic_id}-{question_counter}"
                question_node = Node("Question", 
                                   id=question_id,
                                   title=title, 
                                   content=content, 
                                   answer=answer,
                                   topic=topic,
                                   user_id=user_id)
                graph.create(question_node)
                question_counter += 1
            # Question连接Topic
            graph.run("""
                MATCH (t:Topic {id: $topic_id})
                MATCH (q:Question {title: $title})
                MERGE (t)-[:INCLUDES]->(q)
            """, topic_id=topic_id, title=title)
            # Tag节点处理
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                for tag_name in tag_list:
                    if tag_name:
                        existing_tag = graph.run("MATCH (t:Tag {name: $name}) RETURN t", name=tag_name).data()
                        if not existing_tag:
                            tag_id = f"tag-{tag_name}"
                            tag_node = Node("Tag", id=tag_id, name=tag_name, user_id=user_id)
                            graph.create(tag_node)
                        graph.run("""
                            MATCH (q:Question {title: $title})
                            MATCH (t:Tag {name: $tag_name})
                            MERGE (q)-[:MARKED_AS]->(t)
                        """, title=title, tag_name=tag_name)
    return True

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    csv_file_path = os.getenv('CSV_FILE_PATH', 'uie_predictions.csv')
    import_csv_to_neo4j(csv_file_path)
    print("数据已成功导入到Neo4j图数据库中！")
