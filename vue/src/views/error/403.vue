<template>
  <div class="forbidden">
    <h1>403</h1>
    <p class="muted">没有权限访问该页面</p>
    <el-button type="primary" @click="goHome">返回首页</el-button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'

const router = useRouter()
const userStore = useUserStore()

function goHome() {
  router.push(userStore.isAdmin ? '/admin/dashboard' : '/user/home')
}
</script>

<style scoped>
.forbidden { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100%; background: var(--bg); gap: 12px; }
h1 { font-size: 56px; margin: 0; color: var(--danger); }
.muted { color: var(--muted); }
</style>
