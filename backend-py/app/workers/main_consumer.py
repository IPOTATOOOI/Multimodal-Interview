"""
统一消费者启动器：在单个进程中使用多线程运行所有 RabbitMQ 消费者。

每个线程使用独立的 RabbitMQ 连接，避免线程安全问题。

启动方式：
    cd SWCUP-backend
    python -m app.workers.main_consumer
"""
import asyncio
import json
import os
import sys
import threading
import time
from typing import Optional

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pika
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# 配置日志：同时输出到控制台和文件
logger.add("logs/main_consumer_{time}.log", rotation="500 MB", encoding="utf-8")
logger.add(sys.stderr, level="INFO")

# 定义使用的队列
QUEUES = {
    "evaluation": "interview_evaluation",
    "audio": "audio_transcription",
}

# 音频转写相关
LOW_QUALITY_FALLBACK_TEXT = "音频文件质量差，无法识别"


def create_connection():
    """创建独立的 RabbitMQ 连接（每个线程一个）"""
    try:
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
        return pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    except Exception as e:
        logger.error(f"创建 RabbitMQ 连接失败: {e}")
        raise


# ========== 评估消费者 ==========
# 评估线程专用的持久 event loop，避免每次 asyncio.run() 销毁旧 loop 导致
# AsyncOpenAI/httpx 单例绑定已关闭的 loop 而静默失败。
_eval_loop: Optional[asyncio.AbstractEventLoop] = None


def _sync_evaluate(history_id: int, answer_qa_id: int, question_content: str, answer_content: str) -> dict:
    """用线程持久 event loop 执行评估，保证 AsyncOpenAI 客户端跨消息复用。"""
    return _eval_loop.run_until_complete(
        _async_evaluate(history_id, answer_qa_id, question_content, answer_content)
    )


async def _async_evaluate(history_id: int, answer_qa_id: int, question_content: str, answer_content: str) -> dict:
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
            """UPDATE qa SET evaluation = %s, feedback = %s, reference_a = %s,
               skill = %s, category = %s, answer_rating = %s WHERE qa_id = %s""",
            (
                eval_result.get("evaluation"),
                eval_result.get("feedback"),
                eval_result.get("reference_a", ""),
                eval_result.get("skill", ""),
                eval_result.get("category", ""),
                eval_result.get("answer_rating"),
                answer_qa_id,
            )
        )
        logger.info(f"评估完成并写入数据库: history_id={history_id}, answer_qa_id={answer_qa_id}")
    except Exception as e:
        logger.error(f"写入评估结果失败: {e}")

    return eval_result


def _on_evaluation_message(channel, method, properties, body):
    """处理评估消息"""
    try:
        job = json.loads(body.decode())
        logger.info(f"收到评估任务: history_id={job['history_id']}, answer_qa_id={job['answer_qa_id']}")
        _sync_evaluate(job["history_id"], job["answer_qa_id"], job["question_content"], job["answer_content"])
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"评估任务完成: history_id={job['history_id']}")
    except Exception as e:
        logger.error(f"处理评估任务异常: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_evaluation_consumer():
    """启动评估消费者（独立连接）"""
    global _eval_loop
    logger.info("启动评估消费者...")
    # 建立持久 event loop 并绑定到本线程，供 _sync_evaluate 跨消息复用同一 loop，
    # 避免 AsyncOpenAI/httpx 单例每次被绑定到已销毁的 loop 上。
    _eval_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_eval_loop)
    try:
        connection = create_connection()
        channel = connection.channel()
        channel.queue_declare(queue=QUEUES["evaluation"], durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUES["evaluation"], on_message_callback=_on_evaluation_message)
        logger.info("评估消费者启动成功")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"评估消费者启动失败: {e}")
        if 'connection' in locals():
            connection.close()
    finally:
        _eval_loop.close()


# ========== 音频转写消费者 ==========
def _on_audio_message(channel, method, properties, body):
    """处理音频转写消息"""
    try:
        job = json.loads(body.decode())
        task_id = job["task_id"]
        history_id = job["history_id"]
        file_path = job["file_path"]
        question_qa_id = job.get("question_qa_id")

        logger.info(f"收到音频转写任务: task_id={task_id}, file_path={file_path}")
        
        from app.services.audio.xfyun_transcribe import XunfeiTranscriber
        from app.database.mysql import execute_update

        transcriber = XunfeiTranscriber()
        transcript = ""

        try:
            transcript = transcriber.transcribe_file(file_path)
            logger.info(f"转写成功: task_id={task_id}")
        except Exception as e:
            err_str = str(e)
            is_low_quality = ("failType: 6" in err_str) or ("音频文件质量太差" in err_str)
            if is_low_quality:
                transcript = LOW_QUALITY_FALLBACK_TEXT
                logger.warning(f"低质量音频，使用兜底文本: task_id={task_id}")
            else:
                logger.error(f"转写失败: task_id={task_id}, error={e}")
                raise

        try:
            if question_qa_id:
                execute_update(
                    "UPDATE qa SET answer = %s, speech_rate = %s, clarity = %s, confidence = %s WHERE qa_id = %s",
                    (transcript, None, None, None, question_qa_id)
                )
            logger.info(f"转写结果写入数据库: task_id={task_id}")
        except Exception as e:
            logger.error(f"写入转写结果失败: {e}")
            raise

        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"音频转写任务完成: task_id={task_id}")
    except Exception as e:
        logger.error(f"处理音频转写任务异常: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_audio_consumer():
    """启动音频转写消费者（独立连接）"""
    logger.info("启动音频转写消费者...")
    try:
        connection = create_connection()
        channel = connection.channel()
        channel.queue_declare(queue=QUEUES["audio"], durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUES["audio"], on_message_callback=_on_audio_message)
        logger.info("音频转写消费者启动成功")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"音频转写消费者启动失败: {e}")
        if 'connection' in locals():
            connection.close()


def main():
    """主函数：启动所有消费者"""
    logger.info("========== 统一消费者启动器 ==========")
    
    # 创建消费者线程（每个线程有独立的 RabbitMQ 连接）
    threads = []
    
    # 评估消费者
    eval_thread = threading.Thread(target=start_evaluation_consumer, name="EvaluationConsumer")
    threads.append(eval_thread)
    
    # 音频转写消费者
    audio_thread = threading.Thread(target=start_audio_consumer, name="AudioConsumer")
    threads.append(audio_thread)
    
    # 启动所有线程
    for thread in threads:
        thread.daemon = True
        thread.start()
        logger.info(f"线程启动: {thread.name}")
    
    logger.info("========== 所有消费者已启动 ==========")
    logger.info("按 Ctrl+C 退出")
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到退出信号，正在关闭...")
        logger.info("所有消费者已停止")


if __name__ == "__main__":
    main()