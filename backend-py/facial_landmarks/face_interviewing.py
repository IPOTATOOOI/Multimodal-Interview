# 直接运行

import cv2
import dlib
import numpy as np
import math
import json
import asyncio
import websockets
import logging
from collections import deque
import time
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('behavior_analysis.log')
    ]
)
logger = logging.getLogger("BehaviorAnalysis")

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "shape_predictor_68_face_landmarks.dat")

# 初始化dlib的人脸检测器和关键点检测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)

# 3D模型点（用于头部姿态估计）
model_points = np.array([
    (0.0, 0.0, 0.0),  # 鼻尖
    (0.0, -330.0, -65.0),  # 下巴
    (-225.0, 170.0, -135.0),  # 左眼左角
    (225.0, 170.0, -135.0),  # 右眼右角
    (-150.0, -150.0, -125.0),  # 左嘴角
    (150.0, -150.0, -125.0)  # 右嘴角
], dtype=np.float64)


# 眼睛纵横比(EAR)计算函数
def eye_aspect_ratio(eye_points):
    # 计算两组垂直方向的欧氏距离
    A = np.linalg.norm(eye_points[1] - eye_points[5])
    B = np.linalg.norm(eye_points[2] - eye_points[4])

    # 计算水平方向的欧氏距离
    C = np.linalg.norm(eye_points[0] - eye_points[3])

    # 计算EAR
    ear = (A + B) / (2.0 * C)
    return ear


# 从旋转矩阵获取欧拉角
def get_euler_angles(rotation_vector):
    # 计算旋转矩阵
    R, _ = cv2.Rodrigues(rotation_vector)

    # 计算欧拉角
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.degrees(x), np.degrees(y), np.degrees(z)


# 计算肩膀角度
def calculate_shoulder_angle(pose_points):
    if len(pose_points) < 2:
        return 0

    left_shoulder = pose_points[0]
    right_shoulder = pose_points[1]

    # 计算肩膀连线的角度（相对于水平线）
    dx = right_shoulder[0] - left_shoulder[0]
    dy = right_shoulder[1] - left_shoulder[1]
    angle = math.degrees(math.atan2(dy, dx))

    return angle


# 改进的微笑强度计算 - 增加灵敏度
def calculate_smile_intensity(mouth_points, prev_mouth_center=None):
    # 计算嘴部特征点
    left_corner = mouth_points[0]
    right_corner = mouth_points[6]
    top_lip_center = mouth_points[2]
    bottom_lip_center = mouth_points[8]

    # 计算嘴部宽度
    mouth_width = np.linalg.norm(left_corner - right_corner)

    # 计算嘴部高度（上唇到嘴角的高度和下唇到嘴角的高度）
    top_left_height = np.linalg.norm(top_lip_center - left_corner)
    top_right_height = np.linalg.norm(top_lip_center - right_corner)
    bottom_left_height = np.linalg.norm(bottom_lip_center - left_corner)
    bottom_right_height = np.linalg.norm(bottom_lip_center - right_corner)

    # 平均高度
    mouth_height = (top_left_height + top_right_height + bottom_left_height + bottom_right_height) / 4.0

    # 计算嘴角的扬起程度
    # 当微笑时，嘴角会向上扬起
    mouth_center = (top_lip_center + bottom_lip_center) / 2.0

    # 如果提供了上一帧的口型中心点，计算嘴角运动
    mouth_movement = 0
    if prev_mouth_center is not None:
        mouth_movement = np.linalg.norm(mouth_center - prev_mouth_center)

    # 计算微笑强度 (基于宽度和高度)
    # 使用对数函数来提高小变化的敏感性
    ratio = max(0.1, mouth_width / max(0.1, mouth_height))  # 避免除以0
    base_intensity = math.log(1 + max(0, ratio - 1.2)) * 60  # 提高自然状态下微笑检测的敏感性

    # 增加嘴角运动影响
    movement_factor = min(1.0, mouth_movement * 10)

    # 综合微笑强度
    smile_intensity = min(100, max(0, base_intensity * (1 + movement_factor * 0.5)))

    return smile_intensity, mouth_center


# 专注度分析
def calculate_attention_score(yaw, pitch):
    # 综合计算头部偏转的影响
    angle_score = max(50, 100 - 1.5 * (abs(yaw) + abs(pitch)))
    return min(100, angle_score)


