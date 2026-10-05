// 多页签状态（见施工规范 §7.6）
import { defineStore } from 'pinia'

export const useTagsViewStore = defineStore('tagsView', {
  state: () => ({
    visited: [],
    cached: [],
  }),
  actions: {
    addView(view) {
      if (!this.visited.some((v) => v.path === view.path)) {
        this.visited.push(view)
      }
      if (view.keepAlive && !this.cached.includes(view.name)) {
        this.cached.push(view.name)
      }
    },
    removeView(path) {
      const idx = this.visited.findIndex((v) => v.path === path)
      if (idx > -1) {
        const [removed] = this.visited.splice(idx, 1)
        const cidx = this.cached.indexOf(removed.name)
        if (cidx > -1) this.cached.splice(cidx, 1)
      }
    },
  },
})
