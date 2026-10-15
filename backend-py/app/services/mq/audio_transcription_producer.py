import json
import os
from loguru import logger

QUEUE_NAME = "audio_transcription"


async def publish_audio_transcription_job(
    task_id: str,
    history_id: int,
    file_path: str,
    question_qa_id: int,
) -> bool:
    """
    向 RabbitMQ 发布语音转写任务。

    Args:
        task_id: 任务唯一标识
        history_id: 面试历史ID
        file_path: 音频文件路径
        question_qa_id: 关联的问题qa_id

    Returns:
        bool: 投递成功返回True，失败返回False
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
                    "task_id": task_id,
                    "history_id": history_id,
                    "file_path": file_path,
                    "question_qa_id": question_qa_id,
                },
                ensure_ascii=False,
            ).encode()
            msg = aio_pika.Message(
                body=payload,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await channel.default_exchange.publish(msg, routing_key=QUEUE_NAME)
            logger.info(f"语音转写任务已投递 RabbitMQ: task_id={task_id}, file_path={file_path}")
            return True
    except ImportError:
        logger.warning("aio-pika 未安装，跳过 RabbitMQ 投递")
        return False
    except Exception as e:
        logger.warning(f"RabbitMQ 投递失败: {e}")
        return False