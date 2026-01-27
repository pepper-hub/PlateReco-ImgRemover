<template>
  <div class="container">
    <div class="header">
      <h1>图片智能消除工具</h1>
      <p class="subtitle">车牌识别消除 / AI 智能消除</p>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-links">
      <el-button type="primary" plain @click="openIOPaint">
        <el-icon><magic-stick /></el-icon> 打开 AI 消除工具
      </el-button>
      <span class="hint">用于复杂场景的智能消除（画笔涂抹、AI修复）</span>
    </div>

    <el-alert v-if="!backendConnected" title="后端服务未连接，请先启动后端" type="error" show-icon :closable="false" class="mb-20" />

    <!-- 上传区域 -->
    <div class="upload-section">
      <el-upload
        v-if="!previewUrl"
        class="upload-area"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="false"
        accept=".jpg,.png,.jpeg"
      >
        <div class="upload-content">
          <el-icon class="upload-icon"><upload-filled /></el-icon>
          <div class="upload-text">拖拽图片到此处</div>
          <div class="upload-hint">或点击选择图片</div>
        </div>
      </el-upload>

      <div v-else class="file-info">
        <el-icon class="check-icon"><check /></el-icon>
        <span>已选择图片</span>
        <el-button type="danger" plain @click="resetFile">
          <el-icon><refresh-right /></el-icon> 重新上传
        </el-button>
      </div>
    </div>

    <!-- 主工作区 -->
    <div class="workspace" v-if="previewUrl">
      <!-- 原图区域 -->
      <div class="panel">
        <div class="panel-header">
          <h3>原图预览</h3>
          <el-tag v-if="allBoxes.length" type="info">
            {{ allBoxes.length }} 个车牌
          </el-tag>
        </div>

        <div class="canvas-container">
          <div class="image-wrapper">
            <img
              :src="previewUrl"
              class="source-image"
              ref="sourceImage"
              @load="onImageLoad"
            />

            <!-- 车牌框 -->
            <div
              v-for="(box, index) in allBoxes"
              :key="index"
              class="box plate-box"
              :class="{ 'selected': selectedBoxes.has(index) }"
              :style="getBoxStyle(box)"
              @click="toggleBox(index)"
            >
              <span class="box-label">{{ index + 1 }}</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="panel-actions">
          <el-button type="primary" size="large" @click="detectPlate" :loading="loading">
            <el-icon><search /></el-icon> 识别车牌
          </el-button>
          <el-button
            type="danger"
            size="large"
            @click="removeSelected"
            :disabled="selectedBoxes.size === 0"
            :loading="processing"
          >
            <el-icon><delete /></el-icon> 消除选中 ({{ selectedBoxes.size }})
          </el-button>
          <el-button
            v-if="allBoxes.length > 1"
            size="large"
            @click="selectAll"
          >
            全选
          </el-button>
          <el-button
            v-if="selectedBoxes.size > 0"
            size="large"
            @click="clearSelection"
          >
            取消选择
          </el-button>
        </div>
      </div>

      <!-- 结果区域 -->
      <div class="panel" v-if="resultUrl">
        <div class="panel-header">
          <h3>处理结果</h3>
        </div>
        <div class="result-container">
          <img :src="resultUrl" class="result-image" />
        </div>
        <div class="panel-actions">
          <a :href="resultUrl" download="cleaned_image.png">
            <el-button type="success" size="large">
              <el-icon><download /></el-icon> 下载图片
            </el-button>
          </a>
        </div>
      </div>
    </div>

    <!-- 使用提示 -->
    <div class="tips" v-if="previewUrl">
      <el-alert type="info" :closable="false">
        <template #title>
          点击"识别车牌"，然后点击红框选择要消除的车牌
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  UploadFilled, Check, RefreshRight, Search,
  Delete, Download, MagicStick
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 状态变量
const backendConnected = ref(false)
const selectedFile = ref(null)
const previewUrl = ref(null)
const resultUrl = ref(null)
const loading = ref(false)
const processing = ref(false)

// 车牌模式
const allBoxes = ref([])
const selectedBoxes = ref(new Set())

// 图片相关
const sourceImage = ref(null)
const imageScale = ref(1)

// 检查后端连接
const checkBackend = async () => {
  try {
    await axios.get('/api/test')
    backendConnected.value = true
  } catch (e) {
    backendConnected.value = false
  }
}
checkBackend()

// 打开 IOPaint WebUI
const openIOPaint = () => {
  window.open('http://127.0.0.1:8003', '_blank')
}

