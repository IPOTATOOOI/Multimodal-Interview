import os
import base64
import logging
from openai import OpenAI

ZHIPU_BASE_URL = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
MODEL = os.getenv("ZHIPU_MODEL", "glm-4v-flash")

client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL) if ZHIPU_API_KEY else None
logger = logging.getLogger(__name__)


def analyze_expression_and_gesture(history_id: int, img_dir: str) -> tuple[str, str]:
    """
    分析指定 history_id 对应的面试截图（取前3张），返回 (expression_evaluation, gesture_evaluation)
    :param img_dir: 图片存放目录绝对路径，例如 "facial_landmarks/img"
    """
    if client is None:
        logger.warning("ZHIPU_API_KEY is not configured; image evaluation is disabled")
        return "", ""

    if not os.path.isdir(img_dir):
        logger.warning(f"Image directory not found: {img_dir}")
        return "", ""

    # 查找所有 his-{history_id}-img-*.jpg 文件
    files = [
        f for f in os.listdir(img_dir)
        if f.startswith(f"his-{history_id}-img-") and f.endswith(".jpg")
    ]
    if not files:
        logger.warning(f"No images found for history_id={history_id} in {img_dir}")
        return "", ""

    # 按文件名排序，取前3张
    files.sort()
    selected_files = files[:3]
    logger.info(f"Analyzing {len(selected_files)} image(s): {selected_files}")

    # 读取所有图片并转为 base64
    image_b64_list = []
    for fname in selected_files:
        img_path = os.path.join(img_dir, fname)
        with open(img_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        image_b64_list.append(img_b64)

    # 构造 prompt（多图综合评价）
    prompt = (
        f"你是一位专业的面试官，这是同一场面试过程中截取的{len(selected_files)}张连续截图。请仔细观察这些图片，"
        "结合多帧信息综合给出以下两个维度的评价，输出中文，每个维度2-3句话，不要使用编号列表：\n"
        "1. 表情神态评价：评价面部表情的自然度、情感传递、亲和力、微表情的变化等。\n"
        "2. 肢体动作评价：评价手势、姿态的开放度、自信度、动作幅度是否得体、是否有不自然的小动作等。\n"
        "请严格按照格式输出，先输出“表情神态评价：”后接内容，换行后输出“肢体动作评价：”后接内容，"
        "不要添加任何额外的标题或解释，在评价时要称图中人物为'面试者'。"
    )

    # 构建消息内容：第一项为文本，后续每一项为图片
    content = [{"type": "text", "text": prompt}]
    for img_b64 in image_b64_list:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
        })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": content}],
            max_tokens=600,
            temperature=0.3,
        )
        result_text = response.choices[0].message.content
        logger.info(f"GLM-4V response: {result_text}")
    except Exception as e:
        logger.exception(f"GLM-4V request failed: {e}")
        return "", ""

    # 解析返回文本（与之前相同的逻辑）
    expression_eval = ""
    gesture_eval = ""
    if "表情神态评价：" in result_text:
        parts = result_text.split("肢体动作评价：")
        if len(parts) >= 1:
            expression_eval = parts[0].replace("表情神态评价：", "").strip()
        if len(parts) >= 2:
            gesture_eval = parts[1].strip()
    else:
        blocks = [b.strip() for b in result_text.split("\n\n") if b.strip()]
        if len(blocks) >= 2:
            expression_eval = blocks[0]
            gesture_eval = blocks[1]
        else:
            expression_eval = result_text

    return expression_eval, gesture_eval
