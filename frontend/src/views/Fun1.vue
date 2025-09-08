<template>
  <div class="fun1-container">
    <header class="header">
      <div class="header-content">
        <h1>AI智能</h1>
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
          <span class="nav-icon">🎯</span>
          <span>Fun2</span>
        </router-link>
      </div>
    </nav>
    
    <main class="main-content">
      <div class="fun1-section">
        <div class="fun1-card">
          <div class="chat-header">
            <h2>🤖 AI 智能助手</h2>
            <p class="chat-subtitle">AI智能</p>
            <div class="model-selector">
              <label for="model-select">选择模型：</label>
              <select id="model-select" v-model="selectedModel" @change="onModelChange" class="model-select">
                 <option v-for="model in modelOptions" :key="model.value" :value="model.value">
                   {{ model.label }} - {{ model.description }}
                 </option>
               </select>
            </div>
          </div>
          
          <div class="chat-container">
            <div class="chat-messages" ref="messagesContainer">
              <div 
                v-for="(message, index) in messages" 
                :key="index" 
                class="message"
                :class="{ 
                  'user-message': message.role === 'user', 
                  'assistant-message': message.role === 'assistant',
                  'system-message': message.role === 'system'
                }"
              >
                <div class="message-avatar">
                  <span v-if="message.role === 'user'">👤</span>
                  <span v-else>🤖</span>
                </div>
                <div class="message-content">
                  <!-- 显示图片（如果有） -->
                  <div v-if="message.hasImages && Array.isArray(message.content)" class="message-images">
                    <div v-for="(item, idx) in message.content" :key="idx">
                      <img v-if="item.type === 'image_url'" :src="item.image_url.url" class="message-image" alt="用户上传的图片" />
                    </div>
                  </div>
                  
                  <div class="message-text" v-html="formatMessage(getMessageText(message.content))"></div>
                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                </div>
              </div>
              
              <div v-if="isLoading" class="message assistant-message">
                <div class="message-avatar">
                  <span>🤖</span>
                </div>
                <div class="message-content">
                  <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
              
              <div v-if="messages.length === 0" class="empty-chat">
                <div class="empty-icon">💬</div>
                <p>开始与AI助手对话吧！</p>
              </div>
            </div>
            
            <div class="chat-input-area">
              <!-- 图片预览区域 -->
              <div v-if="selectedImages.length > 0" class="image-preview-area">
                <div class="image-preview-list">
                  <div v-for="(image, index) in selectedImages" :key="index" class="image-preview-item">
                    <img :src="image.preview" :alt="`预览图片 ${index + 1}`" class="preview-image" />
                    <button @click="removeImage(index)" class="remove-image-btn">×</button>
                  </div>
                </div>
              </div>
              
              <div class="input-container">
                <textarea 
                  v-model="currentMessage" 
                  @keydown="handleKeydown"
                  :placeholder="isVisionModel ? '输入您的问题或上传图片...' : '输入您的问题...'"
                  class="chat-input"
                  rows="1"
                  :disabled="isLoading"
                ></textarea>
                
                <!-- 图片上传按钮 -->
                <button 
                  v-if="isVisionModel"
                  @click="triggerImageUpload"
                  class="image-upload-btn"
                  :disabled="isLoading"
                  title="上传图片"
                >
                  📷
                </button>
                
                <button 
                  @click="sendMessage" 
                  :disabled="(!currentMessage.trim() && selectedImages.length === 0) || isLoading"
                  class="send-button"
                >
                  <span v-if="!isLoading">发送</span>
                  <span v-else>发送中...</span>
                </button>
              </div>
              
              <!-- 隐藏的文件输入 -->
              <input 
                ref="fileInput"
                type="file"
                accept="image/*"
                multiple
                @change="handleImageUpload"
                style="display: none;"
              />
              
              <div class="input-actions">
                <button @click="clearChat" class="clear-button" :disabled="messages.length === 0">
                  清空对话
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { marked } from 'marked'

// 配置marked选项
marked.setOptions({
  breaks: true, // 支持换行
  gfm: true, // 支持GitHub风格的markdown
  sanitize: false // 允许HTML标签
})

const router = useRouter()
const authStore = useAuthStore()

// AI聊天功能
const messages = ref([])
const currentMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const selectedModel = ref('glm-4.5')
const selectedImages = ref([])
const fileInput = ref(null)

// 计算属性：判断是否为视觉模型
const isVisionModel = computed(() => selectedModel.value === 'glm-4.5v')

// 可选模型列表
const modelOptions = [
  { value: 'glm-4.5', label: 'GLM-4.5', description: 'model' },
  { value: 'glm-4.5v', label: 'GLM-4.5V', description: 'model' },
  { value: 'glm-4.5-air', label: 'GLM-4.5-Air', description: 'model' }
]

// 智谱AI配置
const API_KEY = '31194c0a13644b808baf9d00888ec545.TJKre9eAhUo89f9X'
const API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'

// 图片处理方法
const triggerImageUpload = () => {
  fileInput.value?.click()
}

