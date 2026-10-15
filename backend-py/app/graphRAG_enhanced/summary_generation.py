
from app.graphRAG_enhanced.graph_operations import Neo4jGraphOperations
import asyncio
import logging
from collections import Counter
import re

logger = logging.getLogger(__name__)

class SummaryGenerator:
    def __init__(self):
        self.graph_ops = Neo4jGraphOperations()

    def generate_all_community_summaries(self, user_id: int = None):
        """为所有社区生成摘要，并支持用户隔离"""
        community_counts = self.graph_ops.get_community_nodes_count()

        print(f"开始为 {len(community_counts)} 个社区生成摘要...")

        summaries_generated = 0
        for community_id, node_count in community_counts.items():
            print(f"处理社区 {community_id} (包含 {node_count} 个节点)")
            summary, keywords = self._generate_single_community_summary(community_id, user_id=user_id)

            if summary:
                self.graph_ops.store_community_summary(community_id, summary, keywords)
                print(f"社区 {community_id} 摘要生成完成")
                summaries_generated += 1
            else:
                print(f"社区 {community_id} 摘要生成失败")

        return summaries_generated

    def _generate_single_community_summary(self, community_id, user_id: int = None):
        """为单个社区生成摘要，并支持用户隔离"""
        # 获取社区子图数据
        subgraph_data = self.graph_ops.get_community_subgraph(community_id, user_id=user_id)
        community_stats = self.graph_ops.get_community_statistics(community_id)

        if not subgraph_data:
            return None, []

        # 分析社区结构
        community_info = self._analyze_community_structure(subgraph_data, community_stats)

        # 构建提示词
        prompt = self._build_summary_prompt(community_info)

        # 调用LLM生成摘要
        summary = self._call_llm_for_summary(prompt)

        # 提取关键词
        keywords = self._extract_keywords(community_info)

        return summary, keywords
    
    def _analyze_community_structure(self, subgraph_data, community_stats):
        """分析社区结构 - 适配您的数据结构"""
        nodes_info = {
            "root_categories": set(),
            "sub_categories": set(),
            "topics": set(),
            "questions": set(),
            "tags": set(),
            "users": set()
        }

        relationship_types = set()
        node_names = {}

        for record in subgraph_data:
            node_name = record["node_name"]
            node_labels = record["node_labels"]
            related_node_name = record["related_node_name"]
            rel_type = record["relationship_type"]

            # 记录节点信息
            if node_name:
                node_names[node_name] = node_labels
                self._categorize_node(nodes_info, node_labels, node_name)

            if related_node_name:
                node_names[related_node_name] = record["related_node_labels"]
                self._categorize_node(nodes_info, record["related_node_labels"], related_node_name)

            if rel_type:
                relationship_types.add(rel_type)

        # 提取主题关键词
        topic_keywords = self._extract_topic_keywords(list(nodes_info["topics"]))

        return {
            "statistics": {
                "root_categories": community_stats["root_categories"],
                "sub_categories": community_stats["sub_categories"],
                "topics": community_stats["topics"],
                "questions": community_stats["questions"],
                "tags": community_stats["tags"],
                "users": community_stats["users"]
            },
            "relationship_types": list(relationship_types),
            "sample_nodes": {
                "root_categories": list(nodes_info["root_categories"])[:5],
                "sub_categories": list(nodes_info["sub_categories"])[:5],
                "topics": list(nodes_info["topics"])[:10],
                "tags": list(nodes_info["tags"])[:10]
            },
            "topic_keywords": topic_keywords
        }

    def _categorize_node(self, nodes_info, labels, node_name):
        """根据节点标签分类节点"""
        if "RootCategory" in labels:
            nodes_info["root_categories"].add(node_name)
        elif "SubCategory" in labels:
            nodes_info["sub_categories"].add(node_name)
        elif "Topic" in labels:
            nodes_info["topics"].add(node_name)
        elif "Question" in labels:
            nodes_info["questions"].add(node_name)
        elif "Tag" in labels:
            nodes_info["tags"].add(node_name)
        elif "User" in labels:
            nodes_info["users"].add(node_name)

    def _extract_topic_keywords(self, topics):
        """从主题名称中提取关键词"""
        if not topics:
            return []

        # 简单的关键词提取：按常见分隔符分割
        all_words = []
        for topic in topics:
            # 移除特殊字符，按空格/斜杠/横杠分割
            words = re.split(r'[\s\/\-]', topic)
            # 过滤空字符串和短词
            words = [word.strip() for word in words if len(word.strip()) > 1]
            all_words.extend(words)

        # 统计词频
        word_freq = Counter(all_words)
        # 返回出现次数最多的10个词
        return [word for word, count in word_freq.most_common(10)]

    def _build_summary_prompt(self, community_info):
        """构建LLM提示词 - 适配您的学习题库场景"""
        stats = community_info["statistics"]
        sample_nodes = community_info["sample_nodes"]
        topic_keywords = community_info["topic_keywords"]

        prompt = f"""你是一个专业的教育知识图谱分析师。请基于以下知识图谱社区信息，生成一个专业、准确的摘要：

社区统计信息：
- 根分类数量: {stats['root_categories']}
- 二级分类数量: {stats['sub_categories']}
- 主题数量: {stats['topics']}
- 题目数量: {stats['questions']}
- 标签数量: {stats['tags']}
- 关联用户数量: {stats['users']}

社区主题关键词: {', '.join(topic_keywords)}

社区中的关系类型: {', '.join(community_info['relationship_types'])}

代表性内容示例：
- 根分类: {', '.join(sample_nodes['root_categories'])}
- 二级分类: {', '.join(sample_nodes['sub_categories'])}
- 主要主题: {', '.join(sample_nodes['topics'])}
- 相关标签: {', '.join(sample_nodes['tags'])}

请用1句话总结这个知识社区的核心特点，描述社区主要涵盖的知识领域和学习主题

摘要应该精炼准确
"""
        return prompt

    def _call_llm_for_summary(self, prompt):
        """调用 Qwen API 生成摘要"""
        try:
            from app.services.AI.qwen_api import call_qwen_api
            result = asyncio.run(call_qwen_api(prompt, max_tokens=256, temperature=0.3))
            if "</think>" in result:
                result = result.split("</think>", 1)[1].strip()
            return result
        except Exception as e:
            logger.error(f"Qwen 摘要生成失败: {str(e)}")
            return f"摘要生成失败: {str(e)}"

    def _extract_keywords(self, community_info):
        """从社区信息中提取关键词"""
        keywords = []

        # 添加主题关键词
        keywords.extend(community_info["topic_keywords"])

        # 添加分类关键词
        keywords.extend(community_info["sample_nodes"]["root_categories"])
        keywords.extend(community_info["sample_nodes"]["sub_categories"])

        # 去重并限制数量
        return list(set(keywords))