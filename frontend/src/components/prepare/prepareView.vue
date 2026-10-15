<template>
  <div
    class="custom-scrollbar bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200 min-h-screen transition-colors duration-300"
  >
    <!-- 添加加载状态 -->
    <div
      v-if="loading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <!-- 显示错误信息 -->
    <div
      v-if="error"
      class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
      role="alert"
    >
      <span class="block sm:inline">{{ error }}</span>
    </div>
    <!-- 顶部信息区 -->
    <header
      class="bg-gradient-to-r from-primary-light to-primary-dark dark:from-primary-dark dark:to-blue-900 text-white p-6 shadow-md relative"
    >
      <div
        class="container mx-auto max-w-6xl flex flex-col md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-blue-400">
            「{{ route.params.category }} - {{ route.params.job }}」面试准备资源
          </h1>
          <p class="mt-2 opacity-90 text-blue-400 flex items-center">
            <Icon icon="lucide:star" class="w-4 h-4 mr-1" />
            专属个性化面试资源，助你轻松应对面试挑战
          </p>
        </div>

        <!-- 模式切换按钮 -->
        <div class="relative mb-4">
          <button
            @click="toggleDarkMode"
            class="flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-50 shadow-lg hover:shadow-xl transform transition-all duration-300 active:scale-95"
            aria-label="切换深色/浅色模式"
          >
            <svg
              t="1751816516961"
              class="icon"
              viewBox="0 0 1024 1024"
              version="1.1"
              xmlns="http://www.w3.org/2000/svg"
              p-id="9080"
              width="30"
              height="30"
            >
              <path
                d="M775.68 988.16H508.587a149.333 149.333 0 0 1-96.64-42.667L181.76 715.733a101.76 101.76 0 0 1 143.573-144v-266.24a101.76 101.76 0 1 1 203.307 0v147.414l218.027 51.626A170.667 170.667 0 0 1 878.293 671.36V886.4A101.76 101.76 0 0 1 775.68 988.16zM253.653 606.293a37.76 37.76 0 0 0-26.666 64L456.96 900.48a85.333 85.333 0 0 0 51.413 23.467H775.68a37.76 37.76 0 0 0 37.76-37.76v-215.04a106.667 106.667 0 0 0-82.56-104.534l-241.493-57.386a32 32 0 0 1-24.534-31.147V305.493a37.76 37.76 0 1 0-75.306 0V648.96a32 32 0 0 1-54.614 22.613l-54.4-54.4a37.547 37.547 0 0 0-26.88-10.88z"
                p-id="9081"
                fill="#ffffff"
              ></path>
              <path
                d="M616.96 411.947A32 32 0 0 1 588.8 364.8a181.333 181.333 0 1 0-320 0 32 32 0 1 1-55.467 30.507 245.333 245.333 0 1 1 431.787 0 32 32 0 0 1-28.16 16.64z"
                p-id="9082"
                fill="#ffffff"
              ></path>
            </svg>
          </button>
          <span
            class="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs text-blue-400 opacity-80 whitespace-nowrap"
          >
            {{ '切换为' + (isDarkMode ? '浅色模式' : '深色模式') }}
          </span>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="container mx-auto max-w-6xl px-4 py-8">
      <!-- 岗位核心能力 -->
      <section class="mb-12">
        <div class="flex items-center justify-between mb-6">
          <h2
            class="text-xl md:text-2xl font-bold text-primary-light dark:text-primary-dark flex items-center"
          >
            <Icon icon="lucide:circle-arrow-out-down-right" class="w-7 h-7 mr-2 text-blue-700" />
            岗位核心能力
          </h2>
          <span
            class="text-sm bg-primary-light/20 dark:bg-primary-dark/20 text-primary-light dark:text-blue-300 px-3 py-1 rounded-full flex items-center"
          >
            <span class="font-bold text-2xl text-blue-600 dark:text-blue-400 mr-1">{{
              competencies.length
            }}</span>
            项关键能力
          </span>
        </div>
        <div
          ref="scrollContainer"
          class="flex overflow-x-auto space-x-4 border-t-0 custom-scrollbar"
          @mouseenter="stopAutoScroll"
          @mouseleave="startAutoScroll"
        >
          <div
            v-for="(comp, index) in competencies"
            :key="index"
            class="w-96 h-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 flex-shrink-0 border border-gray-200 dark:border-gray-700"
          >
            <div class="flex flex-col md:flex-row items-center justify-center">
              <div
                class="bg-primary-light/10 dark:bg-primary-dark/20 text-primary-light dark:text-blue-400 p-1 rounded-sm mr-3 mt-4"
              >
                <Icon icon="lucide:star" class="w-6 h-6 text-blue-700" />
              </div>
              <div class="flex-1">
                <h3 class="font-bold text-lg text-gray-800 dark:text-white">
                  {{ comp.name }}
                </h3>
                <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                  {{ comp.description }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 悬浮按钮 -->
      <button
        @click="startInterview"
        class="fixed bottom-6 right-6 z-10 flex items-center px-5 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 dark:bg-secondary-dark text-white rounded-full shadow-lg hover:from-purple-600 hover:to-indigo-700 transition-all transform hover:scale-105 flex items-center"
      >
        胸有成竹了？立即开始面试
      </button>

      <!-- 术语速查 -->
      <section class="mb-12">
        <div class="flex items-center justify-between mb-6">
          <h2
            class="text-xl md:text-2xl font-bold text-primary-light dark:text-primary-dark flex items-center"
          >
            <Icon icon="lucide:scan-search" class="w-8 h-8 mr-2 text-green-700" />
            岗位术语速查
          </h2>
          <span
            class="text-sm bg-primary-light/20 dark:bg-primary-dark/20 text-primary-light dark:text-blue-300 px-3 py-1 rounded-full flex items-center"
          >
            <span class="font-bold text-2xl text-green-600 dark:text-green-400 mr-1">{{
              terms.length
            }}</span>
            个专业术语
          </span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <div
            v-for="(term, index) in terms"
            :key="index"
            class="flip-card cursor-pointer h-48"
            :class="{ flipped: currentFlippedIndex === index }"
            @click="handleFlip(index)"
          >
            <div class="flip-card-inner rounded-xl">
              <div
                class="flip-card-front bg-white dark:bg-gray-800 rounded-xl shadow h-full p-5 flex flex-col justify-between border border-gray-200 dark:border-gray-700"
              >
                <div class="relative w-full">
                  <!-- 右上角频率标签 -->
                  <div class="absolute top-2 right-2">
                    <span
                      :class="{
                        'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300':
                          term.frequency === '高频',
                        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300':
                          term.frequency === '中频',
                        'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300':
                          term.frequency === '低频',
                      }"
                      class="text-sm px-2 py-1 rounded-lg font-medium"
                    >
                      {{ term.frequency }}
                    </span>
                  </div>

                  <!-- 中间大字展示 -->
                  <div class="flex items-center justify-center h-full py-8">
                    <h3 class="font-bold text-3xl mt-8 text-center text-gray-800 dark:text-white">
                      {{ term.name }}
                    </h3>
                  </div>
                </div>
                <div
                  class="text-center text-gray-500 dark:text-gray-400 text-sm mt-4 flex items-center justify-center"
                >
                  点击翻转查看解释
                </div>
              </div>
              <div
                class="flip-card-back bg-white dark:bg-gray-800 rounded-xl shadow h-full p-5 flex items-center justify-center border border-gray-200 dark:border-gray-700"
              >
                <!-- 移除p标签可能的默认margin，确保垂直居中无偏移 -->
                <p class="text-gray-600 dark:text-gray-300 text-center m-0 text-2xl font-bold">
                  {{ term.definition }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 高频题型拆解 -->
      <section>
        <div class="flex items-center justify-between mb-6">
          <h2
            class="text-xl md:text-2xl font-bold text-primary-light dark:text-primary-dark flex items-center"
          >
            <Icon icon="lucide:clipboard-list" class="w-8 h-8 mr-2 text-orange-600" />
            高频题型拆解
          </h2>
          <span
            class="text-sm bg-primary-light/20 dark:bg-primary-dark/20 text-primary-light dark:text-blue-300 px-3 py-1 rounded-full"
          >
            <span class="font-bold text-2xl text-orange-600 dark:text-orange-400 mr-1">{{
              questions.length
            }}</span>
            种高频题型
          </span>
        </div>

        <div class="space-y-8">
          <div
            v-for="(q, index) in questions"
            :key="index"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 transition-transform duration-300"
          >
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-start">
                <div
                  class="bg-gradient-to-r from-red-500 to-orange-500 text-white text-sm font-bold px-3 py-1 rounded mr-3"
                >
                  题型 {{ index + 1 }}
                </div>
                <h3 class="font-bold text-lg text-gray-800 dark:text-white">{{ q.type }}</h3>
              </div>
              <div
                class="mt-4 bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <p class="italic font-bold text-gray-700 dark:text-gray-300">"{{ q.example }}"</p>
              </div>
            </div>

            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
              <h4
                class="font-bold text-primary-light dark:text-primary-dark flex items-center mb-3"
              >
                <Icon icon="lucide:target" class="w-5 h-5 mr-2 text-orange-500" /> 评分重点
              </h4>
              <div class="mt-3 flex flex-wrap gap-2">
                <span
                  v-for="(point, idx) in q.scoringPoints"
                  :key="idx"
                  class="bg-gradient-to-r from-red-400/20 to-orange-400/20 dark:from-red-500/20 dark:to-orange-500/20 text-red-700 dark:text-red-100 px-3 py-1.5 rounded-full text-sm font-medium"
                >
                  {{ point }}
                </span>
              </div>
            </div>

            <div class="p-6">
              <div class="flex justify-between items-center mb-4">
                <h4 class="font-bold text-primary-light dark:text-primary-dark flex items-center">
                  <Icon icon="lucide:circle-check-big" class="w-5 h-5 mr-2 text-orange-500" />
                  优秀回答模板
                </h4>
                <button
                  @click="q.showTemplate = !q.showTemplate"
                  class="text-sm text-primary-light dark:text-blue-400 hover:text-primary-dark dark:hover:text-blue-300 font-medium flex items-center transition-colors"
                >
                  <i :class="q.showTemplate ? 'fas fa-eye-slash' : 'fas fa-eye'" class="mr-1.5"></i>
                  {{ q.showTemplate ? '隐藏模板' : '显示模板' }}
                </button>
              </div>

              <transition name="slide-fade">
                <div
                  v-if="q.showTemplate"
                  class="relative mt-4 bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <pre
                    class="whitespace-pre-wrap text-sm leading-relaxed text-gray-800 dark:text-gray-200 font-sans"
                    >{{ q.template }}</pre
                  >
                  <button
                    @click="copyToClipboard(q.template)"
                    class="absolute top-3 right-3 px-3 py-1.5 bg-white dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-500 transition-colors flex items-center text-sm"
                  >
                    <Icon icon="lucide:copy" class="w-4 h-4 mr-1" /> 复制
                  </button>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Icon } from '@iconify/vue'