// 处理文件上传
const handleFileChange = (file) => {
  const isValid = ['image/jpeg', 'image/png'].includes(file.raw.type)
  if (!isValid) {
    ElMessage.error('仅支持 JPG/PNG 格式')
    return
  }
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  resultUrl.value = null
  allBoxes.value = []
  selectedBoxes.value = new Set()
}

// 重置文件
const resetFile = () => {
  selectedFile.value = null
  previewUrl.value = null
  resultUrl.value = null
  allBoxes.value = []
  selectedBoxes.value = new Set()
}

// 图片加载完成
const onImageLoad = () => {
  if (sourceImage.value) {
    const naturalWidth = sourceImage.value.naturalWidth
    const displayWidth = sourceImage.value.width
    imageScale.value = displayWidth / naturalWidth
  }
}

// 获取框的样式
const getBoxStyle = (box) => {
  const [x1, y1, x2, y2] = box
  const scale = imageScale.value
  return {
    left: `${x1 * scale}px`,
    top: `${y1 * scale}px`,
    width: `${(x2 - x1) * scale}px`,
    height: `${(y2 - y1) * scale}px`
  }
}

// 识别车牌
const detectPlate = async () => {
  if (!selectedFile.value) return
  loading.value = true

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await axios.post('/api/detect-plate', formData)
    if (res.data.data.plate_boxes.length > 0) {
      allBoxes.value = res.data.data.plate_boxes
      selectedBoxes.value = new Set()
      ElMessage.success(`识别成功，检测到 ${res.data.data.count} 个车牌`)
    } else {
      ElMessage.warning('未识别到车牌')
      allBoxes.value = []
    }
  } catch (error) {
    ElMessage.error('识别请求失败')
  } finally {
    loading.value = false
  }
}

// 切换选择
const toggleBox = (index) => {
  if (selectedBoxes.value.has(index)) {
    selectedBoxes.value.delete(index)
  } else {
    selectedBoxes.value.add(index)
  }
  selectedBoxes.value = new Set(selectedBoxes.value)
}

// 全选
const selectAll = () => {
  selectedBoxes.value = new Set(allBoxes.value.map((_, i) => i))
}

// 清除选择
const clearSelection = () => {
  selectedBoxes.value = new Set()
}

// 消除选中
const removeSelected = async () => {
  if (selectedBoxes.value.size === 0 || !selectedFile.value) return
  processing.value = true

  const boxesToRemove = Array.from(selectedBoxes.value).map(i => allBoxes.value[i])

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('boxes', JSON.stringify(boxesToRemove))

  try {
    const res = await axios.post('/api/remove-area', formData, { responseType: 'blob' })
    resultUrl.value = URL.createObjectURL(res.data)
    ElMessage.success('消除完成')
  } catch (error) {
    ElMessage.error('消除失败')
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.quick-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
}

.quick-links .el-button {
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.quick-links .el-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: white;
}

.quick-links .hint {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.mb-20 {
  margin-bottom: 20px;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
}

.upload-content {
  padding: 50px 20px;
  text-align: center;
}

.upload-icon {
  font-size: 60px;
  color: #409eff;
}

.upload-text {
  font-size: 16px;
  color: #303133;
  margin-top: 15px;
}

.upload-hint {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 20px;
  background: #f0f9ff;
  border: 2px dashed #67c23a;
  border-radius: 12px;
}

.check-icon {
  font-size: 28px;
  color: #67c23a;
}

.workspace {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.panel {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.canvas-container,
.result-container {
  position: relative;
  padding: 20px;
  display: flex;
  justify-content: center;
  background: #f5f7fa;
  min-height: 300px;
}

.image-wrapper {
  position: relative;
  display: inline-block;
}

.source-image,
.result-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  user-select: none;
}

.box {
  position: absolute;
  border: 2px solid;
  pointer-events: none;
}

.plate-box {
  border-color: rgba(255, 0, 0, 0.7);
  background-color: rgba(255, 0, 0, 0.1);
  cursor: pointer;
  pointer-events: auto;
}

.plate-box:hover {
  border-color: rgba(255, 0, 0, 1);
  background-color: rgba(255, 0, 0, 0.25);
}

.plate-box.selected {
  border-color: #67c23a;
  background-color: rgba(103, 194, 58, 0.2);
  border-width: 3px;
}

.box-label {
  position: absolute;
  top: -22px;
  left: 0;
  background: rgba(255, 0, 0, 0.9);
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
}

.plate-box.selected .box-label {
  background: rgba(103, 194, 58, 0.9);
}

.panel-actions {
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.panel-actions .el-button .el-icon {
  margin-right: 5px;
}

.tips {
  margin-top: 20px;
}
</style>
