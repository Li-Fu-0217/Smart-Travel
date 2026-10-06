<template>
  <div class="page">
    <div class="toolbar">
      <el-button type="primary" @click="openCreate">新增菜单</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" width="140" />
        <el-table-column prop="path" label="路径" />
        <el-table-column prop="icon" label="图标" width="120" />
        <el-table-column prop="sortOrder" label="排序" width="80" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">{{ (row.roles || []).join(', ') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.id ? '编辑菜单' : '新增菜单'" width="440px">
      <el-form label-width="80px">
        <el-form-item label="名称"><el-input v-model="dialog.form.name" /></el-form-item>
        <el-form-item label="路径"><el-input v-model="dialog.form.path" placeholder="/admin/xxx" /></el-form-item>
        <el-form-item label="图标"><el-input v-model="dialog.form.icon" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="dialog.form.sortOrder" :min="0" /></el-form-item>
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
import { getManagedMenus, createMenu, updateMenu, deleteMenu } from '../../api/menu'

const rows = ref([])
const loading = ref(false)
const dialog = reactive({ visible: false, id: null, form: { name: '', path: '', icon: '', sortOrder: 0 } })

async function load() {
  loading.value = true
  try {
    rows.value = await getManagedMenus()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  dialog.id = null
  dialog.form = { name: '', path: '', icon: '', sortOrder: 0 }
  dialog.visible = true
}

function openEdit(row) {
  dialog.id = row.id
  dialog.form = { name: row.name, path: row.path, icon: row.icon, sortOrder: row.sortOrder }
  dialog.visible = true
}

async function save() {
  if (dialog.id) await updateMenu(dialog.id, dialog.form)
  else await createMenu(dialog.form)
  dialog.visible = false
  ElMessage.success('已保存')
  load()
}

async function confirmDelete(row) {
  try { await ElMessageBox.confirm(`确认删除菜单「${row.name}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteMenu(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; gap: var(--sp-card-gap); align-items: center; }
.table-wrap { overflow-x: auto; }
</style>
