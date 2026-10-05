// 认证接口
// 覆盖端点：GET /auth/captcha、POST /auth/login、POST /auth/register、GET /auth/me
import request from '../utils/request'

export function getCaptcha() {
  return request.get('/auth/captcha')
}

export function login(data) {
  return request.post('/auth/login', data)
}

export function register(data) {
  return request.post('/auth/register', data)
}

export function getMe() {
  return request.get('/auth/me')
}
