// 角色接口（仅查询）
// 覆盖端点：GET /roles
import request from '../utils/request'

export function getRoles() {
  return request.get('/roles')
}
