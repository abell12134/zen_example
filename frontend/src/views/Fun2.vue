<template>
  <div class="file-server-container">
    <header class="header">
      <div class="header-content">
        <h1>📁 文件服务器</h1>
        <div class="user-info">
          <span>欢迎，{{ authStore.user?.phone }}</span>
          <button @click="handleLogout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </header>
    
    <nav class="navigation">
      <div class="nav-content">
        <router-link to="/home" class="nav-item" :class="{ active: $route.path === '/home' }">
          <span class="nav-icon">🏠</span>
          <span>首页</span>
        </router-link>
        <router-link to="/fun1" class="nav-item" :class="{ active: $route.path === '/fun1' }">
          <span class="nav-icon">⚡</span>
          <span>Fun1</span>
        </router-link>
        <router-link to="/fun2" class="nav-item" :class="{ active: $route.path === '/fun2' }">
          <span class="nav-icon">📁</span>
          <span>文件服务器</span>
        </router-link>
      </div>
    </nav>
    
    <main class="main-content">
      <div class="file-server-section">
        <div class="file-server-card">
          <div class="file-server-header">
            <h2>📁 文件管理系统</h2>
            <p class="file-server-subtitle">上传、下载和管理您的文件</p>
          </div>
          
          <div class="file-management-area">
            <!-- 文件上传区域 -->
            <div class="upload-section">
              <h3>📤 文件上传</h3>
              <div class="upload-area" 
                   @drop="handleDrop" 
                   @dragover.prevent 
                   @dragenter.prevent
                   :class="{ 'drag-over': isDragOver }"
                   @dragenter="isDragOver = true"
                   @dragleave="isDragOver = false">
                <div class="upload-content">
                  <div class="upload-icon">📁</div>
                  <p>拖拽文件到此处或点击选择文件</p>
                  <input type="file" 
                         ref="fileInput" 
                         @change="handleFileSelect" 
                         multiple 
                         style="display: none">
                  <button @click="$refs.fileInput.click()" class="select-file-btn">
                    选择文件
                  </button>
                </div>
              </div>
              
              <!-- 上传进度 -->
              <div v-if="uploadingFiles.length > 0" class="upload-progress">
                <h4>上传进度</h4>
                <div v-for="file in uploadingFiles" :key="file.name" class="progress-item">
                  <div class="file-info">
                    <span class="file-name">{{ file.name }}</span>
                    <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: file.progress + '%' }"></div>
                  </div>
                  <span class="progress-text">{{ file.progress }}%</span>
                </div>
              </div>
            </div>
            
            <!-- 文件浏览区域 -->
            <div class="file-browser-section">
              <h3>📂 文件浏览</h3>
              
              <!-- 路径导航 -->
              <div class="breadcrumb">
                <span @click="navigateToPath('')" class="breadcrumb-item" :class="{ active: currentPath === '' }">
                  📁 根目录
                </span>
                <template v-if="currentPath">
                  <span class="breadcrumb-separator">/</span>
                  <span class="breadcrumb-item active">{{ currentPath }}</span>
                </template>
              </div>
              
              <!-- 操作按钮 -->
              <div class="file-actions">
                <button @click="refreshFileList" class="action-btn refresh">
                  🔄 刷新
                </button>
                <button @click="createFolder" class="action-btn create">
                  📁+ 新建文件夹
                </button>
              </div>
              
              <!-- 文件列表 -->
              <div class="file-list">
                <div v-if="loading" class="loading">
                  <div class="loading-spinner"></div>
                  <p>加载中...</p>
                </div>
                
                <div v-else-if="fileList.length === 0" class="empty-state">
                  <div class="empty-icon">📂</div>
                  <p>此文件夹为空</p>
                </div>
                
                <div v-else class="file-grid">
                  <div v-for="item in fileList" 
                       :key="item.name" 
                       class="file-item"
                       @click="handleItemClick(item)"
                       @contextmenu.prevent="showContextMenu(item, $event)">
                    <div class="file-icon">
                      {{ item.type === 'folder' ? '📁' : getFileIcon(item.name) }}
                    </div>
                    <div class="file-info">
                      <div class="file-name" :title="item.name">{{ item.name }}</div>
                      <div class="file-meta">
                        <span v-if="item.type === 'file'" class="file-size">
                          {{ formatFileSize(item.size) }}
                        </span>
                        <span class="file-date">{{ formatDate(item.modified) }}</span>
                      </div>
                    </div>
                    <div class="file-actions-menu">
                      <button @click.stop="downloadItem(item)" 
                              class="action-btn-small download"
                              :title="item.type === 'folder' ? '下载文件夹(压缩)' : '下载文件'">
                        ⬇️
                      </button>
                      <button @click.stop="deleteItem(item)" 
                              class="action-btn-small delete"
                              title="删除">
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 文件服务器状态
const currentPath = ref('')
const fileList = ref([])
const loading = ref(false)
const isDragOver = ref(false)
const uploadingFiles = ref([])

