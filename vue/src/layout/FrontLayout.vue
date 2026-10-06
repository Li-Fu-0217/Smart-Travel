<template>
  <div class="front-layout" data-scope="front">
    <header class="topbar">
      <div class="brand">智慧旅游智能助手</div>
      <nav class="nav">
        <router-link v-for="n in nav" :key="n.path" :to="n.path" class="nav-item">
          {{ n.name }}
        </router-link>
      </nav>
      <router-link to="/user/notifications" class="bell" aria-label="消息中心">
        <span class="bell-dot" v-if="unread > 0">{{ unread > 99 ? '99+' : unread }}</span>
      </router-link>
      <ThemeSwitcher />
      <div class="logout" @click="handleLogout">退出</div>
    </header>
    <main class="content">
      <router-view />
    </main>
    <nav class="tabbar">
      <router-link v-for="n in nav" :key="n.path" :to="n.path" class="tab-item">{{ n.name }}</router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FRONT_NAV } from '../config/frontNav'
import { useUserStore } from '../store/user'
import { getUnreadCount } from '../api/notification'
import ThemeSwitcher from '../components/ThemeSwitcher.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const nav = FRONT_NAV
const unread = ref(0)

async function refreshUnread() {
  try {
    unread.value = await getUnreadCount()
  } catch (e) {
    unread.value = 0
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

onMounted(refreshUnread)
watch(() => route.fullPath, refreshUnread)
</script>

<style scoped>
.front-layout { min-height: 100%; background: var(--bg); color: var(--ink); font-family: var(--font-sans); padding-bottom: var(--sp-section); }
.topbar { display: flex; align-items: center; gap: var(--sp-card-inner); padding: var(--sp-card-gap) var(--sp-card-inner); background: var(--surface); border-bottom: 1px solid var(--line); }
.brand { font-family: var(--font-serif); font-size: var(--fs-h2); font-weight: 600; }
.nav { display: flex; gap: var(--sp-card-gap); flex-wrap: wrap; }
.nav-item { padding: var(--sp-card-gap); border-radius: var(--r-btn-pill); color: var(--muted); }
.nav-item.router-link-active { background: var(--surface-2); color: var(--accent); }
.bell { position: relative; min-width: var(--min-tap); min-height: var(--min-tap); display: inline-flex; align-items: center; justify-content: center; color: var(--muted); }
.bell::before { content: ''; width: var(--fs-h2); height: var(--fs-h2); border: 2px solid currentColor; border-radius: var(--r-btn-pill) var(--r-btn-pill) var(--r-btn-pill) var(--r-btn-pill); }
.bell-dot { position: absolute; top: 4px; right: 4px; min-width: var(--fs-body); height: var(--fs-body); padding: 0 3px; border-radius: var(--r-btn-pill); background: var(--danger); color: var(--on-color); font-size: var(--fs-caption); line-height: 1; display: inline-flex; align-items: center; justify-content: center; }
.logout { margin-left: auto; color: var(--danger); cursor: pointer; }
.content { padding: var(--sp-card-inner); }
.tabbar { display: none; position: fixed; left: 0; right: 0; bottom: 0; background: var(--surface); border-top: 1px solid var(--line); z-index: 10; }
.tab-item { flex: 1; min-height: var(--min-tap); display: flex; align-items: center; justify-content: center; font-size: var(--fs-caption); color: var(--muted); }
.tab-item.router-link-active { color: var(--accent); }
@media (max-width: 768px) {
  .nav { display: none; }
  .tabbar { display: flex; overflow-x: auto; }
}
</style>
