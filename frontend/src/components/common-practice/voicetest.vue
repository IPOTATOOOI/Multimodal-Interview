<template>
  <div class="dark:bg-gray-900 dark:text-white">
    <el-button @click="goToPractice" :disabled="isRecording" type="primary" class="mb-4">
      返回通用训练列表
    </el-button>

    <div class="max-w-3xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md space-y-6">
      <!-- Header -->
      <div class="text-center space-y-2">
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white">面试语音测速仪</h2>
        <p class="text-gray-500 dark:text-gray-300">练习控制语速，确保表达清晰流畅</p>
      </div>

      <!-- Status Indicator -->
      <div
        class="flex items-center justify-center gap-3 px-4 py-3 rounded-lg border transition-colors dark:border-gray-600"
        :class="{
          'bg-red-50 border-red-100 dark:bg-red-900/20 dark:border-red-800': isRecording,
          'bg-gray-50 border-gray-200 dark:bg-gray-700 dark:border-gray-600': !isRecording,
        }"
      >
        <i
          class="fas fa-microphone text-xl transition-transform animate-pulse dark:text-red-400"
          :class="{ 'text-red-500': isRecording }"
        ></i>
        <span
          class="text-sm font-medium dark:text-gray-200"
          :class="{ 'text-red-700 dark:text-red-300': isRecording }"
        >
          {{ isRecording ? '正在录音...' : '点击开始测试' }}
        </span>
      </div>

      <!-- Speed Display -->
      <div class="text-center">
        <div class="text-4xl font-bold text-gray-900 dark:text-white">
          {{ currentSpeed }} <span class="text-lg">WPM</span>
        </div>
        <div class="mt-2 text-gray-600 dark:text-gray-300">
          理想语速:
          <span class="font-semibold text-green-600 dark:text-green-400">120-160 WPM</span>
        </div>
      </div>

      <!-- Controls -->
      <div class="flex justify-center gap-4">
        <button
          @click="toggleRecording"
          :disabled="isProcessing"
          class="px-5 py-2 rounded-md text-white font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
          :class="{
            'bg-green-600 hover:bg-green-700 focus:ring-green-500': !isRecording,
            'bg-red-600 hover:bg-red-700 focus:ring-red-500': isRecording,
            'opacity-60 cursor-not-allowed': isProcessing,
          }"
        >
          {{ isRecording ? '停止' : '开始' }}
        </button>
        <button
          @click="resetTest"
          :disabled="isRecording || !transcript"
          class="px-5 py-2 rounded-md bg-red-500 text-white font-medium hover:bg-red-600 transition focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed dark:focus:ring-offset-gray-800"
        >
          重置
        </button>
      </div>

      <!-- Transcript -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h3 class="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-200">语音转文字</h3>
        <div
          v-if="transcript"
          class="min-h-[80px] text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap"
        >
          {{ transcript }}
        </div>
        <div v-else class="text-gray-400 italic dark:text-gray-400">
          测试完成后，这里将显示你的语音内容
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="feedback" class="rounded-lg p-4 bg-green-50 dark:bg-green-900/20">
        <h3 class="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-200">语速反馈</h3>
        <div
          class="text-lg font-medium mb-2 dark:text-gray-200"
          :class="{
            'text-orange-600 dark:text-orange-400': feedbackClass === 'slow',
            'text-red-600 dark:text-red-400': feedbackClass === 'fast',
            'text-green-600 dark:text-green-400': feedbackClass === 'ideal',
          }"
        >
          {{ feedback }}
        </div>
        <div v-if="tips.length" class="mt-2">
          <h4 class="font-medium text-gray-700 dark:text-gray-300">改进建议:</h4>
          <ul class="list-disc pl-5 mt-1 space-y-1 text-gray-600 dark:text-gray-300">
            <li v-for="(tip, i) in tips" :key="i">{{ tip }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'

export default {
  name: 'SpeechSpeedTester',
  data() {
    return {
      recognition: null,
      isRecording: false,
      isProcessing: false,
      startTime: null,
      endTime: null,
      transcript: '',
      currentSpeed: 0,
      feedback: '',
      feedbackClass: '',
      tips: [],
      idealSpeedRange: [120, 160],
    }
  },
  mounted() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      ElMessage.error('抱歉，您的浏览器不支持语音识别功能。请使用Chrome、Edge等现代浏览器。')
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    this.recognition = new SpeechRecognition()

    this.recognition.continuous = true
    this.recognition.interimResults = true
    this.recognition.lang = 'zh-CN'

    this.recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0])
        .map((result) => result.transcript)
        .join('')
      this.transcript = transcript
    }

    this.recognition.onend = () => {
      if (this.isRecording) {
        this.recognition.start()
      } else {
        this.processResults()
      }
    }

    this.recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
      this.isRecording = false
      this.isProcessing = false
      alert(`语音识别错误: ${event.error}`)
    }
  },
  methods: {
    toggleRecording() {
      if (this.isRecording) {
        this.stopRecording()
      } else {
        this.startRecording()
      }
    },
    startRecording() {
      if (this.isProcessing) return

      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then(() => {
          this.isRecording = true
          this.isProcessing = false
          this.transcript = ''
          this.currentSpeed = 0
          this.feedback = ''
          this.tips = []
          this.startTime = new Date()
          this.recognition.start()
        })
        .catch((error) => {
          console.error('获取麦克风权限失败:', error)
          ElMessage.error('请允许访问麦克风以使用语音测速功能')
        })
    },
    stopRecording() {
      this.isRecording = false
      this.endTime = new Date()
      this.isProcessing = true
      if (this.recognition) {
        try {
          this.recognition.stop() // 然后关闭服务
          setTimeout(() => {
            if (this.isProcessing) {
              this.processResults()
            }
          }, 1000)
        } catch (e) {
          console.error('停止录音失败:', e)
          this.isProcessing = false
        }
      } else {
        this.isProcessing = false
      }
    },
    processResults() {
      if (!this.transcript) {
        this.isProcessing = false
        return
      }

      const duration = (this.endTime - this.startTime) / 60000
      const chineseWords = this.transcript.match(/[\u4e00-\u9fa5]/g) || []
      const englishWords = this.transcript.split(/\s+/).filter((word) => /[a-zA-Z]/.test(word))

      const wordCount = chineseWords.length + englishWords.length
      this.currentSpeed = Math.round(wordCount / duration)

      this.generateFeedback()
      this.isProcessing = false
    },
    generateFeedback() {
      const [minSpeed, maxSpeed] = this.idealSpeedRange

      if (this.currentSpeed < minSpeed) {
        this.feedback = `语速较慢 (${this.currentSpeed} WPM)`
        this.feedbackClass = 'slow'
        this.tips = ['尝试加快语速，保持流畅性', '减少不必要的停顿', '练习用更简洁的语言表达观点']
      } else if (this.currentSpeed > maxSpeed) {
        this.feedback = `语速过快 (${this.currentSpeed} WPM)`
        this.feedbackClass = 'fast'
        this.tips = [
          '适当放慢语速，确保听众能理解',
          '重要内容处可刻意停顿',
          '练习将长句子拆分成短句',
        ]
      } else {
        this.feedback = `语速适中 (${this.currentSpeed} WPM)`
        this.feedbackClass = 'ideal'
        this.tips = ['保持当前语速，非常适合面试场景', '注意语调的抑扬顿挫', '重要观点可适当强调']
      }
    },
    resetTest() {
      this.transcript = ''
      this.currentSpeed = 0
      this.feedback = ''
      this.tips = []
    },
    goToPractice() {
      this.$router.push({ name: 'CommonPractice' })
    },
  },
  beforeDestroy() {
    if (this.recognition) {
      this.recognition.stop()
    }
  },
}
</script>
