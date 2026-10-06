<template>
  <div class="page">
    <div class="toolbar">
      <h2 class="title">我的旅游记录</h2>
      <el-button type="primary" @click="distill">更新我的偏好</el-button>
    </div>
    <div class="list">
      <div v-for="r in rows" :key="r.id" class="card">
        <div class="card-head">
          <span class="dest">{{ r.destination }}</span>
          <StatusBadge type="visibility" :value="r.visibility" />
        </div>
        <div class="meta">{{ r.visitedDate }} · 评分 {{ r.rating }}</div>
        <div class="content">{{ r.content }}</div>
      </div>
      <p v-if="!rows.length" class="muted">暂无记录</p>
    </div>
    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="prev, pager, next" @current-change="load" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getRecords } from '../../api/record'
import { distillPreferences } from '../../api/traveler'
import StatusBadge from '../../components/StatusBadge.vue'

const route = useRoute()
const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const travelerId = ref(Number(route.query.travelerId) || 0)

async function load() {
  const data = await getRecords({ current: current.value, size: size.value })
  rows.value = data.records
  total.value = data.total
}

async function distill() {
  if (!travelerId.value) { ElMessage.warning('未指定旅行者'); return }
  const p = await distillPreferences(travelerId.value)
  ElMessage.success(`已提炼偏好：${p.preferenceTags || '无'}`)
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; align-items: center; justify-content: space-between; }
.title { margin: 0; font-size: var(--fs-h2); }
.list { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.dest { font-family: var(--font-serif); font-size: var(--fs-h3); }
.meta { color: var(--muted); font-size: var(--fs-aux); }
.content { margin-top: var(--sp-card-gap); }
.muted { color: var(--muted); }
.pager { display: flex; justify-content: center; }
</style>
