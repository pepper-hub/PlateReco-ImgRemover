# 图片智能消除工具

一个基于 **YOLOv8 + OpenCV** 的车牌识别消除工具，支持快速车牌检测与区域消除。同时集成 **IOPaint** 用于复杂场景的 AI 智能消除。

## 功能特性

- **车牌识别**：自动识别图片中的车牌位置
- **区域消除**：快速消除选中的车牌区域
- **多车牌处理**：支持识别多个车牌，可选择性地消除
- **AI 消除工具**：集成 IOPaint，支持画笔涂抹和 AI 修复

## 技术栈

### 后端
- Python 3.12
- FastAPI - Web 框架
- YOLOv8 - 车牌检测
- OpenCV - 图像处理与消除

### 前端
- Vue 3
- Element Plus
- Axios
- Vite

## 项目结构

```
IMGcleaner/
├── main.py              # 后端服务入口
├── requirements.txt     # Python 依赖
├── yolov8s.pt          # 车牌检测模型
├── frontend/           # 前端项目
│   ├── src/
│   │   ├── App.vue     # 主页面组件
│   │   └── main.js     # 入口文件
│   ├── package.json
│   └── vite.config.js
└── promt.md            # 需求文档
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 下载车牌检测模型

将 `yolov8s.pt` 模型文件放置在项目根目录。

### 3. 启动服务

**终端 1 - 启动车牌识别后端：**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**终端 2 - 启动 IOPaint（可选）：**
```bash
iopaint start --port 8003
```

**终端 3 - 启动前端：**
```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用

- 前端页面：`http://localhost:5173`（Vite 默认端口）
- 后端 API：`http://127.0.0.1:8001/docs`
- IOPaint：`http://127.0.0.1:8003`

## API 接口

### 测试接口
```
GET /api/test
```

### 车牌识别
```
POST /api/detect-plate
Content-Type: multipart/form-data

参数:
- file: 图片文件
- lang: 车牌类型 (cn/eu/global)
- conf: 置信度阈值 (0-1)
- iou: IOU阈值 (0-1)

返回:
{
  "code": 200,
  "data": {
    "plate_boxes": [[x1, y1, x2, y2], ...],
    "count": 2,
    "lang": "cn"
  },
  "msg": "识别成功，检测到 2 个车牌"
}
```

### 区域消除
```
POST /api/remove-area
Content-Type: multipart/form-data

参数:
- file: 图片文件
- boxes: JSON 字符串 "[[x1,y1,x2,y2], ...]"

返回: 图片二进制流
```

## 使用说明

1. **上传图片**：拖拽或点击上传 JPG/PNG 图片
2. **识别车牌**：点击"识别车牌"按钮
3. **选择区域**：点击红框选择要消除的车牌（变绿色为已选中）
4. **消除处理**：点击"消除选中"按钮
5. **下载结果**：点击"下载图片"保存处理后的图片

## 依赖版本

```
fastapi
uvicorn
python-multipart
ultralytics
opencv-python
numpy
```

## Docker 部署

### 快速启动

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 服务端口

| 服务 | 容器名 | 端口 |
|------|--------|------|
| 前端 | imgcleaner-frontend | 80 |
| 后端 | imgcleaner-backend | 8001 |

### 访问地址

- 前端：`http://localhost`
- 后端 API：`http://localhost:8001/docs`

## 注意事项

- 车牌检测模型针对中国车牌训练，对其他类型车牌识别效果可能不佳
- 消除功能使用 OpenCV Inpaint 算法，速度快但效果有限
- 如需更好的消除效果，请使用集成的 IOPaint AI 消除工具

## 许可证

MIT License
