<template>
  <div class="front-layout" data-scope="front">
    <header class="topbar">
      <div class="brand">智慧旅游智能助手</div>
      <nav class="nav">
        <router-link v-for="n in nav" :key="n.path" :to="n.path" class="nav-item">
          {{ n.name }}
        </router-link>
      </nav>
      <ThemeSwitcher />
      <div class="logout" @click="handleLogout">退出</div>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { FRONT_NAV } from '../config/frontNav'
import { useUserStore } from '../store/user'
import ThemeSwitcher from '../components/ThemeSwitcher.vue'

const router = useRouter()
const userStore = useUserStore()
const nav = FRONT_NAV

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.front-layout { min-height: 100%; background: var(--bg); color: var(--ink); font-family: var(--font-sans); }
.topbar { display: flex; align-items: center; gap: 16px; padding: 12px 16px; background: var(--surface); border-bottom: 1px solid var(--line); }
.brand { font-family: var(--font-serif); font-size: 22px; font-weight: 600; }
.nav { display: flex; gap: 8px; flex-wrap: wrap; }
.nav-item { padding: 10px 12px; border-radius: 999px; color: var(--muted); }
.nav-item.router-link-active { background: var(--surface-2); color: var(--accent); }
.logout { margin-left: auto; color: var(--danger); cursor: pointer; }
.content { padding: 16px; }
</style>
