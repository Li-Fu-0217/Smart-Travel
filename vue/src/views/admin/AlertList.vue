<template>
  <div class="page">
    <div class="toolbar">
      <el-select v-model="status" class="status" placeholder="全部状态" clearable @change="load">
        <el-option label="待处理" value="open" />
        <el-option label="处理中" value="handling" />
        <el-option label="已关闭" value="closed" />
      </el-select>
      <el-button type="primary" @click="load">刷新</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="travelerName" label="旅行者" width="120" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }"><StatusBadge type="alert_type" :value="row.alertType" /></template>
        </el-table-column>
        <el-table-column prop="location" label="位置" width="140" />
        <el-table-column prop="message" label="内容" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><StatusBadge type="alert" :value="row.status" /></template>
        </el-table-column>
        <el-table-column prop="createTime" label="时间" width="170" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button v-if="row.status === 'open'" link type="primary" @click="updateStatus(row, 'handling')">开始处理</el-button>
            <el-button v-if="row.status !== 'closed'" link type="success" @click="updateStatus(row, 'closed')">关闭</el-button>
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
import { ElMessage } from 'element-plus'
import { getAdminAlerts, updateAdminAlert } from '../../api/alert'
import StatusBadge from '../../components/StatusBadge.vue'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const status = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await getAdminAlerts({ current: current.value, size: size.value, status: status.value || undefined })
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function updateStatus(row, next) {
  await updateAdminAlert(row.id, { status: next })
  ElMessage.success('已更新')
  load()
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; gap: var(--sp-card-gap); align-items: center; }
.status { width: 160px; }
.table-wrap { overflow-x: auto; }
.pager { display: flex; justify-content: flex-end; }
</style>
