<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索标题/目的地" clearable class="search" @keyup.enter="load" @clear="load" />
      <el-button type="primary" @click="load">搜索</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="destination" label="目的地" width="120" />
        <el-table-column prop="travelerId" label="旅行者ID" width="90" />
        <el-table-column prop="startDate" label="开始" width="120" />
        <el-table-column prop="endDate" label="结束" width="120" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><StatusBadge type="trip" :value="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="110">
          <template #default="{ row }">
            <el-button link type="primary" @click="openTodos(row)">待办</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="total, prev, pager, next" @current-change="load" />
    </div>

    <el-dialog v-model="todoVisible" :title="`待办（${todoTitle}）`" width="560px">
      <el-table :data="todos" v-loading="todoLoading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="itemName" label="事项" />
        <el-table-column prop="dueTime" label="截止" width="170" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <StatusBadge v-if="row.status === 2 && overdue(row.dueTime)" type="todo" :value="2" />
            <StatusBadge v-else type="todo" :value="row.status" />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTrips, getTripTodos, deleteTrip } from '../../api/trip'
import StatusBadge from '../../components/StatusBadge.vue'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const keyword = ref('')
const loading = ref(false)
const todoVisible = ref(false)
const todoTitle = ref('')
const todos = ref([])
const todoLoading = ref(false)

function overdue(dueTime) {
  return !!dueTime && new Date(dueTime.replace(' ', 'T')) < new Date()
}

async function load() {
  loading.value = true
  try {
    const data = await getTrips({ current: current.value, size: size.value, keyword: keyword.value })
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function openTodos(row) {
  todoVisible.value = true
  todoTitle.value = row.title || `行程 ${row.id}`
  todoLoading.value = true
  try {
    todos.value = await getTripTodos(row.id)
  } finally {
    todoLoading.value = false
  }
}

async function confirmDelete(row) {
  try { await ElMessageBox.confirm(`确认删除行程「${row.title || row.id}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteTrip(row.id)
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
