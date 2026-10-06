<template>
  <div class="home">
    <!-- 1. 品牌问候区 -->
    <section class="greet">
      <h1 class="greet-title">{{ greeting }}</h1>
      <p class="greet-sub">{{ travelerName ? `正在为「${travelerName}」安排出行` : '绑定家人后，助手可为全家安排行程' }}</p>
    </section>

    <!-- 2. 搜索入口 -->
    <section class="search">
      <el-input v-model="query" placeholder="搜索目的地攻略（如：申根签证）" clearable class="search-input" @keyup.enter="doSearch">
        <template #append><el-button @click="doSearch">搜索</el-button></template>
      </el-input>
    </section>

    <!-- 3. 快捷入口宫格 -->
    <section class="shortcuts">
      <router-link v-for="n in shortcuts" :key="n.path" :to="n.path" class="shortcut">
        <el-icon class="shortcut-icon"><component :is="n.icon" /></el-icon>
        <span class="shortcut-name">{{ n.name }}</span>
      </router-link>
    </section>

    <!-- 4. 目的地精选（去过的目的地，CSS 渐变封面） -->
    <section v-if="dests.length" class="block">
      <h2 class="block-title">去过的目的地</h2>
      <div class="dest-grid">
        <div v-for="d in dests" :key="d" class="dest-card" :style="{ background: destinationTheme(d).gradient }" @click="searchDest(d)">
          <span class="dest-name">{{ d }}</span>
        </div>
      </div>
    </section>

    <!-- 5. 精选榜单（热门模板） -->
    <section v-if="topTemplates.length" class="block">
      <h2 class="block-title">热门行程模板</h2>
      <div class="tpl-list">
        <router-link v-for="t in topTemplates" :key="t.id" to="/user/templates" class="tpl-card">
          <div class="tpl-cover" :style="{ background: destinationTheme(t.destination).gradient }"></div>
          <div class="tpl-body">
            <span class="tpl-title">{{ t.title }}</span>
            <span class="tpl-meta">{{ t.destination }} · {{ t.dayCount }} 天 · 已用 {{ t.useCount }} 次</span>
          </div>
        </router-link>
      </div>
    </section>

    <!-- 6. 智能助手 CTA -->
    <section class="cta" :style="{ background: cover.gradient }">
      <h2 class="cta-title">让智能助手帮你安排</h2>
      <p class="cta-sub">查待办、约体验、推荐行程，一句对话搞定</p>
      <el-button type="primary" class="cta-btn" @click="$router.push('/user/chat')">去对话</el-button>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FRONT_NAV } from '../../config/frontNav'
import { destinationTheme } from '../../config/destinationThemes'
import { getMyTravelers } from '../../api/family'
import { getRecords } from '../../api/record'
import { getTemplates } from '../../api/template'

const router = useRouter()
const query = ref('')
const travelers = ref([])
const records = ref([])
const templates = ref([])

const shortcuts = FRONT_NAV.filter((n) => n.path !== '/user/home' && n.path !== '/user/chat')
const cover = destinationTheme('海岛')

const travelerName = computed(() => travelers.value[0]?.name || '')
const greeting = computed(() => (travelerName.value ? `你好，${travelerName.value}` : '你好'))

// 去过的目的地（去重，最多 6 个）
const dests = computed(() => [...new Set(records.value.map((r) => r.destination).filter(Boolean))].slice(0, 6))

// 热门模板（按被使用次数倒序，取前 3）
const topTemplates = computed(() => [...templates.value].sort((a, b) => b.useCount - a.useCount).slice(0, 3))

function doSearch() {
  const q = query.value.trim()
  if (q) router.push(`/user/chat?q=${encodeURIComponent(q)}`)
}

function searchDest(d) {
  router.push(`/user/chat?q=${encodeURIComponent(`去${d}要注意什么`)}`)
}

onMounted(async () => {
  try { travelers.value = await getMyTravelers() } catch { /* 空态 */ }
  try { const d = await getRecords({ current: 1, size: 100 }); records.value = d.records || [] } catch { /* 空态 */ }
  try { templates.value = await getTemplates() } catch { /* 空态 */ }
})
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: var(--sp-section); }
.greet { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.greet-title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h1); }
.greet-sub { margin: 0; color: var(--muted); font-size: var(--fs-body); }
.search-input { max-width: 480px; }
.shortcuts { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--sp-card-gap); }
.shortcut {
  min-height: var(--min-tap);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: var(--sp-card-gap); background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--r-card); padding: var(--sp-card-inner); font-size: var(--fs-aux);
  text-decoration: none; color: var(--ink);
}
.shortcut-icon { font-size: var(--fs-h2); color: var(--accent); }
.block { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.block-title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h2); }
.dest-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--sp-card-gap); }
.dest-card {
  min-height: 96px; display: flex; align-items: flex-end; padding: var(--sp-card-inner);
  border-radius: var(--r-card); color: var(--on-color); cursor: pointer;
}
.dest-name { font-family: var(--font-serif); font-size: var(--fs-h3); }
.tpl-list { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.tpl-card { display: flex; gap: var(--sp-card-gap); background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); overflow: hidden; text-decoration: none; color: var(--ink); }
.tpl-cover { width: 88px; flex-shrink: 0; }
.tpl-body { display: flex; flex-direction: column; justify-content: center; gap: var(--sp-card-gap); padding: var(--sp-card-inner); }
.tpl-title { font-family: var(--font-serif); font-size: var(--fs-h3); }
.tpl-meta { color: var(--muted); font-size: var(--fs-aux); }
.cta { border-radius: var(--r-card-lg); padding: var(--sp-section) var(--sp-card-inner); display: flex; flex-direction: column; align-items: flex-start; gap: var(--sp-card-gap); color: var(--on-color); }
.cta-title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h2); }
.cta-sub { margin: 0; opacity: 0.9; font-size: var(--fs-body); }
.cta-btn { min-height: var(--min-tap); }
@media (min-width: 768px) {
  .shortcuts { grid-template-columns: repeat(6, 1fr); }
  .dest-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
