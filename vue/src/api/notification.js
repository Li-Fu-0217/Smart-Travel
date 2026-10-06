// 站内消息接口
// 覆盖端点：GET /notifications、GET /notifications/unread-count、PUT /notifications/{id}/read、PUT /notifications/read-all
import request from '../utils/request'

export function getNotifications(params) {
  return request.get('/notifications', { params })
}

export function getUnreadCount() {
  return request.get('/notifications/unread-count')
}

export function markRead(id) {
  return request.put(`/notifications/${id}/read`)
}

export function markReadAll() {
  return request.put('/notifications/read-all')
}
