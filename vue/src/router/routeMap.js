// 路径 → 页面组件登记表（见施工规范 §7.2、§7.4）
// ⚠️ 后台 14 条路径与后端 common/menu_paths.py 白名单、sys_menu 种子三者一致，勿改名（避坑 18）
// 组件在阶段 4.1/4.2 逐步替换为真实页面，暂用占位组件
const placeholder = () => import('../views/common/PagePlaceholder.vue')

export const routeMap = {
  // ===== 后台 14 条（照 sys_menu 原名）=====
  '/admin/dashboard': () => import('../views/admin/dashboard.vue'),
  '/admin/travelers': () => import('../views/admin/TravelerList.vue'),
  '/admin/trips': () => import('../views/admin/TripList.vue'),
  '/admin/templates': () => import('../views/admin/TemplateList.vue'),
  '/admin/bookings': () => import('../views/admin/BookingList.vue'),
  '/admin/groups': () => import('../views/admin/GroupTourList.vue'),
  '/admin/alerts': () => import('../views/admin/AlertList.vue'),
  '/admin/guides': placeholder,      // 阶段 5
  '/admin/records': () => import('../views/admin/RecordList.vue'),
  '/admin/agent-tools': placeholder, // 阶段 6
  '/admin/agent-logs': placeholder,  // 阶段 6
  '/admin/users': () => import('../views/admin/UserList.vue'),
  '/admin/logs': () => import('../views/admin/SystemLogList.vue'),
  '/admin/menus': () => import('../views/admin/MenuList.vue'),

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
