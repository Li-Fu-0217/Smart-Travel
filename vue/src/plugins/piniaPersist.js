// 简易 Pinia 持久化插件：store 变化时写回 localStorage（见施工规范 §7.6）
const KEY_PREFIX = 'travel-assistant-store:'

export function piniaPersist({ store }) {
  const key = KEY_PREFIX + store.$id
  // 创建时读回
  const saved = localStorage.getItem(key)
  if (saved) {
    try {
      store.$patch(JSON.parse(saved))
    } catch (e) {
      /* 忽略损坏的缓存 */
    }
  }
  // 变化时写回
  store.$subscribe((_mutation, state) => {
    localStorage.setItem(key, JSON.stringify(state))
  })
}