import { getApiUrl } from '@/config/api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const error = ref('')

// 修改数据结构为空数组
const competencies = ref([])
const terms = ref([])
const questions = ref([])
const startInterview = () => {
  router.push('/app/interview')
}

const isDarkMode = ref(false)

// 切换深色/浅色模式
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
    localStorage.theme = 'dark'
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.theme = 'light'
  }
}

// 添加后端请求函数
const fetchPositionInfo = async () => {
  loading.value = true
  error.value = ''

  try {
    // 创建 FormData 对象
    const formData = new FormData()
    formData.append('domain_name', route.params.category)
    formData.append('position_name', route.params.job)

    const response = await axios.post(
      getApiUrl('/position_info'),
      formData,
      // 不需要设置 Content-Type，axios 会自动设置为 multipart/form-data
    )

    console.log(response.data)
    // 转换核心能力数据
    competencies.value = response.data.core_competences.map((item) => ({
      name: item.competence_name,
      description: item.competence_description,
    }))

    // 转换术语数据
    terms.value = response.data.terms.map((item) => ({
      name: item.term_name,
      frequency: item.frequency,
      definition: item.term_explanation,
      flipped: false,
    }))

    // 转换高频题型数据
    questions.value = response.data.high_freq_questions.map((item) => ({
      type: item.question_type_name,
      example: item.question_example,
      // 将 scoring_focus 字符串转换为数组
      scoringPoints: item.scoring_focus
        .split('；')
        .map((point) => point.replace(/^\d+\.\s*/, '').trim()),
      template: item.answer_template,
      showTemplate: false,
    }))
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = '未找到该领域或岗位信息'
    } else {
      error.value = '获取岗位信息失败，请稍后重试'
    }
    ElMessage.error(error.value)
    // 可选：导航回上一页
    // router.back()
  } finally {
    loading.value = false
  }
}

