from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from app.graphRAG_enhanced.index_manager import index_manager

# 创建独立的路由器
graph_rag_router = APIRouter(prefix="/graph-rag-enhanced", tags=["GraphRAG_enhanced"])

# 请求/响应模型
class BuildIndexResponse(BaseModel):
    message: str
    success: bool
    details: Optional[dict] = None

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    question: str
    similar_communities: List[dict]
    answer: str



@graph_rag_router.post("/build-index", response_model=BuildIndexResponse)
async def build_index():
    """手动触发索引构建（如果已存在则跳过）"""
    try:
        success = await index_manager.build_full_index()

        if success:
            return BuildIndexResponse(
                message="索引构建完成",
                success=True
            )
        else:
            return BuildIndexResponse(
                message="索引构建失败",
                success=False
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引构建失败: {str(e)}")

@graph_rag_router.post("/initialize-index", response_model=BuildIndexResponse)
async def initialize_index():
    """手动初始化索引"""
    try:
        success = await index_manager.initialize_index()
        
        if success:
            return BuildIndexResponse(
                message="索引初始化完成",
                success=True
            )
        else:
            return BuildIndexResponse(
                message="索引初始化失败",
                success=False
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引初始化失败: {str(e)}")
    
@graph_rag_router.post("/query", response_model=QueryResponse)
async def query_knowledge_graph(request: QueryRequest):
    """查询知识图谱"""
    try:
        # 确保索引已构建
        if not index_manager._index_built:
            raise HTTPException(status_code=400, detail="索引尚未构建，请先调用 /build-index 或 /initialize-index 接口")

        # 搜索相似社区
        search_results = index_manager.search_similar_communities(
            request.question,
            request.top_k
        )

        # 构建响应
        similar_communities = []
        for i, (doc, metadata) in enumerate(zip(
                search_results['documents'][0],
                search_results['metadatas'][0]
        )):
            similar_communities.append({
                "rank": i + 1,
                "community_id": metadata['community_id'],
                "summary": doc,
                "node_count": metadata['node_count']
            })

        # 生成简单答案
        if similar_communities:
            answer = f"找到 {len(similar_communities)} 个相关社区。最相关的社区主题: {similar_communities[0]['summary'][:150]}..."
        else:
            answer = "未找到相关社区信息。"

        return QueryResponse(
            question=request.question,
            similar_communities=similar_communities,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@graph_rag_router.get("/community/{community_id}")
async def get_community_details(community_id: int):
    """获取特定社区的详细信息"""
    try:
        # 检查索引是否已构建
        if not index_manager._index_built:
            raise HTTPException(status_code=400, detail="索引尚未构建，请先调用 /build-index 或 /initialize-index 接口")

        subgraph_data = index_manager.get_community_details(community_id)
        return {
            "community_id": community_id,
            "node_count": len(set([r['node1_name'] for r in subgraph_data if r['node1_name']] +
                                  [r['node2_name'] for r in subgraph_data if r['node2_name']])),
            "relationships": subgraph_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取社区信息失败: {str(e)}")