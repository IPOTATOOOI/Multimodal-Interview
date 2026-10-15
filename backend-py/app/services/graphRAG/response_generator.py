import requests
import json
from typing import List, Dict, Any
from app.graphRAG.config import settings
from app.graphRAG.models import RetrievedNode

class ResponseGenerator:
    """回答生成服务类"""

    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.model = settings.QWEN_MODEL

    def generate_response(self, question: str, retrieved_nodes: List[RetrievedNode]) -> str:
        """
        基于检索到的信息生成回答

        Args:
            question: 用户问题
            retrieved_nodes: 检索到的节点信息

        Returns:
            str: 生成的回答
        """

        # 构建提示词
        prompt = self._build_response_prompt(question, retrieved_nodes)

        try:
            with requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.3,  # 降低随机性，保持回答一致性
                        "top_p": 0.9
                    }
                },
                timeout=180,
                stream=True
            ) as response:
                response.raise_for_status()

                # 逐步读取流式响应
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            # 解析每一行的 JSON 数据
                            data = json.loads(line)
                            chunk = data.get("response", "").strip()
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            print(f"解析流式响应失败: {line}")
                            continue

        except requests.exceptions.ConnectionError as e:
            self.ollama_available = False
            self.last_error = str(e)
            print(f"Ollama服务连接失败: {e}")
            yield "抱歉，无法连接到Ollama服务。请确认Ollama服务已启动，并检查网络连接和配置。"
        except requests.exceptions.Timeout as e:
            print(f"Ollama服务请求超时: {e}")
            yield "抱歉，回答生成超时。请稍后再试或简化问题。"
        except requests.exceptions.HTTPError as e:
            print(f"Ollama服务返回错误: {e}")
            if response.status_code == 500:
                yield "抱歉，Ollama服务内部错误。可能是模型加载失败或服务异常，请检查Ollama服务状态。"
            else:
                yield f"抱歉，回答生成失败。错误码: {response.status_code}"
        except Exception as e:
            print(f"回答生成失败: {e}")
            yield "抱歉，我暂时无法回答这个数学领域的问题。请稍后再试或尝试重新提问。"

    def _build_response_prompt(self, question: str, retrieved_nodes: List[RetrievedNode]) -> str:
        """构建回答生成提示词"""

        # 格式化检索到的信息
        context_info = self._format_retrieved_nodes(retrieved_nodes)

        prompt = f"""
        你是一个专业的问答助手，基于以下检索到的知识图谱信息来回答用户的问题。
        
        # 检索到的相关信息：
        {context_info}
        
        # 用户问题：
        {question}
        
        # 回答要求：
        1. 基于检索到的信息进行回答，不要编造不存在的信息
        2. 如果信息充分，提供详细、准确的回答
        3. 如果信息不充分，可以基于已有知识进行合理推断，但要说明哪些是推断内容
        4. 回答要专业、清晰、有条理
        5. 如果涉及题目，可以提供解题思路和答案
        6. 使用中文回答
        
        请直接给出回答，不要提及"根据检索到的信息"等前缀。
        """

        return prompt

    def _format_retrieved_nodes(self, nodes: List[RetrievedNode]) -> str:
        """格式化检索到的节点信息"""

        if not nodes:
            return "未检索到相关信息"

        formatted_info = []
        for i, node in enumerate(nodes, 1):
            node_info = f"{i}. 节点类型: {node.node_type}\n"
            node_info += f"   相似度: {node.similarity_score:.2f}\n"

            content = node.content
            # 根据不同节点类型格式化内容
            if "name" in content:
                node_info += f"   名称: {content.get('name', '')}\n"
            if "text" in content:
                text_content = content.get('text', '')
                if len(text_content) > 200:
                    text_content = text_content[:200] + "..."
                node_info += f"   内容: {text_content}\n"
            if "type" in content:
                node_info += f"   类型: {content.get('type', '')}\n"
            if "description" in content:
                desc = content.get('description', '')
                if len(desc) > 150:
                    desc = desc[:150] + "..."
                node_info += f"   描述: {desc}\n"
            if node.neighbors:
                node_info += "   邻居节点:\n"
                for neighbor in node.neighbors:  
                    node_info += f"     - [{neighbor['type']}] {neighbor['properties'].get('name', 'N/A')}\n"
            
            # 添加关系信息
            if node.relationships:
                node_info += "   关系:\n"
                for rel in node.relationships:  # 限制显示前3个关系
                    node_info += f"     - {rel['type']}\n"

            formatted_info.append(node_info)
        return "\n".join(formatted_info)

    def _clean_response(self, response: str) -> str:
        """清理回答内容"""

        # 移除可能的多余前缀
        prefixes = ["回答：", "答案：", "根据以上信息，", "基于检索到的信息，"]
        for prefix in prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        return response