from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.graphRAG.entity_extractor import EntityExtractor
from app.services.graphRAG.graph_retriever import GraphRetriever
from app.services.graphRAG.response_generator import ResponseGenerator
from app.graphRAG.models import GraphRAGRequest, GraphRAGResponse
from fastapi.responses import StreamingResponse
import json

# 创建路由
router = APIRouter(prefix="/graphrag", tags=["GraphRAG"])

# 初始化服务
entity_extractor = EntityExtractor()
graph_retriever = GraphRetriever()
response_generator = ResponseGenerator()

@router.post("/query")
async def graph_rag_query(request: GraphRAGRequest) :
    """
    GraphRAG查询端点

    Args:
        request: GraphRAG请求参数

    Returns:
        StreamingResponse: 流式输出的回答
    """
    async def generate_response():
        try:
            # 步骤1: 提取实体
            print(f"开始提取实体: {request.question}")
            entities = entity_extractor.extract_entities(request.question)
            print(f"提取到实体: {[entity.text for entity in entities]}")

            # 步骤2: 检索相关节点
            max_nodes = request.max_retrieval_nodes or 50
            retrieved_nodes = graph_retriever.retrieve_related_nodes(entities, max_nodes)
            print(f"检索到节点数: {len(retrieved_nodes)}")

            # 步骤3: 生成回答（流式）
            yield f"data: {json.dumps({'status': 'started', 'message': '开始生成回答'})}\n\n"
            answer_chunks = []
            for chunk in response_generator.generate_response(request.question, retrieved_nodes):
                answer_chunks.append(chunk)
                # 将每个块以SSE格式发送
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            full_answer = ''.join(answer_chunks)
            
            # 发送最终结果
            response_data = {
                "type": "final",
                "content": full_answer,
                "entities": [entity.dict() for entity in entities],
                "retrieved_nodes_count": len(retrieved_nodes)
            }
            yield f"data: {json.dumps(response_data)}\n\n"
            
        except Exception as e:
            print(f"GraphRAG查询失败: {e}")
            error_data = {
                "type": "error",
                "content": f"查询失败: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """健康检查端点"""
    return {"status": "healthy", "service": "GraphRAG"}

# 关闭时清理资源
@router.on_event("shutdown")
async def shutdown_event():
    graph_retriever.close()