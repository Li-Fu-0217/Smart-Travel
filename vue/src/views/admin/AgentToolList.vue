<template>
  <div class="page">
    <h2 class="title">助手工具</h2>
    <p class="sub">共 {{ tools.length }} 个工具 · 供智能助手调用（只读说明书）</p>
    <div class="cards">
      <article v-for="t in tools" :key="t.name" class="tool-card">
        <header class="tool-head">
          <h3 class="tool-label">{{ t.label }}</h3>
          <span class="side" :class="t.side_effect ? 'write' : 'read'">{{ t.side_effect ? '写库' : '只读' }}</span>
        </header>
        <div class="tool-meta">
          <code class="tool-name">{{ t.name }}</code>
          <span class="cat">{{ t.category }}</span>
        </div>
        <p class="desc">{{ t.description }}</p>
        <div class="params">
          <span v-for="p in t.params" :key="p.name" class="param">{{ p.name }}<em v-if="!p.required">?</em></span>
        </div>
        <p class="rules">规则：{{ t.rules }}</p>
        <div class="examples">
          <span v-for="(e, i) in t.examples" :key="i" class="example">“{{ e }}”</span>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAgentTools } from '../../api/agent'

const tools = ref([])

onMounted(async () => {
  tools.value = await getAgentTools()
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.title { margin: 0; font-family: var(--font-serif); font-size: var(--fs-h1); }
.sub { margin: 0; color: var(--muted); font-size: var(--fs-aux); }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--sp-card-gap); }
.tool-card {
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
  padding: var(--sp-card-inner);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-card);
}
.tool-head { display: flex; align-items: center; justify-content: space-between; gap: var(--sp-card-gap); }
.tool-label { margin: 0; font-size: var(--fs-h3); }
.side { padding: 0 var(--sp-card-gap); line-height: 1.8; border-radius: var(--r-badge); font-size: var(--fs-caption); }
.side.read { color: var(--ok); border: 1px solid var(--ok); }
.side.write { color: var(--warn); border: 1px solid var(--warn); }
.tool-meta { display: flex; align-items: center; gap: var(--sp-card-gap); }
.tool-name { font-family: var(--font-mono, monospace); font-size: var(--fs-aux); color: var(--accent); }
.cat { padding: 0 var(--sp-card-gap); line-height: 1.8; border: 1px solid var(--line); border-radius: var(--r-badge); color: var(--muted); font-size: var(--fs-caption); }
.desc { margin: 0; font-size: var(--fs-aux); line-height: 1.6; }
.params { display: flex; flex-wrap: wrap; gap: var(--sp-card-gap); }
.param { padding: 0 var(--sp-card-gap); line-height: 1.8; border-radius: var(--r-badge); background: var(--surface); border: 1px solid var(--line); font-size: var(--fs-caption); color: var(--muted); }
.param em { font-style: normal; color: var(--accent); }
.rules { margin: 0; color: var(--muted); font-size: var(--fs-caption); }
.examples { display: flex; flex-wrap: wrap; gap: var(--sp-card-gap); }
.example { color: var(--muted); font-size: var(--fs-caption); }
</style>
