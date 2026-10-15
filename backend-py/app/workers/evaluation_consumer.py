"""
评估 Worker：独立进程，消费 RabbitMQ 中的单题评估任务，
调用 Qwen API 完成评估并将结果写入 qa 表。

启动方式：
    cd SWCUP-backend
    python -m app.workers.evaluation_consumer
"""
import asyncio
import json
import os
import sys

# 确保项目根目录在 Python 路径中（直接运行时需要）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pika
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

logger.add("logs/evaluation_worker_{time}.log", rotation="500 MB", encoding="utf-8")

QUEUE_NAME = "interview_evaluation"


def _sync_evaluate(history_id: int, answer_qa_id: int, question_content: str, answer_content: str) -> dict:
    """在独立 asyncio 事件循环中执行异步 Qwen 评估，然后写库。"""
    return asyncio.run(_async_evaluate(history_id, answer_qa_id, question_content, answer_content))


async def _async_evaluate(
    history_id: int, answer_qa_id: int, question_content: str, answer_content: str
) -> dict:
    from app.services.AI.qwen_api import call_qwen_api
    from app.services.interview.interactive_interview import _build_single_eval_prompt
    from app.services.interview.interview_end import _parse_with_repair
    from app.database.mysql import execute_update

    prompt = _build_single_eval_prompt(question_content, answer_content)
    try:
        raw = await call_qwen_api(prompt, max_tokens=1024, temperature=0.5)
        eval_result = _parse_with_repair(raw, history_id)
    except Exception as e:
        logger.error(f"Qwen 评估调用失败: history_id={history_id}, answer_qa_id={answer_qa_id}, error={e}")
        eval_result = {
            "evaluation": "评估失败",
            "feedback": "请重新尝试",
            "reference_a": "",
            "skill": "",
            "category": "",
            "answer_rating": None,
        }

    try:
        execute_update(
            """UPDATE qa SET evaluation=%s, feedback=%s, reference_a=%s,
                              skill=%s, category=%s, answer_rating=%s
               WHERE qa_id=%s""",
            (
                eval_result.get("evaluation"),
                eval_result.get("feedback"),
                eval_result.get("reference_a", ""),
                eval_result.get("skill", ""),
                eval_result.get("category", ""),
                eval_result.get("answer_rating"),
                answer_qa_id,
            ),
        )
        logger.info(
            f"评估结果已写库: answer_qa_id={answer_qa_id}, rating={eval_result.get('answer_rating')}"
        )
    except Exception as e:
        logger.error(f"评估结果写库失败: answer_qa_id={answer_qa_id}, error={e}")

    return eval_result


def _on_message(channel, method, properties, body):
    try:
        job = json.loads(body.decode())
        history_id = job["history_id"]
        answer_qa_id = job["answer_qa_id"]
        question_content = job["question_content"]
        answer_content = job["answer_content"]

        logger.info(f"收到评估任务: history_id={history_id}, answer_qa_id={answer_qa_id}")
        _sync_evaluate(history_id, answer_qa_id, question_content, answer_content)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"任务处理完成: answer_qa_id={answer_qa_id}")
    except Exception as e:
        logger.error(f"处理评估任务异常，消息将被 nack 重新入队: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
    logger.info(f"评估 Worker 启动，连接 RabbitMQ: {rabbitmq_url}")

    params = pika.URLParameters(rabbitmq_url)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=_on_message)

    logger.info(f"等待评估任务（队列: {QUEUE_NAME}）... 按 Ctrl+C 停止")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Worker 收到停止信号，正在退出...")
        channel.stop_consuming()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
