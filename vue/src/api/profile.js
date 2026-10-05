// 个人中心接口
// 覆盖端点：PUT /profile、PUT /profile/avatar、PUT /profile/password
import request from '../utils/request'

export function updateProfile(data) {
  return request.put('/profile', data)
}

export function updateAvatar(data) {
  return request.put('/profile/avatar', data)
}

export function updatePassword(data) {
  return request.put('/profile/password', data)
}
