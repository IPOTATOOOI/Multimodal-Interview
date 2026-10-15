<template>
  <section id="hero" class="mt-5 overflow-hidden">
    <div class="top-section pt-16 pb-32" :style="gradientStyle">
      <div class="container mx-auto px-4 md:px-8 mt-0 relative">
        <div class="flex flex-col md:flex-row items-center">
          <div class="w-full md:w-1/2 mb-12 md:mb-0 md:pr-12">
            <div class="mb-6 animate-enter delay-100 flex items-center gap-3">
              <img src="/images/logo/logo2.png" alt="Logo" class="h-16 w-auto object-contain" />
              <img src="/images/名称2.png" alt="面工坊" class="h-16 w-auto object-contain" />
            </div>

            <h1
              class="text-4xl md:text-5xl font-bold text-gray-700 dark:text-white mb-6 leading-tight animate-enter delay-200"
            >
              提升面试技巧，<br />
              <span class="text-gray-800 dark:text-gray-100">轻松斩获心仪Offer</span>
            </h1>

            <div class="text-lg text-blue-50 mb-10 space-y-3">
              <div class="list-item-hover flex items-center animate-enter delay-300">
                <i class="fas fa-check-circle text-blue-400 dark:text-blue-300 mr-2"></i>
                <span class="inline-flex items-center text-gray-600 dark:text-gray-200 font-medium">
                  <svg
                    class="w-5 h-5 mr-1 text-blue-500"
                    viewBox="0 0 1024 1024"
                    version="1.1"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M512 42.666667c259.2 0 469.333333 210.133333 469.333333 469.333333a467.370667 467.370667 0 0 1-103.850666 294.485333l-60.757334-60.8A382.336 382.336 0 0 0 896 512c0-212.074667-171.925333-384-384-384S128 299.925333 128 512s171.925333 384 384 384c93.376 0 178.986667-33.322667 245.546667-88.746667l60.565333 60.522667A467.498667 467.498667 0 0 1 512 981.333333C252.8 981.333333 42.666667 771.2 42.666667 512S252.8 42.666667 512 42.666667z m181.013333 305.984l60.352 60.352-301.696 301.696-181.034666-181.034667L330.986667 469.333333l120.682666 120.682667 241.344-241.365333z"
                      fill="currentColor"
                    ></path>
                  </svg>
                  无需预约面试官，随时练习
                </span>
              </div>
              <div class="list-item-hover flex items-center animate-enter delay-400">
                <i class="fas fa-check-circle text-blue-400 dark:text-blue-300 mr-2"></i>
                <span class="inline-flex items-center text-gray-600 dark:text-gray-200 font-medium">
                  <svg
                    class="w-5 h-5 mr-1 text-blue-500"
                    viewBox="0 0 1024 1024"
                    version="1.1"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M512 42.666667c259.2 0 469.333333 210.133333 469.333333 469.333333a467.370667 467.370667 0 0 1-103.850666 294.485333l-60.757334-60.8A382.336 382.336 0 0 0 896 512c0-212.074667-171.925333-384-384-384S128 299.925333 128 512s171.925333 384 384 384c93.376 0 178.986667-33.322667 245.546667-88.746667l60.565333 60.522667A467.498667 467.498667 0 0 1 512 981.333333C252.8 981.333333 42.666667 771.2 42.666667 512S252.8 42.666667 512 42.666667z m181.013333 305.984l60.352 60.352-301.696 301.696-181.034666-181.034667L330.986667 469.333333l120.682666 120.682667 241.344-241.365333z"
                      fill="currentColor"
                    ></path>
                  </svg>
                  智能反馈，精准指出改进点
                </span>
              </div>
              <div class="list-item-hover flex items-center animate-enter delay-500">
                <i class="fas fa-check-circle text-blue-400 dark:text-blue-300 mr-2"></i>
                <span class="inline-flex items-center text-gray-600 dark:text-gray-200 font-medium">
                  <svg
                    class="w-5 h-5 mr-1 text-blue-500"
                    viewBox="0 0 1024 1024"
                    version="1.1"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M512 42.666667c259.2 0 469.333333 210.133333 469.333333 469.333333a467.370667 467.370667 0 0 1-103.850666 294.485333l-60.757334-60.8A382.336 382.336 0 0 0 896 512c0-212.074667-171.925333-384-384-384S128 299.925333 128 512s171.925333 384 384 384c93.376 0 178.986667-33.322667 245.546667-88.746667l60.565333 60.522667A467.498667 467.498667 0 0 1 512 981.333333C252.8 981.333333 42.666667 771.2 42.666667 512S252.8 42.666667 512 42.666667z m181.013333 305.984l60.352 60.352-301.696 301.696-181.034666-181.034667L330.986667 469.333333l120.682666 120.682667 241.344-241.365333z"
                      fill="currentColor"
                    ></path>
                  </svg>
                  多场景模拟，真实还原环境
                </span>
              </div>
            </div>

            <div class="flex flex-col sm:flex-row gap-4 animate-enter delay-1000">
              <button
                @click="startInterview"
                class="btn-bounce bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-bold text-lg py-4 px-10 rounded-full shadow-xl hover:shadow-blue-500/50 transition-all duration-300 flex items-center justify-center transform hover:scale-105"
              >
                立即开始使用
                <svg
                  class="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  ></path>
                </svg>
              </button>
            </div>
          </div>

          <div class="w-full md:w-1/2 flex justify-center animate-enter delay-400">
            <div class="relative img-float drop-shadow-2xl">
              <img
                src="/images/面试.png"
                alt="AI面试"
                class="w-full max-w-lg h-auto rounded-2xl object-cover"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="curve-separator border-none">
        <svg viewBox="0 0 1000 100" preserveAspectRatio="none">
          <path
            d="M1000,0c0,0 -420.987,98 -650,98c-229.013,0 -350,-98 -350,-98l0,100l1000,0l0,-100Z"
          ></path>
        </svg>
      </div>
    </div>

    <div class="container mx-auto px-4 md:px-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 mt-10 pb-16">
        <div
          class="card animate-enter delay-600 bg-white dark:bg-gray-800 shadow-lg border border-gray-50 dark:border-gray-700"
        >
          <div class="flex card-1 flex-row items-center justify-start p-5 h-full gap-4">
            <div class="icon-container-1">
              <moni />
            </div>
            <div class="text-left">
              <h3 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-1">模拟面试</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                沉浸式多场景 AI 面试还原，实时捕捉表达细节与肢体语言
              </p>
            </div>
          </div>
        </div>

        <div
          class="card animate-enter delay-700 bg-white dark:bg-gray-800 shadow-lg border border-gray-50 dark:border-gray-700"
        >
          <div class="flex card-1 flex-row items-center justify-start p-5 h-full gap-4">
            <div class="icon-container-1">
              <lishi />
            </div>
            <div class="text-left">
              <h3 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-1">历史测评</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                自动归档面试数据，精准定位短板，跟踪进步轨迹
              </p>
            </div>
          </div>
        </div>

        <div
          class="card animate-enter delay-800 bg-white dark:bg-gray-800 shadow-lg border border-gray-50 dark:border-gray-700"
        >
          <div class="flex card-1 flex-row items-center justify-start p-5 h-full gap-4">
            <div class="icon-container-1">
              <xuexi />
            </div>
            <div class="text-left">
              <h3 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-1">学习资源</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                海量学习资源库，行业面试真题与技巧，攻克难题
              </p>
            </div>
          </div>
        </div>

        <div
          class="card animate-enter delay-900 bg-white dark:bg-gray-800 shadow-lg border border-gray-50 dark:border-gray-700"
        >
          <div class="flex card-1 flex-row items-center justify-start p-5 h-full gap-4">
            <div class="icon-container-1">
              <jianli />
            </div>
            <div class="text-left">
              <h3 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-1">AI 简历</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                智能结构化呈现经历，量化成果，突破简历筛选瓶颈
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useAppStore } from '@/store/app'

