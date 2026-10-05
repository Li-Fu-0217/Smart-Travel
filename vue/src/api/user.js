// 用户管理接口（管理员）
// 覆盖端点：GET /users、GET /users/{id}、POST /users、PUT /users/{id}、DELETE /users/{id}、DELETE /users/batch
import request from '../utils/request'

export function getUsers(params) {
  return request.get('/users', { params })
}

export function getUser(id) {
  return request.get(`/users/${id}`)
}

export function createUser(data) {
  return request.post('/users', data)
}

export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

export function deleteUsers(ids) {
  return request.delete('/users/batch', { data: ids })
}
