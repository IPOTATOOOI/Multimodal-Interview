<template>
  <div class="container mx-auto px-4 py-8">
    <h1
      class="text-3xl font-bold mb-4 dark:text-white text-center flex items-center justify-center"
    >
      <Icon icon="lucide:wrench" class="text-lg mr-2 w-8 h-8 text-blue-500" />
      通用训练工具
    </h1>
    <p class="mt-2 text-lg text-gray-500 dark:text-gray-400 text-center">
      专治「语速失控、口头禅泛滥、抗压崩盘、逻辑混乱」四大表达硬伤
    </p>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-25">
      <!-- 语音测速仪卡片 -->
      <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 transition-all hover:shadow-2xl cursor-pointer"
        @click="navigateTo('speech-speed')"
      >
        <div class="flex items-center mb-6">
          <div class="p-4 rounded-full bg-blue-200 dark:bg-blue-700 mr-6">
            <svg
              class="w-8 h-8 text-blue-700 dark:text-blue-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              ></path>
            </svg>
          </div>
          <h2 class="text-2xl font-semibold dark:text-white">语音测速仪</h2>
        </div>
        <p class="text-gray-700 dark:text-gray-300 text-base">
          测试您的演讲语速，实时显示并对比推荐区间
        </p>
      </div>

      <!-- 口头禅过滤卡片 -->
      <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 transition-all hover:shadow-2xl cursor-pointer"
        @click="navigateTo('filler-words')"
      >
        <div class="flex items-center mb-6">
          <div class="p-4 rounded-full bg-green-200 dark:bg-green-700 mr-6">
            <svg
              class="w-8 h-8 text-green-700 dark:text-green-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              ></path>
            </svg>
          </div>
          <h2 class="text-2xl font-semibold dark:text-white">口头禅过滤</h2>
        </div>
        <p class="text-gray-700 dark:text-gray-300 text-base">一键高亮低效词，帮助提升表达效率</p>
      </div>

      <!-- 压力测试器卡片 -->
      <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 transition-all hover:shadow-2xl cursor-pointer"
        @click="navigateTo('stress-test')"
      >
        <div class="flex items-center mb-6">
          <div class="p-4 rounded-full bg-red-200 dark:bg-red-700 mr-6">
            <svg
              class="w-8 h-8 text-red-700 dark:text-red-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
          </div>
          <h2 class="text-2xl font-semibold dark:text-white">压力测试器</h2>
        </div>
        <p class="text-gray-700 dark:text-gray-300 text-base">倒计时压迫训练，提高抗压能力</p>
      </div>

      <!-- 逻辑思维拆解器卡片 -->
      <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 transition-all hover:shadow-2xl cursor-pointer"
        @click="navigateTo('logic-decomposer')"
      >
        <div class="flex items-center mb-6">
          <div class="p-4 rounded-full bg-purple-200 dark:bg-purple-700 mr-6">
            <svg
              class="w-8 h-8 text-purple-700 dark:text-purple-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
              ></path>
            </svg>
          </div>
          <h2 class="text-2xl font-semibold dark:text-white">逻辑思维拆解器</h2>
        </div>
        <p class="text-gray-700 dark:text-gray-300 text-base">
          结构化模板+案例，让面试官秒懂你的逻辑
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()
const navigateTo = (tool) => {
  // 这里实现路由跳转逻辑
  console.log(`Navigating to ${tool} tool`)
  if (tool === 'speech-speed') {
    router.push('common-practice/voice-test')
  } else if (tool === 'filler-words') {
    router.push('common-practice/tag-filter')
  } else if (tool === 'stress-test') {
    router.push('common-practice/pressure-test')
  } else if (tool === 'logic-decomposer') {
    router.push('common-practice/logic-decomposer')
  }
}
</script>
