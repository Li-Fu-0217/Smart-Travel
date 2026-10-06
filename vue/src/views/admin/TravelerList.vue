<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索姓名" clearable class="search" @keyup.enter="load" @clear="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="primary" @click="openCreate">新增档案</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="70" />
        <el-table-column prop="phone" label="手机" width="130" />
        <el-table-column prop="preferenceTags" label="偏好标签" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><StatusBadge type="traveler" :value="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="total, prev, pager, next" @current-change="load" />
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.id ? '编辑档案' : '新增档案'" width="480px">
      <el-form label-width="90px">
        <el-form-item label="姓名"><el-input v-model="dialog.form.name" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="dialog.form.gender" clearable><el-option label="男" value="男" /><el-option label="女" value="女" /></el-select>
        </el-form-item>
        <el-form-item label="手机"><el-input v-model="dialog.form.phone" /></el-form-item>
        <el-form-item label="偏好文本"><el-input v-model="dialog.form.preferences" type="textarea" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="dialog.form.status"><el-option label="正常" :value="1" /><el-option label="停用" :value="0" /></el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTravelers, createTraveler, updateTraveler, deleteTraveler } from '../../api/traveler'
import StatusBadge from '../../components/StatusBadge.vue'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const keyword = ref('')
const loading = ref(false)
const dialog = reactive({ visible: false, id: null, form: { name: '', gender: '', phone: '', preferences: '', status: 1 } })

async function load() {
  loading.value = true
  try {
    const data = await getTravelers({ current: current.value, size: size.value, keyword: keyword.value })
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  dialog.id = null
  dialog.form = { name: '', gender: '', phone: '', preferences: '', status: 1 }
  dialog.visible = true
}

function openEdit(row) {
  dialog.id = row.id
  dialog.form = { name: row.name, gender: row.gender, phone: row.phone, preferences: row.preferences, status: row.status }
  dialog.visible = true
}

async function save() {
  if (dialog.id) await updateTraveler(dialog.id, dialog.form)
  else await createTraveler(dialog.form)
  dialog.visible = false
  ElMessage.success('已保存')
  load()
}

async function confirmDelete(row) {
  try { await ElMessageBox.confirm(`确认删除档案「${row.name}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteTraveler(row.id)
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
