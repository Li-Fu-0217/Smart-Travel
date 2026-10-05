// 系统日志接口（管理员）
// 覆盖端点：GET /logs、DELETE /logs/batch
import request from '../utils/request'

export function getLogs(params) {
  return request.get('/logs', { params })
}

export function deleteLogs(type, ids) {
  return request.delete('/logs/batch', { data: { type, ids } })
}
