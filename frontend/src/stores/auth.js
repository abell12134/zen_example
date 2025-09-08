import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  
  // 计算属性
  const isAuthenticated = computed(() => {
    return !!token.value && !!user.value
  })
  
  // 动作
  const login = async (phone, password) => {
    try {
      // 固定管理员账号验证
      if (phone === 'admin' && password === 'Huawei123456') {
        const mockToken = 'admin-token-' + Date.now()
        token.value = mockToken
        user.value = { phone: 'admin', id: 'admin', role: 'admin' }
        
        // 保存到localStorage
        localStorage.setItem('token', mockToken)
        localStorage.setItem('user', JSON.stringify(user.value))
        
        return { success: true }
      } else {
        throw new Error('用户名或密码错误')
      }
    } catch (error) {
      return { success: false, message: error.message }
    }
  }
  
  // 注册功能已关闭
  
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  const initAuth = () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    initAuth
  }
})