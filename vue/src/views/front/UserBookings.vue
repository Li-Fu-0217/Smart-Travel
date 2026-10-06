<template>
  <div class="page">
    <h2 class="title">预约中心</h2>
    <div class="section">
      <div class="section-title">可预约项目</div>
      <div v-for="c in catalogs" :key="c.id" class="catalog">
        <div class="catalog-info">
          <div class="catalog-name">{{ c.name }}</div>
          <div class="muted">{{ c.durationMinutes }} 分钟 · ¥{{ c.price }}</div>
        </div>
        <el-button type="primary" @click="pick(c)">预约</el-button>
      </div>
    </div>
    <div class="section">
      <div class="section-title">我的预约</div>
      <div v-for="o in orders" :key="o.id" class="order">
        <div class="order-info">
          <span>{{ o.catalogName }}</span>
          <span class="muted">{{ o.slot }}</span>
        </div>
        <div class="order-actions">
          <StatusBadge type="booking" :value="o.status" />
          <el-button v-if="o.status === 'pending' || o.status === 'confirmed'" link type="danger" @click="cancel(o)">取消</el-button>
        </div>
      </div>
      <p v-if="!orders.length" class="muted">暂无预约</p>
    </div>

    <el-dialog v-model="slotVisible" :title="`选择时段（${curCatalog?.name}）`" width="340px">
      <div class="slots">
        <button v-for="s in slots" :key="s" class="slot" @click="book(s)">{{ s }}</button>
      </div>
      <p v-if="!slots.length" class="muted">暂无可约时段</p>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCatalog, getSlots, createOrder, getOrders, cancelOrder } from '../../api/booking'
import { getMyTravelers } from '../../api/family'
import StatusBadge from '../../components/StatusBadge.vue'

const catalogs = ref([])
const orders = ref([])
const travelers = ref([])
const slotVisible = ref(false)
const slots = ref([])
let curCatalog = null

async function load() {
  catalogs.value = await getCatalog()
  const od = await getOrders({ current: 1, size: 20 })
  orders.value = od.records
  travelers.value = await getMyTravelers()
}

async function pick(c) {
  curCatalog = c
  const data = await getSlots({ itemType: c.itemType, days: 7 })
  const entry = data.find((d) => d.catalogId === c.id)
  slots.value = entry ? entry.slots : []
  slotVisible.value = true
}

async function book(slot) {
  if (!travelers.value.length) { ElMessage.warning('请先绑定家人'); return }
  await createOrder({ travelerId: travelers.value[0].id, catalogId: curCatalog.id, slot, guestCount: 1 })
  slotVisible.value = false
  ElMessage.success('预约成功')
  load()
}

async function cancel(o) {
  try { await ElMessageBox.confirm('确认取消该预约？', '提示', { type: 'warning' }) } catch { return }
  await cancelOrder(o.id)
  ElMessage.success('已取消')
  load()
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-section); }
.title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h1); }
.section { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.section-title { font-weight: 600; }
.catalog, .order { display: flex; align-items: center; justify-content: space-between; min-height: var(--min-tap); gap: var(--sp-card-gap); }
.catalog-name { font-family: var(--font-serif); font-size: var(--fs-h3); }
.order-info { display: flex; flex-direction: column; }
.order-actions { display: flex; align-items: center; gap: var(--sp-card-gap); }
.slots { display: flex; flex-wrap: wrap; gap: var(--sp-card-gap); }
.slot { min-height: var(--min-tap); padding: 0 var(--sp-card-gap); border: 1px solid var(--line); border-radius: var(--r-card); background: var(--surface); }
.muted { color: var(--muted); }
</style>
