// 旅游记录接口
// 覆盖端点：GET /records、POST /records、PUT /records/{id}、DELETE /records/{id}、GET /admin/records
import request from '../utils/request'

export function getRecords(params) {
  return request.get('/records', { params })
}

export function createRecord(data) {
  return request.post('/records', data)
}

export function updateRecord(id, data) {
  return request.put(`/records/${id}`, data)
}

export function deleteRecord(id) {
  return request.delete(`/records/${id}`)
}

export function getAdminRecords(params) {
  return request.get('/admin/records', { params })
}