// API基础URL
const API_BASE_URL = 'http://127.0.0.1:5000/api'

// 文件上传处理
const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  const files = Array.from(event.dataTransfer.files)
  uploadFiles(files)
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  uploadFiles(files)
  event.target.value = '' // 清空input
}

const uploadFiles = async (files) => {
  for (const file of files) {
    const uploadFile = {
      name: file.name,
      size: file.size,
      progress: 0,
      file: file
    }
    
    uploadingFiles.value.push(uploadFile)
    
    try {
      await uploadFileToServer(uploadFile)
      // 上传完成后刷新文件列表
      await refreshFileList()
    } catch (error) {
      console.error('文件上传失败:', error)
      alert(`文件 ${file.name} 上传失败: ${error.message}`)
    } finally {
      // 移除上传进度项
      const index = uploadingFiles.value.findIndex(f => f.name === file.name)
      if (index > -1) {
        uploadingFiles.value.splice(index, 1)
      }
    }
  }
}

// 真实文件上传到服务器
const uploadFileToServer = async (uploadFile) => {
  const formData = new FormData()
  formData.append('file', uploadFile.file)
  formData.append('path', currentPath.value)
  
  try {
    uploadFile.progress = 10
    
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
      mode: 'cors',
      credentials: 'omit'
    })
    
    uploadFile.progress = 90
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '上传失败')
    }
    
    uploadFile.progress = 100
    const result = await response.json()
    console.log('文件上传成功:', result)
  } catch (error) {
    console.error('上传错误:', error)
    throw error
  }
}

// 文件列表管理
const refreshFileList = async () => {
  loading.value = true
  try {
    const response = await fetch(`${API_BASE_URL}/files?path=${encodeURIComponent(currentPath.value)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      mode: 'cors',
      credentials: 'omit'
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '获取文件列表失败')
    }
    
    const data = await response.json()
    fileList.value = data.files || []
  } catch (error) {
    console.error('获取文件列表失败:', error)
    if (error.message === 'Failed to fetch') {
      alert('无法连接到服务器，请检查后端服务是否正常运行')
    } else {
      alert(`获取文件列表失败: ${error.message}`)
    }
    fileList.value = []
  } finally {
    loading.value = false
  }
}

// 文件/文件夹操作
const handleItemClick = (item) => {
  if (item.type === 'folder') {
    navigateToPath(item.path)
  }
}

const navigateToPath = (path) => {
  currentPath.value = path
  refreshFileList()
}

const createFolder = async () => {
  const folderName = prompt('请输入文件夹名称:')
  if (folderName && folderName.trim()) {
    try {
      const response = await fetch(`${API_BASE_URL}/folder`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: folderName.trim(),
          path: currentPath.value
        }),
        mode: 'cors',
        credentials: 'omit'
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || '创建文件夹失败')
      }
      
      const result = await response.json()
      alert(`文件夹 "${result.name}" 创建成功`)
      await refreshFileList()
    } catch (error) {
      console.error('创建文件夹失败:', error)
      alert(`创建文件夹失败: ${error.message}`)
    }
  }
}

const downloadItem = (item) => {
  try {
    const downloadUrl = `${API_BASE_URL}/download/${encodeURIComponent(item.path)}`
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = item.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    if (item.type === 'file') {
      alert(`开始下载文件: ${item.name}`)
    } else {
      alert(`开始压缩并下载文件夹: ${item.name}`)
    }
  } catch (error) {
    console.error('下载失败:', error)
    alert(`下载失败: ${error.message}`)
  }
}

const deleteItem = async (item) => {
  if (confirm(`确定要删除 ${item.type === 'folder' ? '文件夹' : '文件'} "${item.name}" 吗？`)) {
    try {
      const response = await fetch(`${API_BASE_URL}/delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          path: item.path
        }),
        mode: 'cors',
        credentials: 'omit'
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || '删除失败')
      }
      
      const result = await response.json()
      alert(result.message)
      await refreshFileList()
    } catch (error) {
      console.error('删除失败:', error)
      alert(`删除失败: ${error.message}`)
    }
  }
}

const showContextMenu = (item, event) => {
  // 右键菜单功能（可以后续扩展）
  console.log('右键点击:', item)
}

