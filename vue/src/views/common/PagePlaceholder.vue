<template>
  <div class="placeholder">
    <h2>{{ $route.meta.title || '页面' }}</h2>
    <p class="muted">该页面在阶段 4 实现。</p>
  </div>
</template>

<script setup>
</script>

<style scoped>
.placeholder h2 { margin: 0 0 var(--sp-card-gap); font-size: var(--fs-h1); }
.muted { color: var(--muted); }
</style>
