// 动态路由（见施工规范 §7.2）：登录后按菜单 addRoute，登出移除
import { getMenus } from '../api/menu'
import { routeMap } from './routeMap'

const fallback = () => import('../views/common/PagePlaceholder.vue')

export async function setupDynamicRoutes(router, userStore) {
  if (!userStore.isAdmin) return
  const menus = await getMenus()
  for (const m of menus) {
    const childPath = m.path.replace('/admin/', '')
    if (router.hasRoute('menu-' + m.id)) continue
    router.addRoute('AdminLayout', {
      path: childPath,
      name: 'menu-' + m.id,
      component: routeMap[m.path] || fallback,
      meta: { title: m.name },
    })
  }
}

export function resetDynamicRoutes(router) {
  const names = router.getRoutes().map((r) => r.name)
  for (const name of names) {
    if (typeof name === 'string' && name.startsWith('menu-')) {
      router.removeRoute(name)
    }
  }
}
