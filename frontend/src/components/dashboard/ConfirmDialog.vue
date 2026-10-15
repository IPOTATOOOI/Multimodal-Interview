<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="fixed inset-0 bg-black opacity-50"></div>
    <div class="relative z-10 w-full max-w-md p-6 bg-white rounded-lg shadow-xl dark:bg-gray-800">
      <h3 class="mb-4 text-lg font-medium text-gray-900 dark:text-white">{{ title }}</h3>
      <p class="mb-6 text-gray-500 dark:text-gray-400">{{ message }}</p>
      <div class="flex justify-end gap-2">
        <button
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          @click="$emit('cancel')"
        >
          取消
        </button>
        <button
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
          @click="$emit('confirm')"
        >
          确认删除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  isOpen: boolean
  title: string
  message: string
}>()

defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()
</script>
