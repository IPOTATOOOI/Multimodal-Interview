import json
import time
from typing import List, Dict, Optional, Tuple
from loguru import logger

try:
    from app.database.neo4j import graph
except Exception as e:
    logger.error("无法导入 Neo4j graph: %s", e)
    graph = None

DEFAULT_GDS_GRAPH_NAME = "gds_rec_projection"
DEFAULT_WRITE_PROPERTY = "fastrp_embedding"
DEFAULT_EMBED_DIM = 128

# --------------------------
# 辅助函数：执行 Cypher 并返回结果
# --------------------------
def run_cypher(cypher: str, params: dict = None):
    if graph is None:
        raise RuntimeError("Neo4j graph 未连接（graph is None）")
    try:
        return graph.run(cypher, **(params or {})).data()
    except Exception as e:
        logger.exception("执行 Cypher 出错: %s\nCypher: %s\nParams: %s", e, cypher, params)
        raise

# --------------------------
# 检查 GDS 是否可用
# --------------------------
def check_gds_available() -> bool:
    """
    通过 CALL gds.version() 检查 GDS 是否安装并可用
    返回 True/False
    """
    try:
        res = run_cypher("CALL gds.version() YIELD version RETURN version")  # 若无权限或无 gds 会抛异常
        if res and isinstance(res, list):
            logger.info("检测到 GDS 可用, version=%s", res[0].get("version"))
            return True
        logger.warning("GDS CALL 返回非预期结果: %s", res)
        return False
    except Exception as e:
        logger.warning("检测 GDS 可用性失败: %s. 请确认 Neo4j 已安装 Graph Data Science (GDS) 插件并且当前用户有相应权限.", e)
        return False

