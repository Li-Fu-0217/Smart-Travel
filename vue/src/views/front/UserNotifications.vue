<template>
  <div class="page">
    <div class="toolbar">
      <h2 class="title">消息中心</h2>
      <el-button type="primary" link @click="readAll">全部已读</el-button>
    </div>
    <div class="list">
      <div v-for="n in rows" :key="n.id" class="msg" :class="{ unread: n.isRead === 0 }" @click="open(n)">
        <div class="msg-title">{{ n.title || '消息' }}</div>
        <div class="msg-content">{{ n.content }}</div>
        <div class="msg-meta">{{ n.createTime }}</div>
      </div>
      <p v-if="!rows.length" class="muted">暂无消息</p>
    </div>
    <div class="pager">
      <el-pagination v-model:current-page="current" v-model:page-size="size" :total="total" layout="prev, pager, next" @current-change="load" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getNotifications, markRead, markReadAll } from '../../api/notification'

const rows = ref([])
const total = ref(0)
const current = ref(1)
const size = ref(10)

async function load() {
  const data = await getNotifications({ current: current.value, size: size.value })
  rows.value = data.records
  total.value = data.total
}

async function open(n) {
  if (n.isRead === 0) {
    await markRead(n.id)
    load()
  }
}

async function readAll() {
  await markReadAll()
  load()
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; align-items: center; justify-content: space-between; }
.title { margin: 0; font-size: var(--fs-h2); }
.list { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.msg { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); min-height: var(--min-tap); }
.msg.unread { border-color: var(--accent); }
.msg-title { font-weight: 600; }
.msg-content { color: var(--muted); font-size: var(--fs-aux); }
.msg-meta { color: var(--muted); font-size: var(--fs-caption); }
.muted { color: var(--muted); }
.pager { display: flex; justify-content: center; }
</style>
