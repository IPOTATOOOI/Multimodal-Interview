from typing import AsyncGenerator, Optional

import httpx
from openai import AsyncOpenAI
from loguru import logger

_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    """
    获取 Qwen（千问）API 客户端。
    """
    global _client
    if _client is None:
        # 通过 pydantic Settings 读取，保证 .env 文件正确加载
        from app.core.config import settings

        api_key: str = settings.QWEN_API_KEY
        base_url: str = settings.QWEN_BASE_URL

        if not api_key:
            logger.error(
                "QWEN_API_KEY 未配置！请在 .env 中填入阿里云 Dashscope API Key。"
            )
            raise RuntimeError("QWEN_API_KEY 未配置")

        logger.info(f"初始化 Qwen 客户端: base_url={base_url}, model={settings.QWEN_MODEL}")

        # 用自定义 httpx 客户端，base_url 在传输层写死，彻底避免 SDK 路由到 OpenAI
        http_client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(120.0),
        )
        _client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client,
        )
    return _client


def _model() -> str:
    from app.core.config import settings
    return settings.QWEN_MODEL


async def call_qwen_api(prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    """非流式调用，返回完整文本（适合 JSON 决策类场景）。"""
    client = _get_client()
    model = _model()
    logger.info(f"Qwen 非流式调用: model={model}, prompt_len={len(prompt)}, max_tokens={max_tokens}")
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        result = resp.choices[0].message.content or ""
        logger.info(f"Qwen 非流式调用完成，返回长度: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Qwen 非流式调用失败: {e}")
        raise


async def call_qwen_api_stream(
    prompt: str, max_tokens: int = 2048, temperature: float = 0.8
) -> AsyncGenerator[str, None]:
    """流式调用，异步生成器，逐 Token yield 文本块。"""
    client = _get_client()
    model = _model()
    logger.info(f"Qwen 流式调用: model={model}, prompt_len={len(prompt)}")
    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        chunk_count = 0
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                chunk_count += 1
                yield delta
        logger.info(f"Qwen 流式调用完成，共 {chunk_count} 个 chunk")
    except Exception as e:
        logger.error(f"Qwen 流式调用失败: {e}")
        raise
