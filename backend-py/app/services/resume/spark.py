import json
import requests
import time
import hmac
import base64
import ast
import re
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.core.redis_cache import build_cache_key, fingerprint_text, get_cache_json, set_cache_json

# 加载环境变量
load_dotenv()

class SparkService:
    # 讯飞星火大模型配置
    XUNFEI_SPARK_URL = os.getenv('XUNFEI_SPARK_URL', 'wss://spark-api.xf-yun.com/v1/x1')
    XUNFEI_SPARK_API_KEY = os.getenv('XUNFEI_SPARK_API_KEY', '')
    XUNFEI_SPARK_API_SECRET = os.getenv('XUNFEI_SPARK_API_SECRET', '')
    
    @staticmethod
    def _create_spark_auth_url() -> str:
        """生成星火认证URL"""
        url = SparkService.XUNFEI_SPARK_URL
        # 解析URL
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path
        
        # 生成时间戳
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        # 拼接
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        
        # 使用hmac-sha256算法结合apiSecret对上面的签名原文计算签名信息
        signature_sha = hmac.new(
            SparkService.XUNFEI_SPARK_API_SECRET.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod='sha256'
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')
        
        authorization_origin = f'api_key="{os.getenv("XUNFEI_SPARK_API_KEY", SparkService.XUNFEI_SPARK_API_KEY)}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        # 拼接鉴权参数，生成url
        auth_url = url + "?"
        for key, value in v.items():
            auth_url += f"{key}={value}&"
        
        return auth_url.rstrip('&')

    @staticmethod
    def _prepare_resume_text(text: str, max_chars: int = 12000) -> str:
        """清洗 OCR 文本，减少噪声与长度，从而提高模型解析速度。"""
        cleaned = (text or "").strip()

        # RapidOCR 在部分情况下会返回 tuple 的字符串表示，如: ('a', 'b', ...)
        if cleaned.startswith("(") and cleaned.endswith(")"):
            try:
                parsed = ast.literal_eval(cleaned)
                if isinstance(parsed, (tuple, list)):
                    cleaned = "\n".join(
                        str(item).strip() for item in parsed
                        if str(item).strip()
                    )
            except Exception:
                pass

        cleaned = cleaned.replace("\\n", "\n")
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars]

        return cleaned

    @staticmethod
    async def process_text_to_json(text: str, user_id: str, domain: str, position: str) -> Dict[str, Any]:
        """处理文本并通过星火大模型转换为JSON格式"""
        headers = {
            'Authorization': f'Bearer {SparkService.XUNFEI_SPARK_API_KEY}',  # APIpassword
            'Content-Type': 'application/json'
        }

        prepared_text = SparkService._prepare_resume_text(text)
        cache_key = build_cache_key(
            "resume",
            "spark",
            user_id,
            domain,
            position,
            fingerprint_text(prepared_text),
        )

        cached_result = await get_cache_json(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 构建提示词，要求模型将文本转换为JSON
        messages = [
            {
                "role": "system",
                "content": "你是简历结构化提取引擎。只做信息抽取与归类，不做解释。输出必须是单个合法 JSON 对象。"
            },
            {
                "role": "user",
                "content": f"""
请从下面简历原文提取字段，返回且仅返回 JSON：

固定字段（中文键名，缺失用 null 或 []）：
- 姓名: string|null
- 年龄: integer|null
- 学校: string|null
- 专业: string|null
- 毕业年份: integer|null（四位年份）
- 技能列表: string[]（去重，保留技术名词）
- 项目经历: string[]（每项一句话，优先含动作+结果）
- 实习经历: string[]（每项一句话，优先含岗位+职责）

抽取规则：
1) 严禁编造；不确定就置空。
2) 忽略宣传性词语和无关符号。
3) 仅输出 JSON，不要 Markdown，不要说明文字。

岗位上下文：domain={domain}; position={position}

简历原文：
{prepared_text}
""".strip()
            }
        ]

        body = {
            "model": "x1",
            "user": "resume_parser",
            "messages": messages,
            "stream": False,
            "functions": [
                {
                    "name": "parse_resume",
                    "description": "Parse resume text into structured JSON format",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "姓名": {"type": "string", "description": "姓名"},
                            "年龄": {"type": "integer", "description": "年龄"},
                            "学校": {"type": "string", "description": "学校"},
                            "专业": {"type": "string", "description": "专业"},
                            "毕业年份": {"type": "integer", "description": "毕业年份"},
                            "技能列表": {"type": "array", "items": {"type": "string"}, "description": "技能列表"},
                            "项目经历": {"type": "array", "items": {"type": "string"}, "description": "项目经历"},
                            "实习经历": {"type": "array", "items": {"type": "string"}, "description": "实习经历"}
                        },
                        "required": ["姓名", "技能列表", "项目经历", "实习经历"]
                    }
                }
            ],
            "temperature": 0,  # 进一步降低随机性，减少生成开销
            "disable_search": True,  # 禁用搜索
            "disable_reasoning": True  # 禁用推理过程
        }

        try:
            response = requests.post(
                url=os.getenv('XUNFEI_SPARK_COMPLETIONS_URL', 'https://spark-api-open.xf-yun.com/v2/chat/completions'),
                json=body,
                headers=headers,
                timeout=35
            )
            
            if response.status_code != 200:
                return {"error": f"星火API请求失败: {response.text}"}

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # 尝试解析JSON
                try:
                    # 查找第一个 { 和最后一个 } 之间的内容
                    json_str = content[content.find('{'):content.rfind('}')+1]
                    parsed_data = json.loads(json_str)
                    
                    # 调用数据库存储逻辑
                    from app.services.resume.db import ResumeDatabaseService
                    db_result = ResumeDatabaseService.save_structured_data(parsed_data, user_id, domain, position)
                    
                    if "error" in db_result:
                        return {"error": db_result["error"]}
                    else:
                        response_data = {
                            "success": "数据已成功存储到数据库",
                            "resume_id": db_result.get("resume_id"),
                            "structured_data": parsed_data,
                        }
                        await set_cache_json(
                            cache_key,
                            response_data,
                            ttl=settings.REDIS_CACHE_RESUME_RESULT_TTL,
                        )
                        return response_data
                        
                except json.JSONDecodeError:
                    return {
                        "error": "无法解析为JSON格式",
                        "raw_text": content
                    }
            else:
                return {"error": "星火响应格式不正确"}
                
        except Exception as e:
            return {"error": str(e)}
