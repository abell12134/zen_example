<template>
  <div class="home-container">
    <header class="header">
      <div class="header-content">
        <h1>欢迎来到 Zen 系统</h1>
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
      <div class="intro-section">
        <div class="intro-card">
          <div class="intro-header">
            <h2>🎉 欢迎使用 Zen 系统</h2>
            <p class="intro-subtitle">一个现代化的 服务 应用平台</p>
          </div>
          
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">🔐</div>
              <h3>安全认证</h3>
              <p>完整的用户注册和登录系统，支持本地数据存储</p>
            </div>
            
            <div class="feature-card">
              <div class="feature-icon">🎨</div>
              <h3>现代UI</h3>
              <p>响应式设计，优雅的用户界面和流畅的交互体验</p>
            </div>
            
            <div class="feature-card">
              <div class="feature-icon">⚡</div>
              <h3>高性能</h3>
              <p>基于 Vue 3 + Vite 构建，快速的开发和构建体验</p>
            </div>
            
            <div class="feature-card">
              <div class="feature-icon">🔧</div>
              <h3>可扩展</h3>
              <p>模块化架构设计，方便添加新功能和组件</p>
            </div>
          </div>
          
          <div class="quick-actions">
            <h3>快速开始</h3>
            <div class="action-buttons">
              <router-link to="/fun1" class="action-btn primary">
                <span class="btn-icon">⚡</span>
                <span>体验 Fun1</span>
              </router-link>
              <router-link to="/fun2" class="action-btn secondary">
                <span class="btn-icon">🎯</span>
                <span>体验 Fun2</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.home-container {
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

.intro-section {
  display: flex;
  justify-content: center;
}

.intro-card {
  background: white;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  width: 100%;
}

.intro-header {
  text-align: center;
  margin-bottom: 40px;
}

.intro-header h2 {
  color: #2c3e50;
  font-size: 32px;
  margin-bottom: 10px;
}

.intro-subtitle {
  color: #666;
  font-size: 18px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.feature-card {
  text-align: center;
  padding: 25px;
  border: 1px solid #eee;
  border-radius: 10px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.feature-card h3 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 18px;
}

.feature-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.quick-actions {
  text-align: center;
}

.quick-actions h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 20px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.secondary {
  background: #f8f9fa;
  color: #667eea;
  border: 2px solid #667eea;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn-icon {
  font-size: 16px;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
  }
  
  .header h1 {
    font-size: 20px;
  }
  
  .nav-content {
    padding: 0 15px;
  }
  
  .main-content {
    padding: 20px 15px;
  }
  
  .intro-card {
    padding: 25px;
  }
  
  .intro-header h2 {
    font-size: 24px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>