# 计算面部占图像的比例（距离估计）
def calculate_face_ratio(face_rect, image_size):
    # 计算面部区域占整个图像的比例
    face_width_ratio = face_rect.width() / image_size[1]
    face_height_ratio = face_rect.height() / image_size[0]

    # 使用平均值作为整体比例
    face_ratio = (face_width_ratio + face_height_ratio) / 2

    # 转换为更直观的距离评分
    # 理想范围：0.25-0.35（太小=太远，太大=太近）
    if face_ratio < 0.15:
        return 30, "离屏幕太远"
    elif face_ratio < 0.20:
        return 60, "略远于理想距离"
    elif face_ratio < 0.25:
        return 80, "接近理想距离"
    elif face_ratio <= 0.35:
        return 100, "理想距离"
    elif face_ratio <= 0.40:
        return 80, "接近理想距离"
    elif face_ratio <= 0.50:
        return 60, "略近于理想距离"
    else:
        return 30, "离屏幕太近"


# 改进的面试行为分析器（维护状态）
class BehaviorAnalyzer:
    def __init__(self):
        self.prev_rotation_vector = None
        self.head_movement_history = deque(maxlen=15)
        self.eye_contact_history = deque(maxlen=15)
        self.smile_history = deque(maxlen=15)
        self.smile_intensity_history = deque(maxlen=15)  # 新增微笑强度历史记录
        self.attention_history = deque(maxlen=20)
        self.distance_history = deque(maxlen=15)  # 存储距离比例值
        self.prev_mouth_center = None  # 记录上一帧的嘴部中心点
        self.smiling_threshold = 30  # 微笑状态阈值 (降低阈值以提高灵敏度)

    def update_state(self, rotation_vector, ear, eye_deviation, smile_intensity, attention_score, face_ratio):
        # 更新头部运动状态
        if self.prev_rotation_vector is not None:
            movement = np.linalg.norm(rotation_vector - self.prev_rotation_vector)
            self.head_movement_history.append(movement)
        self.prev_rotation_vector = rotation_vector.copy()

        # 更新眼神接触状态
        self.eye_contact_history.append(1 if eye_deviation < 0.2 and ear > 0.2 else 0)

        # 更新微笑状态 - 使用较低的阈值提高灵敏度
        self.smile_history.append(smile_intensity > self.smiling_threshold)
        self.smile_intensity_history.append(smile_intensity)

        # 更新专注状态
        self.attention_history.append(attention_score > 75)

        # 更新距离状态
        self.distance_history.append(face_ratio)

    def get_head_stability(self):
        if len(self.head_movement_history) < 5:
            return 80  # 默认值

        # 计算头部运动的稳定性（方差越小越稳定）
        movement_std = np.std(self.head_movement_history)
        stability = max(50, 100 - movement_std * 25)
        return stability

    def get_eye_contact_consistency(self):
        if not self.eye_contact_history:
            return 75  # 默认值

        # 计算眼神接触一致性的百分比
        good_contact_frames = sum(self.eye_contact_history)
        return min(100, int(good_contact_frames / len(self.eye_contact_history) * 100))

    def get_smile_frequency(self):
        if not self.smile_history:
            return 30  # 默认值降低以提高敏感性

        # 计算微笑频率的百分比
        smiling_frames = sum(self.smile_history)
        return min(100, int(smiling_frames / len(self.smile_history) * 100))

    def get_average_smile_intensity(self):
        if not self.smile_intensity_history:
            return 25  # 默认值降低以提高敏感性

        # 计算平均微笑强度
        return np.mean(self.smile_intensity_history)

    def get_attention_consistency(self):
        if not self.attention_history:
            return 75  # 默认值

        # 计算专注度一致性的百分比
        attentive_frames = sum(self.attention_history)
        return min(100, int(attentive_frames / len(self.attention_history) * 100))

    def get_distance_consistency(self):
        if not self.distance_history:
            return "未知"

        # 计算平均距离比例
        avg_ratio = np.mean(self.distance_history)
        if avg_ratio < 0.25:
            return "通常偏远"
        elif avg_ratio < 0.30:
            return "经常保持良好距离"
        elif avg_ratio <= 0.35:
            return "稳定保持理想距离"
        elif avg_ratio <= 0.40:
            return "经常保持良好距离"
        else:
            return "通常偏近"


