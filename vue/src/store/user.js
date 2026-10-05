// 用户状态（见施工规范 §7.6）
import { defineStore } from 'pinia'
import { login as apiLogin, getMe } from '../api/auth'
import { getToken, setToken, removeToken } from '../utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken(),
    userInfo: null,
  }),
  getters: {
    role: (state) => state.userInfo?.role || '',
    isAdmin: (state) => state.userInfo?.role === 'ADMIN',
  },
  actions: {
    async login(payload) {
      const data = await apiLogin(payload)
      this.token = data.token
      this.userInfo = data.user
      setToken(data.token)
      return data.user
    },
    async fetchMe() {
      if (!this.token) return null
      this.userInfo = await getMe()
      return this.userInfo
    },
    logout() {
      this.token = ''
      this.userInfo = null
      removeToken()
    },
  },
})
