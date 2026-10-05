<template>
  <div class="admin-layout" data-scope="admin">
    <aside class="sidebar">
      <div class="brand">智慧旅游智能助手</div>
      <nav>
        <router-link v-for="m in menus" :key="m.path" :to="m.path" class="nav-item">
          {{ m.name }}
        </router-link>
      </nav>
      <div class="logout" @click="handleLogout">退出登录</div>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMenus } from '../api/menu'
import { useUserStore } from '../store/user'
import { markDynamicReset } from '../router'

const router = useRouter()
const userStore = useUserStore()
const menus = ref([])

async function handleLogout() {
  userStore.logout()
  markDynamicReset()
  router.push('/login')
}

onMounted(async () => {
  try {
    menus.value = await getMenus()
  } catch (e) {
    menus.value = []
  }
})
</script>

<style scoped>
.admin-layout { display: flex; height: 100%; background: var(--bg); color: var(--ink); }
.sidebar { width: 200px; background: var(--surface); border-right: 1px solid var(--line); padding: 16px; }
.brand { font-weight: 600; margin-bottom: 16px; }
.nav-item { display: block; padding: 10px 12px; border-radius: 8px; color: var(--muted); }
.nav-item.router-link-active { background: var(--surface-2); color: var(--accent); }
.logout { margin-top: 24px; cursor: pointer; color: var(--danger); }
.content { flex: 1; overflow: auto; padding: 20px; }
</style>
