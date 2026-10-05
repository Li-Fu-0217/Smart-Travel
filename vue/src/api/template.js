// 行程模板接口
// 覆盖端点：GET /templates、GET /templates/{id}、POST /templates、POST /templates/{id}/copy、
//           GET /admin/templates、PUT /admin/templates/{id}、DELETE /admin/templates/{id}
import request from '../utils/request'

export function getTemplates(params) {
  return request.get('/templates', { params })
}

export function getTemplate(id) {
  return request.get(`/templates/${id}`)
}

export function publishTemplate(data) {
  return request.post('/templates', data)
}

export function copyTemplate(id, data) {
  return request.post(`/templates/${id}/copy`, data)
}

export function getAdminTemplates(params) {
  return request.get('/admin/templates', { params })
}

export function updateAdminTemplate(id, data) {
  return request.put(`/admin/templates/${id}`, data)
}

export function deleteAdminTemplate(id) {
  return request.delete(`/admin/templates/${id}`)
}
