import json
import os
from loguru import logger

QUEUE_NAME = "interview_evaluation"


async def publish_evaluation_job(
    history_id: int,
    answer_qa_id: int,
    question_content: str,
    answer_content: str,
) -> bool:
    """
    向 RabbitMQ 发布单题评估任务。
    失败时返回 False，调用方应降级到 FastAPI BackgroundTasks。
    """
    try:
        import aio_pika

        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
        conn = await aio_pika.connect_robust(rabbitmq_url)
        async with conn:
            channel = await conn.channel()
            await channel.declare_queue(QUEUE_NAME, durable=True)
            payload = json.dumps(
                {
                    "history_id": history_id,
                    "answer_qa_id": answer_qa_id,
                    "question_content": question_content,
                    "answer_content": answer_content,
                },
                ensure_ascii=False,
            ).encode()
            msg = aio_pika.Message(
                body=payload,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await channel.default_exchange.publish(msg, routing_key=QUEUE_NAME)
            logger.info(f"评估任务已投递 RabbitMQ: answer_qa_id={answer_qa_id}, history_id={history_id}")
            return True
    except ImportError:
        logger.warning("aio-pika 未安装，跳过 RabbitMQ 投递")
        return False
    except Exception as e:
        logger.warning(f"RabbitMQ 投递失败，将降级到 BackgroundTask: {e}")
        return False
