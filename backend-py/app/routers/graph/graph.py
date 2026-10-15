from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.graph.graph_service import get_graph_data, delete_nodes, delete_relationships

router = APIRouter(prefix="/graph", tags=["图数据"])

# 请求模型
class DeleteNodesRequest(BaseModel):
    user_id: int
    is_admin: bool = False
    node_ids: List[str]

class RelationshipInfo(BaseModel):
    source: str
    target: str
    name: str

class DeleteRelationshipsRequest(BaseModel):
    user_id: int
    is_admin: bool = False
    relationships: List[RelationshipInfo]

@router.get("/data", summary="获取图数据")
async def get_graph(
    user_id: int = Query(..., description="用户ID"),
    is_admin: bool = Query(False, description="是否为管理员，默认为False")
):
    """
    从Neo4j图数据库获取节点和关系数据，支持用户权限过滤:
    - user_id: 用户ID，用于过滤节点
    - is_admin: 是否为管理员，True时返回所有节点，False时只返回用户自己的节点和公共节点(user_id=0)
    
    返回格式:
    - nodes: 节点列表，包含id、name、type和properties
    - links: 关系列表，包含source、target、name和properties
    """
    try:
        data = get_graph_data(user_id, is_admin)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")

@router.delete("/nodes", summary="删除节点")
async def delete_graph_nodes(request: DeleteNodesRequest):
    """
    删除图数据库中的节点
    
    参数:
    - user_id: 用户ID，用于权限验证
    - is_admin: 是否为管理员，True时删除所有指定节点，False时只删除自己的节点和公共节点
    - node_ids: 要删除的节点ID列表
    
    返回:
    - deleted_count: 实际删除的节点数量
    """
    try:
        result = delete_nodes(request.node_ids, request.user_id, request.is_admin)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除节点失败: {str(e)}")

@router.delete("/relationships", summary="删除关系")
async def delete_graph_relationships(request: DeleteRelationshipsRequest):
    """
    删除图数据库中的关系
    
    参数:
    - user_id: 用户ID，用于权限验证
    - is_admin: 是否为管理员，True时删除所有指定关系，False时只删除涉及自己节点的关系
    - relationships: 要删除的关系列表，每个关系包含source、target和name
    
    返回:
    - deleted_count: 实际删除的关系数量
    """
    try:
        # 转换关系信息为字典格式
        relationships_data = [rel.dict() for rel in request.relationships]
        result = delete_relationships(relationships_data, request.user_id, request.is_admin)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除关系失败: {str(e)}")