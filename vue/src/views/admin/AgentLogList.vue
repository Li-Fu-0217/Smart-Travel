<template>
  <div class="page">
    <h2 class="title">助手日志</h2>
    <div class="toolbar">
      <el-select v-model="toolName" clearable placeholder="按工具名筛选" class="tool" @change="reload">
        <el-option v-for="t in tools" :key="t.name" :label="t.label" :value="t.name" />
      </el-select>
      <el-input v-model="sessionId" placeholder="按会话 ID 筛选" clearable class="sess" @keyup.enter="reload" />
      <el-button type="primary" @click="reload">查询</el-button>
    </div>

    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="toolName" label="工具名" width="180" />
        <el-table-column prop="sessionId" label="会话" min-width="200" show-overflow-tooltip />
        <el-table-column prop="costMs" label="耗时(ms)" width="90" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><StatusBadge type="agent" :value="row.status" /></template>
        </el-table-column>
        <el-table-column prop="createTime" label="时间" width="170" />
      </el-table>
    </div>

    <div class="cards">
      <div v-for="r in rows" :key="r.id" class="card">
        <div class="card-head"><span class="tn">{{ r.toolName }}</span><StatusBadge type="agent" :value="r.status" /></div>
        <div class="card-meta">会话 {{ r.sessionId }}</div>
        <div class="card-meta">{{ r.costMs }}ms · {{ r.createTime }}</div>
      </div>
      <p v-if="!rows.length" class="empty">暂无日志</p>
    </div>

    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="total, prev, pager, next" @current-change="load" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAgentTools, getAgentToolLogs } from '../../api/agent'
import StatusBadge from '../../components/StatusBadge.vue'

const tools = ref([])
const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const toolName = ref('')
const sessionId = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const params = { current: current.value, size: size.value }
    if (toolName.value) params.toolName = toolName.value
    if (sessionId.value) params.sessionId = sessionId.value
    const data = await getAgentToolLogs(params)
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function reload() {
  current.value = 1
  load()
}

onMounted(async () => {
  tools.value = await getAgentTools()
  await load()
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h1); }
.toolbar { display: flex; flex-wrap: wrap; gap: var(--sp-card-gap); align-items: center; }
.tool { width: 200px; }
.sess { width: 260px; }
.table-wrap { overflow-x: auto; }
.pager { display: flex; justify-content: flex-end; }
.cards { display: none; }
.card {
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
  padding: var(--sp-card-inner);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-card);
}
.card-head { display: flex; align-items: center; justify-content: space-between; }
.tn { font-weight: 600; font-family: var(--font-mono, monospace); }
.card-meta { color: var(--muted); font-size: var(--fs-aux); word-break: break-all; }
.empty { color: var(--muted); }
@media (max-width: 768px) {
  .table-wrap { display: none; }
  .cards { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
}
</style>
