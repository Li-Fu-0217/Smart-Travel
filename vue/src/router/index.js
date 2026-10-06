// 路由与全局守卫（见施工规范 §7.2）
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'
import { getToken } from '../utils/auth'
import { setupDynamicRoutes, resetDynamicRoutes } from './dynamicRoutes'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/login/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/login/Register.vue') },
  {
    path: '/admin',
    name: 'AdminLayout',
    component: () => import('../layout/AdminLayout.vue'),
    meta: { scope: 'admin' },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/dashboard.vue'),
        meta: { title: '数据概览' },
      },
    ],
  },
  { path: '/admin/403', name: 'Admin403', component: () => import('../views/error/403.vue'), meta: { scope: 'admin' } },
  {
    path: '/user',
    name: 'FrontLayout',
    component: () => import('../layout/FrontLayout.vue'),
    meta: { scope: 'user' },
    children: [
      {
        path: 'home',
        name: 'UserHome',
        component: () => import('../views/front/home.vue'),
        meta: { title: '首页' },
      },
    ],
  },
  { path: '/user/403', name: 'User403', component: () => import('../views/error/403.vue'), meta: { scope: 'user' } },
  { path: '/', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

let dynamicReady = false
const publicPages = ['/login', '/register']

router.beforeEach(async (to) => {
  const userStore = useUserStore()
  const token = getToken()

  // 有 token 但本地用户信息丢失 → 先拉取最新信息，再按真实角色判断
  if (token && !userStore.userInfo) {
    try {
      await userStore.fetchMe()
    } catch (e) {
      /* 拉取失败由请求拦截器兜底跳登录，此处不阻断 */
    }
  }

  // 1. 无 token 且非公开页 → 登录
  if (!token && !publicPages.includes(to.path)) {
    return '/login'
  }
  // 2. 有 token 访问登录/注册 → 按角色跳首页
  if (token && publicPages.includes(to.path)) {
    return userStore.isAdmin ? '/admin/dashboard' : '/user/home'
  }
  // 3. 已登录但动态路由未就绪 → 拉菜单注入
  if (token && !dynamicReady) {
    try {
      await setupDynamicRoutes(router, userStore)
    } catch (e) {
      /* 菜单拉取失败不阻断，仅静态路由可用 */
    }
    dynamicReady = true
    return { ...to, replace: true }
  }
  // 4. 跨端拦截（角色互斥）
  if (to.meta.scope === 'admin' && !userStore.isAdmin) {
    return '/user/403'
  }
  if (to.meta.scope === 'user' && userStore.isAdmin) {
    return '/admin/403'
  }
  return true
})

// body 也带 data-scope，让 body 背景色随主题/端变化（§7.9.10）
router.afterEach((to) => {
  document.body.setAttribute('data-scope', to.meta.scope === 'admin' ? 'admin' : 'front')
})

export function markDynamicReset() {
  dynamicReady = false
  resetDynamicRoutes(router)
}

export default router
