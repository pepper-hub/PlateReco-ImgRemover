AI 提示词文档：图片消除 + 车牌识别工具（前后端开发）
文档说明
本提示词文档用于指导 AI 辅助开发「图片消除 + 车牌识别」工具，明确后端（Python+FastAPI）、前端（Vue3）的核心需求、功能边界、技术规范，确保 AI 生成的代码 / 方案贴合 “极简开发、自用练手” 的核心目标。
一、通用基础要求
核心场景：个人自用的图片处理工具，支持 “上传图片→自动识别车牌→消除车牌区域”，兼顾手动框选消除其他杂物的基础功能；
技术栈：后端 = Python+FastAPI+IOPaint+YOLOv8（车牌识别）；前端 = Vue3+Element Plus；
复杂度要求：极简实现，优先保证核心功能跑通，无需复杂鉴权、性能优化、异常处理（仅保留基础报错提示）；
运行环境：Windows 系统，后端运行在本地虚拟环境，前端支持本地调试，前后端通过 HTTP 接口通信。
二、后端（Python+FastAPI）明确需求
1. 核心功能需求
功能模块	详细需求
基础服务搭建	1. 创建 FastAPI 项目，启动端口 8080;
2. 支持跨域请求（解决前端跨域问题）；
3. 提供接口文档（FastAPI 自动生成的 /docs 页面）。
车牌识别接口	1. 接收前端上传的图片文件；
2. 调用 YOLOv8 轻量化车牌检测模型（yolov8n-plate.pt），识别图片中的车牌位置（返回 x1,y1,x2,y2 坐标）；
3. 接口返回格式：{"code":200,"data":{"plate_boxes":[(x1,y1,x2,y2)]},"msg":"识别成功"}；
4. 无车牌时返回：{"code":200,"data":{"plate_boxes":[]},"msg":"未识别到车牌"}。
图片消除接口	1. 接收前端上传的图片文件 + 消除区域坐标（支持车牌自动识别的坐标 / 手动框选的坐标）；
2. 调用 IOPaint 的核心函数（而非 API）完成图片消除，模型指定为 stable-diffusion-inpaint；
3. 返回处理后的图片二进制流（前端可直接展示 / 下载）；
4. 基础参数：hd_strategy=resize，enable-mobile=True，device=cpu。
辅助接口	1. 提供 “测试接口”（/api/test），返回 {"msg":"服务正常"}，用于前端检测后端是否启动；
2. 无需数据库持久化（练手阶段省略）。
2. 技术约束
依赖包明确：fastapi、uvicorn、ultralytics（YOLOv8）、iopaint、python-multipart（处理文件上传）；
代码结构：单文件 main.py 实现所有功能（无需分模块），注释清晰；
运行命令：提供启动命令（uvicorn main:app --reload --port 8080）；
错误处理：仅捕获 “图片格式错误、文件为空” 的基础异常，返回 {"code":500,"msg":"错误信息"}。
3. AI 提示词模板（后端）
plaintext
请用Python+FastAPI实现一个图片消除+车牌识别的后端服务，要求：
1. 技术栈：Python 3.12 + FastAPI + YOLOv8（yolov8n-plate.pt） + IOPaint；
2. 核心接口：
   - POST /api/detect-plate：接收图片文件，识别车牌坐标，返回JSON格式；
   - POST /api/remove-area：接收图片文件+消除区域坐标，调用IOPaint消除该区域，返回处理后的图片二进制流；
   - GET /api/test：测试接口，返回{"msg":"服务正常"}；
3. 要求：
   - 代码为单文件main.py，注释清晰；
   - 解决跨域问题；
   - 提供启动命令；
   - 仅做基础异常处理（图片格式错误、文件为空）；
   - 无需数据库，无需复杂鉴权；
   - IOPaint使用stable-diffusion-inpaint模型，device=cpu，开启hd_strategy=resize。
三、前端（Vue3）明确需求
1. 核心功能需求
功能模块	详细需求
页面布局	1. 单页面布局，分为 “上传区、预览区、操作区、结果区”；
2. 使用 Element Plus 组件：Upload（上传图片）、Button（识别 / 消除 / 下载）、Image（预览图片）、Alert（提示信息）；
3. 适配移动端（简单适配，无需复杂响应式）。
图片上传	1. 支持上传 jpg/png 格式图片，上传后在预览区显示原图；
2. 上传失败提示 “仅支持 jpg/png 格式”。
车牌识别	1. 点击 “识别车牌” 按钮，调用后端 /api/detect-plate 接口；
2. 识别成功后，在预览图上用红色框标注车牌位置；
3. 识别失败 / 无车牌时，弹出提示框告知用户。
图片消除	1. 支持两种消除方式：
- 自动消除：识别车牌后，点击 “消除车牌” 按钮，调用 /api/remove-area 接口（传入车牌坐标）；
- 手动消除：提供简单的框选工具（可选，简化版可省略，仅保留自动消除）；
2. 消除完成后，在结果区显示处理后的图片；
3. 提供 “下载图片” 按钮，下载处理后的图片。
状态提示	1. 接口请求中显示 “加载中” loading；
2. 操作成功 / 失败弹出对应提示（Element Plus 的 ElMessage）；
3. 后端服务未启动时，提示 “后端服务未连接”。
2. 技术约束
依赖：Vue3 + Vue CLI + Element Plus + axios（接口请求）；
代码结构：单页面组件（App.vue）+ main.js（入口文件），无需路由、状态管理（Pinia/Vuex）；
接口地址：固定为本地后端地址（http://127.0.0.1:8080）；
样式：使用 Element Plus 内置样式，无需自定义复杂 CSS。
3. AI 提示词模板（前端）
plaintext
请用Vue3+Element Plus实现一个图片消除+车牌识别的前端页面，要求：
1. 技术栈：Vue3 + Vue CLI + Element Plus + axios；
2. 页面结构：上传区、预览区、操作区、结果区；
3. 核心功能：
   - 上传jpg/png图片，预览原图；
   - 点击“识别车牌”按钮，调用http://127.0.0.1:8080/api/detect-plate接口，识别成功后用红框标注车牌位置；
   - 点击“消除车牌”按钮，调用http://127.0.0.1:8080/api/remove-area接口，展示处理后的图片；
   - 提供“下载图片”按钮，下载处理后的图片；
   - 接口请求时显示loading，操作结果用ElMessage提示；
4. 要求：
   - 代码为极简版，单页面（App.vue + main.js）；
   - 适配移动端简单样式；
   - 无需路由、状态管理；
   - 处理跨域请求（前端侧无需额外配置，依赖后端跨域）；
   - 仅保留核心功能，省略手动框选消除（仅做自动车牌消除）。
四、前后端联调核心提示
后端启动后，先访问 http://127.0.0.1:8080/docs 测试接口是否正常；
前端 axios 请求配置：
javascript
运行
axios.defaults.baseURL = 'http://127.0.0.1:8080';
axios.defaults.headers.post['Content-Type'] = 'multipart/form-data';
图片消除接口返回二进制流时，前端处理方式：
javascript
运行
axios.post('/api/remove-area', formData, { responseType: 'blob' })
  .then(res => {
    const url = URL.createObjectURL(res.data);
    // 展示图片/下载图片
  });