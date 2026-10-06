<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索用户名" clearable class="search" @keyup.enter="load" @clear="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="primary" @click="openCreate">新增用户</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">{{ row.role === 'ADMIN' ? '管理员' : '普通用户' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><StatusBadge type="user" :value="row.status" /></template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="170" />
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

    <el-dialog v-model="dialog.visible" :title="dialog.id ? '编辑用户' : '新增用户'" width="420px">
      <el-form label-width="80px">
        <el-form-item label="用户名"><el-input v-model="dialog.form.username" :disabled="!!dialog.id" /></el-form-item>
        <el-form-item v-if="!dialog.id" label="密码"><el-input v-model="dialog.form.password" type="password" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="dialog.form.role"><el-option label="管理员" value="ADMIN" /><el-option label="普通用户" value="USER" /></el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="dialog.form.status"><el-option label="启用" :value="1" /><el-option label="禁用" :value="0" /></el-select>
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
import { getUsers, createUser, updateUser, deleteUser } from '../../api/user'
import StatusBadge from '../../components/StatusBadge.vue'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const keyword = ref('')
const loading = ref(false)
const dialog = reactive({ visible: false, id: null, form: { username: '', password: '', role: 'USER', status: 1 } })

async function load() {
  loading.value = true
  try {
    const data = await getUsers({ current: current.value, size: size.value, keyword: keyword.value })
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  dialog.id = null
  dialog.form = { username: '', password: '', role: 'USER', status: 1 }
  dialog.visible = true
}

function openEdit(row) {
  dialog.id = row.id
  dialog.form = { username: row.username, role: row.role, status: row.status }
  dialog.visible = true
}

async function save() {
  if (dialog.id) await updateUser(dialog.id, { role: dialog.form.role, status: dialog.form.status })
  else await createUser(dialog.form)
  dialog.visible = false
  ElMessage.success('已保存')
  load()
}

async function confirmDelete(row) {
  try { await ElMessageBox.confirm(`确认删除用户「${row.username}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteUser(row.id)
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