# 分析行为并返回结果
def analyze_behavior(image, analyzer=None):
    try:
        # 转换为灰度图
        if image is None or image.size == 0:
            return default_result("无效图像")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_size = image.shape[:2]  # 获取(height, width)

        # 检测人脸
        faces = detector(gray)
        if len(faces) == 0:
            return default_result("未检测到人脸")

        # 取最大的人脸
        face = max(faces, key=lambda rect: rect.width() * rect.height())

        # 检测关键点
        shape = predictor(gray, face)
        shape_points = np.array([[p.x, p.y] for p in shape.parts()])

        # 提取需要的6个点（用于头部姿态估计）
        image_points = np.array([
            shape_points[30],  # 鼻尖
            shape_points[8],  # 下巴
            shape_points[36],  # 左眼左角
            shape_points[45],  # 右眼右角
            shape_points[48],  # 左嘴角
            shape_points[54]  # 右嘴角
        ], dtype=np.float64)

        # 初始化相机矩阵（假设没有畸变）
        size = image.shape
        focal_length = size[1]
        center = (size[1] / 2, size[0] / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1))  # 假设没有镜头畸变

        # 使用solvePnP求解头部姿态
        _, rotation_vector, _ = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        # 获取欧拉角
        pitch, yaw, roll = get_euler_angles(rotation_vector)

        # 1. 表情分析（基于头部偏航角和微笑）
        expression_score = max(50, 100 - 1.8 * min(35, abs(yaw)))

        # 2. 眼神接触分析
        # 提取眼睛关键点
        left_eye = shape_points[36:42]
        right_eye = shape_points[42:48]

        # 计算眼睛纵横比
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        # 眼睛注视方向分析
        left_eye_center = np.mean(left_eye, axis=0)
        right_eye_center = np.mean(right_eye, axis=0)
        eye_center = (left_eye_center + right_eye_center) / 2

        # 计算眼睛中心与图像中心的偏差
        image_center = np.array([size[1] / 2, size[0] / 2])
        deviation = np.linalg.norm(eye_center - image_center)
        max_deviation = math.sqrt((size[1] / 2) ** 2 + (size[0] / 2) ** 2)
        deviation_ratio = min(1.0, deviation / max_deviation)  # 限制在0-1之间

        # 眼神接触得分（基于偏差和眼睛张开程度）
        eye_contact_score = max(0, min(100, 100 - 50 * deviation_ratio)) if ear > 0.2 else 30

        # 3. 姿态分析（基于肩膀角度）
        # 假设肩膀位置
        left_shoulder = shape_points[2]  # 左眉毛外侧
        right_shoulder = shape_points[14]  # 右眉毛外侧

        # 计算肩膀角度
        shoulder_angle = calculate_shoulder_angle([left_shoulder, right_shoulder])
        pose_score = max(50, 100 - 1.5 * min(40, abs(shoulder_angle)))

        # 4. 微笑分析 - 使用改进的函数
        mouth_points = shape_points[48:68]
        prev_mouth_center = analyzer.prev_mouth_center if analyzer else None
        smile_intensity, mouth_center = calculate_smile_intensity(mouth_points, prev_mouth_center)

        # 5. 专注度分析
        attention_score = calculate_attention_score(yaw, pitch)

        # 6. 屏幕距离分析
        # 计算面部占图像的比例作为距离估计
        face_ratio = (face.width() / size[1] + face.height() / size[0]) / 2.0
        distance_score, distance_status = calculate_face_ratio(face, size)

        # 7. 状态更新和多帧分析
        head_stability_score = 80
        eye_consistency_score = 75
        smile_frequency = 30  # 默认值降低以提高敏感性
        average_smile_intensity = 25  # 默认值降低以提高敏感性
        attention_consistency = 75
        distance_consistency = "未知"

        if analyzer is not None:
            # 保存当前帧的嘴部中心供下一帧使用
            analyzer.prev_mouth_center = mouth_center

            analyzer.update_state(
                rotation_vector,
                ear,
                deviation_ratio,
                smile_intensity,
                attention_score,
                face_ratio
            )
            head_stability_score = analyzer.get_head_stability()
            eye_consistency_score = analyzer.get_eye_contact_consistency()
            smile_frequency = analyzer.get_smile_frequency()
            attention_consistency = analyzer.get_attention_consistency()
            distance_consistency = analyzer.get_distance_consistency()
            average_smile_intensity = analyzer.get_average_smile_intensity()

        # 8. 自信心和专业度分析
        # 自信心 = 姿态(40%) + 微笑(30%) + 头部稳定性(30%)
        # 使用平均微笑强度而不是当前帧的强度
        confidence_score = int(
            0.4 * pose_score +
            0.3 * average_smile_intensity +
            0.3 * head_stability_score
        )

        # 专业度 = 眼神接触(40%) + 专注度(30%) + 头部稳定性(30%)
        professionalism_score = int(
            0.4 * eye_contact_score +
            0.3 * attention_score +
            0.3 * head_stability_score
        )

        # 9. 面试综合评分 - 增加距离权重
        interview_score = int((
                expression_score * 0.15 +
                eye_contact_score * 0.20 +
                pose_score * 0.15 +
                distance_score * 0.10 +  # 增加距离权重
                confidence_score * 0.20 +
                professionalism_score * 0.20
        ))

        # 10. 生成反馈
        feedbacks = []

        # 表情反馈
        if abs(yaw) > 90:
            feedbacks.append({
                "message": "头偏角度过大，请正视前方",
                "level": "warning"
            })
        elif abs(yaw) < 5:
            feedbacks.append({
                "message": "表情自然，眼神聚焦",
                "level": "positive"
            })
        else:
            feedbacks.append({
                "message": "基本保持正视，可进一步优化",
                "level": "suggestion"
            })

        # 眼神接触反馈
        if ear < 0.2:
            feedbacks.append({
                "message": "请保持双眼睁开",
                "level": "critical"
            })
        elif deviation_ratio > 0.3:
            feedbacks.append({
                "message": "眼神聚焦不足，视线需保持在屏幕中心区域",
                "level": "warning"
            })
        elif analyzer and eye_consistency_score < 60:
            feedbacks.append({
                "message": "眼神交流不稳定，请保持持续的眼神接触",
                "level": "suggestion"
            })
        else:
            feedbacks.append({
                "message": "眼神交流自然，与面试官保持良好互动",
                "level": "positive"
            })

        # 姿态反馈
        if abs(shoulder_angle) > 15:
            feedbacks.append({
                "message": "肩部不平衡，请放松并保持对称姿势",
                "level": "warning"  # 修复了这里的错误
            })
        elif abs(shoulder_angle) > 8:
            feedbacks.append({
                "message": "姿态基本端正，可进一步放松肩部",
                "level": "suggestion"
            })
        else:
            feedbacks.append({
                "message": "姿态自信大方，展现专业形象",
                "level": "positive"
            })

        # 微笑和自信反馈 - 使用更敏感的判断条件
        # 新增条件：即使当前帧没有微笑，但整体微笑频率低且平均强度低，也要提示
        if smile_frequency < 30 and average_smile_intensity < 30:
            # 判断是否需要微笑反馈，如果平均强度很低且频率低，说明一直很严肃
            feedbacks.append({
                "message": "表情较严肃，请适当微笑展现亲和力",
                "level": "suggestion"
            })
        elif analyzer and confidence_score < 70:
            feedbacks.append({
                "message": "自信表现不足，请保持自然微笑和开放姿态",
                "level": "suggestion"
            })
        elif analyzer and confidence_score > 85:
            feedbacks.append({
                "message": "自信表达自然，给人积极印象",
                "level": "positive"
            })
        elif smile_intensity < 25:
            # 如果当前帧微笑强度很低，直接提示表情严肃
            feedbacks.append({
                "message": "当前表情较严肃，可展现适度微笑",
                "level": "suggestion"
            })

        # 距离反馈
        if distance_score <= 60 and analyzer and distance_consistency in ["通常偏远", "通常偏近"]:
            feedbacks.append({
                "message": f"您当前{distance_status}，{distance_consistency}，建议调整摄像头距离",
                "level": "warning"
            })
        elif distance_score <= 80:
            feedbacks.append({
                "message": f"您当前{distance_status}，建议稍作调整",
                "level": "suggestion"
            })
        elif distance_score >= 90:
            feedbacks.append({
                "message": f"您当前{distance_status}，非常合适",
                "level": "positive"
            })

        # 添加面试整体表现反馈
        if interview_score >= 90:
            feedbacks.append({
                "message": "面试表现优异：专业度与自信俱佳",
                "level": "excellent"
            })
        elif interview_score >= 80:
            feedbacks.append({
                "message": "面试表现良好：整体专业形象佳",
                "level": "positive"
            })
        elif interview_score >= 70:
            feedbacks.append({
                "message": "面试表现合格：部分细节待提升",
                "level": "neutral"
            })
        else:
            feedbacks.append({
                "message": "面试需改进：重点关注眼神交流和姿态",
                "level": "improvement"
            })

        # 返回所有指标和分析结果
        return {
            "expression": int(expression_score),
            "eyeContact": int(eye_contact_score),
            "pose": int(pose_score),
            "distance": int(distance_score),  # 新增距离评分
            "smileIntensity": int(smile_intensity),
            "smileFrequency": int(smile_frequency),  # 新增微笑频率指标
            "averageSmileIntensity": int(average_smile_intensity),  # 新增平均微笑强度
            "attention": int(attention_score),
            "headStability": int(head_stability_score),
            "eyeConsistency": int(eye_consistency_score),
            "confidence": int(confidence_score),
            "professionalism": int(professionalism_score),
            "interview": int(interview_score),
            "feedbacks": feedbacks
        }

    except Exception as e:
        logger.error(f"分析行为时出错: {str(e)}", exc_info=True)
        return default_result("分析错误")