const appStore = useAppStore()
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useTheme } from '@/components/layout/ThemeProvider.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

import moni from './Card/moni.vue'
import lishi from './Card/lishi.vue'
import xuexi from './Card/xuexi.vue'
import jianli from './Card/jianli.vue'

const currentPageTitle = ref('Blank Page')

const { isDarkMode } = useTheme()

// 背景渐变保持或者微调，使其更干净
const gradientStyle = computed(() => ({
  background: isDarkMode.value
    ? 'radial-gradient(circle at 90% 10%, rgba(148, 51, 255, 0.4) 0%, rgba(103, 58, 183, 0.3) 30%, rgba(41, 98, 255, 0.2) 70%, rgba(16, 24, 40, 1) 100%)'
    : 'radial-gradient(circle at 90% 10%, rgba(230, 240, 255, 0.9) 0%, rgba(240, 245, 255, 0.8) 30%, rgba(245, 248, 255, 0.8) 70%, rgba(255, 255, 255, 0.9) 100%)',
}))

const startInterview = () => {
  router.push('/app/interview')
}
</script>

<style scoped>
/* ==================== 动画系统 ==================== */

/* 1. 基础进场动画 (向上浮现) */
.animate-enter {
  opacity: 0;
  animation: fadeInUp 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 延迟类 */
.delay-100 {
  animation-delay: 100ms;
}
.delay-200 {
  animation-delay: 200ms;
}
.delay-300 {
  animation-delay: 300ms;
}
.delay-400 {
  animation-delay: 400ms;
}
.delay-500 {
  animation-delay: 500ms;
}
.delay-600 {
  animation-delay: 600ms;
}
.delay-700 {
  animation-delay: 700ms;
}
.delay-800 {
  animation-delay: 800ms;
}
.delay-900 {
  animation-delay: 900ms;
}
.delay-1000 {
  animation-delay: 1000ms;
}

/* 2. 按钮持续跳动动画 */
.btn-bounce {
  animation: customBounce 3.5s infinite cubic-bezier(0.28, 0.84, 0.42, 1);
}

@keyframes customBounce {
  0%,
  20%,
  50%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

/* 3. 图片上下悬浮动画 */
.img-float {
  animation: float 8s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-15px);
  }
  100% {
    transform: translateY(0px);
  }
}

