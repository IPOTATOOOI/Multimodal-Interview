import os
import re
import time
import logging
from dotenv import load_dotenv, find_dotenv
import numpy as np
import librosa
import whisper
import pymysql
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import imageio_ffmpeg

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] = os.path.dirname(ffmpeg_exe) + os.pathsep + os.environ.get("PATH", "")

# ----------------------------- 参数设置 -----------------------------
FILLER_WORDS_ZH = {"呃", "嗯", "啊", "这个", "那个", "就是说", "然后"}
FILLER_WORDS_EN = {"um", "uh", "er", "ah", "like", "you know", "i mean", "so"}

# ----------------------------- 数据库配置 -----------------------------
load_dotenv(find_dotenv())

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "swcup"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "swcup"),
    "charset": "utf8mb4"
}

# ----------------------------- 音频分析工具函数 -----------------------------
def count_syllables(word, lang):
    """简单估计一个词的音节数（中文按字数，英文按元音组数）"""
    if lang == "zh":
        return len(word)
    word = word.lower()
    syllables = re.findall(r'[aeiouy]+', word)
    return max(1, len(syllables))

def detect_silence_ratio(y, sr, top_db=25, hop_length=512):
    """能量低于 top_db 的帧占比（停顿比例）"""
    intervals = librosa.effects.split(y, top_db=top_db)
    total_speech = sum(end - start for start, end in intervals)
    total_length = len(y)
    silence_length = total_length - total_speech
    return silence_length / total_length

def extract_f0_stats(y, sr):
    """提取基频变异系数（CV）"""
    f0, voiced_flag, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    if f0 is None or np.sum(voiced_flag) < 5:
        return None, None
    f0_voiced = f0[voiced_flag]
    f0_voiced = f0_voiced[~np.isnan(f0_voiced)]
    if len(f0_voiced) < 5:
        return None, None
    return np.mean(f0_voiced), np.std(f0_voiced) / np.mean(f0_voiced)

# ----------------------------- 核心分析函数 -----------------------------
def analyze_wav(file_path, model):
    """分析单个 wav 文件，返回分析结果字典"""
    y, sr = librosa.load(file_path, sr=16000)
    duration_sec = len(y) / sr
    logger.info(f"分析音频: {file_path}, 时长: {duration_sec:.2f} 秒")

    result = model.transcribe(
        y,
        word_timestamps=True,
        language=None,
        temperature=0.0,
        condition_on_previous_text=False
    )
    detected_lang = result.get("language", "en")
    segments = result["segments"]
    all_words = []
    word_confidences = []
    filler_count = 0

    filler_set = FILLER_WORDS_ZH if detected_lang.startswith("zh") else FILLER_WORDS_EN

    for seg in segments:
        for w in seg.get("words", []):
            word_text = w["word"].strip().lower()
            if not word_text:
                continue
            all_words.append(word_text)
            if "confidence" in w:
                word_confidences.append(w["confidence"])
            if word_text in filler_set:
                filler_count += 1

    total_words = len(all_words)
    if total_words == 0:
        logger.warning("未识别到任何词，跳过该文件。")
        return None

    # 语速 SPM
    total_syllables = sum(count_syllables(w, detected_lang) for w in all_words)
    spm = (total_syllables / duration_sec) * 60

    # 清晰度
    if word_confidences:
        clarity = np.mean(word_confidences) * 100
    else:
        logprobs = [seg.get("avg_logprob", -2.0) for seg in segments]
        if logprobs:
            avg_logprob = np.mean(logprobs)
            clarity = max(0.0, min(100.0, (avg_logprob + 2.5) / 1.5 * 100))
        else:
            clarity = 0.0

    # 自信度
    silence_ratio = detect_silence_ratio(y, sr, top_db=25)
    filler_ratio = filler_count / total_words if total_words else 0
    f0_mean, f0_cv = extract_f0_stats(y, sr)
    if f0_cv is None:
        f0_cv = 0.15
    norm_f0_cv = min(f0_cv / 0.3, 1.0)
    confidence = 100 * (1.0 - (0.4 * silence_ratio + 0.4 * filler_ratio + 0.2 * (1.0 - norm_f0_cv)))
    confidence = max(0.0, min(100.0, confidence))

    logger.info(f"语速: {spm:.1f} SPM, 清晰度: {clarity:.1f}%, 自信度: {confidence:.1f}%")
    return {
        "spm": round(spm, 1),
        "clarity": round(clarity, 1),
        "confidence": round(confidence, 1)
    }

