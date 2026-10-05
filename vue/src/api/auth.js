// 认证接口
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
