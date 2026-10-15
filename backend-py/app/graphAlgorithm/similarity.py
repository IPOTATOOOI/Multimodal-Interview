import math
import time
from typing import List, Dict, Tuple, Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

try:
    from app.database.neo4j import graph
except Exception as e:
    logger.error("无法导入 Neo4j graph：%s", e)
    graph = None


def _get_random_tags_from_neo4j(count: int = 500) -> List[Dict[str, str]]:
    if graph is None:
        logger.error("Neo4j graph is None, cannot query tags.")
        return []
    try:
        q = "MATCH (t:Tag) RETURN t.id AS id, t.name AS name ORDER BY rand() LIMIT $count"
        rows = graph.run(q, count=count).data()
        tags = [{"id": r["id"], "name": r["name"]} for r in rows]
        logger.info("查询到 %d 个 Tag", len(tags))
        return tags
    except Exception as e:
        logger.exception("查询 Tag 失败：%s", e)
        return []


def _normalize_embeddings(emb: np.ndarray) -> np.ndarray:
    """ L2 归一化 """
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return emb / norms


def get_topk_pairs_for_rows(
    emb_norm: np.ndarray,
    indices: List[int],
    top_k: int,
    threshold: float
) -> List[Tuple[int, int, float]]:
    """
    对 emb_norm 中指定 rows (indices) 逐行计算相似度并返回满足阈值的 top_k 对。
    返回 (i, j, score)，其中 i 是行索引，j 是相似标签索引。
    """
    N, D = emb_norm.shape
    results = []
    for i in indices:
        # similarities to all others
        sims = emb_norm[i].dot(emb_norm.T)  # shape (N,)
        sims[i] = -1.0  # 排除自身
        # 找到满足阈值的索引
        mask_idx = np.where(sims >= threshold)[0]
        if mask_idx.size == 0:
            continue
        # 排序并取 top_k
        candidates = mask_idx[np.argsort(-sims[mask_idx])]
        selected = candidates[:top_k]
        for j in selected:
            results.append((i, int(j), float(sims[j])))
    return results


def compute_similar_pairs(
    texts: List[str],
    top_k: int = 5,
    threshold: float = 0.75,
    model_name: str = "uer/sbert-base-chinese-nli",
    batch_size: int = 64,
    max_rows_per_chunk: int = 500
) -> Tuple[np.ndarray, List[Tuple[int, int, float]]]:
    """
    生成文本 embeddings，并计算满足阈值/top_k 的相似对（索引层面）。
    返回 (embeddings, pairs)，其中 embeddings shape=(N, dim)，pairs 是 (i,j,score) 列表。
    """
    logger.info("加载模型：%s", model_name)
    model = SentenceTransformer(model_name)

    logger.info("编码文本，共 %d 条", len(texts))
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=batch_size)
    emb = np.asarray(embeddings, dtype=np.float32)
    emb_norm = _normalize_embeddings(emb)

    N = emb_norm.shape[0]
    logger.info("开始计算相似度：N=%d, top_k=%d, threshold=%.4f", N, top_k, threshold)

    # 若规模不大，直接一并计算；若大则分块逐行计算
    pairs = []
    estimated_pairs = N * N
    if N * N <= 5_000_000:  # 约 5M 的相似度数可以直接矩阵乘
        sims_all = emb_norm.dot(emb_norm.T)
        np.fill_diagonal(sims_all, -1.0)
        for i in range(N):
            row = sims_all[i]
            # 筛选阈值
            cand_idx = np.where(row >= threshold)[0]
            if cand_idx.size == 0:
                continue
            # 取 top_k
            sorted_idx = cand_idx[np.argsort(-row[cand_idx])]
            for j in sorted_idx[:top_k]:
                pairs.append((i, int(j), float(row[j])))
    else:
        # 分块按行计算，避免 memory blowup
        logger.info("大矩阵，采用分块计算相似度")
        indices = list(range(N))
        # 将 indices 划分为块
        chunks = [indices[i:i + max_rows_per_chunk] for i in range(0, N, max_rows_per_chunk)]
        for chunk in chunks:
            chunk_pairs = get_topk_pairs_for_rows(emb_norm, chunk, top_k, threshold)
            pairs.extend(chunk_pairs)

    logger.info("共找到 %d 条相似对 (i,j,score)", len(pairs))
    return emb, pairs


