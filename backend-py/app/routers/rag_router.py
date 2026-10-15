import chromadb
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import logging
import json
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger("rag_router")

DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 初始化客户端 (使用正确的 API 地址)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
client = OpenAI(api_key=OPENAI_API_KEY, base_url=DASHSCOPE_BASE_URL) if OPENAI_API_KEY else None


# 初始化Chroma向量数据库客户端
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

chroma_client = chromadb.PersistentClient(path=os.getenv('VECTOR_DB_PATH', 'vecDB/SW_vector_db'))
collection = chroma_client.get_or_create_collection(name="legal_documents")

similarity_search = "vecDB/paraphrase-multilingual-MiniLM-L12-v2"


SYSTEM_PROMPT = """
你是一个面试助手，能为用户解答面试问题。
你可以在知识库中检索知识。
用户输入问题后，你来解答用户的问题。

你的输出必须严格遵循以下格式，不允许任何偏差：

知识库检索增强：
{这里放置从知识库中检索到的相关内容，用一段文字描述。如果知识库无直接内容，可简要说明或写“未检索到相关增强内容”。}

AI解答：
{这里放置你对用户问题的具体回答，必须用一段连续的文本输出，禁止使用列表、分点、编号或换行符。回答应连贯、完整，像一段散文。}

重要提示：
- 输出必须包含“知识库检索增强”和“AI解答”两部分，且顺序不可改变。
- AI解答部分必须是一段文字（即一个段落），不能分段或使用项目符号。如果内容较多，用连接词串联成整体。
- 知识库检索增强部分也应保持简洁，避免列表。

下面是应用场景第一个举例：
用户问：Java异常类有哪些？
你输出:
知识库检索增强：
异常主要就是Exception，Error。Exception主要就是运行时异常和检查时异常，为了保证代码的正常运行，我们需要主动使用try/catch进行捕获，常见的就是IoEception，SQLExceptinon。Error主要就是就是发生在运行时的异常，就比如：oom，threadDeath

AI解答：
Java中的异常类主要分为Exception和Error两大类别。Exception包括运行时异常和检查时异常，例如空指针异常或IO异常，这些异常需要程序员通过try-catch块主动处理以确保代码健壮性；而Error如内存溢出错误，通常表示严重系统问题，程序无法简单恢复。异常处理是Java编程的核心概念，有助于提升应用程序的可靠性。

下面是应用场景第二个举例：
用户问：redis底层数据结构
你输出:
知识库检索增强：
String类型的底层使用动态字符串实现的。List类型的底层使用双向链表+压缩数组实现的。set类型的底层使用哈希表+数组整数数组实现的。hash类型的底层使用压缩数组+哈希表实现的。zset类型的底层使用压缩数组+跳表实现的。

AI解答：
Redis的底层数据结构根据数据类型的不同而多样化，例如String类型使用动态字符串来实现高效修改，List类型结合双向链表和压缩数组以平衡内存和性能，Set类型依赖哈希表或整数数组来优化集合操作，Hash类型采用压缩数组和哈希表组合以适应不同数据规模，而Zset类型则通过压缩数组和跳表结构支持有序数据的高效查询。这些设计共同提升了Redis在处理各种数据场景时的速度和灵活性。

下面是应用场景第三个举例：
用户问：java的流有哪些
你输出:
知识库检索增强：
从方向方面，主要就是输入流和输出流。从单位方面，主要就是分为字节流和字符流。字节流主要就是InputStream，OutputStream。字符流主要就是Reader，Writer。

AI解答：
Java中的流体系按数据流向可分为输入流和输出流，按处理单位则分为字节流和字符流两大类；其中字节流通过InputStream和OutputStream实现原始字节数据的高效传输，而字符流则借助Reader和Writer提供字符级操作并自动处理字符编码问题，这种分层设计使得Java能够灵活应对不同场景下的I/O处理需求。
"""


def retrieve_documents(query, norm_type, n_results=1):
    where_filter = {"type": norm_type} if norm_type else None

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter
    )

    # 格式化检索结果
    retrieved_docs = []
    for i in range(len(results['documents'][0])):
        doc_id = results['ids'][0][i]
        doc_content = results['documents'][0][i]
        doc_metadata = results['metadatas'][0][i]

        # 格式化元数据
        meta_str = []

        retrieved_docs.append({
            "id": doc_id,
            "content": doc_content,
            "metadata": ", ".join(meta_str),
            "distance": results['distances'][0][i]
        })

    return retrieved_docs


def retrieve_similar_questions(self, user_question, top_k):
    """核心：检索相似问题"""
    query_vector = chroma_client

    results = self.vector_db.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    # 映射到对应的答案
    qa_pairs = []
    for match in results.matches:
        qa_pairs.append({
            'retrieved_question': match.metadata['question'],
            'mapped_answer': match.metadata['answer'],  # 关键映射！
            'similarity': match.score
        })

    return qa_pairs


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


def RAG_agent(text: str) -> str:
    """RAG 代理函数，处理用户查询"""
    if client is None:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text}
    ]

    try:
        response = client.chat.completions.create(
            model="qwen-max",
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            stream=True
        )

        def generate():
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield json.dumps({"content": chunk.choices[0].delta.content})

        return generate()
    except Exception as e:
        logger.error(f"RAG Agent Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI 服务错误: {str(e)}"
        )


# 创建路由
router = APIRouter()


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """处理聊天请求"""
    try:
        return StreamingResponse(
            RAG_agent(request.message),
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Endpoint Error: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")
