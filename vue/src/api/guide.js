// 攻略库接口
// 覆盖端点：POST /guides/query、GET/POST /admin/guides/documents、GET /admin/guides/documents/{id}/chunks、DELETE /admin/guides/documents/{id}
import request from '../utils/request'

export function queryGuide(text) {
  return request.post('/guides/query', { text })
}

export function getDocuments(params) {
  return request.get('/admin/guides/documents', { params })
}

export function createDocument(data) {
  return request.post('/admin/guides/documents', data)
}

export function getChunks(id) {
  return request.get(`/admin/guides/documents/${id}/chunks`)
}

export function deleteDocument(id) {
  return request.delete(`/admin/guides/documents/${id}`)
}