// 添加一个新的 ref 来跟踪当前翻转的卡片索引
const currentFlippedIndex = ref(-1) // -1 表示没有卡片被翻转

// 修改翻转处理函数
const handleFlip = (index) => {
  if (currentFlippedIndex.value === index) {
    // 如果点击的是当前已翻转的卡片,则翻转回去
    currentFlippedIndex.value = -1
  } else {
    // 如果点击的是其他卡片,则更新当前翻转的索引
    currentFlippedIndex.value = index
  }
}

// 初始化主题
onMounted(async () => {
  // 主题初始化
  if (
    localStorage.theme === 'dark' ||
    (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
  ) {
    document.documentElement.classList.add('dark')
    isDarkMode.value = true
  } else {
    document.documentElement.classList.remove('dark')
    isDarkMode.value = false
  }

  // 获取岗位信息
  await fetchPositionInfo()
  startAutoScroll()
})

const scrollContainer = ref(null)
let scrollInterval = null

const startAutoScroll = () => {
  stopAutoScroll()
  scrollInterval = setInterval(() => {
    const container = scrollContainer.value
    if (container) {
      container.scrollLeft += 0.4 // 控制速度

      // 循环滚动逻辑
      if (container.scrollLeft + container.clientWidth >= container.scrollWidth) {
        container.scrollLeft = 0
      }
    }
  }, 10)
}

const stopAutoScroll = () => clearInterval(scrollInterval)

onMounted(() => {
  startAutoScroll()
})

onBeforeUnmount(() => {
  stopAutoScroll()
})

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
  alert('模板已复制到剪贴板！')
}

const startPractice = (question) => {
  console.log('开始练习:', question.type)
  // 实际应用中这里会导航到练习页面
  alert(`开始练习: ${question.type}`)
}
</script>

<style scoped>
.flip-card {
  perspective: 1000px;
  height: 220px;
}
.flip-card-inner {
  transition: transform 0.6s;
  transform-style: preserve-3d;
  position: relative;
  width: 100%;
  height: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.flip-card.flipped .flip-card-inner {
  transform: rotateY(180deg);
}
.flip-card-front,
.flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
}
.flip-card-back {
  transform: rotateY(180deg);
  padding: 1.25rem;
}
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(10px);
  opacity: 0;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

* {
  transition:
    background-color 0.3s,
    border-color 0.3s;
}
</style>
