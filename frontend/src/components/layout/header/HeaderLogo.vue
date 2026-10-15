<template>
  <router-link to="/" class="lg:hidden">
    <div class="flex flex-row justify-center items-center gap-4">
      <img class="w-15" :src="appStore.appLogo" alt="Logo" />
      <img class="h-12" :src="appStore.appIcon" :alt="appStore.appName" />
    </div>
  </router-link>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useAppStore } from '@/store/app'

const appStore = useAppStore()
</script>
