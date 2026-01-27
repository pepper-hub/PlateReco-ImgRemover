import io
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from typing import List

app = FastAPI()

# 1. 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 初始化多语言车牌检测模型
# 支持的车牌类型: cn(中国), eu(欧洲), us(美国), ru(俄罗斯), kr(韩国)
plate_models = {}

# 模型配置: 名称 -> 模型文件路径
MODEL_CONFIG = {
    "cn": "yolov8n-plate.pt",      # 中国车牌
    "eu": "yolov8n-plate-eu.pt",   # 欧洲车牌
    "global": "yolov8n-plate.pt",  # 通用模型
}

# 默认加载中文车牌模型
try:
    plate_models["cn"] = YOLO('yolov8s.pt')  # 使用从 GitHub 下载的新模型
    plate_models["default"] = plate_models["cn"]
    print("中国车牌模型加载成功！")
except Exception as e:
    print(f"车牌模型加载失败: {e}")
    plate_models = None


@app.get("/api/test")
async def test_service():
    """测试接口"""
    return {"msg": "服务正常"}


@app.get("/api/get")
async def get_service():
    """GET 测试接口"""
    return {"code": 200, "msg": "GET 请求正常", "models": list(plate_models.keys()) if plate_models else []}


@app.post("/api/detect-plate")
async def detect_plate(
    file: UploadFile = File(...),
    lang: str = Form("cn"),  # 语言参数: cn, eu, us, kr, global
    conf: float = Form(0.25),  # 置信度阈值，越低检测越多，默认0.25
    iou: float = Form(0.5)     # IOU阈值，用于NMS去重
):
    """
    识别车牌位置
    lang: 车牌类型 (cn, eu, global)
    conf: 置信度阈值 (0-1)，越低检测越多，但可能误检
    iou: IOU阈值 (0-1)，用于去除重复框，越小去重越严格
    """
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return {"code": 500, "msg": "文件格式错误"}

    if plate_models is None:
        return {"code": 500, "msg": "车牌模型未加载"}

    # 选择对应语言的模型，如果没有则用默认
    model = plate_models.get(lang, plate_models.get("default"))

    # 读取图片
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 推理（使用自定义参数）
    results = model(img, conf=conf, iou=iou)

    boxes = []
    for result in results:
        for box in result.boxes:
            coords = box.xyxy[0].tolist()
            boxes.append(coords)

    if not boxes:
        return {"code": 200, "data": {"plate_boxes": []}, "msg": "未识别到车牌"}

    return {
        "code": 200,
        "data": {
            "plate_boxes": boxes,
            "count": len(boxes),
            "lang": lang
        },
        "msg": f"识别成功，检测到 {len(boxes)} 个车牌"
    }


@app.post("/api/remove-area")
async def remove_area(
    file: UploadFile = File(...),
    boxes: str = Form(...)  # JSON 字符串: "[[x1,y1,x2,y2], [x1,y1,x2,y2], ...]"
):
    """
    图片消除接口 - 支持多个区域
    boxes: JSON 字符串，包含要消除的区域坐标列表
    """
    try:
        import json

        contents = await file.read()
        image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

        # 解析坐标列表
        box_list = json.loads(boxes)

        # 构建 Mask (黑底白框，白色区域是要消除的部分)
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)

        # 将所有区域都设为白色
        padding = 5
        for box in box_list:
            x1, y1, x2, y2 = box
            cv2.rectangle(
                mask,
                (max(0, int(x1) - padding), max(0, int(y1) - padding)),
                (min(w, int(x2) + padding), min(h, int(y2) + padding)),
                255, -1
            )

        # 使用 OpenCV 的 inpaint 算法
        result = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)

        # 转为二进制流返回
        _, encoded_img = cv2.imencode('.png', result)
        return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type="image/png")

    except Exception as e:
        print(f"Error: {e}")
        return {"code": 500, "msg": f"消除失败: {str(e)}"}


# 启动命令: uvicorn main:app --reload --host 0.0.0.0 --port 8001
