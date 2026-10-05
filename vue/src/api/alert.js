// 旅途求助接口
// 覆盖端点：POST /alerts/sos、GET /alerts、GET /admin/alerts、PUT /admin/alerts/{id}
import request from '../utils/request'

export function sos(data) {
  return request.post('/alerts/sos', data)
}

export function getAlerts(params) {
  return request.get('/alerts', { params })
}

export function getAdminAlerts(params) {
  return request.get('/admin/alerts', { params })
}

export function updateAdminAlert(id, data) {
  return request.put(`/admin/alerts/${id}`, data)
}