# ----------------------------- 数据库操作 -----------------------------
def get_qa_id_by_seq(history_id, seq, max_retries=10, retry_interval=5):
    """根据 history_id 和音频序号（从1开始），获取对应的 qa_id
       如果记录还未生成，会进行重试，直到找到或达到最大重试次数。
    """
    for attempt in range(max_retries):
        connection = None
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = """
                    SELECT qa_id FROM qa
                    WHERE history_id = %s AND role = 1
                    ORDER BY created_at ASC
                    LIMIT 1 OFFSET %s
                """
                cursor.execute(sql, (history_id, seq - 1))
                row = cursor.fetchone()
                if row:
                    return row[0]
                else:
                    if attempt < max_retries - 1:
                        logger.info(f"未找到 qa 记录 (history_id={history_id}, seq={seq})，{retry_interval}秒后重试 ({attempt+1}/{max_retries})")
                        time.sleep(retry_interval)
                    else:
                        logger.error(f"重试{max_retries}次后仍未找到对应的回答记录: history_id={history_id}, seq={seq}")
                        return None
        except Exception as e:
            logger.error(f"查询 qa_id 失败 (尝试 {attempt+1}): {e}")
            if connection:
                connection.rollback()
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                return None
        finally:
            if connection:
                connection.close()
    return None


def update_qa_in_db(history_id, qa_id, analysis_result):
    """将分析结果更新到 qa 表中（同时匹配 history_id 和 qa_id）"""
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            sql = """
                UPDATE qa
                SET speech_rate = %s,
                    clarity = %s,
                    confidence = %s
                WHERE history_id = %s AND qa_id = %s
            """
            cursor.execute(sql, (
                analysis_result["spm"],
                analysis_result["clarity"],
                analysis_result["confidence"],
                history_id,
                qa_id
            ))
        connection.commit()
        logger.info(f"数据库更新成功: history_id={history_id}, qa_id={qa_id}, 结果={analysis_result}")
    except Exception as e:
        logger.error(f"数据库更新失败: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

# ----------------------------- watchdog 事件处理 -----------------------------
class WavFileHandler(FileSystemEventHandler):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.processed_files = set()  # 避免重复处理同一文件

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if not file_path.lower().endswith(".wav"):
            return
        # 避免重复事件触发
        if file_path in self.processed_files:
            return
        self.processed_files.add(file_path)

        logger.info(f"检测到新音频文件: {file_path}")
        # 等待文件完全写入（简单延迟）
        time.sleep(1)

        # 解析文件名: his-{history_id}-audioid-{seq}.wav
        filename = os.path.basename(file_path)
        match = re.match(r"his-(\d+)-audioid-(\d+)\.wav", filename, re.IGNORECASE)
        if not match:
            logger.error(f"文件名格式不符，无法提取信息: {filename}")
            return
        history_id = int(match.group(1))
        audio_seq = int(match.group(2))  # 序号，从1开始

        # 根据序号查询真正的 qa_id（带重试）
        qa_id = get_qa_id_by_seq(history_id, audio_seq)
        if qa_id is None:
            return

        # 分析音频
        result = analyze_wav(file_path, self.model)
        if result:
            update_qa_in_db(history_id, qa_id, result)

# ----------------------------- 启动监控 -----------------------------
observer = None

def start_monitoring(watch_dir: str, model_size: str = "small"):
    """
    启动 watchdog 监控线程。
    watch_dir: 要监控的文件夹路径，建议使用绝对路径。
    model_size: Whisper 模型大小
    """
    global observer
    if observer is not None:
        logger.warning("监控已经在运行中。")
        return

    model = whisper.load_model(model_size)


    event_handler = WavFileHandler(model)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    logger.info(f"音频分析启动，开始监控目录: {watch_dir}")

def stop_monitoring():
    """停止监控（在应用关闭时调用）"""
    global observer
    if observer:
        observer.stop()
        observer.join()
        observer = None
        logger.info("监控已停止。")
