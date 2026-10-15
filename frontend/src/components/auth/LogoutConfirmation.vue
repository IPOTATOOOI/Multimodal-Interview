<template>
  <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-sm">
      <h2 class="text-lg font-semibold text-gray-800 dark:text-white">确认退出登录</h2>
      <p class="mt-2 text-gray-600 dark:text-gray-400">您确定要退出登录吗？</p>
      <div class="mt-4 flex justify-end space-x-2">
        <button
          @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          取消
        </button>
        <button
          @click="$emit('confirm')"
          class="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-600"
        >
          确认
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(['confirm', 'cancel'])
</script>