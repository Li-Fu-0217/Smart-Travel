<template>
  <div class="home">
    <div class="hero" :style="{ background: cover.gradient }">
      <h1 class="hero-title">智慧旅游智能助手</h1>
      <p class="hero-sub">为家人的每一次出行，安排得明明白白</p>
    </div>
    <div class="shortcuts">
      <router-link v-for="n in nav" :key="n.path" :to="n.path" class="shortcut">
        <el-icon class="shortcut-icon"><component :is="n.icon" /></el-icon>
        <span class="shortcut-name">{{ n.name }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { FRONT_NAV } from '../../config/frontNav'
import { destinationTheme } from '../../config/destinationThemes'

const nav = FRONT_NAV
const cover = destinationTheme('海岛')  // 首页封面固定用「海岛」主题
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: var(--sp-section); }
.hero { border-radius: var(--r-card-lg); padding: var(--sp-section) var(--sp-card-inner); color: var(--ink); }
.hero-title { font-family: var(--font-serif); font-size: var(--fs-h1); margin: 0 0 var(--sp-card-gap); }
.hero-sub { font-size: var(--fs-body); margin: 0; opacity: 0.85; }
.shortcuts { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--sp-card-gap); }
.shortcut { min-height: var(--min-tap); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--sp-card-gap); background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); font-size: var(--fs-body); }
.shortcut-icon { font-size: var(--fs-h2); color: var(--accent); }
@media (min-width: 768px) { .shortcuts { grid-template-columns: repeat(4, 1fr); } }
</style>