def default_result(reason):
    return {
        "expression": 0,
        "eyeContact": 0,
        "pose": 0,
        "distance": 0,
        "smileIntensity": 0,
        "smileFrequency": 0,
        "averageSmileIntensity": 0,
        "attention": 0,
        "headStability": 0,
        "eyeConsistency": 0,
        "confidence": 0,
        "professionalism": 0,
        "interview": 0,
        "feedbacks": [{"message": reason, "level": "critical"}]
    }


# 图像处理队列
class FrameProcessor:
    def __init__(self, max_fps=5):
        self.max_fps = max_fps
        self.last_processed = 0
        self.frame_queue = deque()
        self.processing = False
        self.analyzer = BehaviorAnalyzer()  # 为每个连接创建行为分析器

    async def add_frame(self, frame_data):
        """添加帧到处理队列"""
        self.frame_queue.append(frame_data)
        if not self.processing:
            asyncio.create_task(self.process_queue())

    async def process_queue(self):
        """处理队列中的帧"""
        self.processing = True
        try:
            while self.frame_queue:
                now = time.time()
                if now - self.last_processed < 1.0 / self.max_fps:
                    await asyncio.sleep(0.01)
                    continue

                frame_data = self.frame_queue.popleft()
                result = analyze_behavior(frame_data, self.analyzer)
                self.last_processed = now
                return result
        finally:
            self.processing = False


