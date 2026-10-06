<template>
  <div class="page">
    <div class="toolbar">
      <el-select v-model="travelerId" class="sel" placeholder="选择旅行者" @change="load">
        <el-option v-for="t in travelers" :key="t.id" :label="t.name" :value="t.id" />
      </el-select>
    </div>
    <div v-if="today" class="today">
      <h2 class="title">{{ today.title || '今日行程' }}</h2>
      <div class="meta">{{ today.date }} · 第 {{ today.dayIndex }} 天 / 共 {{ today.dayCount }} 天</div>
      <div class="section">
        <div class="section-title">今天安排</div>
        <div v-for="td in today.todayTodos" :key="td.id" class="item">
          <span class="time">{{ td.timeSlot }}</span><span>{{ td.itemName }}</span>
        </div>
        <p v-if="!today.todayTodos.length" class="muted">今天没有安排</p>
      </div>
      <div class="section overdue">
        <div class="section-title">已逾期待办</div>
        <div v-for="td in today.overdueTodos" :key="td.id" class="item"><span>{{ td.itemName }}</span><span class="muted">{{ td.dueTime }}</span></div>
        <p v-if="!today.overdueTodos.length" class="muted">无逾期</p>
      </div>
      <div class="section">
        <div class="section-title">接下来</div>
        <div v-for="d in today.nextDays" :key="d.date" class="item"><span class="muted">{{ d.date }}</span><span>{{ (d.items || []).join('、') }}</span></div>
      </div>
    </div>
    <p v-else class="muted">今天没有进行中的行程</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getMyTravelers } from '../../api/family'
import { getTripToday } from '../../api/trip'

const route = useRoute()
const travelers = ref([])
const travelerId = ref(Number(route.query.travelerId) || 0)
const today = ref(null)

async function loadTravelers() {
  travelers.value = await getMyTravelers()
  if (!travelerId.value && travelers.value.length) {
    travelerId.value = travelers.value[0].id
  }
}

async function load() {
  if (!travelerId.value) return
  today.value = await getTripToday(travelerId.value)
}

onMounted(async () => { await loadTravelers(); await load() })
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; }
.sel { width: 160px; }
.today { display: flex; flex-direction: column; gap: var(--sp-section); }
.title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h1); }
.meta { color: var(--muted); }
.section { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.section.overdue { border-color: var(--danger); }
.section-title { font-weight: 600; }
.item { display: flex; gap: var(--sp-card-gap); min-height: var(--min-tap); align-items: center; }
.time { color: var(--accent); width: 60px; }
.muted { color: var(--muted); }
</style>
