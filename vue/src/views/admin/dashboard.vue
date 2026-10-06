<template>
  <div class="dashboard">
    <h2 class="title">数据概览</h2>
    <div class="kpi-grid">
      <div v-for="kpi in KPIS" :key="kpi" class="kpi-card">
        <span class="kpi-label">{{ kpi }}</span>
        <span class="kpi-value">--</span>
      </div>
    </div>
    <div class="chart-grid">
      <div v-for="chart in CHARTS" :key="chart" class="chart-card">
        <h3 class="chart-title">{{ chart }}</h3>
        <div class="chart-placeholder">统计端点阶段 7 接入</div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 8 张 KPI 卡片 + 4 个图表容器（§7.7）；数据端点阶段 7 接入，此处不编造数据
const KPIS = ['在册旅行者', '活跃用户', '待确认预约', '未关闭求助', '上架拼团活动', '当前逾期待办', '攻略文档', '助手调用次数']
const CHARTS = ['预约状态分布', '项目类型预约量', '近 7 日预约趋势', '助手工具调用分布']
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
.chart-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--sp-card-gap); }
.chart-card {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--r-card); padding: var(--sp-card-inner);
  min-height: 220px;
}
.chart-title { margin: 0 0 var(--sp-card-inner); font-size: var(--fs-h3); }
.chart-placeholder { color: var(--muted); font-size: var(--fs-aux); }
@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .chart-grid { grid-template-columns: 1fr; }
}
</style>
