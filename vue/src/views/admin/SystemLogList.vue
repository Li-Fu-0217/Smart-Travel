<template>
  <div class="page">
    <div class="toolbar">
      <el-select v-model="type" class="type" @change="load">
        <el-option label="登录日志" value="login" />
        <el-option label="操作日志" value="operation" />
      </el-select>
      <el-button type="primary" @click="load">刷新</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户" width="120" />
        <template v-if="type === 'operation'">
          <el-table-column prop="module" label="模块" width="120" />
          <el-table-column prop="action" label="动作" width="120" />
          <el-table-column prop="url" label="URL" />
          <el-table-column prop="costMs" label="耗时(ms)" width="100" />
        </template>
        <template v-else>
          <el-table-column prop="message" label="结果" />
          <el-table-column prop="ip" label="IP" width="140" />
        </template>
        <el-table-column prop="createTime" label="时间" width="170" />
      </el-table>
    </div>
    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="total, prev, pager, next" @current-change="load" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLogs } from '../../api/log'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const type = ref('login')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await getLogs({ type: type.value, current: current.value, size: size.value })
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; gap: var(--sp-card-gap); align-items: center; }
.type { width: 160px; }
.table-wrap { overflow-x: auto; }
.pager { display: flex; justify-content: flex-end; }
</style>
