<template>
  <div class="page">
    <h2 class="title">模板广场</h2>
    <div class="filters">
      <el-input v-model="keyword" placeholder="搜索标题/目的地" clearable class="kw" />
      <el-input v-model="destination" placeholder="目的地" clearable class="dest" />
      <el-select v-model="dayRange" class="days" clearable placeholder="天数">
        <el-option label="1-2 天" value="1-2" />
        <el-option label="3-4 天" value="3-4" />
        <el-option label="5 天以上" value="5+" />
      </el-select>
    </div>
    <div class="list">
      <div v-for="t in filtered" :key="t.id" class="card">
        <div class="cover" :style="{ background: themeOf(t.destination).gradient }"></div>
        <div class="body">
          <div class="card-head">
            <span class="tpl-title">{{ t.title }}</span>
            <span class="muted">已用 {{ t.useCount }} 次</span>
          </div>
          <div class="meta">{{ t.destination }} · {{ t.dayCount }} 天 · {{ t.authorName }}</div>
          <el-button type="primary" class="copy" @click="copy(t)">一键复制</el-button>
        </div>
      </div>
      <p v-if="!filtered.length" class="muted">暂无匹配模板</p>
    </div>

    <el-dialog v-model="copyVisible" title="复制行程" width="340px">
      <el-form label-width="90px">
        <el-form-item label="旅行者">
          <el-select v-model="copyTravelerId"><el-option v-for="t in travelers" :key="t.id" :label="t.name" :value="t.id" /></el-select>
        </el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="copyStartDate" type="date" value-format="YYYY-MM-DD" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!copyStartDate" @click="doCopy">复制</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTemplates, copyTemplate } from '../../api/template'
import { getMyTravelers } from '../../api/family'
import { destinationTheme } from '../../config/destinationThemes'

const router = useRouter()
const templates = ref([])
const travelers = ref([])
const keyword = ref('')
const destination = ref('')
const dayRange = ref('')
const copyVisible = ref(false)
const copyTravelerId = ref(0)
const copyStartDate = ref('')
let curTemplate = null

const filtered = computed(() => {
  return templates.value.filter((t) => {
    if (keyword.value && !((t.title || '').includes(keyword.value) || (t.destination || '').includes(keyword.value))) return false
    if (destination.value && !(t.destination || '').includes(destination.value)) return false
    if (dayRange.value) {
      const [lo, hi] = dayRange.value === '5+' ? [5, Infinity] : dayRange.value.split('-').map(Number)
      if (!(t.dayCount >= lo && t.dayCount <= hi)) return false
    }
    return true
  })
})

function themeOf(name) {
  return destinationTheme(name)
}

async function load() {
  templates.value = await getTemplates()
  travelers.value = await getMyTravelers()
}

function copy(t) {
  curTemplate = t
  copyTravelerId.value = travelers.value.length ? travelers.value[0].id : 0
  copyStartDate.value = ''
  copyVisible.value = true
}

async function doCopy() {
  const trip = await copyTemplate(curTemplate.id, { travelerId: copyTravelerId.value, startDate: copyStartDate.value })
  copyVisible.value = false
  ElMessage.success('复制成功')
  router.push('/user/trips')
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h1); }
.filters { display: flex; flex-wrap: wrap; gap: var(--sp-card-gap); }
.kw { flex: 1; min-width: 140px; }
.dest { width: 140px; }
.days { width: 120px; }
.list { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); overflow: hidden; }
.cover { height: 120px; }
.body { padding: var(--sp-card-inner); display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.tpl-title { font-family: var(--font-serif); font-size: var(--fs-h3); }
.meta { color: var(--muted); font-size: var(--fs-aux); }
.copy { min-height: var(--min-tap); }
.muted { color: var(--muted); }
</style>
