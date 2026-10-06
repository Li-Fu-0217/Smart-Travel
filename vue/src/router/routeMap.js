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
  '/admin/guides': () => import('../views/admin/GuideList.vue'),
  '/admin/records': () => import('../views/admin/RecordList.vue'),
  '/admin/agent-tools': () => import('../views/admin/AgentToolList.vue'),
  '/admin/agent-logs': () => import('../views/admin/AgentLogList.vue'),
  '/admin/users': () => import('../views/admin/UserList.vue'),
  '/admin/logs': () => import('../views/admin/SystemLogList.vue'),
  '/admin/menus': () => import('../views/admin/MenuList.vue'),

  // ===== 前台 11 条（8 导航 + 3 隐藏入口，见 §7.4）=====
  '/user/home': () => import('../views/front/home.vue'),
  '/user/dashboard': () => import('../views/front/TravelerDashboard.vue'),
  '/user/trips': () => import('../views/front/TripPlanner.vue'),
  '/user/today': () => import('../views/front/TripToday.vue'),
  '/user/templates': () => import('../views/front/TripTemplates.vue'),
  '/user/bookings': () => import('../views/front/UserBookings.vue'),
  '/user/groups': () => import('../views/front/UserGroups.vue'),
  '/user/chat': () => import('../views/front/AgentChat.vue'),
  '/user/traveler-detail': () => import('../views/front/TravelerDetail.vue'),
  '/user/records': () => import('../views/front/MyRecords.vue'),
  '/user/notifications': () => import('../views/front/UserNotifications.vue'),

  // ===== 隐藏页 =====
  '/user/403': () => import('../views/error/403.vue'),
  '/admin/403': () => import('../views/error/403.vue'),
}
