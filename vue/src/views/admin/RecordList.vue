<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索目的地" clearable class="search" @keyup.enter="load" @clear="load" />
      <el-button type="primary" @click="load">搜索</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="travelerName" label="旅行者" width="120" />
        <el-table-column prop="destination" label="目的地" />
        <el-table-column prop="visitedDate" label="到访日期" width="120" />
        <el-table-column prop="rating" label="评分" width="80" />
        <el-table-column label="可见性" width="110">
          <template #default="{ row }"><StatusBadge type="visibility" :value="row.visibility" /></template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="170" />
        <el-table-column label="操作" width="90">
          <template #default="{ row }">
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="total, prev, pager, next" @current-change="load" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminRecords, deleteRecord } from '../../api/record'
import StatusBadge from '../../components/StatusBadge.vue'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const keyword = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await getAdminRecords({ current: current.value, size: size.value })
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function confirmDelete(row) {
  try { await ElMessageBox.confirm(`确认删除「${row.destination || '该条'}」的记录？`, '提示', { type: 'warning' }) } catch { return }
  await deleteRecord(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; gap: var(--sp-card-gap); align-items: center; }
.search { width: 220px; }
.table-wrap { overflow-x: auto; }
.pager { display: flex; justify-content: flex-end; }
</style>
