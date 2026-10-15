from py2neo import Graph, Node
import os
from loguru import logger
from app.core.config import settings  # 新增导入

# 创建数据库连接
try:
    graph = Graph(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
    # 测试连接
    graph.run("RETURN 1 as test").data()
    logger.info("Neo4j数据库连接成功")
except Exception as e:
    logger.error(f"Neo4j数据库连接失败: {str(e)}")
    # 创建一个None的graph对象，避免应用崩溃
    graph = None

def save_media(
        id: str,
        filename: str,
        media_type: str,
        transcript: str,
        timestamp: str,
):
    """
    通用 Media 节点。
    id: UUID
    filename: 原始文件名
    media_type: 'audio' / 'video' / 'image' ...
    transcript: 转写文字（若非语音，可留空或备注）
    timestamp: ISO 字符串
    """
    tx = graph.begin()
    node = Node(
        "Media",
        id=id,
        filename=filename,
        mediaType=media_type,
        transcript=transcript,
        timestamp=timestamp,
    )
    # 额外给音频贴 Audio 标签（可选）
    if media_type == "audio":
        node.add_label("Audio")
    tx.merge(node, "Media", "id")
    tx.commit()
