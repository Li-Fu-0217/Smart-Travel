// 家庭绑定接口
// 覆盖端点：GET /family/my-travelers、GET /family/bindings、POST /family/bind、DELETE /family/bindings/{id}、
//           GET /admin/family、POST /admin/family、DELETE /admin/family/{id}
import request from '../utils/request'

export function getMyTravelers() {
  return request.get('/family/my-travelers')
}

export function getBindings() {
  return request.get('/family/bindings')
}

export function bindTraveler(data) {
  return request.post('/family/bind', data)
}

export function unbind(id) {
  return request.delete(`/family/bindings/${id}`)
}

export function getAdminFamily(params) {
  return request.get('/admin/family', { params })
}

export function adminBind(data) {
  return request.post('/admin/family', data)
}

export function adminUnbind(id) {
  return request.delete(`/admin/family/${id}`)
}