const handleImageUpload = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        selectedImages.value.push({
          file: file,
          preview: e.target.result,
          base64: e.target.result.split(',')[1] // 去掉data:image/xxx;base64,前缀
        })
      }
      reader.readAsDataURL(file)
    }
  })
  // 清空input值，允许重复选择同一文件
  event.target.value = ''
}

const removeImage = (index) => {
  selectedImages.value.splice(index, 1)
}

// 发送消息
const sendMessage = async () => {
  if ((!currentMessage.value.trim() && selectedImages.value.length === 0) || isLoading.value) return
  
  const messageContent = isVisionModel.value && selectedImages.value.length > 0 
    ? createMultiModalContent()
    : currentMessage.value.trim()
  
  const userMessage = {
    role: 'user',
    content: messageContent,
    timestamp: new Date(),
    hasImages: selectedImages.value.length > 0
  }
  
  messages.value.push(userMessage)
  const messageToSend = messageContent
  currentMessage.value = ''
  const imagesToSend = [...selectedImages.value]
  selectedImages.value = []
  isLoading.value = true
  
  await scrollToBottom()
  
  try {
    await callAI(messageToSend, imagesToSend)
  } catch (error) {
    console.error('AI调用失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，AI服务暂时不可用，请稍后再试。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

// 创建多模态内容
const createMultiModalContent = () => {
  const content = []
  
  // 添加图片
  selectedImages.value.forEach(image => {
    content.push({
      type: 'image_url',
      image_url: {
        url: `data:image/jpeg;base64,${image.base64}`
      }
    })
  })
  
  // 添加文本
  if (currentMessage.value.trim()) {
    content.push({
      type: 'text',
      text: currentMessage.value.trim()
    })
  } else {
    content.push({
      type: 'text',
      text: '请描述这个图片'
    })
  }
  
  return content
}

// 为非视觉模型处理兼容性
const getCompatibleContent = (content) => {
  // 如果当前模型不是视觉模型，且content是数组格式（多模态），则提取文本内容
  if (!isVisionModel.value && Array.isArray(content)) {
    const textContent = content.find(item => item.type === 'text')
    return textContent ? textContent.text : ''
  }
  return content
}

// 调用智谱AI API
const callAI = async (message, images = []) => {
  const requestBody = {
    model: selectedModel.value,
    messages: [
      ...messages.value.slice(-10).map(msg => ({
        role: msg.role,
        content: getCompatibleContent(msg.content)
      })),
      {
        role: 'user',
        content: message
      }
    ],
    stream: true,
    max_tokens: 4096,
    temperature: 0.0
  }
  
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify(requestBody)
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  
  const assistantMessage = {
    role: 'assistant',
    content: '',
    timestamp: new Date()
  }
  
  messages.value.push(assistantMessage)
  
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()
          if (data === '[DONE]') {
            return
          }
          
          try {
            const parsed = JSON.parse(data)
            if (parsed.choices && parsed.choices[0] && parsed.choices[0].delta && parsed.choices[0].delta.content) {
              assistantMessage.content += parsed.choices[0].delta.content
              await scrollToBottom()
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

// 处理键盘事件
const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// 清空对话
const clearChat = () => {
  messages.value = []
  selectedImages.value = []
}

// 获取消息文本内容
const getMessageText = (content) => {
  if (typeof content === 'string') {
    return content
  }
  if (Array.isArray(content)) {
    const textItem = content.find(item => item.type === 'text')
    return textItem ? textItem.text : ''
  }
  return ''
}

// 格式化消息内容
  const formatMessage = (content) => {
    return marked(content)
  }

  // 监听模型切换
  const onModelChange = () => {
    const selectedModelInfo = modelOptions.find(model => model.value === selectedModel.value)
    if (selectedModelInfo) {
      messages.value.push({
        role: 'system',
        content: `已切换到 ${selectedModelInfo.label}（${selectedModelInfo.description}）`,
        timestamp: Date.now()
      })
      nextTick(() => {
        scrollToBottom()
      })
    }
  }

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.fun1-container {
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

.fun1-card {
  background: white;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.chat-header {
  text-align: center;
  margin-bottom: 24px;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.chat-header h2 {
  color: #1a1a1a;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.chat-subtitle {
  color: #8e8e93;
  font-size: 14px;
  font-weight: 400;
  margin-bottom: 16px;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.model-selector label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.model-select {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
}

.model-select:hover {
  border-color: #667eea;
}

.model-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 650px;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #fafafa;
}

.message {
  display: flex;
  margin-bottom: 24px;
  animation: fadeIn 0.4s ease-out;
}

.user-message {
  justify-content: flex-end;
}

.assistant-message {
  justify-content: flex-start;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin: 0 12px;
  flex-shrink: 0;
  margin-top: 4px;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  order: 2;
  color: white;
}

.assistant-message .message-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  order: 1;
  color: white;
}

.message-content {
  max-width: 75%;
  background: white;
  border-radius: 16px;
  padding: 14px 18px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  border: 1px solid #f0f0f0;
}

.user-message .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 6px;
  border: none;
}

.assistant-message .message-content {
  background: #ffffff;
  color: #1a1a1a;
  border-bottom-left-radius: 6px;
  border: 1px solid #e5e7eb;
}

.system-message {
  justify-content: center;
  margin: 16px 0;
}

.system-message .message-avatar {
  display: none;
}

.system-message .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 13px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  max-width: 300px;
}

.system-message .message-text {
  margin: 0;
}

.system-message .message-time {
  display: none;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  font-weight: 400;
}

/* Markdown样式 */
.message-text h1,
.message-text h2,
.message-text h3,
.message-text h4,
.message-text h5,
.message-text h6 {
  margin: 16px 0 8px 0;
  font-weight: 600;
  line-height: 1.25;
}

.message-text h1 { font-size: 1.5em; }
.message-text h2 { font-size: 1.3em; }
.message-text h3 { font-size: 1.1em; }

.message-text p {
  margin: 8px 0;
}

.message-text ul,
.message-text ol {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text li {
  margin: 4px 0;
}

.message-text code {
  background: #f1f3f4;
  color: #d73a49;
  padding: 3px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 0.9em;
  font-weight: 500;
  border: 1px solid #e1e4e8;
}

.message-text pre {
  background: #2d3748;
  color: #e2e8f0;
  border: 1px solid #4a5568;
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 0.9em;
  line-height: 1.5;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
}

.message-text pre::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px 8px 0 0;
}

.message-text pre code {
  background: none;
  color: inherit;
  padding: 0;
  border-radius: 0;
  border: none;
  font-weight: normal;
}

/* 简单的语法高亮样式 */
.message-text pre .token.comment {
  color: #8b949e;
  font-style: italic;
}

.message-text pre .token.string {
  color: #a5d6ff;
}

.message-text pre .token.number {
  color: #79c0ff;
}

.message-text pre .token.keyword {
  color: #ff7b72;
  font-weight: bold;
}

.message-text pre .token.function {
  color: #d2a8ff;
}

.message-text pre .token.operator {
  color: #ff7b72;
}

.message-text pre .token.punctuation {
  color: #c9d1d9;
}

/* 代码块复制按钮样式 */
.message-text pre {
  position: relative;
}

.message-text pre:hover::after {
  content: '📋';
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.message-text pre:hover::after:hover {
  background: rgba(255, 255, 255, 0.2);
}

.message-text blockquote {
  border-left: 4px solid #dfe2e5;
  padding-left: 16px;
  margin: 12px 0;
  color: #6a737d;
  font-style: italic;
}

.message-text table {
  border-collapse: collapse;
  margin: 12px 0;
  width: 100%;
}

.message-text th,
.message-text td {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
  text-align: left;
}

.message-text th {
  background: #f6f8fa;
  font-weight: 600;
}

.message-text a {
  color: #0366d6;
  text-decoration: none;
}

.message-text a:hover {
  text-decoration: underline;
}

.message-text strong {
  font-weight: 600;
}

.message-text em {
  font-style: italic;
}

.message-text hr {
  border: none;
  border-top: 1px solid #e1e4e8;
  margin: 16px 0;
}

.message-time {
  font-size: 11px;
  opacity: 0.6;
  margin-top: 6px;
  text-align: right;
  font-weight: 400;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.assistant-message .message-time {
  color: #8e8e93;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 12px 0;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c7c7cc;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #8e8e93;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.6;
}

.chat-input-area {
  border-top: 1px solid #f0f0f0;
  background: #ffffff;
  padding: 24px;
}

/* 图片预览区域样式 */
.image-preview-area {
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.image-preview-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.image-preview-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e5e7eb;
  background: white;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #ef4444;
  color: white;
  border: none;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.remove-image-btn:hover {
  background: #dc2626;
  transform: scale(1.1);
}

/* 消息中的图片样式 */
.message-images {
  margin-bottom: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.message-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.message-image:hover {
  transform: scale(1.05);
}

.input-container {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  background: #f8f9fa;
  border-radius: 24px;
  padding: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.input-container:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chat-input {
  flex: 1;
  min-height: 44px;
  max-height: 120px;
  padding: 12px 16px;
  border: none;
  border-radius: 18px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  background: transparent;
  color: #1a1a1a;
  line-height: 1.5;
}

.chat-input::placeholder {
  color: #8e8e93;
}

.chat-input:disabled {
  background: transparent;
  cursor: not-allowed;
  opacity: 0.6;
}

.image-upload-btn {
  padding: 12px;
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  height: 44px;
}

.image-upload-btn:hover:not(:disabled) {
  background: #e5e7eb;
  color: #374151;
}

.image-upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button {
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 80px;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.send-button:disabled {
  background: #c7c7cc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.clear-button {
  padding: 8px 16px;
  background: transparent;
  color: #8e8e93;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-button:hover:not(:disabled) {
  background: #fff5f5;
  color: #ef4444;
  border-color: #fecaca;
}

.clear-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
  }
  
  .main-content {
    padding: 20px 15px;
  }
  
  .fun1-card {
    padding: 25px;
  }
  
  .counter-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .input-group, .todo-input {
    flex-direction: column;
  }
}
</style>