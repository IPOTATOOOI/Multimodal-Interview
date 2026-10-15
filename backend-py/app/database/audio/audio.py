from py2neo import Node
from datetime import datetime

def save_audio(
        id: str,
        filename: str,
        transcript: str,
        timestamp: str,
):
    """
    保存音频节点到Neo4j数据库。
    id: UUID
    filename: 原始文件名
    transcript: 转写文字
    timestamp: ISO 字符串
    """
    from app.database.neo4j import graph
    
    tx = graph.begin()
    node = Node(
        "Media",
        "Audio",  # 添加Audio标签
        id=id,
        filename=filename,
        mediaType="audio",
        transcript=transcript,
        timestamp=timestamp,
    )
    tx.merge(node, "Media", "id")
    tx.commit() 