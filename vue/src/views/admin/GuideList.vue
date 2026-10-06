<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索标题/文件/类型/状态" clearable class="search" @keyup.enter="load" @clear="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <el-upload :show-file-list="false" :http-request="doUpload" accept=".txt,.md,.pdf">
        <el-button type="primary">上传文档</el-button>
      </el-upload>
    </div>
    <div class="table-wrap">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="filePath" label="文件" width="180" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ DOC_TYPE[row.docType] || row.docType }}</template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }"><StatusBadge type="catalog" :value="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewChunks(row)">切片</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="total, prev, pager, next" @current-change="load" />
    </div>

    <el-dialog v-model="chunkVisible" :title="`切片（${chunkTitle}）`" width="560px">
      <div v-for="c in chunks" :key="c.id" class="chunk">
        <div class="chunk-idx">#{{ c.chunkIndex }}</div>
        <div class="chunk-content">{{ c.content }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocuments, getChunks, deleteDocument, createDocument } from '../../api/guide'
import { uploadFile } from '../../api/file'
import StatusBadge from '../../components/StatusBadge.vue'

const DOC_TYPE = { visa: '签证政策', document: '出行证件', destination: '目的地指南', tips: '出行注意' }
const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const keyword = ref('')
const loading = ref(false)
const chunkVisible = ref(false)
const chunkTitle = ref('')
const chunks = ref([])

async function load() {
  loading.value = true
  try {
    const data = await getDocuments({ current: current.value, size: size.value, keyword: keyword.value })
    rows.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function doUpload({ file }) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('category', 'common')
  const up = await uploadFile(fd)
  const title = file.name.replace(/\.(txt|md|pdf)$/, '')
  const docType = file.name.includes('visa') ? 'visa' : file.name.includes('doc') ? 'document' : file.name.includes('dest') ? 'destination' : 'tips'
  await createDocument({ title, filePath: up.path, docType })
  ElMessage.success('上传成功')
  load()
}

async function viewChunks(row) {
  chunkVisible.value = true
  chunkTitle.value = row.title
  chunks.value = await getChunks(row.id)
}

async function confirmDelete(row) {
  try { await ElMessageBox.confirm(`确认删除文档「${row.title}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteDocument(row.id)
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
.chunk { background: var(--surface-2); border-radius: var(--r-card); padding: var(--sp-card-inner); margin-bottom: var(--sp-card-gap); }
.chunk-idx { color: var(--accent); font-size: var(--fs-caption); }
.chunk-content { font-size: var(--fs-aux); }
</style>
