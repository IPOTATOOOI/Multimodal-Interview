"""
语音转写 Worker：独立进程，消费 RabbitMQ 中的语音转写任务，
调用讯飞 API 完成转写并将结果写入 qa 表。

启动方式：
    cd SWCUP-backend
    python -m app.workers.audio_transcription_consumer
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pika
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

logger.add("logs/audio_worker_{time}.log", rotation="500 MB", encoding="utf-8")

QUEUE_NAME = "audio_transcription"
LOW_QUALITY_FALLBACK_TEXT = "音频文件质量差，无法识别"


def _sync_transcribe(task_id: str, history_id: int, file_path: str, question_qa_id: int) -> None:
    """在同步上下文中执行讯飞转写，然后写库。"""
    from app.services.audio.xfyun_transcribe import XunfeiTranscriber
    from app.database.mysql import execute_insert, execute_query
    from datetime import datetime

    transcriber = XunfeiTranscriber()
    transcript = ""

    try:
        transcript = transcriber.transcribe_file(file_path)
        logger.info(f"转写成功: task_id={task_id}, file_path={file_path}")
    except Exception as e:
        err_str = str(e)
        is_low_quality = ("failType: 6" in err_str) or ("音频文件质量太差" in err_str)

        if is_low_quality:
            transcript = LOW_QUALITY_FALLBACK_TEXT
            logger.warning(
                f"检测到低质量音频，使用兜底文本: task_id={task_id}, text={transcript}"
            )
        else:
            logger.error(f"转写失败: task_id={task_id}, error={e}")
            raise

    # 保存转写文本
    file_id = os.path.splitext(os.path.basename(file_path))[0]
    txt_path = os.path.join(os.path.dirname(file_path), f"{file_id}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    logger.info(f"转写文本已保存: {txt_path}")

    # 写入qa表
    try:
        count_query = "SELECT COUNT(*) AS answer_count FROM qa WHERE history_id = %s AND role = 1"
        count_result = execute_query(count_query, (history_id,))
        answer_count = int(count_result[0].get("answer_count", 0)) if count_result else 0
        answer_index = answer_count + 1

        insert_query = """
        INSERT INTO qa (history_id, role, content, created_at, key_words)
        VALUES (%s, %s, %s, %s, %s)
        """
        key_words = f"qid:{question_qa_id}" if question_qa_id else None
        params = (history_id, 1, transcript, datetime.now(), key_words)
        execute_insert(insert_query, params)
        logger.info(f"转写文本已存入qa表: task_id={task_id}, answer_index={answer_index}")
    except Exception as e:
        logger.error(f"写库失败: task_id={task_id}, error={e}")
        raise


def _on_message(channel, method, properties, body):
    try:
        job = json.loads(body.decode())
        task_id = job["task_id"]
        history_id = job["history_id"]
        file_path = job["file_path"]
        question_qa_id = job.get("question_qa_id")

        logger.info(f"收到转写任务: task_id={task_id}, file_path={file_path}")
        _sync_transcribe(task_id, history_id, file_path, question_qa_id)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"任务处理完成: task_id={task_id}")
    except Exception as e:
        logger.error(f"处理转写任务异常，消息将被 nack 重新入队: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
    logger.info(f"语音转写 Worker 启动，连接 RabbitMQ: {rabbitmq_url}")

    params = pika.URLParameters(rabbitmq_url)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=_on_message)

    logger.info(f"等待转写任务（队列: {QUEUE_NAME}）... 按 Ctrl+C 停止")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Worker 收到停止信号，正在退出...")
        channel.stop_consuming()
    finally:
        conn.close()


if __name__ == "__main__":
    main()