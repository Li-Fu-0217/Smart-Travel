// 路径 → 页面组件登记表（见施工规范 §7.2，所有页面先在这里登记）
export const routeMap = {
  '/admin/dashboard': () => import('../views/admin/dashboard.vue'),
  '/user/home': () => import('../views/front/home.vue'),
  '/user/403': () => import('../views/error/403.vue'),
  '/admin/403': () => import('../views/error/403.vue'),
  // 阶段 4 补齐其余后台页与前台页
}
