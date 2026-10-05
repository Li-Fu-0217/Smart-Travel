// Axios 封装（见施工规范 §7.3）
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './auth'

const request = axios.create({
  baseURL: '/api',
  timeout: 20000,
})

// 请求拦截：注入 token
request.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let lastError = { msg: '', ts: 0 }

// 响应拦截：剥壳 {code, message, data}
request.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data || {}
    if (code === 200) {
      return data
    }
    showError(message || '请求失败')
    if (code === 401) {
      removeToken()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(new Error(message || '请求失败'))
  },
  (error) => {
    const data = error.response?.data
    const status = error.response?.status
    if (status === 401 && data?.code === 401) {
      showError(data.message || '登录已过期')
      removeToken()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else if (data && data.message) {
      showError(data.message)
    } else {
      showError('后端未启动或网络异常')
    }
    return Promise.reject(error)
  },
)

// 错误提示去重（避免同一错误弹多次）
function showError(msg) {
  const now = Date.now()
  if (msg === lastError.msg && now - lastError.ts < 2000) {
    return
  }
  lastError = { msg, ts: now }
  ElMessage.error(msg)
}

export default request
