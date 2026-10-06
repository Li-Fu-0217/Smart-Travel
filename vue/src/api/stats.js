// 看板统计接口（见施工规范 §4.5、§7.7）
// 覆盖端点：GET /admin/stats（管理端）、GET /stats/dashboard（用户前台）
import request from '../utils/request'

export function getAdminStats() {
  return request.get('/admin/stats')
}

export function getFrontDashboard() {
  return request.get('/stats/dashboard')
}
