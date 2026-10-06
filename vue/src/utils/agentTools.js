// 智能助手前端工具（见施工规范 §6 产出、§7.8）
// 会话标识持久化 + 模板详情 → 行程卡片结构的转换（ItineraryCard 两处共用）

const SESSION_KEY = 'agent-session-id'

export function getSessionId() {
  return localStorage.getItem(SESSION_KEY) || ''
}

export function setSessionId(id) {
  if (id) localStorage.setItem(SESSION_KEY, id)
}

export function clearSessionId() {
  localStorage.removeItem(SESSION_KEY)
}

// 模板详情（TemplateDetailVO）→ ItineraryCard 结构（camelCase，供 ItineraryCard.vue 渲染）
export function templateToCard(t) {
  const dayMap = {}
  for (const it of t.items || []) {
    if (!dayMap[it.dayIndex]) {
      dayMap[it.dayIndex] = { dayIndex: it.dayIndex, title: `第 ${it.dayIndex} 天`, items: [] }
    }
    dayMap[it.dayIndex].items.push(it.itemName)
  }
  return {
    title: t.title,
    destination: t.destination,
    dayCount: t.dayCount,
    days: Object.values(dayMap).sort((a, b) => a.dayIndex - b.dayIndex),
    tags: [],
    tips: t.description || null,
  }
}
