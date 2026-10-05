// 旅行者档案接口（登录级，数据隔离）+ 偏好提炼
// 覆盖端点：GET /travelers、GET /travelers/{id}、GET /travelers/{id}/profile、POST /travelers、
//           PUT /travelers/{id}、DELETE /travelers/{id}、POST /travelers/{id}/preferences/distill、PUT /travelers/{id}/preferences
import request from '../utils/request'

export function getTravelers(params) {
  return request.get('/travelers', { params })
}

export function getTraveler(id) {
  return request.get(`/travelers/${id}`)
}

export function getTravelerProfile(id) {
  return request.get(`/travelers/${id}/profile`)
}

export function createTraveler(data) {
  return request.post('/travelers', data)
}

export function updateTraveler(id, data) {
  return request.put(`/travelers/${id}`, data)
}

export function deleteTraveler(id) {
  return request.delete(`/travelers/${id}`)
}

export function distillPreferences(id) {
  return request.post(`/travelers/${id}/preferences/distill`)
}

export function updatePreferences(id, tags) {
  return request.put(`/travelers/${id}/preferences`, { tags })
}
