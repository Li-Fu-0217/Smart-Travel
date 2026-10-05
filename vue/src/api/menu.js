// 菜单接口
import request from '../utils/request'

export function getMenus() {
  return request.get('/menus')
}
