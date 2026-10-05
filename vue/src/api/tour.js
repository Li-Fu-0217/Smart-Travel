// 拼团活动接口
// 覆盖端点：GET /tours、POST /tours/{id}/signup、GET /tours/my-signups、
//           GET/POST /admin/tours、PUT/DELETE /admin/tours/{id}、GET /admin/tours/signups
import request from '../utils/request'

export function getTours() {
  return request.get('/tours')
}

export function signupTour(id, data) {
  return request.post(`/tours/${id}/signup`, data)
}

export function getMySignups() {
  return request.get('/tours/my-signups')
}

export function getAdminTours(params) {
  return request.get('/admin/tours', { params })
}

export function createAdminTour(data) {
  return request.post('/admin/tours', data)
}

export function updateAdminTour(id, data) {
  return request.put(`/admin/tours/${id}`, data)
}

export function deleteAdminTour(id) {
  return request.delete(`/admin/tours/${id}`)
}

export function getAdminSignups(params) {
  return request.get('/admin/tours/signups', { params })
}