# --------------------------
# 创建 / 覆盖 GDS 图投影
# --------------------------
def create_gds_graph_projection(
    graph_name: str,
    node_labels: List[str],
    rel_types: List[str],
    overwrite: bool = True
) -> None:
    """
    在 Neo4j 中创建 gds.graph.create(graph_name, nodeProjection, relationshipProjection)
    node_labels: 列表 ["User","Question","Tag",...]
    rel_types: 列表 ["INTERACTS","MARKED_AS","TESTS",...]
    overwrite: 若已存在是否先 drop
    """
    if not check_gds_available():
        raise RuntimeError("GDS 不可用，无法创建投影。")

    # 尝试 drop 已存在的图（如果允许覆盖）
    if overwrite:
        try:
            # use drop if exists if available
            run_cypher(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")
            logger.info("若存在，已删除旧的 GDS 图：%s", graph_name)
        except Exception:
            # 有些 gds 版本没有 drop with flag; 尝试直接 drop 并忽略错误
            try:
                run_cypher(f"CALL gds.graph.drop('{graph_name}')")
                logger.info("删除旧的 GDS 图（fallback）: %s", graph_name)
            except Exception:
                logger.debug("忽略 drop 错误（可能是不存在）：%s", graph_name)

    # 构造 nodeProjection 列表与 relationshipProjection Map 字符串
    # nodeProjection 可以是数组形式，如 ['User','Question','Tag']
    node_proj = "[" + ", ".join([f"'{lbl}'" for lbl in node_labels]) + "]"

    # relationshipProjection 例如: { INTERACTS: {type:'INTERACTS', orientation:'UNDIRECTED'}, ... }
    rel_items = []
    for rel in rel_types:
        rel_items.append(f"{rel}: {{type: '{rel}', orientation: 'UNDIRECTED'}}")
    rel_proj = "{" + ", ".join(rel_items) + "}"

    cypher = (
        "CALL gds.graph.create(\n"
        f"  '{graph_name}',\n"
        f"  {node_proj},\n"
        f"  {rel_proj}\n"
        ");"
    )

    logger.info("创建 GDS 图投影：graph_name=%s, nodes=%s, rels=%s", graph_name, node_labels, rel_types)
    # 执行创建
    res = run_cypher(cypher)
    logger.info("gds.graph.create 返回: %s", res)

# --------------------------
# 在投影上运行 FastRP 并写回节点属性
# --------------------------
def run_fastrp_write(
    graph_name: str,
    embedding_dimension: int = DEFAULT_EMBED_DIM,
    write_property: str = DEFAULT_WRITE_PROPERTY,
    random_seed: Optional[int] = 42
) -> Dict:
    """
    在指定 graphName 上运行 FastRP，并把 embedding 写回节点的 write_property 字段。
    返回 GDS 执行的结果信息（以 dict 形式）
    """
    if not check_gds_available():
        raise RuntimeError("GDS 不可用，无法运行 FastRP。")

    params = {
        "graphName": graph_name,
        "embeddingDimension": embedding_dimension,
        "writeProperty": write_property
    }
    if random_seed is not None:
        params["randomSeed"] = random_seed

    # 使用 gds.fastRP.write({ ... })
    # 注意：gds.fastRP.write 的参数键名和 GDS 版本有关，使用通用写法
    cypher = (
        "CALL gds.fastRP.write({\n"
        f"  graphName: '{params['graphName']}',\n"
        f"  embeddingDimension: {params['embeddingDimension']},\n"
        f"  writeProperty: '{params['writeProperty']}',\n"
        f"  randomSeed: {params.get('randomSeed', 42)}\n"
        "}) YIELD nodesWritten, embeddingsWritten, runtimeSeconds, embeddingDimension\n"
        "RETURN nodesWritten, embeddingsWritten, runtimeSeconds, embeddingDimension;"
    )

    logger.info("运行 FastRP：graph=%s dim=%d writeProp=%s", graph_name, embedding_dimension, write_property)
    res = run_cypher(cypher)
    logger.info("FastRP 结果: %s", res)
    # 返回第一条结果的 dict（如果有）
    return res[0] if res else {}

# --------------------------
# 从 Neo4j 读取写回的 embedding（按 label）
# --------------------------
def fetch_embeddings_from_neo4j(
    write_property: str = DEFAULT_WRITE_PROPERTY,
    labels: Optional[List[str]] = None,
    limit_per_label: Optional[int] = None
) -> Dict[str, Dict[str, List[float]]]:
    """
    从 Neo4j 读取已写回的 embedding。
    返回格式: { label: { node_id: embedding_list, ... }, ... }
    labels: 若为 None 则尝试读取所有带该属性的节点（代价较大）
    limit_per_label: 每个 label 最多读取多少节点（调试用）
    """
    out = {}
    if graph is None:
        raise RuntimeError("Neo4j graph is None")

    if labels:
        for lbl in labels:
            # 根据你的节点 schema，id 字段是 t.id / q.id / kp.id / user.id 等
            # 我们尽量统一使用 `id` 属性名（文档中都是 id）
            q = f"""
            MATCH (n:{lbl})
            WHERE EXISTS(n.{write_property})
            RETURN n.id AS id, n.{write_property} AS emb
            {'LIMIT ' + str(limit_per_label) if limit_per_label else ''}
            """
            rows = run_cypher(q)
            d = {}
            for r in rows:
                node_id = r.get("id")
                emb = r.get("emb")
                # emb 从 Neo4j 读出通常是 list -> 转成 Python list of floats
                if emb is None:
                    continue
                # safety: ensure list of float
                d[node_id] = [float(x) for x in emb]
            out[lbl] = d
            logger.info("读取 label=%s 共 %d 个 embedding", lbl, len(d))
    else:
        # 全库扫描带有属性的节点（谨慎）
        q = f"""
        MATCH (n)
        WHERE EXISTS(n.{write_property})
        RETURN labels(n) AS labels, n.id AS id, n.{write_property} AS emb
        LIMIT 10000
        """
        rows = run_cypher(q)
        for r in rows:
            lbls = r.get("labels") or []
            first_lbl = lbls[0] if lbls else "Unknown"
            out.setdefault(first_lbl, {})
            emb = r.get("emb")
            if emb is None:
                continue
            out[first_lbl][r.get("id")] = [float(x) for x in emb]
        logger.info("全量读取完成，label buckets=%d", len(out))
    return out

# --------------------------
# 导出 embeddings 为本地 npz 文件
# --------------------------
def export_embeddings_npz(out_path: str, embeddings_dict: Dict[str, Dict[str, List[float]]]):
    """
    把 embeddings_dict 导出为一个 npz 文件，结构为：
    np.savez(out_path, label1_ids=..., label1_embs=..., label2_ids=..., label2_embs=...)
    """
    import numpy as np
    payload = {}
    for lbl, mapping in embeddings_dict.items():
        ids = list(mapping.keys())
        embs = [mapping[i] for i in ids]
        if not ids:
            continue
        payload[f"{lbl}_ids"] = np.array(ids, dtype=object)
        payload[f"{lbl}_embs"] = np.array(embs, dtype=np.float32)
    np.savez(out_path, **payload)
    logger.info("导出 embeddings 到 %s, keys=%s", out_path, list(payload.keys()))

# --------------------------
# 主流程函数（整合）
# --------------------------
def generate_and_export_fastrp(
    node_labels: List[str],
    rel_types: List[str],
    graph_name: str = DEFAULT_GDS_GRAPH_NAME,
    embedding_dimension: int = DEFAULT_EMBED_DIM,
    write_property: str = DEFAULT_WRITE_PROPERTY,
    export_npz_path: Optional[str] = None,
    drop_projection_after: bool = False
) -> Tuple[Dict, Dict]:
    """
    1) 在 Neo4j 创建投影 (node_labels, rel_types)
    2) 运行 FastRP 并写回属性 write_property
    3) 读取写回的 embeddings（按 node_labels）
    4) 可选导出到 npz
    返回 (fastrp_run_result_dict, embeddings_dict)
    """
    start = time.time()
    logger.info("开始 FastRP 流程，labels=%s, rels=%s", node_labels, rel_types)
    create_gds_graph_projection(graph_name, node_labels, rel_types, overwrite=True)
    res = run_fastrp_write(graph_name, embedding_dimension=embedding_dimension, write_property=write_property)
    logger.info("FastRP 写回完成，结果：%s", res)
    embeddings = fetch_embeddings_from_neo4j(write_property=write_property, labels=node_labels)
    if export_npz_path:
        export_embeddings_npz(export_npz_path, embeddings)

    if drop_projection_after:
        try:
            run_cypher(f"CALL gds.graph.drop('{graph_name}')")
            logger.info("已删除 GDS 投影: %s", graph_name)
        except Exception:
            logger.warning("删除 GDS 投影失败或被忽略")

    elapsed = time.time() - start
    logger.info("FastRP 全流程完成，用时 %.2fs", elapsed)
    return res, embeddings

# if __name__ == "__main__":
#     # 你可以按需修改以下 node_labels 与 rel_types（根据你 DB 的实际标签）
#     node_labels = ["User", "Question", "Tag", "KnowledgePoint", "Content"]
#     rel_types = [
#         "INTERACTS",   # (User)-[:INTERACTS]->(Question)
#         "VIEWED",      # (User)-[:VIEWED]->(Content)
#         "TESTS",       # (Question)-[:TESTS]->(KnowledgePoint)
#         "COVERS",      # (Content)-[:COVERS]->(KnowledgePoint)
#         "MARKED_AS",   # (Question)-[:MARKED_AS]->(Tag)
#         "PREREQUISITE",# (KnowledgePoint)-[:PREREQUISITE]->(KnowledgePoint)
#         "SIMILAR_TO"   # semantic similarity edges (if present)
#     ]
#
#     try:
#         out_res, out_embeddings = generate_and_export_fastrp(
#             node_labels=node_labels,
#             rel_types=rel_types,
#             graph_name="fastrp_rec_graph",
#             embedding_dimension=128,
#             write_property="fastrp_embedding",
#             export_npz_path="fastrp_embeddings.npz",
#             drop_projection_after=False  # 若想保留 projection 改为 False/True
#         )
#         logger.info("Done. fastRP result: %s", out_res)
#         # 简要展示读取到的 embedding 统计
#         for lbl, mp in out_embeddings.items():
#             logger.info("Label=%s count=%d", lbl, len(mp))
#     except Exception as e:
#         logger.exception("执行 FastRP 流程失败: %s", e)
#         logger.error("请确认 Neo4j 已安装并启用 GDS 插件，且当前用户有执行 GDS 的权限；"
#                      "或者联系 DBA 在 Neo4j 服务端运行 FastRP 并回写节点属性。")
