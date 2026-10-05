// 预约接口
// 覆盖端点：GET /booking/catalog、GET /booking/slots、POST /booking/orders、GET /booking/orders、
//           GET /booking/orders/{id}、POST /booking/orders/{id}/cancel、
//           GET/POST /admin/booking/catalog、PUT/DELETE /admin/booking/catalog/{id}、
//           GET /admin/booking/orders、PUT /admin/booking/orders/{id}
import request from '../utils/request'

export function getCatalog() {
  return request.get('/booking/catalog')
}

export function getSlots(params) {
  return request.get('/booking/slots', { params })
}

export function createOrder(data) {
  return request.post('/booking/orders', data)
}

export function getOrders(params) {
  return request.get('/booking/orders', { params })
}

export function getOrder(id) {
  return request.get(`/booking/orders/${id}`)
}

export function cancelOrder(id) {
  return request.post(`/booking/orders/${id}/cancel`)
}

export function getAdminCatalog(params) {
  return request.get('/admin/booking/catalog', { params })
}

export function createAdminCatalog(data) {
  return request.post('/admin/booking/catalog', data)
}

export function updateAdminCatalog(id, data) {
  return request.put(`/admin/booking/catalog/${id}`, data)
}

export function deleteAdminCatalog(id) {
  return request.delete(`/admin/booking/catalog/${id}`)
}

export function getAdminOrders(params) {
  return request.get('/admin/booking/orders', { params })
}

export function updateAdminOrder(id, data) {
  return request.put(`/admin/booking/orders/${id}`, data)
}