def write_pairs_to_neo4j(
    tag_ids: List[str],
    pairs: List[Tuple[int, int, float]],
    dry_run: bool = False,
    batch_commit: int = 200
) -> int:
    """
    把 (i,j,score) 对写到 Neo4j 的 :SIMILAR_TO 边上。
    - tag_ids: 原始 tag id 列表，索引对应 embeddings 的索引
    - pairs: (i,j,score)
    - 若 dry_run True，则只打印并不写回
    返回写入或将要写入的边数量
    """
    if graph is None:
        logger.error("Neo4j graph is None，无法写回")
        return 0

    created = 0
    tx = None
    try:
        if dry_run:
            for i, j, s in pairs:
                # 保证无重复（规范化顺序）
                id1, id2 = tag_ids[i], tag_ids[j]
                if id1 == id2:
                    continue
                if id1 > id2:
                    id1, id2 = id2, id1
                logger.info("[dry_run] %s <-> %s  score=%.4f", id1, id2, s)
            return len(pairs)
        tx = graph.begin()
        count = 0
        for i, j, s in pairs:
            id_i = tag_ids[i]; id_j = tag_ids[j]
            if id_i == id_j:
                continue
            # 规范化顺序，避免重复双向创建
            a_id, b_id = (id_i, id_j) if id_i <= id_j else (id_j, id_i)
            # MERGE 无向边写法： (a)-[r:SIMILAR_TO]-(b)
            cypher = """
            MATCH (a:Tag {id:$a_id}), (b:Tag {id:$b_id})
            MERGE (a)-[r:SIMILAR_TO]-(b)
            SET r.score = $score, r.updated_at = $now
            """
            tx.run(cypher, a_id=a_id, b_id=b_id, score=float(s), now=int(time.time() * 1000))
            count += 1
            created += 1
            if count >= batch_commit:
                tx.commit()
                tx = graph.begin()
                count = 0
        if tx is not None:
            tx.commit()
    except Exception as e:
        logger.exception("写入 Neo4j 失败: %s", e)
        if tx is not None:
            try:
                tx.rollback()
            except Exception:
                pass
    logger.info("写入/更新了 %d 条 SIMILAR_TO 边", created)
    return created


def compute_and_write_similar_tags(
    tags: Optional[List[Dict[str, str]]] = None,
    sample_count: int = 500,
    top_k: int = 5,
    threshold: float = 0.75,
    model_name: str = "uer/sbert-base-chinese-nli",
    dry_run: bool = False,
    batch_size: int = 64
) -> Dict[str, int]:
    """
    主函数：
    - tags: 如果传入则使用该列表（每项包含 'id' 和 'name'）；否则从 Neo4j 随机抓取 sample_count 条
    - top_k: 每个 tag 至多建立 top_k 个相似边
    - threshold: 相似度阈值
    - 返回字典统计结果
    """
    start_ts = time.time()
    if tags is None:
        tags = _get_random_tags_from_neo4j(count=sample_count)
    if not tags:
        logger.warning("没有可处理的 tags，退出")
        return {"status": 0}

    tag_ids = [t["id"] for t in tags]
    names = [t["name"] for t in tags]

    emb, pairs = compute_similar_pairs(
        texts=names,
        top_k=top_k,
        threshold=threshold,
        model_name=model_name,
        batch_size=batch_size
    )

    # pairs currently contains directed pairs (i->j) ；我们在写入时会去重合并为无向
    created = write_pairs_to_neo4j(tag_ids, pairs, dry_run=dry_run)
    cost_s = time.time() - start_ts
    logger.info("总耗时：%.2fs，处理 tags=%d，写入边=%d", cost_s, len(tags), created)
    return {"status": 1, "tags_processed": len(tags), "edges_written": created, "time_s": cost_s}

#
# if __name__ == "__main__":
#     res = compute_and_write_similar_tags(
#         tags=None,          # None = 从 Neo4j 随机取 sample_count 个标签
#         sample_count=500,   # 随机抽样数量；或传入 tags 列表
#         top_k=5,
#         threshold=0.75,
#         model_name="uer/sbert-base-chinese-nli",
#         dry_run=False,
#         batch_size=64
#     )
#     print(res)
