<template>
  <div class="dashboard">
    <h2 class="title">数据概览</h2>
    <div class="kpi-grid">
      <div v-for="k in kpis" :key="k.label" class="kpi-card">
        <span class="kpi-label">{{ k.label }}</span>
        <span class="kpi-value">{{ k.value }}</span>
        <span v-if="k.sub" class="kpi-sub">{{ k.sub }}</span>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h3 class="chart-title">预约状态分布</h3><div ref="pieRef" class="chart"></div></div>
      <div class="chart-card"><h3 class="chart-title">项目类型预约量</h3><div ref="barRef" class="chart"></div></div>
      <div class="chart-card"><h3 class="chart-title">近 7 日预约趋势</h3><div ref="lineRef" class="chart"></div></div>
      <div class="chart-card"><h3 class="chart-title">助手工具调用分布</h3><div ref="toolRef" class="chart"></div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getAdminStats } from '../../api/stats'

const kpis = ref([])
const pieRef = ref(null)
const barRef = ref(null)
const lineRef = ref(null)
const toolRef = ref(null)
let chartInstances = []
let observer = null

const KPI_DEFS = [
  { key: 'travelers', label: '在册旅行者' },
  { key: 'activeUsers', label: '活跃用户' },
  { key: 'pendingBookings', label: '待确认预约' },
  { key: 'openAlerts', label: '未关闭求助' },
  { key: 'activeTours', label: '上架拼团活动' },
  { key: 'overdueTodos', label: '当前逾期待办' },
  { key: 'guideDocs', label: '攻略文档', sub: (k) => `已就绪 ${k.guideReady}` },
  { key: 'agentCalls', label: '助手调用次数' },
]

function cssVar(name, fallback) {
  const v = getComputedStyle(document.body).getPropertyValue(name).trim()
  return v || fallback
}

function themeColors() {
  return { ink: cssVar('--ink', '#14171C'), muted: cssVar('--muted', '#6B7280'), line: cssVar('--line', '#E4E7EC') }
}

function baseOption() {
  const c = themeColors()
  return {
    textStyle: { color: c.ink },
    grid: { left: 8, right: 16, top: 24, bottom: 8, containLabel: true },
  }
}

function initChart(el) {
  const chart = echarts.init(el)
  chartInstances.push(chart)
  return chart
}

function renderPie(data) {
  const c = themeColors()
  initChart(pieRef.value).setOption({
    ...baseOption(),
    tooltip: { trigger: 'item' },
    series: [{ type: 'pie', radius: ['40%', '68%'], center: ['50%', '55%'], data, label: { color: c.ink } }],
  })
}

function renderBar(data) {
  const c = themeColors()
  initChart(barRef.value).setOption({
    ...baseOption(),
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map((d) => d.name), axisLine: { lineStyle: { color: c.line } }, axisLabel: { color: c.muted } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: c.line } }, axisLabel: { color: c.muted } },
    series: [{ type: 'bar', data: data.map((d) => d.value), barMaxWidth: 40, itemStyle: { color: cssVar('--accent', '#1B6CA8') } }],
  })
}

function renderLine(data) {
  const c = themeColors()
  initChart(lineRef.value).setOption({
    ...baseOption(),
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map((d) => d.date.slice(5)), axisLine: { lineStyle: { color: c.line } }, axisLabel: { color: c.muted } },
    yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: c.line } }, axisLabel: { color: c.muted } },
    series: [{ type: 'line', data: data.map((d) => d.count), smooth: true, itemStyle: { color: cssVar('--accent', '#1B6CA8') }, areaStyle: { opacity: 0.08 } }],
  })
}

function renderTool(data) {
  const c = themeColors()
  initChart(toolRef.value).setOption({
    ...baseOption(),
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: c.line } }, axisLabel: { color: c.muted } },
    yAxis: { type: 'category', data: data.map((d) => d.name), axisLine: { lineStyle: { color: c.line } }, axisLabel: { color: c.ink } },
    series: [{ type: 'bar', data: data.map((d) => d.value), barMaxWidth: 20, itemStyle: { color: cssVar('--accent', '#1B6CA8') } }],
  })
}

async function load() {
  const data = await getAdminStats()
  const k = data.kpis
  kpis.value = KPI_DEFS.map(({ key, label, sub }) => ({ label, value: k[key], sub: sub ? sub(k) : '' }))
  renderPie(data.charts.bookingStatus)
  renderBar(data.charts.itemTypeCount)
  renderLine(data.charts.trend7d)
  renderTool(data.charts.toolDistribution)
}

function resizeAll() {
  chartInstances.forEach((c) => c.resize())
}

onMounted(async () => {
  await load()
  window.addEventListener('resize', resizeAll)
  // 主题切换时重渲染（图表文字/轴线颜色跟随主题）
  observer = new MutationObserver(() => {
    chartInstances.forEach((c) => c.dispose())
    chartInstances = []
    load()
  })
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeAll)
  if (observer) observer.disconnect()
  chartInstances.forEach((c) => c.dispose())
  chartInstances = []
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: var(--sp-section); }
.title { margin: 0; font-size: var(--fs-h1); }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--sp-card-gap); }
.kpi-card {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--r-card); padding: var(--sp-card-inner);
  display: flex; flex-direction: column; gap: var(--sp-card-gap);
}
.kpi-label { color: var(--muted); font-size: var(--fs-aux); }
.kpi-value { font-size: var(--fs-h2); font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }
.kpi-sub { color: var(--muted); font-size: var(--fs-caption); }
.chart-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--sp-card-gap); }
.chart-card {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--r-card); padding: var(--sp-card-inner);
}
.chart-title { margin: 0 0 var(--sp-card-inner); font-size: var(--fs-h3); }
.chart { height: 260px; }
@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .chart-grid { grid-template-columns: 1fr; }
}
</style>
