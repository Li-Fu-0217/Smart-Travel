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
      </div>
      <p v-if="!trips.length" class="muted">暂无行程</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTrips, getTripTodos } from '../../api/trip'
import { doneTodo, undoTodo } from '../../api/todo'
import StatusBadge from '../../components/StatusBadge.vue'

const trips = ref([])

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
.muted { color: var(--muted); }
</style>
