<template>
  <div class="page">
    <div class="toolbar">
      <el-button type="primary" @click="openCreate">新增活动</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="destination" label="目的地" width="120" />
        <el-table-column prop="capacity" label="名额" width="80" />
        <el-table-column prop="startTime" label="开始时间" width="170" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><StatusBadge type="tour" :value="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="openSignups(row)">报名</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="total, prev, pager, next" @current-change="load" />
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.id ? '编辑活动' : '新增活动'" width="440px">
      <el-form label-width="80px">
        <el-form-item label="标题"><el-input v-model="dialog.form.title" /></el-form-item>
        <el-form-item label="目的地"><el-input v-model="dialog.form.destination" /></el-form-item>
        <el-form-item label="名额"><el-input-number v-model="dialog.form.capacity" :min="0" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="dialog.form.content" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="signupVisible" :title="`报名列表（${signupTitle}）`" width="520px">
      <el-table :data="signups" v-loading="signupLoading">
        <el-table-column prop="travelerName" label="旅行者" width="120" />
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><StatusBadge type="signup" :value="row.status" /></template>
        </el-table-column>
        <el-table-column prop="createTime" label="报名时间" width="170" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminTours, createAdminTour, updateAdminTour, deleteAdminTour, getAdminSignups } from '../../api/tour'
import StatusBadge from '../../components/StatusBadge.vue'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const loading = ref(false)
const dialog = reactive({ visible: false, id: null, form: { title: '', destination: '', capacity: 0, content: '' } })
const signupVisible = ref(false)
const signupTitle = ref('')
const signups = ref([])
const signupLoading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await getAdminTours({ current: current.value, size: size.value })
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  dialog.id = null
  dialog.form = { title: '', destination: '', capacity: 0, content: '' }
  dialog.visible = true
}

function openEdit(row) {
  dialog.id = row.id
  dialog.form = { title: row.title, destination: row.destination, capacity: row.capacity, content: row.content }
  dialog.visible = true
}

async function save() {
  if (dialog.id) await updateAdminTour(dialog.id, dialog.form)
  else await createAdminTour(dialog.form)
  dialog.visible = false
  ElMessage.success('已保存')
  load()
}

async function confirmDelete(row) {
  try { await ElMessageBox.confirm(`确认删除活动「${row.title}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteAdminTour(row.id)
  ElMessage.success('已删除')
  load()
}

async function openSignups(row) {
  signupVisible.value = true
  signupTitle.value = row.title
  signupLoading.value = true
  try {
    const data = await getAdminSignups({ tourId: row.id, current: 1, size: 100 })
    signups.value = data.records
  } finally {
    signupLoading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; gap: var(--sp-card-gap); align-items: center; }
.table-wrap { overflow-x: auto; }
.pager { display: flex; justify-content: flex-end; }
</style>
