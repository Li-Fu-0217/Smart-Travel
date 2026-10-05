// 路径 → 页面组件登记表（见施工规范 §7.2、§7.4）
// ⚠️ 后台 14 条路径与后端 common/menu_paths.py 白名单、sys_menu 种子三者一致，勿改名（避坑 18）
// 组件在阶段 4.1/4.2 逐步替换为真实页面，暂用占位组件
const placeholder = () => import('../views/common/PagePlaceholder.vue')

export const routeMap = {
  // ===== 后台 14 条（照 sys_menu 原名）=====
  '/admin/dashboard': () => import('../views/admin/dashboard.vue'),
  '/admin/travelers': placeholder,
  '/admin/trips': placeholder,
  '/admin/templates': placeholder,
  '/admin/bookings': placeholder,
  '/admin/groups': placeholder,
  '/admin/alerts': placeholder,
  '/admin/guides': placeholder,
  '/admin/records': placeholder,
  '/admin/agent-tools': placeholder,
  '/admin/agent-logs': placeholder,
  '/admin/users': placeholder,
  '/admin/logs': placeholder,
  '/admin/menus': placeholder,

  // ===== 前台 11 条（8 导航 + 3 隐藏入口，见 §7.4）=====
  '/user/home': () => import('../views/front/home.vue'),
  '/user/dashboard': placeholder,
  '/user/trips': placeholder,
  '/user/today': placeholder,
  '/user/templates': placeholder,
  '/user/bookings': placeholder,
  '/user/groups': placeholder,
  '/user/chat': placeholder,
  '/user/traveler-detail': placeholder,   // TravelerDetail（看板卡片点入）
  '/user/records': placeholder,           // MyRecords（看板入口点入）
  '/user/notifications': placeholder,     // UserNotifications（消息铃铛点入）

  // ===== 隐藏页 =====
  '/user/403': () => import('../views/error/403.vue'),
  '/admin/403': () => import('../views/error/403.vue'),
}
