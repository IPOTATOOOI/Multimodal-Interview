import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse, urlencode
import ssl
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import websocket
from loguru import logger
from app.core.config import settings

# 配置 loguru
logger.add("logs/spark_api_{time}.log", rotation="500 MB", encoding="utf-8")

# 星火大模型配置
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

APPID = os.getenv('APPID', '')
API_KEY = os.getenv('API_KEY', '')
API_SECRET = os.getenv('API_SECRET', '')
SPARK_URL = os.getenv('SPARK_URL', 'wss://spark-api.xf-yun.com/v1/x1')
DOMAIN = os.getenv('DOMAIN', 'x1')


def _is_detailed_log_enabled() -> bool:
    """是否开启详细日志，由代码配置字段控制。"""
    return bool(settings.LLM_DETAILED_LOG)

class Ws_Param:
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                               digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        return self.Spark_url + '?' + urlencode(v)

def on_error(ws, error):
    logger.error(f"WebSocket错误: {error}")

def on_close(ws, one, two):
    logger.info("WebSocket连接关闭")

def on_open(ws):
    logger.info("WebSocket连接已建立")
    thread.start_new_thread(run, (ws,))

def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, domain=ws.domain, question=ws.question))
    logger.debug(f"发送请求数据: {data}")
    ws.send(data)

def on_message(ws, message):
    if _is_detailed_log_enabled():
        logger.debug(f"收到原始消息: {message}")

    # 默认仅做结构化处理，避免输出原始消息
    data = json.loads(message)
    code = data['header']['code']
    ws.last_code = code
    if code != 0:
        ws.api_error = f"星火API错误: code={code}, data={data}"
        logger.error(ws.api_error)
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        text = choices['text'][0]
        
        # 思维链内容仅在详细模式下输出
        if 'reasoning_content' in text and text['reasoning_content']:
            if _is_detailed_log_enabled():
                logger.info(f"思维链内容: {text['reasoning_content']}")
            ws.has_reasoning = True
            ws.isFirstcontent = True

        # 模型正文仅在详细模式下输出
        if 'content' in text and text['content']:
            content = text["content"]
            if _is_detailed_log_enabled():
                if ws.isFirstcontent:
                    logger.info("*******************以上为思维链内容，模型回复内容如下********************")
                logger.info(f"模型回复: {content}")
            ws.answer += content
            ws.content_chunks += 1
            ws.isFirstcontent = False

        if status == 2:
            if not ws.answer:
                logger.warning(
                    f"星火流式响应结束但无正文: chunks={ws.content_chunks}, has_reasoning={ws.has_reasoning}, code={ws.last_code}"
                )
            logger.info(
                f"星火流式响应完成: chunks={ws.content_chunks}, has_reasoning={ws.has_reasoning}, answer_len={len(ws.answer)}"
            )
            ws.close()

def gen_params(appid, domain, question):
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234",
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 1.2,
                "max_tokens": 32768
            }
        },
        "payload": {
            "message": {
                "text": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            }
        }
    }
    return data

def call_spark_api(prompt: str) -> str:
    """
    调用星火大模型API的通用方法
    
    Args:
        prompt: 提示词
        
    Returns:
        str: 模型返回的文本结果
    """
    if _is_detailed_log_enabled():
        logger.info(f"开始调用星火API，提示词: {prompt}")
    else:
        logger.info(f"开始调用星火API，提示词长度: {len(prompt)}")
    wsParam = Ws_Param(APPID, API_KEY, API_SECRET, SPARK_URL)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = APPID
    ws.question = prompt
    ws.domain = DOMAIN
    ws.answer = ""
    ws.isFirstcontent = False
    ws.has_reasoning = False
    ws.content_chunks = 0
    ws.last_code = None
    ws.api_error = None
    
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    if ws.api_error:
        raise RuntimeError(ws.api_error)
    
    if _is_detailed_log_enabled():
        logger.info(f"星火API调用完成，返回结果: {ws.answer}")
    else:
        logger.info(f"星火API调用完成，返回文本长度: {len(ws.answer)}")
    return ws.answer
