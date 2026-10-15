// 给Neo4j知识图谱中的所有节点添加user_id属性
// 注意：这里假设所有节点都应该属于系统用户（user_id = 0）
// 您可以根据实际需求修改user_id的值

// 1. 给所有现有节点添加user_id属性（默认值为0，表示系统节点）
MATCH (n)
WHERE n.user_id IS NULL
SET n.user_id = 0
RETURN count(n) as nodes_updated;

// 2. 查看更新结果
MATCH (n)
RETURN labels(n) as node_labels, count(n) as count, 
       collect(DISTINCT n.user_id) as user_ids
ORDER BY count DESC;

// 3. 如果需要给特定标签的节点设置不同的user_id，可以这样做：
// 例如：给User节点设置user_id为节点本身的id
MATCH (u:User)
WHERE u.id IS NOT NULL
SET u.user_id = toInteger(u.id)
RETURN count(u) as user_nodes_updated;

// 4. 给Question节点设置user_id（假设为1）
MATCH (q:Question)
SET q.user_id = 1
RETURN count(q) as question_nodes_updated;

// 5. 给Topic节点设置user_id（假设为1）
MATCH (t:Topic)
SET t.user_id = 1
RETURN count(t) as topic_nodes_updated;

// 6. 给Tag节点设置user_id（假设为1）
MATCH (tag:Tag)
SET tag.user_id = 1
RETURN count(tag) as tag_nodes_updated;

// 7. 给Media节点设置user_id（假设为1）
MATCH (m:Media)
SET m.user_id = 1
RETURN count(m) as media_nodes_updated;

// 8. 给SubCategory节点设置user_id（假设为1）
MATCH (s:SubCategory)
SET s.user_id = 1
RETURN count(s) as subcategory_nodes_updated;

// 9. 验证所有节点都有user_id属性
MATCH (n)
WHERE n.user_id IS NULL
RETURN count(n) as nodes_without_user_id;

// 10. 查看最终的统计信息
MATCH (n)
RETURN 
    labels(n)[0] as node_type,
    count(n) as total_count,
    collect(DISTINCT n.user_id) as user_ids,
    min(n.user_id) as min_user_id,
    max(n.user_id) as max_user_id
ORDER BY total_count DESC;
