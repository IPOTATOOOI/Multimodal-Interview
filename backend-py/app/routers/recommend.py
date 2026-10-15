# app/routes/recommend_with_models.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional, Set, Tuple
from loguru import logger
import numpy as np
import math
import time

from app.database.neo4j import graph

router = APIRouter(tags=["recommend"])

# 默认 Tag 列表（用于补全不足20题时）
DEFAULT_TAG_IDS: List[str] = [
    "tag-polymorphism", "tag-collection", "tag-interface", "tag-exception", "tag-set",
    "tag-map", "tag-thread", "tag-sync", "tag-io", "tag-wrapper", "tag-constructor",
    "tag-method", "tag-file", "tag-overload", "tag-static", "tag-jvm-structure",
    "tag-db-backup", "tag-transaction", "tag-memory", "tag-plugin"
]

# 要限制的根分类名称（或 id），按需修改
ROOT_CATEGORY_NAME_OR_ID = "软件开发"  # 也可以填写 'dev' 等 id


# ----------------------------
# Neo4j helper queries
# ----------------------------
def _get_one_question_by_tag(tag_id: str, root_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    根据 Tag ID 从 Neo4j 中随机查询一道题目。
    若传入 root_name，则仅在该 RootCategory 下的题目中随机抽取。
    返回题目信息字典，找不到题目时返回 None。
    """
    if graph is None:
        return None

    if root_name:
        cypher = (
            "MATCH (rc:RootCategory) "
            "WHERE rc.name = $root_name OR rc.id = $root_name "
            "MATCH (rc)-[:HAS_SUB]->(sc:SubCategory)-[:CONTAINS_TOPIC]->(tp:Topic)-[:INCLUDES]->(q:Question) "
            "MATCH (q)-[:MARKED_AS]->(t:Tag {id: $tag_id}) "
            "OPTIONAL MATCH (q)-[:TESTS]->(kp:KnowledgePoint) "
            "WITH q, t, collect(DISTINCT kp.name) AS knowledge_points "
            "RETURN q.id AS id, q.title AS title, q.content AS content, "
            "       q.choice AS choice, q.type AS type, q.difficulty AS difficulty, "
            "       q.answer AS answer, t.name AS tag_name, "
            "       knowledge_points[0] AS knowledgepoint_name "
            "ORDER BY rand() LIMIT 1"
        )
        params = {"tag_id": tag_id, "root_name": root_name}
    else:
        cypher = (
            "MATCH (t:Tag {id: $tag_id})-[:MARKED_AS]-(q:Question) "
            "OPTIONAL MATCH (q)-[:TESTS]->(kp:KnowledgePoint) "
            "WITH q, t, collect(DISTINCT kp.name) AS knowledge_points "
            "RETURN q.id AS id, q.title AS title, q.content AS content, "
            "       q.choice AS choice, q.type AS type, q.difficulty AS difficulty, "
            "       q.answer AS answer, t.name AS tag_name, "
            "       knowledge_points[0] AS knowledgepoint_name "
            "ORDER BY rand() LIMIT 1"
        )
        params = {"tag_id": tag_id}

    try:
        result = graph.run(cypher, **params).data()
        if not result:
            return None
        row = result[0]
        return {
            "question_id": row.get("id"),
            "title": row.get("title"),
            "content": row.get("content"),
            "choice": row.get("choice") or " ",
            "question_type": row.get("type"),
            "difficulty": row.get("difficulty"),
            "standard_answer": row.get("answer"),
            "tag_name": row.get("tag_name"),
            "knowledgepoint_name": row.get("knowledgepoint_name") or "",
            "question_score": 5.0,
        }
    except Exception as e:
        logger.exception("查询单题失败: %s", e)
        return None


def _get_user_tag_ids(user_id: Any) -> List[str]:
    """
    获取用户在 Neo4j 中关联的 Tag ID 列表
    """
    if graph is None:
        return []
    try:
        try:
            uid = int(user_id)
        except Exception:
            uid = user_id
        cypher = (
            "MATCH (u:User {id: $uid})-[:WEAK_AT]->(t:Tag) "
            "RETURN DISTINCT t.id AS id"
        )
        rows = graph.run(cypher, uid=uid).data()
        return [r["id"] for r in rows if r.get("id")]
    except Exception as e:
        logger.error(f"查询用户关联Tag失败: {str(e)}")
        return []


# 获取指定 RootCategory 下的所有 Question id（用于限制题目来源）
def _get_question_ids_under_root(root_name_or_id: str) -> Set[str]:
    """
    返回属于给定 RootCategory (name 或 id) 下的所有 Question id 的集合
    路径： (RootCategory)-[:HAS_SUB]->(SubCategory)-[:CONTAINS_TOPIC]->(Topic)-[:INCLUDES]->(Question)
    """
    if graph is None:
        return set()
    try:
        cypher = (
            "MATCH (rc:RootCategory) "
            "WHERE rc.name = $root OR rc.id = $root "
            "MATCH (rc)-[:HAS_SUB]->(sc:SubCategory)-[:CONTAINS_TOPIC]->(tp:Topic)-[:INCLUDES]->(q:Question) "
            "RETURN DISTINCT q.id AS qid"
        )
        rows = graph.run(cypher, root=root_name_or_id).data()
        qids = {str(r["qid"]) for r in rows if r.get("qid")}
        logger.info("在 RootCategory(%s) 下查询到 %d 个题目", root_name_or_id, len(qids))
        return qids
    except Exception as e:
        logger.exception("查询 RootCategory 下的题目失败: %s", e)
        return set()


# 用于获取用户与题目的 INTERACTS 交互（用于构建邻接）
def _export_interactions(limit: Optional[int] = None) -> List[Tuple[str, str, float]]:
    """
    返回 [(user_id, question_id, correctness_float), ...]
    correctness: 1.0 or 0.0
    limit: optional cap for rows（便于在大表上做速测）
    """
    if graph is None:
        return []
    try:
        cypher = "MATCH (u:User)-[r:INTERACTS]->(q:Question) RETURN u.id AS uid, q.id AS qid, r.correctness AS correctness"
        if limit:
            cypher += f" LIMIT {limit}"
        rows = graph.run(cypher).data()
        out = []
        for r in rows:
            uid = r.get("uid")
            qid = r.get("qid")
            c = r.get("correctness")
            correctness = 1.0 if c in (True, 1, '1') else 0.0
            out.append((str(uid), str(qid), float(correctness)))
        return out
    except Exception as e:
        logger.exception("导出 interactions 失败: %s", e)
        return []


# 获取 question -> tags 关系 (以及 strength 如果存在)
def _export_question_tags() -> List[Tuple[str, str, float]]:
    if graph is None:
        return []
    try:
        cypher = "MATCH (q:Question)-[r:MARKED_AS]->(t:Tag) RETURN q.id AS qid, t.id AS tid, r.strength AS strength"
        rows = graph.run(cypher).data()
        out = []
        for r in rows:
            qid = str(r.get("qid"))
            tid = str(r.get("tid"))
            s = r.get("strength")
            s_val = float(s) if s is not None else 1.0
            out.append((qid, tid, s_val))
        return out
    except Exception as e:
        logger.exception("导出 question-tags 失败: %s", e)
        return []


# 读取（若存在）节点上的 fastrp_embedding 属性
def _read_fastrp_embeddings_for_label(label: str) -> Dict[str, np.ndarray]:
    """
    读取节点上的 FastRP 向量，自动探测属性名（fastrp_embedding / embedding / fastRPEmbedding）。
    返回 dict: {node_id_str: np.array(embedding)}
    """
    out: Dict[str, np.ndarray] = {}
    if graph is None:
        return out

    # 按优先级探测属性名
    candidate_props = ["fastrp_embedding", "embedding", "fastRPEmbedding", "node2vec_embedding"]
    prop_name: Optional[str] = None
    for prop in candidate_props:
        try:
            probe = graph.run(
                f"MATCH (n:{label}) WHERE n.{prop} IS NOT NULL RETURN count(n) AS cnt LIMIT 1"
            ).data()
            if probe and probe[0].get("cnt", 0) > 0:
                prop_name = prop
                logger.info(f"检测到 {label} 节点使用向量属性: {prop}")
                break
        except Exception:
            continue

    if prop_name is None:
        raise RuntimeError(f"{label} 节点未找到任何已知向量属性")

    try:
        cypher = (
            f"MATCH (n:{label}) WHERE n.{prop_name} IS NOT NULL "
            f"RETURN n.id AS id, n.{prop_name} AS emb"
        )
        rows = graph.run(cypher).data()
        for r in rows:
            nid = r.get("id")
            emb = r.get("emb")
            if nid is not None and emb:
                out[str(nid)] = np.array([float(x) for x in emb], dtype=np.float32)
        logger.info(f"读取 {label} FastRP 向量完成，共 {len(out)} 个节点，属性名={prop_name}")
    except Exception as e:
        logger.warning(f"读取 {label} FastRP 向量失败: {e}")

    return out


# ----------------------------
# 简化 LightGCN 风格传播（无训练，只做传播/聚合）
# ----------------------------
def _build_mappings(interactions: List[Tuple[str, str, float]], qtags: List[Tuple[str, str, float]]):
    """
    返回映射与邻接结构：
    user2idx, q2idx, tag2idx, adj_u_to_q: dict user_idx->[q_idx,...], adj_q_to_u, adj_q_to_t, adj_t_to_q
    只包含出现在 interactions 或 qtags 的节点
    """
    users = set()
    qs = set()
    tags = set()
    for u, q, c in interactions:
        users.add(str(u)); qs.add(str(q))
    for q, t, s in qtags:
        qs.add(str(q)); tags.add(str(t))

    user_list = sorted(list(users))
    q_list = sorted(list(qs))
    tag_list = sorted(list(tags))

    user2idx = {u: i for i, u in enumerate(user_list)}
    q2idx = {q: i for i, q in enumerate(q_list)}
    tag2idx = {t: i for i, t in enumerate(tag_list)}

    adj_u_to_q = {user2idx[u]: [] for u in user_list}
    adj_q_to_u = {q2idx[q]: [] for q in q_list}
    for u, q, c in interactions:
        ui = user2idx[str(u)]; qi = q2idx[str(q)]
        adj_u_to_q[ui].append((qi, float(c)))
        adj_q_to_u[qi].append((ui, float(c)))

    adj_q_to_t = {q2idx[q]: [] for q in q_list}
    adj_t_to_q = {tag2idx[t]: [] for t in tag_list}
    for q, t, s in qtags:
        qi = q2idx[str(q)]; ti = tag2idx[str(t)]
        adj_q_to_t[qi].append((ti, float(s)))
        adj_t_to_q[ti].append(qi)

    return user2idx, q2idx, tag2idx, adj_u_to_q, adj_q_to_u, adj_q_to_t, adj_t_to_q


def _init_embeddings_from_fastrp_or_random(user2idx, q2idx, tag2idx, emb_dim=64):
    """
    尝试读取 Neo4j 的 fastrp_embedding；若不存在则随机初始化。
    返回: user_emb (n_users, dim), q_emb (n_q, dim), tag_emb (n_tag, dim)
    """
    # default random
    n_u = len(user2idx); n_q = len(q2idx); n_t = len(tag2idx)
    user_emb = np.random.normal(scale=0.01, size=(n_u, emb_dim)).astype(np.float32)
    q_emb = np.random.normal(scale=0.01, size=(n_q, emb_dim)).astype(np.float32)
    tag_emb = np.random.normal(scale=0.01, size=(n_t, emb_dim)).astype(np.float32)

    # try load fastrp
    try:
        user_fastrp = _read_fastrp_embeddings_for_label("User")
        q_fastrp = _read_fastrp_embeddings_for_label("Question")
        t_fastrp = _read_fastrp_embeddings_for_label("Tag")
        # If available, map into our index sets (resizing if dim mismatch)
        for uid, idx in user2idx.items():
            if uid in user_fastrp:
                v = user_fastrp[uid]
                if v.shape[0] != emb_dim:
                    # project or pad/truncate
                    if v.shape[0] > emb_dim:
                        v = v[:emb_dim]
                    else:
                        v = np.pad(v, (0, emb_dim - v.shape[0]))
                user_emb[idx] = v.astype(np.float32)
        for qid, idx in q2idx.items():
            if qid in q_fastrp:
                v = q_fastrp[qid]
                if v.shape[0] != emb_dim:
                    if v.shape[0] > emb_dim:
                        v = v[:emb_dim]
                    else:
                        v = np.pad(v, (0, emb_dim - v.shape[0]))
                q_emb[idx] = v.astype(np.float32)
        for tid, idx in tag2idx.items():
            if tid in t_fastrp:
                v = t_fastrp[tid]
                if v.shape[0] != emb_dim:
                    if v.shape[0] > emb_dim:
                        v = v[:emb_dim]
                    else:
                        v = np.pad(v, (0, emb_dim - v.shape[0]))
                tag_emb[idx] = v.astype(np.float32)
        return user_emb, q_emb, tag_emb, True  # True = FastRP loaded
    except Exception as e:
        logger.warning(
            "Neo4j 中未找到 fastrp_embedding 属性，回退到随机初始化。"
            "LightGCN 在随机初始化下效果退化为随机排序，建议提前运行 gds.fastRP.mutate。错误: %s", e
        )

    return user_emb, q_emb, tag_emb, False  # False = random init


def _lightgcn_propagate(user_emb, q_emb, tag_emb,
                        adj_u_to_q, adj_q_to_u, adj_q_to_t, adj_t_to_q,
                        n_layers=2):
    """
    简化版 LightGCN 推理（不训练）：基于初始 embedding 做 n_layers 次均值聚合
    返回 final_user_emb, final_q_emb, final_tag_emb (各自 shape 相同)
    """
    # 存储每层 embedding（layer0 就是初始）
    u_layers = [user_emb.copy()]
    q_layers = [q_emb.copy()]
    t_layers = [tag_emb.copy()]

    for l in range(n_layers):
        # user <- mean of its interacted question embeddings
        new_u = np.zeros_like(user_emb)
        for ui, neighs in adj_u_to_q.items():
            if not neighs:
                new_u[ui] = user_emb[ui]  # fallback to self
                continue
            neigh_idx = [qi for qi, c in neighs]
            new_u[ui] = q_emb[neigh_idx].mean(axis=0)
        # question <- mean(users who interacted, tags associated)
        new_q = np.zeros_like(q_emb)
        for qi, user_neighs in adj_q_to_u.items():
            parts = []
            if user_neighs:
                uidxs = [ui for ui, c in user_neighs]
                parts.append(user_emb[uidxs].mean(axis=0))
            tag_neighs = adj_q_to_t.get(qi, [])
            if tag_neighs:
                tidxs = [ti for ti, s in tag_neighs]
                parts.append(tag_emb[tidxs].mean(axis=0))
            if parts:
                new_q[qi] = np.stack(parts, axis=0).mean(axis=0)
            else:
                new_q[qi] = q_emb[qi]
        # tag <- mean(items under this tag
        new_t = np.zeros_like(tag_emb)
        for ti, q_neighbors in adj_t_to_q.items():
            if q_neighbors:
                new_t[ti] = q_emb[q_neighbors].mean(axis=0)
            else:
                new_t[ti] = tag_emb[ti]
        # append and set current
        u_layers.append(new_u)
        q_layers.append(new_q)
        t_layers.append(new_t)
        # update anchors for next iteration
        user_emb = new_u
        q_emb = new_q
        tag_emb = new_t

    # average across layers
    final_user = np.mean(np.stack(u_layers, axis=1), axis=1)
    final_q = np.mean(np.stack(q_layers, axis=1), axis=1)
    final_t = np.mean(np.stack(t_layers, axis=1), axis=1)
    return final_user, final_q, final_t


# ----------------------------
# 简化 HAN：节点级聚合 + 语义级注意力（3 条元路径）
# ----------------------------
def _compute_user_han_embedding(
    user_idx: int,
    user_init_emb: np.ndarray,
    q_emb: np.ndarray,
    tag_emb: np.ndarray,
    adj_u_to_q: Dict[int, List[Tuple[int, float]]],
    adj_q_to_t: Dict[int, List[Tuple[int, float]]],
    adj_t_to_q: Dict[int, List[int]],
    user_to_weak_tag_ids: List[str],   # list of tag ids (string) for later tag membership checks
    qid_list_from_idx: Dict[int, str],
    tagidx_to_tagid: Dict[int, str],
    user2idx_map: Dict[str, int],
    alpha_cf: float = 0.6,
    alpha_kl: float = 0.3,
    alpha_tagassoc: float = 0.1
) -> np.ndarray:
    """
    构造三条元路径的表示并做语义级注意力融合，返回最终 user embedding vector.
    - path 1 (CF): 聚合用户交互的题目（对 correctness 低的题目加权）
    - path 2 (Knowledge logic): 聚合用户弱标签下的题目
    - path 3 (Tag association): 聚合与弱标签相似/关联的标签下的题目（近似: tags themselves）
    """
    # node-level aggregations -> path embeddings
    dim = user_init_emb.shape[0]

    # Path 1: CF aggregation: weighted mean of interacted q embeddings, weight = (1 - correctness) to focus on weak items
    neighs = adj_u_to_q.get(user_idx, [])
    if neighs:
        weights = np.array([1.0 - c for (_, c) in neighs], dtype=np.float32)
        idxs = np.array([qi for (qi, c) in neighs], dtype=np.int32)
        if weights.sum() > 0:
            weights = weights / weights.sum()
            path1 = (q_emb[idxs] * weights[:, None]).sum(axis=0)
        else:
            path1 = q_emb[idxs].mean(axis=0)
    else:
        path1 = np.zeros(dim, dtype=np.float32)

    # Path 2: Knowledge logic: for each weak tag of the user, aggregate questions under that tag
    # user_to_weak_tag_ids is list of tag ids (string). Map to tagidx
    weak_tag_idxs = []
    for tidx, tid in tagidx_to_tagid.items():
        if tid in user_to_weak_tag_ids:
            weak_tag_idxs.append(tidx)
    if weak_tag_idxs:
        q_idxs = []
        for t in weak_tag_idxs:
            q_idxs.extend(adj_t_to_q.get(t, []))
        q_idxs = list(set(q_idxs))
        if q_idxs:
            path2 = q_emb[q_idxs].mean(axis=0)
        else:
            path2 = np.zeros(dim, dtype=np.float32)
    else:
        path2 = np.zeros(dim, dtype=np.float32)

    # Path 3: Tag association: include neighbor tags (we approximate by tags themselves since SIMILAR_TO may exist)
    # We'll aggregate questions from tags that are in user weak tags and tags that share questions with them.
    assoc_qs = set()
    for t in weak_tag_idxs:
        # questions of this tag
        assoc_qs.update(adj_t_to_q.get(t, []))
        # also include questions of other tags that co-occur with these questions (simple co-occurrence)
        for q in adj_t_to_q.get(t, []):
            # other tags of this q
            other_tags = [ti for ti, _ in adj_q_to_t.get(q, [])] if adj_q_to_t.get(q) else []
            for ot in other_tags:
                assoc_qs.update(adj_t_to_q.get(ot, []))
    if assoc_qs:
        path3 = q_emb[list(assoc_qs)].mean(axis=0)
    else:
        path3 = np.zeros(dim, dtype=np.float32)

    # Put paths into list and compute semantic-level attention weights
    paths = np.stack([path1, path2, path3], axis=0)  # shape (3, dim)
    # For attention score use dot(user_init_emb, path) scaled
    scores = np.dot(paths, user_init_emb)  # (3,)
    # softmax
    maxs = np.max(scores)
    exp = np.exp(scores - maxs)
    alphas = exp / (exp.sum() + 1e-9)  # shape (3,)
    # final user emb as weighted sum of paths
    final = (alphas[0] * paths[0] + alphas[1] * paths[1] + alphas[2] * paths[2])
    # fallback: if final is zero vector, return user_init
    if np.linalg.norm(final) < 1e-8:
        final = user_init_emb
    return final


# ----------------------------
# Main recommend endpoint (替换原逻辑)
# ----------------------------
@router.get("/recommend")
async def recommend_questions(
    userId: str = Query(..., description="用户ID"),
    tagHints: Optional[str] = Query(None, description="逗号分隔的优先tag_id，来自画像priority_tag_ids"),
):
    """
    使用简化 LightGCN + HAN 聚合给用户推荐 Top-20 题目。题目来源限制为 ROOT_CATEGORY_NAME_OR_ID。
    tagHints：画像传入的优先 tag_id（含笔试失败数据），与 WEAK_AT 合并后进行两层 boost。
    回退：若无交互数据，退回到原来的按 WEAK_AT 随机抽题逻辑（但也限定 Root 下题目）。
    """
    try:
        if graph is None:
            raise HTTPException(status_code=500, detail="Neo4j数据库未连接")

        logger.info(f"收到推荐题目请求: userId={userId}, tagHints={'有' if tagHints else '无'}")
        # step0: get user weak tags from Neo4j (WEAK_AT)
        user_tag_ids = _get_user_tag_ids(userId)

        # 合并画像传入的 priority_tag_ids（含笔试失败 tag，是对 WEAK_AT 的补充）
        hint_ids: List[str] = []
        if tagHints:
            hint_ids = [t.strip() for t in tagHints.split(',') if t.strip()]
            existing_set = set(user_tag_ids)
            extra = [t for t in hint_ids if t not in existing_set]
            user_tag_ids = user_tag_ids + extra
            logger.info(f"tagHints 补充 {len(extra)} 个新 tag，合并后共 {len(user_tag_ids)} 个")

        logger.info(f"用户已关联Tag数量（含画像补充）: {len(user_tag_ids)}")

        # step1: determine allowed question ids under the target root category
        allowed_qids = _get_question_ids_under_root(ROOT_CATEGORY_NAME_OR_ID)
        if not allowed_qids:
            logger.warning("未在 RootCategory(%s) 下查询到题目，回退为不做限制", ROOT_CATEGORY_NAME_OR_ID)
            # 若确实查不到题目，可以选择继续但此处我们允许继续但不限制
            # allowed_qids = set()  # 保持空表示不限制
        else:
            logger.info("限制题目来源至 RootCategory(%s)，题目数量=%d", ROOT_CATEGORY_NAME_OR_ID, len(allowed_qids))

        # step2: export interactions and q-tags (限制条数以防大表)
        interactions = _export_interactions(limit=20000)  # 取上限避免超时
        qtags = _export_question_tags()

        # 如果存在 allowed_qids 则过滤 interactions 与 qtags，只保留在该集合内的题目
        if allowed_qids:
            interactions = [it for it in interactions if it[1] in allowed_qids]
            qtags = [qt for qt in qtags if qt[0] in allowed_qids]

        if not interactions:
            # 回退到老逻辑：每个弱 tag 抽 1 题（但限定于指定 root）
            logger.info("用户没有交互数据或被过滤掉，回退到随机按弱标签抽题逻辑（限定 RootCategory）")
            questions = []
            used_tag_ids: Set[str] = set()
            for tag_id in user_tag_ids:
                if len(questions) >= 20:
                    break
                q = _get_one_question_by_tag(tag_id, root_name=ROOT_CATEGORY_NAME_OR_ID)
                if q:
                    questions.append(q); used_tag_ids.add(tag_id)
            if len(questions) < 20:
                for tag_id in DEFAULT_TAG_IDS:
                    if len(questions) >= 20:
                        break
                    if tag_id in used_tag_ids:
                        continue
                    q = _get_one_question_by_tag(tag_id, root_name=ROOT_CATEGORY_NAME_OR_ID)
                    if q:
                        questions.append(q); used_tag_ids.add(tag_id)
            return {"code": 200, "message": "success", "data": {"user_id": userId, "total": len(questions), "questions": questions}}

        # step3: build mappings + adjacency
        user2idx, q2idx, tag2idx, adj_u_to_q, adj_q_to_u, adj_q_to_t, adj_t_to_q = _build_mappings(interactions, qtags)
        logger.info(f"映射 sizes - users:{len(user2idx)} qs:{len(q2idx)} tags:{len(tag2idx)}")

        # if userId not in user2idx -> fallback to random weak tags selection (but limited root)
        if str(userId) not in user2idx:
            logger.info("用户无交互（或未被导出），使用弱标签抽取备选题（限定 RootCategory）")
            questions = []
            used_tag_ids = set()
            for tag_id in user_tag_ids:
                if len(questions) >= 20:
                    break
                q = _get_one_question_by_tag(tag_id, root_name=ROOT_CATEGORY_NAME_OR_ID)
                if q:
                    questions.append(q); used_tag_ids.add(tag_id)
            if len(questions) < 20:
                for tag_id in DEFAULT_TAG_IDS:
                    if len(questions) >= 20:
                        break
                    if tag_id in used_tag_ids:
                        continue
                    q = _get_one_question_by_tag(tag_id, root_name=ROOT_CATEGORY_NAME_OR_ID)
                    if q:
                        questions.append(q); used_tag_ids.add(tag_id)
            return {"code": 200, "message": "success", "data": {"user_id": userId, "total": len(questions), "questions": questions}}

        # step4: init embeddings (try fastrp else random)
        EMB_DIM = 64
        user_emb, q_emb, tag_emb, fastrp_loaded = _init_embeddings_from_fastrp_or_random(user2idx, q2idx, tag2idx, emb_dim=EMB_DIM)
        if not fastrp_loaded:
            logger.warning("LightGCN 使用随机初始化，推荐质量降级。将主要依赖 WEAK_AT 梯度 boost 维持效果。")

        # step5: propagate LightGCN-style to get final embeddings (no heavy training)
        final_user_embs, final_q_embs, final_tag_embs = _lightgcn_propagate(
            user_emb.copy(), q_emb.copy(), tag_emb.copy(),
            adj_u_to_q, adj_q_to_u, adj_q_to_t, adj_t_to_q,
            n_layers=2
        )
        # build reverse maps
        qidx_to_qid = {v: k for k, v in q2idx.items()}
        tagidx_to_tagid = {v: k for k, v in tag2idx.items()}

        # step6: HAN-style aggregation for this user
        uid_idx = user2idx[str(userId)]
        user_init = final_user_embs[uid_idx]
        user_final = _compute_user_han_embedding(
            uid_idx, user_init,
            final_q_embs, final_tag_embs,
            adj_u_to_q, adj_q_to_t, adj_t_to_q,
            user_to_weak_tag_ids=user_tag_ids,
            qid_list_from_idx=qidx_to_qid,
            tagidx_to_tagid=tagidx_to_tagid,
            user2idx_map=user2idx
        )

        # step7: candidate pool = all questions (in our filtered q2idx) excluding those user already interacted with
        interacted_q_idxs = set([qi for (qi, _) in adj_u_to_q.get(uid_idx, [])])
        all_q_idxs = list(range(len(final_q_embs)))
        cand_idxs = [qi for qi in all_q_idxs if qi not in interacted_q_idxs]

        if not cand_idxs:
            logger.info("候选题为空（在限定 RootCategory 后），回退到弱标签逻辑（限定 RootCategory）")
            questions = []
            used_tag_ids: Set[str] = set()
            for tag_id in user_tag_ids:
                if len(questions) >= 20:
                    break
                q = _get_one_question_by_tag(tag_id, root_name=ROOT_CATEGORY_NAME_OR_ID)
                if q:
                    questions.append(q); used_tag_ids.add(tag_id)
            if len(questions) < 20:
                for tag_id in DEFAULT_TAG_IDS:
                    if len(questions) >= 20:
                        break
                    if tag_id in used_tag_ids:
                        continue
                    q = _get_one_question_by_tag(tag_id, root_name=ROOT_CATEGORY_NAME_OR_ID)
                    if q:
                        questions.append(q); used_tag_ids.add(tag_id)
            return {"code": 200, "message": "success", "data": {"user_id": userId, "total": len(questions), "questions": questions}}

        # step8: score candidates by dot product + boost if in weak tag
        uvec = user_final
        qvecs = final_q_embs[cand_idxs]  # (M, dim)
        dots = qvecs.dot(uvec)  # (M,)
        # boost if question has weak tag
        # compute q_idx -> tag ids
        qidx_to_tagids = {}
        for qi, taglist in adj_q_to_t.items():
            qidx_to_tagids[qi] = [tagidx_to_tagid[ti] for (ti, s) in taglist]

        # 第一层 boost（WEAK_AT）：与匹配薄弱 Tag 数量成比例，最大 +0.2
        user_tag_set = set(user_tag_ids)
        boost = []
        for qi in cand_idxs:
            tags_of_q = qidx_to_tagids.get(qi, [])
            match_count = sum(1 for t in tags_of_q if t in user_tag_set)
            boost.append(min(0.2, match_count * 0.07))
        boost = np.array(boost, dtype=np.float32)

        # 第二层 boost（画像 priority tag）：对画像传入 tag 再加成，最大 +0.15
        # hint_ids 含笔试失败 tag，是 WEAK_AT 以外的补充信号
        if hint_ids:
            hint_set = set(hint_ids)
            portrait_boost = []
            for qi in cand_idxs:
                tags_of_q = qidx_to_tagids.get(qi, [])
                portrait_match = sum(1 for t in tags_of_q if t in hint_set)
                portrait_boost.append(min(0.15, portrait_match * 0.05))
            scores = dots + boost + np.array(portrait_boost, dtype=np.float32)
        else:
            scores = dots + boost

        # pick top K
        K = 20
        topk_idx = np.argsort(-scores)[:K]
        selected_q_idxs = [cand_idxs[int(i)] for i in topk_idx]

        # step9: fetch question details by ids (use existing query for single question but better to batch)
        questions = []
        for qi in selected_q_idxs:
            qid = qidx_to_qid[qi]
            # get question detail
            # 请注意这里我们不再额外检查 root，因为候选集已被限制
            cypher = (
                "MATCH (q:Question {id:$qid})-[:MARKED_AS]->(t:Tag) "
                "OPTIONAL MATCH (q)-[:TESTS]->(kp:KnowledgePoint) "
                "RETURN q.id AS id, q.title AS title, q.content AS content, q.choice AS choice, q.type AS type, q.difficulty AS difficulty, q.answer AS answer, collect(DISTINCT t.name) AS tag_names, collect(DISTINCT kp.name)[0] AS kp_name LIMIT 1"
            )
            rows = graph.run(cypher, qid=qid).data()
            if not rows:
                continue
            r = rows[0]
            questions.append({
                "question_id": r.get("id"),
                "title": r.get("title"),
                "content": r.get("content"),
                "choice": r.get("choice") or " ",
                "question_type": r.get("type"),
                "difficulty": r.get("difficulty"),
                "standard_answer": r.get("answer"),
                "tag_names": r.get("tag_names") or [],
                "knowledgepoint_name": r.get("kp_name") or "",
                "score": None
            })

        # if less than K, supplement by default tag random picks (like original) - but restrict to root
        used_q_ids = {q["question_id"] for q in questions if q.get("question_id")}
        if len(questions) < K:
            for tag_id in DEFAULT_TAG_IDS:
                if len(questions) >= K:
                    break
                if tag_id in user_tag_ids:
                    continue
                q = _get_one_question_by_tag(tag_id, root_name=ROOT_CATEGORY_NAME_OR_ID)
                if q and q["question_id"] not in used_q_ids:
                    questions.append(q)
                    used_q_ids.add(q["question_id"])

        logger.info(f"最终推荐题目数量: {len(questions)}")
        return {"code": 200, "message": "success", "data": {"user_id": userId, "total": len(questions), "questions": questions}}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"获取推荐题目失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取推荐题目失败: {str(e)}")