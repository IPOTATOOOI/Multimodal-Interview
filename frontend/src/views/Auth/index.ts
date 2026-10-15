import axios from 'axios'
import { API_BASE_URL } from '@/config/api'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
})

// 请求拦截器（自动添加Token）
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_access_token') || localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器（处理401错误）
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_access_token')
      localStorage.removeItem('access_token')
      // 使用window.location.reload()或路由重定向到登录页
      window.location.reload() // 强制刷新跳转登录
    }
    return Promise.reject(error)
  },
)

export default api
