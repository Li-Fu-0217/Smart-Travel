<template>
  <div v-if="steps && steps.length" class="steps">
    <div v-for="s in steps" :key="s.round" class="step">
      <div class="step-head">
        <span class="round">{{ s.round }}</span>
        <span class="thought">{{ s.thought }}</span>
        <span v-if="s.action" class="action">{{ s.action }}</span>
      </div>
      <p v-if="s.observation" class="observation">{{ s.observation }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  steps: { type: Array, default: () => [] },
})
</script>

<style scoped>
.steps {
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
}
.step {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.step-head {
  display: flex;
  align-items: center;
  gap: var(--sp-card-gap);
}
.round {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--accent-ink);
  font-size: 11px;
}
.thought {
  color: var(--muted);
  font-size: var(--fs-aux);
}
.action {
  padding: 0 8px;
  border-radius: var(--r-badge);
  background: var(--surface);
  border: 1px solid var(--line);
  font-size: var(--fs-aux);
  font-family: var(--font-mono, monospace);
}
.observation {
  margin: 0;
  padding-left: 26px;
  color: var(--muted);
  font-size: var(--fs-aux);
}
</style>
