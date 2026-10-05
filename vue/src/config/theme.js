// 6 套主题（见施工规范 §7.9.2）与切换逻辑
// data-theme 在 <html>，切换全局生效（前后台同时变）；用户选择写 localStorage 持久化
export const THEMES = [
  { value: 'sunset-light', label: '暖砂 · 亮', hue: 'sunset', mode: 'light' },
  { value: 'sunset-dark', label: '暖砂 · 暗', hue: 'sunset', mode: 'dark' },
  { value: 'ocean-light', label: '海蓝 · 亮', hue: 'ocean', mode: 'light' },
  { value: 'ocean-dark', label: '海蓝 · 暗', hue: 'ocean', mode: 'dark' },
  { value: 'forest-light', label: '苔绿 · 亮', hue: 'forest', mode: 'light' },
  { value: 'forest-dark', label: '苔绿 · 暗', hue: 'forest', mode: 'dark' },
]

const KEY = 'travel-assistant-theme'
const RE = /^(sunset|ocean|forest)-(light|dark)$/

export function getCurrentTheme() {
  return document.documentElement.getAttribute('data-theme') || 'sunset-light'
}

export function setTheme(value) {
  if (!RE.test(value)) return
  document.documentElement.setAttribute('data-theme', value)
  localStorage.setItem(KEY, value)
}
