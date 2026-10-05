// 菜单接口
// 覆盖端点：GET /menus、GET /menus/manage、POST /menus、PUT /menus/{id}、DELETE /menus/{id}、DELETE /menus/batch
import request from '../utils/request'

export function getMenus() {
  return request.get('/menus')
}

export function getManagedMenus() {
  return request.get('/menus/manage')
}

export function createMenu(data) {
  return request.post('/menus', data)
}

export function updateMenu(id, data) {
  return request.put(`/menus/${id}`, data)
}

export function deleteMenu(id) {
  return request.delete(`/menus/${id}`)
}

export function deleteMenus(ids) {
  return request.delete('/menus/batch', { data: ids })
}