// 工具函数
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getFileIcon = (fileName) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  const iconMap = {
    'pdf': '📄',
    'doc': '📝', 'docx': '📝',
    'xls': '📊', 'xlsx': '📊',
    'ppt': '📈', 'pptx': '📈',
    'txt': '📃',
    'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
    'mp4': '🎥', 'avi': '🎥', 'mov': '🎥',
    'mp3': '🎵', 'wav': '🎵',
    'zip': '📦', 'rar': '📦', '7z': '📦',
    'js': '📜', 'html': '📜', 'css': '📜', 'json': '📜'
  }
  return iconMap[ext] || '📄'
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 初始化
onMounted(() => {
  refreshFileList()
})
</script>

<style scoped>
.file-server-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.header h1 {
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info span {
  color: #666;
  font-size: 14px;
}

.logout-btn {
  padding: 8px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: #c0392b;
}

.navigation {
  background: white;
  border-bottom: 1px solid #eee;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  gap: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 15px 20px;
  text-decoration: none;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.nav-item:hover {
  color: #667eea;
  background: #f8f9ff;
}

.nav-item.active {
  color: #667eea;
  border-bottom-color: #667eea;
  background: #f8f9ff;
}

.nav-icon {
  font-size: 18px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.file-server-section {
  background: white;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.file-server-card {
  background: white;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.file-server-header {
  text-align: center;
  margin-bottom: 40px;
}

.file-server-header h2 {
  color: #2c3e50;
  font-size: 32px;
  margin-bottom: 10px;
}

.file-server-subtitle {
  color: #666;
  font-size: 18px;
}

.file-management-area {
  display: grid;
  gap: 40px;
}

.upload-section {
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 10px;
  background: #fafbfc;
}

.upload-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 20px;
  text-align: center;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 10px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #667eea;
  background: #f8f9ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  font-size: 48px;
  color: #667eea;
}

.select-file-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.select-file-btn:hover {
  background: #5a6fd8;
}

.upload-progress {
  margin-top: 20px;
}

.upload-progress h4 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.progress-item {
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
}

.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.file-name {
  font-weight: 500;
  color: #2c3e50;
}

.file-size {
  color: #666;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin-right: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 14px;
  color: #666;
  min-width: 40px;
  text-align: right;
}

.file-browser-section {
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 10px;
  background: #fafbfc;
}

.file-browser-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 20px;
  text-align: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 20px;
  padding: 10px;
  background: white;
  border-radius: 5px;
  border: 1px solid #eee;
}

.breadcrumb-item {
  padding: 5px 10px;
  background: #f8f9fa;
  border-radius: 3px;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 14px;
}

.breadcrumb-item:hover {
  background: #e9ecef;
}

.breadcrumb-item.active {
  background: #667eea;
  color: white;
}

.breadcrumb-separator {
  color: #666;
}

.file-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-btn:hover {
  background: #f8f9fa;
  border-color: #667eea;
  color: #667eea;
}

.action-btn.refresh {
  border-color: #28a745;
  color: #28a745;
}

.action-btn.create {
  border-color: #007bff;
  color: #007bff;
}

.file-list {
  background: white;
  border-radius: 8px;
  border: 1px solid #eee;
  overflow: hidden;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.loading-spinner {
  display: inline-block;
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.5;
}

.file-grid {
  display: grid;
  gap: 0;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.3s;
  position: relative;
}

.file-item:hover {
  background: #f8f9fa;
}

.file-item:last-child {
  border-bottom: none;
}

.file-icon {
  font-size: 24px;
  margin-right: 15px;
  min-width: 30px;
  text-align: center;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 5px;
  word-break: break-all;
}

.file-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
}

.file-size {
  color: #666;
}

.file-date {
  color: #666;
}

.file-actions-menu {
  display: flex;
  gap: 5px;
  opacity: 0;
  transition: opacity 0.3s;
}

.file-item:hover .file-actions-menu {
  opacity: 1;
}

.action-btn-small {
  padding: 5px 8px;
  border: none;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.action-btn-small:hover {
  background: rgba(0, 0, 0, 0.2);
}

.action-btn-small.download {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.action-btn-small.download:hover {
  background: rgba(40, 167, 69, 0.2);
}

.action-btn-small.delete {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.action-btn-small.delete:hover {
  background: rgba(220, 53, 69, 0.2);
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
  }
  
  .main-content {
    padding: 20px 15px;
  }
  
  .fun2-card {
    padding: 25px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .chart-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .timer-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .timer-value {
    font-size: 36px;
  }
}
</style>