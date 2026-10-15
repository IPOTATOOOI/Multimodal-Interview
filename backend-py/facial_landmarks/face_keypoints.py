
# import the necessary packages
import numpy as np
import argparse
import imutils
import dlib
import cv2
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img-landmarks")

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
                help="path to facial landmark predictor")
ap.add_argument("-i", "--image", required=True,
                help="path to input image")
args = vars(ap.parse_args())


def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y
    # return a tuple of (x, y, w, h)
    return (x, y, w, h)


def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)
    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    # return the list of (x, y)-coordinates
    return coords


current_dir = os.path.dirname(os.path.abspath(__file__))
def load_pose_model():
    protoFile = os.path.join(current_dir, "pose_deploy.prototxt")
    weightsFile = os.path.join(current_dir, "pose_iter_584000.caffemodel")

    # 检查模型文件是否存在
    if not os.path.isfile(protoFile) or not os.path.isfile(weightsFile):
        print("[警告] 未找到人体姿态模型文件，将仅检测面部关键点")
        return None

    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
    print("[INFO] 人体姿态模型加载成功!")
    return net


# 更新：检测上半身关键点（肩膀、手臂）
def detect_upper_body_keypoints(image, net):
    if net is None:
        return image

    # 人体姿态关键点对应索引（OpenPose BODY_25模型）
    NECK = 1
    R_SHOULDER = 2
    R_ELBOW = 3  # 右肘
    R_WRIST = 4  # 右手腕
    L_SHOULDER = 5
    L_ELBOW = 6  # 左肘
    L_WRIST = 7  # 左手腕

    # 获取图像尺寸
    frameHeight, frameWidth = image.shape[:2]

    # 输入网络的预处理
    inWidth = 368
    inHeight = 368
    inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (inWidth, inHeight),
                                    (0, 0, 0), swapRB=False, crop=False)

    # 输入网络进行预测
    net.setInput(inpBlob)
    output = net.forward()

    H = output.shape[2]
    W = output.shape[3]

    # 存储检测到的关键点
    detected_points = {}

    # 要检测的关键点列表
    point_list = [NECK, R_SHOULDER, R_ELBOW, R_WRIST, L_SHOULDER, L_ELBOW, L_WRIST]

    for i in point_list:
        # 获取置信度图
        probMap = output[0, i, :, :]

        # 找到全局最大值
        _, prob, _, point = cv2.minMaxLoc(probMap)

        # 缩放到原始图像尺寸
        x = int((frameWidth * point[0]) / W)
        y = int((frameHeight * point[1]) / H)

        # 仅保存置信度高于0.1的关键点
        if prob > 0.1:
            detected_points[i] = (x, y, prob)

    # 在图像上绘制关键点并连接
    # 1. 绘制关键点
    for idx, (x, y, prob) in detected_points.items():
        # 不同部位使用不同颜色和标记
        colors = {
            R_SHOULDER: (255, 0, 0),  # 右肩 - 蓝色
            R_ELBOW: (0, 0, 255),  # 右肘 - 红色
            R_WRIST: (255, 255, 0),  # 右手腕 - 青色
            L_SHOULDER: (0, 255, 0),  # 左肩 - 绿色
            L_ELBOW: (255, 0, 255),  # 左肘 - 品红
            L_WRIST: (0, 255, 255),  # 左手腕 - 黄色
            NECK: (0, 165, 255)  # 颈部 - 橙色
        }

        sizes = {
            R_SHOULDER: 10,
            R_ELBOW: 8,
            R_WRIST: 6,
            L_SHOULDER: 10,
            L_ELBOW: 8,
            L_WRIST: 6,
            NECK: 8
        }

        color = colors.get(idx, (0, 0, 255))  # 默认为红色
        size = sizes.get(idx, 5)

        cv2.circle(image, (x, y), size, color, thickness=-1)

        # 标记关键点类型和置信度
        keypoint_names = {
            R_SHOULDER: "Right Shoulder",
            R_ELBOW: "Right Elbow",
            R_WRIST: "Right Wrist",
            L_SHOULDER: "Left Shoulder",
            L_ELBOW: "Left Elbow",
            L_WRIST: "Left Wrist",
            NECK: "Neck"
        }

        if idx in keypoint_names:
            label = f"{keypoint_names[idx]}: {prob:.2f}"
            cv2.putText(image, label, (x + 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    # 2. 连接关键点形成手臂
    # 右臂连接：肩 -> 肘 -> 腕
    if R_SHOULDER in detected_points and R_ELBOW in detected_points:
        cv2.line(image, detected_points[R_SHOULDER][:2], detected_points[R_ELBOW][:2],
                 (255, 0, 0), 2)  # 蓝色线连接肩-肘

    if R_ELBOW in detected_points and R_WRIST in detected_points:
        cv2.line(image, detected_points[R_ELBOW][:2], detected_points[R_WRIST][:2],
                 (0, 0, 255), 2)  # 红色线连接肘-腕

    # 左臂连接：肩 -> 肘 -> 腕
    if L_SHOULDER in detected_points and L_ELBOW in detected_points:
        cv2.line(image, detected_points[L_SHOULDER][:2], detected_points[L_ELBOW][:2],
                 (0, 255, 0), 2)  # 绿色线连接肩-肘

    if L_ELBOW in detected_points and L_WRIST in detected_points:
        cv2.line(image, detected_points[L_ELBOW][:2], detected_points[L_WRIST][:2],
                 (255, 0, 255), 2)  # 品红线连接肘-腕

    # 3. 连接肩膀
    if R_SHOULDER in detected_points and L_SHOULDER in detected_points:
        cv2.line(image, detected_points[R_SHOULDER][:2], detected_points[L_SHOULDER][:2],
                 (0, 255, 255), 2)  # 黄色线连接左右肩

    # 4. 连接颈部到肩膀（可选）
    if NECK in detected_points:
        if R_SHOULDER in detected_points:
            cv2.line(image, detected_points[NECK][:2], detected_points[R_SHOULDER][:2],
                     (255, 165, 0), 2)  # 橙色线连接颈-右肩

        if L_SHOULDER in detected_points:
            cv2.line(image, detected_points[NECK][:2], detected_points[L_SHOULDER][:2],
                     (255, 165, 0), 2)  # 橙色线连接颈-左肩

    return image


# 加载人体姿态模型
pose_net = load_pose_model()

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.path.join(current_dir, "shape_predictor_68_face_landmarks.dat"))

# load the input image, resize it, and convert it to grayscale
image = cv2.imread(args["image"])
orig = image.copy()
image = imutils.resize(image, width=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# detect faces in the grayscale image
rects = detector(gray, 1)

# loop over the face detections
for (i, rect) in enumerate(rects):
    # determine the facial landmarks for the face region, then
    # convert the facial landmark (x, y)-coordinates to a NumPy
    # array
    shape = predictor(gray, rect)
    shape = shape_to_np(shape)

    # convert dlib's rectangle to a OpenCV-style bounding box
    # [i.e., (x, y, w, h)], then draw the face bounding box
    (x, y, w, h) = rect_to_bb(rect)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # show the face number
    cv2.putText(image, "Face #{}".format(i + 1), (x - 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # loop over the (x, y)-coordinates for the facial landmarks
    # and draw them on the image
    for (x, y) in shape:
        cv2.circle(image, (x, y), 1, (0, 0, 255), -1)

# 在图像上检测并绘制上半身关键点（肩膀和手臂）
image = detect_upper_body_keypoints(image, pose_net)

# 生成输出路径 (保留原文件名并添加_landmarks)
input_filename = os.path.basename(args["image"])
name, ext = os.path.splitext(input_filename)
output_filename = f"{name}_landmarks{ext}"
output_path = os.path.join(OUTPUT_DIR, output_filename)

# 保存图片
cv2.imwrite(output_path, image)
print(f"结果已保存到: {output_path}")