/* 4. 列表悬停微小滑动 */
.list-item-hover {
  transition: transform 0.5s ease;
}
.list-item-hover:hover {
  transform: translateX(8px);
}

/* ==================== 组件样式 ==================== */

.card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  height: 140px; /* 稍微调高以适应内容 */
}

.card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow:
    0 20px 25px -5px rgba(59, 130, 246, 0.1),
    0 10px 10px -5px rgba(59, 130, 246, 0.04);
}

.dark .card {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

.dark .card:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  border-color: #374151; /* 鼠标悬浮时边框微亮 */
}

.top-section {
  position: relative;
  overflow: hidden;
  padding-bottom: 120px; /* 为弧线流出空间 */
}

.curve-separator {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 98px;
}

.curve-separator svg {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* 适配暗亮模式的波浪底色 */
.curve-separator path {
  fill: #ffffff; /* 如果你的卡片区背景是白色，这里填白色 */
}

.dark .curve-separator path {
  fill: #111827; /* 对应 Tailwind 的 gray-900 */
}

/* 图标容器基座 */
.icon-container-1 {
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.dark .icon-container-1 {
  background: linear-gradient(135deg, #1e3a8a, #1e40af);
}

.card:hover .icon-container-1 {
  transform: rotate(-5deg) scale(1.1);
}

@media screen and (max-width: 1600px) {
  .top-section {
    padding-bottom: 80px;
  }
  .curve-separator {
    height: 50px;
  }
  .card {
    height: auto;
    min-height: 120px;
  }
  .card-1 {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    padding: 1rem;
    gap: 1rem;
  }
  .icon-container-1 {
    min-width: 60px;
    width: 60px;
    height: 60px;
    flex-shrink: 0;
  }
}

@media screen and (max-width: 1024px) {
  .top-section {
    padding-bottom: 60px;
  }
  .curve-separator {
    height: 40px;
  }
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .card {
    height: auto;
    min-height: 110px;
  }
  h1 {
    font-size: 2.5rem !important;
  }
}

@media screen and (max-width: 768px) {
  .top-section {
    padding-bottom: 40px;
  }
  .curve-separator {
    height: 30px;
  }
  .card {
    height: auto;
    min-height: 100px;
  }
  h1 {
    font-size: 2rem !important;
  }
  .btn-bounce {
    padding: 0.75rem 2rem;
    font-size: 1rem;
  }
  .icon-container-1 {
    min-width: 50px;
    width: 50px;
    height: 50px;
  }
  .card-1 {
    padding: 0.75rem;
  }
}

@media screen and (max-width: 480px) {
  .top-section {
    padding-bottom: 30px;
  }
  .curve-separator {
    height: 20px;
  }
  h1 {
    font-size: 1.75rem !important;
  }
  .btn-bounce {
    padding: 0.5rem 1.5rem;
    font-size: 0.875rem;
  }
  .icon-container-1 {
    min-width: 40px;
    width: 40px;
    height: 40px;
  }
  .card-1 {
    padding: 0.5rem;
  }
  .list-item-hover {
    font-size: 0.875rem;
  }
}
</style>
