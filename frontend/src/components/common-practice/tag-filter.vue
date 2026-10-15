<template>
  <div class="dark:bg-gray-900 dark:text-white min-h-screen">
    <el-button @click="goToPractice" type="primary" class="mb-4 mt-4 ml-4">
      返回通用训练列表
    </el-button>
    <div class="max-w-3xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md space-y-6">
      <div class="mb-6 text-center">
        <h2 class="text-2xl sm:text-3xl font-bold text-gray-800 dark:text-gray-100">
          面试口头禅过滤器
        </h2>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          语音输入实时检测并高亮"嗯""然后"等低效词汇，优化你的回答表达
        </p>
      </div>

      <!-- 语音输入区域 -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4 transition-all">
        <div class="flex flex-col items-center">
          <div class="w-full mb-4">
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 text-center"
            >
              使用语音输入你的面试回答
            </label>
            <div class="flex justify-center">
              <!-- 语音控制按钮 -->
              <button
                @click="toggleSpeechRecognition"
                :class="[
                  'relative flex items-center justify-center rounded-full w-24 h-24 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-300',
                  isListening
                    ? 'bg-red-500 hover:bg-red-600 focus:ring-red-500 animate-pulse'
                    : 'bg-blue-500 hover:bg-blue-600 focus:ring-blue-500',
                ]"
              >
                <svg
                  v-if="!isListening"
                  class="w-12 h-12 text-white"
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
                <svg
                  v-else
                  class="w-12 h-12 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
                  ></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- 语音识别状态 -->
          <div class="w-full text-center">
            <div v-if="isListening" class="flex flex-col items-center">
              <div class="flex space-x-1 mb-2">
                <div
                  class="w-2 h-6 bg-blue-500 rounded-full animate-wave"
                  style="animation-delay: 0ms"
                ></div>
                <div
                  class="w-2 h-4 bg-blue-500 rounded-full animate-wave"
                  style="animation-delay: 200ms"
                ></div>
                <div
                  class="w-2 h-8 bg-blue-500 rounded-full animate-wave"
                  style="animation-delay: 400ms"
                ></div>
                <div
                  class="w-2 h-5 bg-blue-500 rounded-full animate-wave"
                  style="animation-delay: 600ms"
                ></div>
                <div
                  class="w-2 h-7 bg-blue-500 rounded-full animate-wave"
                  style="animation-delay: 800ms"
                ></div>
              </div>
              <p class="text-sm text-blue-600 dark:text-blue-400 font-medium">
                正在聆听中...请开始说话
              </p>
            </div>
            <p v-else-if="recognitionError" class="text-sm text-red-500 font-medium">
              {{ recognitionError }}
            </p>
            <p v-else class="text-sm text-gray-500 dark:text-gray-400">
              点击麦克风按钮开始语音输入
            </p>
          </div>
        </div>
      </div>

      <!-- 高亮预览区域 -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4 transition-all">
        <div class="flex justify-between items-center mb-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            识别内容（低效词汇已高亮）
          </label>
          <span
            class="text-xs px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
          >
            已检测到 {{ inefficientCount }} 个低效词汇
          </span>
        </div>
        <div
          class="px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 leading-relaxed"
          v-html="highlightedText"
        ></div>
      </div>

      <!-- 低效词汇列表 -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4 transition-all">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          当前过滤的低效词汇
        </h3>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(word, index) in detectedWordsList"
            :key="index"
            class="px-2 py-1 text-xs rounded-full bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200"
          >
            {{ word }}
          </span>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex justify-center gap-4">
        <button
          @click="resetInput"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          重置内容
        </button>
        <button
          @click="copyText"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
          :disabled="!userInput"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            ></path>
          </svg>
          复制优化文本
        </button>
      </div>
    </div>

    <!-- 浏览器兼容性提示 -->
    <div
      v-if="!isSpeechSupported"
      class="max-w-2xl mx-auto mt-6 p-4 bg-yellow-50 dark:bg-yellow-900 rounded-lg"
    >
      <div class="flex items-start">
        <svg class="w-5 h-5 text-yellow-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
            clip-rule="evenodd"
          ></path>
        </svg>
        <div class="text-yellow-700 dark:text-yellow-200 text-sm">
          <strong>注意：</strong>
          您的浏览器不支持语音识别功能，请使用最新版Chrome、Edge或Safari浏览器。语音识别功能需要HTTPS安全连接。
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  methods: {
    goToPractice() {
      this.$router.push({ name: 'CommonPractice' })
    },
  },
  setup() {
    // 配置：低效词汇列表（可扩展）
    const inefficientWords = ref([
      '嗯',
      '嗯嗯',
      '嗯呐',
      '然后',
      '就是',
      '那个',
      '啊',
      '哦',
      '呃',
      '好像',
      '可能',
      '大概',
      '就是说',
      '这个',
      '那个',
      '其实',
      '基本上',
      '比如说',
      '那么',
      '呃...',
      '啊...',
    ])

    // 响应式数据
    const userInput = ref('')
    const highlightedText = ref('')
    const inefficientCount = ref(0)
    const isListening = ref(false)
    const recognition = ref(null)
    const recognitionError = ref('')
    const isSpeechSupported = ref(true)
    const interimTranscript = ref('') // 存储中间结果
    const detectedWordsList = ref([]) // 存储检测到的低效词汇
    const isManualStop = ref(false) // 手动停止标志

    // 初始化语音识别
    const initSpeechRecognition = () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

      if (!SpeechRecognition) {
        isSpeechSupported.value = false
        recognitionError.value = '您的浏览器不支持语音识别功能'
        return
      }

      recognition.value = new SpeechRecognition()
      recognition.value.continuous = true
      recognition.value.pause = false // 确保不会自动暂停
      recognition.value.interimResults = true
      recognition.value.lang = 'zh-CN'

      recognition.value.onresult = (event) => {
        interimTranscript.value = ''
        let finalTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          if (result.isFinal) {
            finalTranscript += result[0].transcript
          } else {
            interimTranscript.value += result[0].transcript
          }
        }

        if (finalTranscript) {
          userInput.value += finalTranscript
          handleInput()
        } else if (interimTranscript.value) {
          handleInput(true)
        }
      }

      recognition.value.onerror = (event) => {
        recognitionError.value = `语音识别错误: ${event.error}`
        isListening.value = false
      }

      recognition.value.onend = () => {
        // 如果有中间结果，添加到最终文本
        if (interimTranscript.value) {
          userInput.value += interimTranscript.value
          interimTranscript.value = ''
          handleInput()
        }

        // 如果不是用户主动停止，则重新启动识别
        if (!isManualStop.value) {
          try {
            recognition.value.start()
          } catch (error) {
            recognitionError.value = '语音识别自动重启失败: ' + error.message
            isListening.value = false
          }
        } else {
          isListening.value = false
        }
      }
    }

    // 开始/停止语音识别
    const toggleSpeechRecognition = () => {
      if (isListening.value) {
        isManualStop.value = true // 标记为用户主动停止
        recognition.value.stop()
        isListening.value = false
      } else {
        try {
          isManualStop.value = false // 重置手动停止标志
          recognition.value.start()
          isListening.value = true
          interimTranscript.value = ''
          recognitionError.value = ''
        } catch (error) {
          recognitionError.value = '无法启动语音识别: ' + error.message
          isListening.value = false
        }
      }
    }

    // 处理输入：实时高亮低效词汇
    const handleInput = (isInterim = false) => {
      const fullText = isInterim ? userInput.value + interimTranscript.value : userInput.value

      if (!fullText) {
        highlightedText.value = ''
        inefficientCount.value = 0
        detectedWordsList.value = []
        return
      }

      // 构建正则：匹配所有低效词汇（全局匹配）
      const regex = new RegExp(`(${inefficientWords.value.map(escapeRegExp).join('|')})`, 'g')

      // 替换匹配到的词汇为高亮标签
      highlightedText.value = fullText.replace(
        regex,
        '<span class="bg-yellow-200 dark:bg-yellow-800 px-0.5 rounded mx-0.1 font-semibold">$1</span>',
      )

      // 统计出现次数并提取检测到的词汇
      const matches = fullText.match(regex)
      inefficientCount.value = matches ? matches.length : 0

      // 更新检测到的词汇列表（去重）
      if (matches) {
        const uniqueWords = [...new Set(matches)]
        detectedWordsList.value = uniqueWords
      } else {
        detectedWordsList.value = []
      }
    }

    // 辅助函数：转义正则特殊字符
    const escapeRegExp = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

    // 重置输入
    const resetInput = () => {
      userInput.value = ''
      highlightedText.value = ''
      inefficientCount.value = 0
      detectedWordsList.value = []
      recognitionError.value = ''
      interimTranscript.value = ''
    }

    // 复制去除低效词汇的优化文本
    const copyText = () => {
      if (!userInput.value) return

      // 创建优化文本（移除低效词汇）
      const regex = new RegExp(`(${inefficientWords.value.map(escapeRegExp).join('|')})`, 'g')
      const cleanText = userInput.value
        .replace(regex, '')
        .replace(/\s{2,}/g, ' ') // 替换多个空格为单个空格
        .trim()

      navigator.clipboard.writeText(cleanText).then(() => {
        // 创建并显示自定义通知
        const notification = document.createElement('div')
        notification.className =
          'fixed bottom-4 right-4 px-4 py-2 bg-green-500 text-white rounded-lg shadow-lg transform transition-transform duration-300 translate-y-20'
        notification.textContent = '优化文本已复制到剪贴板'
        document.body.appendChild(notification)

        // 触发重绘
        void notification.offsetWidth

        // 显示通知
        notification.classList.remove('translate-y-20')
        notification.classList.add('translate-y-0')

        // 3秒后移除通知
        setTimeout(() => {
          notification.classList.remove('translate-y-0')
          notification.classList.add('translate-y-20')
          setTimeout(() => {
            document.body.removeChild(notification)
          }, 300)
        }, 3000)
      })
    }

    // 初始化
    onMounted(() => {
      initSpeechRecognition()
    })

    // 组件卸载时停止语音识别
    onUnmounted(() => {
      if (recognition.value && isListening.value) {
        recognition.value.stop()
      }
    })

    return {
      inefficientWords,
      userInput,
      highlightedText,
      inefficientCount,
      isListening,
      recognitionError,
      isSpeechSupported,
      detectedWordsList,
      toggleSpeechRecognition,
      handleInput,
      resetInput,
      copyText,
    }
  },
}
</script>

<style scoped>
.animate-wave {
  animation: wave 1s infinite ease-in-out;
}

@keyframes wave {
  0%,
  100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(0.5);
  }
}

/* 语音按钮动画 */
@keyframes pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
  }
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
  }
}

.animate-pulse {
  animation: pulse 2s infinite;
}
</style>
