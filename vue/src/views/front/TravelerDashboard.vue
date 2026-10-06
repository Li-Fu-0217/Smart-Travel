<template>
  <div class="page">
    <div class="toolbar">
      <h2 class="title">关怀看板</h2>
      <el-button type="primary" @click="bindVisible = true">绑定家人</el-button>
    </div>

    <div class="stats">
      <div class="stat"><span class="stat-num">{{ unread }}</span><span class="stat-label">未读消息</span></div>
      <div class="stat"><span class="stat-num">{{ ongoingTrips.length }}</span><span class="stat-label">进行中行程</span></div>
    </div>

    <div class="section overdue-section">
      <div class="section-title">逾期待办</div>
      <div v-for="od in overdue" :key="od.id" class="overdue-item">
        <span>{{ od.itemName }}</span><span class="muted">{{ od.dueTime }}</span>
      </div>
      <p v-if="!overdue.length" class="muted">暂无逾期待办</p>
    </div>

    <div class="section">
      <div class="section-title">近期预约</div>
      <div v-for="b in recentBookings" :key="b.id" class="booking-item">
        <span>{{ b.catalogName }}</span>
        <StatusBadge type="booking" :value="b.status" />
      </div>
      <p v-if="!recentBookings.length" class="muted">暂无预约</p>
    </div>

    <div class="section">
      <div class="section-title">我的家人</div>
      <router-link v-for="t in travelers" :key="t.id" :to="`/user/traveler-detail?id=${t.id}`" class="card">
        <div class="card-head">
          <span class="name">{{ t.name }}</span>
          <StatusBadge type="traveler" :value="t.status" />
        </div>
        <PreferenceTags v-if="t.preferenceTags" :model-value="tagsOf(t)" disabled />
      </router-link>
      <p v-if="!travelers.length" class="muted">尚未绑定家人</p>
    </div>

    <el-dialog v-model="bindVisible" title="绑定家人" width="340px">
      <el-form label-width="80px">
        <el-form-item label="姓名"><el-input v-model="bindForm.name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="bindForm.phone" /></el-form-item>
        <el-form-item label="关系"><el-input v-model="bindForm.relation" placeholder="如：父亲" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindVisible = false">取消</el-button>
        <el-button type="primary" @click="doBind">绑定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyTravelers, bindTraveler } from '../../api/family'
import { getTripToday } from '../../api/trip'
import { getTrips } from '../../api/trip'
import { getOrders } from '../../api/booking'
import { getUnreadCount } from '../../api/notification'
import StatusBadge from '../../components/StatusBadge.vue'
import PreferenceTags from '../../components/PreferenceTags.vue'

const travelers = ref([])
const unread = ref(0)
const overdue = ref([])
const recentBookings = ref([])
const ongoingTrips = ref([])
const bindVisible = ref(false)
const bindForm = reactive({ name: '', phone: '', relation: '' })

function tagsOf(t) {
  return (t.preferenceTags || '').split(',').filter(Boolean)
}

async function load() {
  travelers.value = await getMyTravelers()
  unread.value = await getUnreadCount()
  const od = await getOrders({ current: 1, size: 5 })
  recentBookings.value = od.records
  const tp = await getTrips({ current: 1, size: 50 })
  ongoingTrips.value = tp.records.filter((t) => t.status === 1)

  const overdueAll = []
  for (const t of travelers.value) {
    const today = await getTripToday(t.id)
    if (today && today.overdueTodos) overdueAll.push(...today.overdueTodos)
  }
  overdue.value = overdueAll
}

async function doBind() {
  await bindTraveler(bindForm)
  bindVisible.value = false
  bindForm.name = ''; bindForm.phone = ''; bindForm.relation = ''
  ElMessage.success('绑定成功')
  load()
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; align-items: center; justify-content: space-between; }
.title { margin: 0; font-size: var(--fs-h2); }
.stats { display: flex; gap: var(--sp-card-gap); }
.stat { flex: 1; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.stat-num { font-size: var(--fs-h2); font-weight: 600; }
.stat-label { color: var(--muted); font-size: var(--fs-aux); }
.section { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.section.overdue-section { border-color: var(--danger); }
.section-title { font-weight: 600; }
.overdue-item, .booking-item { display: flex; justify-content: space-between; min-height: var(--min-tap); align-items: center; }
.card { display: flex; flex-direction: column; gap: var(--sp-card-gap); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.name { font-family: var(--font-serif); font-size: var(--fs-h3); }
.muted { color: var(--muted); }
</style>
