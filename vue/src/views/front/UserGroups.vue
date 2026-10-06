<template>
  <div class="page">
    <h2 class="title">活动天地</h2>
    <div class="list">
      <div v-for="t in tours" :key="t.id" class="card">
        <div class="card-head">
          <span class="tour-title">{{ t.title }}</span>
          <StatusBadge type="tour" :value="t.status" />
        </div>
        <div class="meta">{{ t.destination }} · 名额 {{ t.capacity }} · {{ t.startTime }}</div>
        <div class="content">{{ t.content }}</div>
        <el-button type="primary" class="signup" @click="signup(t)">报名</el-button>
      </div>
      <p v-if="!tours.length" class="muted">暂无活动</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTours, signupTour } from '../../api/tour'
import { getMyTravelers } from '../../api/family'
import StatusBadge from '../../components/StatusBadge.vue'

const tours = ref([])
const travelers = ref([])

async function load() {
  tours.value = await getTours()
  travelers.value = await getMyTravelers()
}

async function signup(t) {
  if (!travelers.value.length) { ElMessage.warning('请先绑定家人'); return }
  try {
    await signupTour(t.id, { travelerId: travelers.value[0].id })
    ElMessage.success('报名成功')
  } catch (e) {
    ElMessage.warning(e.message || '报名失败')
  }
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h1); }
.list { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.tour-title { font-family: var(--font-serif); font-size: var(--fs-h3); }
.meta { color: var(--muted); font-size: var(--fs-aux); }
.content { font-size: var(--fs-body); }
.signup { min-height: var(--min-tap); }
.muted { color: var(--muted); }
</style>