# WebSocket服务器处理函数
async def behavior_analysis(websocket):
    logger.info("客户端已连接")
    frame_processor = FrameProcessor(max_fps=5)
    config = None

    try:
        # 处理消息循环
        async for message in websocket:
            # 文本消息（配置）
            if isinstance(message, str):
                try:
                    config = json.loads(message)
                    logger.info(f"收到配置: {config}")

                    # 发送确认
                    await websocket.send(json.dumps({
                        "type": "config_ack",
                        "status": "success",
                        "message": "配置已接收"
                    }))
                except json.JSONDecodeError:
                    logger.warning("收到无效的JSON配置")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "无效的JSON配置"
                    }))

            # 二进制消息（图像帧）
            elif isinstance(message, bytes):
                try:
                    # 解码图像
                    nparr = np.frombuffer(message, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if img is None or img.size == 0:
                        logger.warning("收到无效图像数据")
                        continue

                    # 添加帧到处理队列
                    await frame_processor.add_frame(img)
                    result = await frame_processor.process_queue()

                    if result:
                        # 发送分析结果
                        response = json.dumps({
                            "type": "metrics",
                            "expression": result["expression"],
                            "eyeContact": result["eyeContact"],
                            "pose": result["pose"],
                            "distance": result["distance"],
                            "smileIntensity": result["smileIntensity"],
                            "smileFrequency": result["smileFrequency"],
                            "averageSmileIntensity": result["averageSmileIntensity"],
                            "attention": result["attention"],
                            "headStability": result["headStability"],
                            "eyeConsistency": result["eyeConsistency"],
                            "confidence": result["confidence"],
                            "professionalism": result["professionalism"],
                            "interview": result["interview"],
                            "feedbacks": result["feedbacks"]
                        })
                        await websocket.send(response)
                except Exception as e:
                    logger.error(f"处理图像时出错: {str(e)}", exc_info=True)
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"处理错误: {str(e)}"
                    }))

    except websockets.exceptions.ConnectionClosed as e:
        logger.info(f"客户端断开连接: code={e.code}, reason={e.reason}")
    except Exception as e:
        logger.error(f"处理错误: {str(e)}", exc_info=True)
    finally:
        logger.info("连接关闭")


# 启动WebSocket服务器
async def main():
    logger.info("启动行为分析服务器...")
    async with websockets.serve(behavior_analysis, "0.0.0.0", 8765, max_size=10 * 1024 * 1024):
        logger.info("服务器已在端口 8765 上运行")
        await asyncio.Future()  # 永久运行


if __name__ == "__main__":
    # 检查模型文件是否存在
    if not os.path.exists(model_path):
        logger.error(f"未找到模型文件: {model_path}")
        logger.error("请从 http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 下载并解压")
        exit(1)
    else:
        logger.info("找到人脸关键点模型文件")

    # 设置事件循环策略
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已关闭")