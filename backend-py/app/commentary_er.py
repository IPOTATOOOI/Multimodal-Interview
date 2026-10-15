# commentary_er.py
import re
import time
import pymysql
from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ========== 数据库配置 ==========
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "swcup"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "swcup"),
    "charset": "utf8mb4",
}

BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
API_KEY = os.getenv('QWEN_API_KEY', '')
MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
client = OpenAI(api_key=API_KEY, base_url=BASE_URL) if API_KEY else None


# 全局变量，记录已处理的最大 qa_id
last_processed_id = 0


def annotate_answer(answer: str) -> str:
    """调用大模型对面试回答进行批注，返回带符号的原文本"""
    if client is None:
        raise RuntimeError("QWEN_API_KEY is not configured")
    system_prompt = """你是一位资深的面试官，正在对候选人的面试回答进行书面批注。
    当前是面试场景，你需要基于通用面试评估标准（如专业准确性、逻辑结构、表达清晰度、优势亮点、失误与纰漏）对候选人的回答直接在原文上增加标记。

    批注规则（严格遵守）：
    1. 绝对不添加、删除或改写任何原始回答的文字，只能插入以下四种批注符号。
       绝对不能重复复制原文中的任何连续片段，原文中的每个字只应在输出中出现一次。
    2. 符号定义：
       - 将回答中正确、专业、有亮点的词或短句用 /+ 具体文本内容 +/ 包裹。
       - 将回答中有误、不专业、表述存在纰漏的词或短句用 /- 具体文本内容 -/ 包裹。
       - 在值得肯定之处，插入 ✅（括号内写正向批语，例如“逻辑清晰”“重点突出”）。
       - 在出现问题之处，插入 ❗（括号内写负面批语，例如“概念混淆”“回答不完整”）。
    3. 符号必须成对出现：每个 /+ 必须与一个 +/ 配对，每个 /- 必须与一个 -/ 配对。禁止出现孤立的 /- 或 -/。
    4. 批注要精准，不要全文都进行批注！只在必要处批注！符号紧贴被评价的词句，批语要简洁、一针见血，符合面试评估的视角。
    5. 输出必须是带批注的原回答，不附加任何解释、寒暄或额外内容。

    示例：
    回答：RESTful API 是一种基于 HTTP 协议的设计风格，它只能用在 Web 系统里，移动端用不了。
    正确输出：
    /+RESTful API 是一种基于 HTTP 协议的设计风格+/✅（定义准确），/-它只能用在 Web 系统里，移动端用不了-/❗（说法过于绝对，移动端也可用 RESTful API）。
    """

    user_prompt = f"候选人回答：{answer}\n请直接在原文上进行批注："

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=2048,
        temperature=0.1,
        top_p=0.8
    )

    annotated = response.choices[0].message.content.strip()

    # 将批注符号 ✅ 和 ❗ 后的英文半角括号替换为中文全角括号，不影响原文其他部分
    # 匹配 ✅ 或 ❗，可选空格，然后 (批语内容)
    annotated = re.sub(
        r'([✅❗])\s*\(([^()]*)\)',
        r'\1（\2）',
        annotated
    )

    return annotated




def init_last_processed_id():
    """初始化：获取表中当前最大 qa_id，确保只处理启动后的新数据"""
    global last_processed_id
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(qa_id) FROM qa")
            result = cursor.fetchone()
            last_processed_id = result[0] if result[0] else 0
        print(f"监视器初始化：当前最大 qa_id = {last_processed_id}，将只处理此后的新增回答。")
    finally:
        conn.close()


def process_unannotated():
    """查询并处理新增的未批注回答"""
    global last_processed_id
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            sql_select = """
                SELECT qa_id, content FROM qa
                WHERE role = 1 AND annotation_status IS NULL AND qa_id > %s
                ORDER BY qa_id ASC
                LIMIT 10
            """
            cursor.execute(sql_select, (last_processed_id,))
            rows = cursor.fetchall()
            if not rows:
                return

            for qa_id, original_content in rows:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 处理 qa_id={qa_id} ...")
                try:
                    annotated = annotate_answer(original_content)
                    sql_update = """
                        UPDATE qa
                        SET content = %s, annotation_status = 'annotated'
                        WHERE qa_id = %s
                    """
                    cursor.execute(sql_update, (annotated, qa_id))
                    conn.commit()
                    last_processed_id = max(last_processed_id, qa_id)
                    print(f"  qa_id={qa_id} 批注成功")
                except Exception as e:
                    print(f"  qa_id={qa_id} 批注失败：{e}")
                    conn.rollback()
    finally:
        conn.close()


def run_monitor():
    """监视器主循环，应在后台线程中运行"""
    init_last_processed_id()
    print("QA 表监视器已启动（仅处理新增回答）")
    while True:
        try:
            process_unannotated()
        except Exception as e:
            print(f"监视器异常：{e}")
        time.sleep(5)
