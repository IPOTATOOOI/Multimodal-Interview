<template>
  <ThemeProvider>
    <SidebarProvider>
      <RouterView />
    </SidebarProvider>
  </ThemeProvider>
</template>

<script setup lang="ts">
import { watch, onMounted } from 'vue'
import ThemeProvider from './components/layout/ThemeProvider.vue'
import SidebarProvider from './components/layout/SidebarProvider.vue'
import { useAppStore } from './store/app'

const appStore = useAppStore()

// 监听isFullName变化，动态修改页面标题
watch(
  () => appStore.isFullName,
  (newValue) => {
    document.title = newValue ? '职面工坊-智面未来，智取先机' : '面工坊-智面未来，智取先机'
  },
  { immediate: true },
)

// 初始化页面标题
onMounted(() => {
  document.title = appStore.isFullName ? '职面工坊-智面未来，智取先机' : '面工坊-智面未来，智取先机'
})
</script>

<style></style>
