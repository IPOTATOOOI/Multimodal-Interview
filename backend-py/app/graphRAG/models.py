from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GraphRAGRequest(BaseModel):
    """GraphRAG请求模型"""
    question: str
    user_id: Optional[str] = None
    max_retrieval_nodes: Optional[int] = 5

class Entity(BaseModel):
    """实体模型"""
    text: str
    type: str  # 实体类型：Question, Topic, Tag等

class RetrievedNode(BaseModel):
    """检索到的节点模型"""
    node_id: str
    node_type: str
    content: Dict[str, Any]
    similarity_score: float
    retrieval_method: str  # text_match 或 semantic_match
    neighbors: Optional[List[Dict[str, Any]]] = None
    relationships: Optional[List[Dict[str, Any]]] = None

class GraphRAGResponse(BaseModel):
    """GraphRAG响应模型"""
    answer: str