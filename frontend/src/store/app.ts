import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 全局布尔变量，控制图标和名称
    isFullName: true,
  }),
  getters: {
    // 根据isFullName返回对应的图标路径
    appIcon: (state) => (state.isFullName ? '/images/名称.png' : '/images/名称2.png'),
    // 根据isFullName返回对应的系统名称
    appName: (state) => (state.isFullName ? '职面工坊' : '面工坊'),
    // 根据isFullName返回对应的logo路径
    appLogo: (state) => (state.isFullName ? '/images/logo/logo.png' : '/images/logo/logo2.png'),
  },
  actions: {
    // 切换isFullName的值
    toggleFullName() {
      this.isFullName = !this.isFullName
    },
    // 设置isFullName的值
    setFullName(value: boolean) {
      this.isFullName = value
    },
  },
})
