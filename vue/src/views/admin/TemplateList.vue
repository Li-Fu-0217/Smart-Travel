<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索标题/目的地/作者/状态" clearable class="search" @keyup.enter="load" @clear="load" />
      <el-select v-model="dayRange" clearable placeholder="天数" class="days" @change="reload">
        <el-option label="1-2 天" value="1-2" />
        <el-option label="3-4 天" value="3-4" />
        <el-option label="5 天以上" value="5+" />
      </el-select>
      <el-select v-model="useRange" clearable placeholder="被使用" class="days" @change="reload">
        <el-option label="1-5 次" value="1-5" />
        <el-option label="6 次以上" value="6+" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="destination" label="目的地" width="120" />
        <el-table-column prop="dayCount" label="天数" width="80" />
        <el-table-column prop="useCount" label="被使用" width="90" />
        <el-table-column prop="authorName" label="作者" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><StatusBadge type="template" :value="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button link :type="row.status === 1 ? 'warning' : 'primary'" @click="toggleStatus(row)">
              {{ row.status === 1 ? '下架' : '上架' }}
            </el-button>
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
import { getAdminTemplates, updateAdminTemplate, deleteAdminTemplate } from '../../api/template'
import StatusBadge from '../../components/StatusBadge.vue'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const keyword = ref('')
const dayRange = ref('')
const useRange = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await getAdminTemplates({ current: current.value, size: size.value, keyword: keyword.value, dayRange: dayRange.value, useRange: useRange.value })
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

async function toggleStatus(row) {
  await updateAdminTemplate(row.id, { status: row.status === 1 ? 0 : 1 })
  ElMessage.success('已更新')
  load()
}

async function confirmDelete(row) {
  try { await ElMessageBox.confirm(`确认删除模板「${row.title}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteAdminTemplate(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; gap: var(--sp-card-gap); align-items: center; }
.search { width: 220px; }
.days { width: 120px; }
.table-wrap { overflow-x: auto; }
.pager { display: flex; justify-content: flex-end; }
</style>
