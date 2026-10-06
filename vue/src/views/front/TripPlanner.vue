<template>
  <div class="page">
    <h2 class="title">行程规划</h2>
    <div class="list">
      <div v-for="t in trips" :key="t.id" class="card">
        <div class="card-head">
          <span class="trip-title">{{ t.title || t.destination || `行程 ${t.id}` }}</span>
          <StatusBadge type="trip" :value="t.status" />
        </div>
        <div class="meta">{{ t.startDate }} ~ {{ t.endDate }}</div>
        <div class="todos">
          <div v-for="td in t.todos" :key="td.id" class="todo" :class="{ done: td.status === 1, overdue: td.status === 2 && overdue(td.dueTime) }">
            <span class="todo-name">{{ td.itemName }}</span>
            <StatusBadge v-if="td.status === 2 && overdue(td.dueTime)" type="todo" :value="2" />
            <el-button v-if="td.status === 2" link type="primary" @click="done(t, td)">打卡</el-button>
            <el-button v-else link @click="undo(t, td)">撤销</el-button>
          </div>
        </div>
        <el-button link type="primary" class="publish" @click="openPublish(t)">发布为模板</el-button>
      </div>
      <p v-if="!trips.length" class="muted">暂无行程</p>
    </div>

    <el-dialog v-model="pubVisible" title="发布为模板" width="340px">
      <el-form label-width="80px">
        <el-form-item label="标题"><el-input v-model="pubForm.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="pubForm.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pubVisible = false">取消</el-button>
        <el-button type="primary" @click="doPublish">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTrips, getTripTodos } from '../../api/trip'
import { doneTodo, undoTodo } from '../../api/todo'
import { publishTemplate } from '../../api/template'
import StatusBadge from '../../components/StatusBadge.vue'

const trips = ref([])
const pubVisible = ref(false)
const pubForm = reactive({ tripId: 0, title: '', description: '' })

function overdue(dueTime) {
  return !!dueTime && new Date(dueTime.replace(' ', 'T')) < new Date()
}

async function load() {
  const data = await getTrips({ current: 1, size: 50 })
  const list = data.records
  for (const t of list) {
    t.todos = await getTripTodos(t.id)
  }
  trips.value = list
}

async function done(t, td) {
  await doneTodo(td.id)
  load()
}

async function undo(t, td) {
  await undoTodo(td.id)
  load()
}

function openPublish(t) {
  pubForm.tripId = t.id
  pubForm.title = t.title || ''
  pubForm.description = ''
  pubVisible.value = true
}

async function doPublish() {
  await publishTemplate({ tripId: pubForm.tripId, title: pubForm.title, description: pubForm.description })
  pubVisible.value = false
  ElMessage.success('已发布为模板')
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.title { margin: 0; font-size: var(--fs-h2); }
.list { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.trip-title { font-family: var(--font-serif); font-size: var(--fs-h3); }
.meta { color: var(--muted); font-size: var(--fs-aux); }
.todos { display: flex; flex-direction: column; gap: var(--sp-card-gap); margin-top: var(--sp-card-gap); }
.todo { display: flex; align-items: center; gap: var(--sp-card-gap); min-height: var(--min-tap); }
.todo-name { flex: 1; }
.todo.done .todo-name { text-decoration: line-through; color: var(--muted); }
.todo.overdue .todo-name { color: var(--danger); }
.publish { min-height: var(--min-tap); }
.muted { color: var(--muted); }
</style>
