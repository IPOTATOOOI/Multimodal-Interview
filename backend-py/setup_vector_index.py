# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """
# Neo4j向量索引设置脚本
# 功能：为Question节点添加embedding属性并创建向量索引
# """
#
# import os
# import sys
# import time
# from py2neo import Graph, NodeMatcher
# import requests
# from dotenv import load_dotenv
# import json
# from typing import List
#
# # 加载环境变量
# def load_env():
#     dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
#     if os.path.exists(dotenv_path):
#         load_dotenv(dotenv_path)
#     else:
#         print(f"警告：未找到.env文件，使用系统环境变量")
#
# # 获取环境变量并设置默认值
# def get_env_vars():
#     neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
#     neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
#     neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
#     ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#     embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-m3")
#     vector_index_name = os.getenv("VECTOR_INDEX_NAME", "question_content_vector_idx")
#     batch_size = int(os.getenv("BATCH_SIZE", "10"))
#
#     return {
#         "neo4j_uri": neo4j_uri,
#         "neo4j_username": neo4j_username,
#         "neo4j_password": neo4j_password,
#         "ollama_base_url": ollama_base_url,
#         "embedding_model": embedding_model,
#         "vector_index_name": vector_index_name,
#         "batch_size": batch_size
#     }
#
# # 连接到Neo4j数据库
# def connect_to_neo4j(uri, username, password):
#     try:
#         graph = Graph(uri, auth=(username, password))
#         # 测试连接
#         graph.run("RETURN 1")
#         print(f"成功连接到Neo4j数据库: {uri}")
#         return graph
#     except Exception as e:
#         print(f"无法连接到Neo4j数据库: {e}")
#         sys.exit(1)
#
# # 使用Ollama API获取嵌入向量
# def get_embeddings(ollama_url, model, texts: List[str]) -> List[List[float]]:
#     embeddings = []
#     for text in texts:
#         payload = {
#             "model": model,
#             "prompt": text
#         }
#         try:
#             response = requests.post(
#                 f"{ollama_url}/api/embeddings",
#                 json=payload,
#                 timeout=60
#             )
#             if response.status_code == 200:
#                 result = response.json()
#                 embedding = result.get("embedding", [])
#                 embeddings.append(embedding)
#             else:
#                 print(f"Ollama API请求失败，状态码: {response.status_code}, 文本: {text[:50]}...")
#                 embeddings.append([])
#         except Exception as e:
#             print(f"Ollama嵌入获取失败: {e}, 文本: {text[:50]}...")
#             embeddings.append([])
#
#         # 避免请求过于频繁
#         time.sleep(0.1)
#
#     return embeddings
#
# # 检查是否已存在向量索引（修复版）
# def check_vector_index(graph, index_name):
#     try:
#         # 尝试使用不同的索引检查方法
#         try:
#             # Neo4j 5.x及以上版本
#             query = "SHOW INDEXES YIELD name RETURN name = $index_name AS exists"
#             result = graph.run(query, index_name=index_name).evaluate()
#             return result
#         except Exception:
#             try:
#                 # 较早的Neo4j版本
#                 query = "CALL db.indexes() YIELD name RETURN name = $index_name AS exists"
#                 result = graph.run(query, index_name=index_name).evaluate()
#                 return result
#             except Exception as e:
#                 print(f"检查索引时出错: {e}")
#                 return False
#     except Exception as e:
#         print(f"检查索引时出错: {e}")
#         return False
#
# # 创建向量索引（修复版）
# def create_vector_index(graph, index_name, dimension=1024):
#     try:
#         # 先检查索引是否存在
#         if check_vector_index(graph, index_name):
#             print(f"向量索引 '{index_name}' 已存在")
#             return True
#
#         print(f"正在创建向量索引 '{index_name}'，维度: {dimension}...")
#
#         # 根据错误信息，使用正确的参数名
#         # 使用Neo4j 5.x及以上版本的语法
#         query = f"""
#         CREATE VECTOR INDEX {index_name}
#         FOR (n:Question)
#         ON (n.embedding)
#         OPTIONS {{indexConfig: {{vector.dimensions: {dimension}, vector.similarity_function: 'cosine'}}}}
#         """
#
#         try:
#             graph.run(query)
#             print(f"成功创建向量索引: {index_name}")
#             return True
#         except Exception as e:
#             print(f"创建向量索引尝试1失败: {e}")
#
#             # 尝试另一种语法（较早版本）
#             print("尝试使用备选语法创建向量索引...")
#             query_alt = f"""
#             CREATE VECTOR INDEX {index_name}
#             FOR (n:Question)
#             ON (n.embedding)
#             OPTIONS {{indexConfig: {{vector.dimensions: {dimension}, vector.similarity_function: 'cosine'}}}}
#             """
#             try:
#                 graph.run(query_alt)
#                 print(f"成功创建向量索引: {index_name}")
#                 return True
#             except Exception as e2:
#                 print(f"创建向量索引尝试2失败: {e2}")
#                 return False
#     except Exception as e:
#         print(f"创建向量索引失败: {e}")
#         return False
#
# # 为Question节点添加embedding属性
# def add_embeddings_to_questions(graph, ollama_url, model, batch_size):
#     try:
#         # 获取Question节点总数
#         total_nodes_query = "MATCH (q:Question) WHERE q.embedding IS NULL RETURN count(q)"
#         total_nodes = graph.run(total_nodes_query).evaluate()
#
#         if total_nodes == 0:
#             print("所有Question节点已经有embedding属性")
#             return 0
#
#         print(f"找到 {total_nodes} 个需要添加embedding属性的Question节点")
#
#         # 分批处理节点
#         processed = 0
#         while processed < total_nodes:
#             # 获取一批节点
#             batch_query = """
#             MATCH (q:Question)
#             WHERE q.embedding IS NULL
#             RETURN id(q) AS id, q.title AS title, q.content AS content
#             LIMIT $batch_size
#             """
#             batch_result = graph.run(batch_query, batch_size=batch_size).data()
#
#             if not batch_result:
#                 break
#
#             # 准备文本用于生成向量
#             node_ids = []
#             texts = []
#
#             for record in batch_result:
#                 node_ids.append(record['id'])
#                 # 结合title和content生成文本表示
#                 title = record.get('title', '') or ''
#                 content = record.get('content', '') or ''
#                 combined_text = f"{title} {content}".strip()
#                 texts.append(combined_text)
#
#             # 获取嵌入向量
#             print(f"正在为第 {processed+1}-{min(processed+batch_size, total_nodes)} 个节点生成向量...")
#             embeddings = get_embeddings(ollama_url, model, texts)
#
#             # 更新节点的embedding属性
#             for i, node_id in enumerate(node_ids):
#                 embedding = embeddings[i]
#                 if embedding:
#                     # 将embedding向量转换为Neo4j支持的格式
#                     update_query = """
#                     MATCH (q) WHERE id(q) = $node_id
#                     SET q.embedding = $embedding
#                     RETURN q
#                     """
#                     graph.run(update_query, node_id=node_id, embedding=embedding)
#                     processed += 1
#
#             # 进度报告
#             progress = min(processed, total_nodes) / total_nodes * 100
#             print(f"进度: {progress:.2f}% ({progress}/{total_nodes})")
#
#         print(f"成功为 {processed} 个Question节点添加了embedding属性")
#         return processed
#     except Exception as e:
#         print(f"处理节点时出错: {e}")
#         return -1
#
# # 主函数
# def main():
#     print("======= Neo4j向量索引设置工具 =======")
#
#     # 加载环境变量
#     load_env()
#
#     # 获取配置
#     config = get_env_vars()
#
#     # 连接到Neo4j
#     graph = connect_to_neo4j(
#         config["neo4j_uri"],
#         config["neo4j_username"],
#         config["neo4j_password"]
#     )
#
#     # 为Question节点添加embedding属性
#     processed_count = add_embeddings_to_questions(
#         graph,
#         config["ollama_base_url"],
#         config["embedding_model"],
#         config["batch_size"]
#     )
#
#     # 如果成功处理了节点，创建向量索引
#     if processed_count >= 0:
#         # 尝试获取向量维度（从第一个有embedding的节点）
#         dimension_query = "MATCH (q:Question) WHERE q.embedding IS NOT NULL RETURN q.embedding LIMIT 1"
#         embedding_sample = graph.run(dimension_query).evaluate()
#
#         dimension = 768  # 默认维度
#         if embedding_sample and isinstance(embedding_sample, list):
#             dimension = len(embedding_sample)
#             print(f"检测到向量维度: {dimension}")
#
#         # 创建向量索引
#         create_vector_index(graph, config["vector_index_name"], dimension)
#
#     print("======= 向量索引设置完成 =======")
#
# if __name__ == "__main__":
#     main()