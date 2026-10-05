<template>
  <el-dropdown trigger="click" @command="onCommand">
    <button class="switcher" type="button" aria-label="切换主题" :title="'主题：' + currentLabel">
      <span class="swatch" aria-hidden="true"></span>
    </button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="t in THEMES"
          :key="t.value"
          :command="t.value"
          :disabled="t.value === current"
        >
          {{ t.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { computed, ref } from 'vue'
import { THEMES, getCurrentTheme, setTheme } from '../config/theme'

const current = ref(getCurrentTheme())
const currentLabel = computed(() => THEMES.find((t) => t.value === current.value)?.label || '')

function onCommand(value) {
  current.value = value
  setTheme(value)
}
</script>

<style scoped>
.switcher {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--min-tap);
  height: var(--min-tap);
  border: none;
  background: transparent;
  cursor: pointer;
}
.swatch {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--line);
}
</style>
