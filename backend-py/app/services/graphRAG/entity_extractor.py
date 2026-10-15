import requests
import json
from typing import List, Dict, Any
from app.graphRAG.config import settings
from app.graphRAG.models import Entity

class EntityExtractor:
    """实体提取服务类"""

    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.model = settings.QWEN_MODEL

    def extract_entities(self, question: str) -> List[Entity]:
        """
        使用Ollama模型提取用户问题中的实体

        Args:
            question: 用户问题

        Returns:
            List[Entity]: 提取的实体列表
        """

        # 构造实体提取提示词
        prompt = self._build_entity_extraction_prompt(question)

        try:
            # 调用Ollama API
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=180
            )
            response.raise_for_status()

            result = response.json()
            extracted_text = result.get("response", "").strip()

            # 解析模型返回的实体信息
            entities = self._parse_entities(extracted_text)
            return entities

        except Exception as e:
            print(f"实体提取失败: {e}")
            # 失败时返回空列表
            return []

    def _build_entity_extraction_prompt(self, question: str) -> str:
        """构建实体提取提示词"""
        prompt = f"""你是一个信息提取助手，需要从用户的问题中提取出与IT行业面试相关的实体。实体类型包括：
    
       - RootCategory: 根分类，只包含软件开发、考公、国央企
       - SubCategory: 二级分类，只包含专项练习、面试真题、行测、申论、公共基础题、性格测试
       - Topic: 主题，例如：操作系统、SQL
       - Question: 题目，例如：两数之和
       - Tag: 标签，例如：哈希表、并发编程
    
      请将提取到的实体以JSON格式输出，包含一个名为"entities"的列表，列表中的每个元素是一个对象，包含两个字段："type"和"name"。
    
      示例输入："我想问一些关于哈希表的问题，比如两数之和这道题"
      示例输出：
     {{ 
       "entities": [ 
         {{"type": "Tag", "name": "哈希表"}}, 
         {{"type": "Question", "name": "两数之和"}} 
       ] 
     }}
    
      现在，请处理以下用户输入：
      用户输入：{question}"""
        return prompt

    def _parse_entities(self, response_text: str) -> List[Entity]:
        """实体解析方法，只处理/think标签后面的内容"""
        entities = []
        try:
            # 查找/think标签，只处理标签后面的内容
            think_tag = "</think>"
            think_pos = response_text.find(think_tag)
            if think_pos != -1:
                # 提取/think标签后面的内容
                response_text = response_text[think_pos + len(think_tag):].strip()
            
            # 尝试查找JSON边界
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            
            if start == -1 or end == 0:
                print("未找到有效的JSON格式")
                return entities
                
            json_str = response_text[start:end]
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 验证并处理实体数据
            if isinstance(data, dict) and "entities" in data and isinstance(data["entities"], list):
                for entity_data in data["entities"]:
                    if isinstance(entity_data, dict):
                        entity_type = entity_data.get("type")
                        entity_name = entity_data.get("name")
                        
                        if entity_type and entity_name:
                            # 使用text和type参数创建Entity对象（根据models.py中的定义）
                            entity = Entity(text=entity_name, type=entity_type)
                            entities.append(entity)
        except Exception as e:
            print(f"实体解析异常: {str(e)}")
            
        return entities