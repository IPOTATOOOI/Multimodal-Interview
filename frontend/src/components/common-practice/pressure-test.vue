<template>
  <div class="dark:bg-gray-900 dark:text-white min-h-screen p-4">
    <!-- 返回按钮 -->
    <el-button @click="goToPractice" type="primary" class="mb-4"> 返回通用训练列表 </el-button>

    <div class="max-w-4xl mx-auto">
      <!-- 标题区域 -->
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-gray-800 dark:text-white mb-2">面试压力测试器</h1>
        <p class="text-gray-600 dark:text-gray-300">自定义题目 + 倒计时训练，提升面试抗压能力</p>
      </div>

      <!-- 主内容区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：题目管理 -->
        <div class="lg:col-span-1 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-white">题目管理</h2>
            <button
              @click="showAddForm = !showAddForm"
              class="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm flex items-center"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                ></path>
              </svg>
              添加题目
            </button>
          </div>

          <!-- 添加题目表单 -->
          <div
            v-if="showAddForm"
            class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg transition-all"
          >
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                >面试题目</label
              >
              <textarea
                v-model="newQuestion.text"
                rows="3"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                placeholder="请输入面试题目..."
              ></textarea>
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                >参考答案</label
              >
              <textarea
                v-model="newQuestion.reference"
                rows="3"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                placeholder="请输入参考答案..."
              ></textarea>
            </div>

            <!-- 新增：题目自定义时间 -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                题目时间（分钟）<span class="text-gray-400 text-xs"
                  >（可选，默认使用全局时间）</span
                >
              </label>
              <input
                type="number"
                v-model.number="newQuestion.customTime"
                min="1"
                max="30"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                placeholder="使用全局时间"
              />
            </div>

            <div class="flex justify-end space-x-2">
              <button
                @click="cancelAddQuestion"
                class="px-3 py-1 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors text-sm"
              >
                取消
              </button>
              <button
                @click="addQuestion"
                class="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm flex items-center"
                :disabled="!newQuestion.text"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  ></path>
                </svg>
                添加
              </button>
            </div>
          </div>

          <!-- 题目列表 -->
          <div class="space-y-3 max-h-[500px] overflow-y-auto pr-2">
            <div
              v-for="(q, index) in questions"
              :key="q.id"
              class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600 transition-all hover:shadow"
            >
              <div class="flex justify-between items-start">
                <div class="font-medium text-gray-800 dark:text-gray-100 flex-1 pr-2">
                  {{ index + 1 }}. {{ q.text }}
                </div>
                <button
                  @click="deleteQuestion(q.id)"
                  class="p-1 text-gray-500 hover:text-red-500 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    ></path>
                  </svg>
                </button>
              </div>

              <!-- 显示题目自定义时间 -->
              <div
                v-if="q.customTime"
                class="mt-1 text-xs text-blue-600 dark:text-blue-400 flex items-center"
              >
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
                自定义时间: {{ q.customTime }} 分钟
              </div>

              <div class="mt-2">
                <button
                  @click="toggleReference(q.id)"
                  class="text-xs text-blue-500 hover:text-blue-700 transition-colors flex items-center"
                >
                  <svg
                    :class="{ 'transform rotate-90': q.showReference }"
                    class="w-4 h-4 mr-1 transition-transform"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 5l7 7-7 7"
                    ></path>
                  </svg>
                  {{ q.showReference ? '隐藏答案' : '查看答案' }}
                </button>

                <div
                  v-if="q.showReference"
                  class="mt-2 p-2 bg-white dark:bg-gray-600 rounded text-sm text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-500"
                >
                  {{ q.reference || '暂无参考答案' }}
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div
              v-if="questions.length === 0"
              class="text-center py-8 text-gray-500 dark:text-gray-400"
            >
              <svg
                class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              <p>暂无题目，请添加自定义题目</p>
            </div>
          </div>
        </div>

        <!-- 右侧：测试区域 -->
        <div class="lg:col-span-2">
          <!-- 测试设置 -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-white mb-4">测试设置</h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >默认每题时间（分钟）</label
                >
                <div class="flex items-center">
                  <button
                    @click="decreaseTime"
                    class="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-l-lg border-r border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                    :disabled="timePerQuestion <= 1"
                  >
                    -
                  </button>
                  <input
                    type="number"
                    v-model.number="timePerQuestion"
                    min="1"
                    max="30"
                    class="w-full px-4 py-2 bg-white dark:bg-gray-800 text-center text-gray-900 dark:text-white border-t border-b border-gray-300 dark:border-gray-600 focus:outline-none"
                  />
                  <button
                    @click="increaseTime"
                    class="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-r-lg border-l border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                    :disabled="timePerQuestion >= 30"
                  >
                    +
                  </button>
                </div>
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  注：题目自定义时间优先于全局时间
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >选择题目</label
                >
                <select
                  v-model="selectedQuestions"
                  class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                >
                  <option value="all">所有题目</option>
                  <option value="custom">自定义选择</option>
                </select>
              </div>
            </div>

            <button
              @click="startTest"
              class="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center"
              :disabled="questions.length === 0"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                ></path>
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
              开始压力测试
            </button>
          </div>

          <!-- 测试进行中 -->
          <div
            v-if="testStatus === 'testing'"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div class="flex justify-between items-center mb-6">
              <div>
                <h2 class="text-xl font-semibold text-gray-800 dark:text-white">正在测试</h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  题目 {{ currentQuestionIndex + 1 }}/{{ testQuestions.length }}
                </p>
              </div>
              <div class="text-right">
                <div
                  class="text-2xl font-mono font-bold"
                  :class="timeLeft <= 10 ? 'text-red-500' : 'text-blue-500'"
                >
                  {{ formatTime(timeLeft) }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">剩余时间</div>
              </div>
            </div>

            <!-- 题目卡片 -->
            <div
              class="bg-blue-50 dark:bg-gray-700 rounded-xl p-6 mb-6 border border-blue-200 dark:border-gray-600"
            >
              <div class="text-lg font-medium text-gray-800 dark:text-white mb-2">问题：</div>
              <div class="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                {{ currentQuestion.text }}
              </div>

              <!-- 显示题目时间设置 -->
              <div class="text-sm text-gray-600 dark:text-gray-300 flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
                本题时间: {{ getQuestionTime(currentQuestion) }} 分钟
              </div>
            </div>

            <div class="flex justify-between">
              <button
                v-if="currentQuestionIndex > 0"
                @click="prevQuestion"
                class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 19l-7-7 7-7"
                  ></path>
                </svg>
                上一题
              </button>

              <div class="flex-1"></div>

              <button
                @click="nextQuestion"
                class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
              >
                {{ currentQuestionIndex < testQuestions.length - 1 ? '下一题' : '完成测试' }}
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5l7 7-7 7"
                  ></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- 测试结果 -->
          <div
            v-if="testStatus === 'completed'"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <h2 class="text-xl font-semibold text-gray-800 dark:text-white mb-6 text-center">
              测试完成！
            </h2>

            <div class="grid grid-cols-3 gap-4 mb-8">
              <div class="bg-blue-50 dark:bg-gray-700 rounded-lg p-4 text-center">
                <div class="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {{ testQuestions.length }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-300">题目数量</div>
              </div>
              <div class="bg-green-50 dark:bg-gray-700 rounded-lg p-4 text-center">
                <div class="text-3xl font-bold text-green-600 dark:text-green-400">
                  {{ completedQuestions }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-300">完成题目</div>
              </div>
              <!-- 修改：平均用时计算 -->
              <div class="bg-amber-50 dark:bg-gray-700 rounded-lg p-4 text-center">
                <div class="text-3xl font-bold text-amber-600 dark:text-amber-400">
                  {{ averageTime }}秒
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-300">平均每题用时</div>
              </div>
            </div>

            <!-- 新增：总用时显示 -->
            <div class="bg-indigo-50 dark:bg-gray-700 rounded-lg p-4 mb-6 text-center">
              <div class="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                {{ totalTime }}秒
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">总用时</div>
            </div>

            <h3 class="font-medium text-gray-700 dark:text-gray-300 mb-3">测试记录</h3>
            <div class="space-y-3 max-h-64 overflow-y-auto pr-2">
              <div
                v-for="(record, index) in testRecords"
                :key="index"
                class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600"
              >
                <div class="flex justify-between items-center mb-2">
                  <div class="font-medium text-gray-800 dark:text-gray-100">
                    {{ index + 1 }}. {{ record.question.text }}
                  </div>
                  <span
                    class="text-sm px-2 py-1 rounded-full"
                    :class="
                      record.timeUsed < getQuestionTime(record.question) * 60
                        ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                        : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                    "
                  >
                    {{ record.timeUsed }}秒
                  </span>
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  限制时间: {{ getQuestionTime(record.question) }} 分钟
                </div>
                <button
                  @click="toggleRecordReference(index)"
                  class="text-xs text-blue-500 hover:text-blue-700 transition-colors"
                >
                  {{ record.showReference ? '隐藏参考答案' : '查看参考答案' }}
                </button>
                <div
                  v-if="record.showReference"
                  class="mt-2 p-2 bg-white dark:bg-gray-600 rounded text-sm text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-500"
                >
                  {{ record.question.reference || '暂无参考答案' }}
                </div>
              </div>
            </div>

            <div class="mt-6 flex justify-center">
              <button
                @click="resetTest"
                class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  ></path>
                </svg>
                重新开始测试
              </button>
            </div>
          </div>

          <!-- 准备开始测试 -->
          <div
            v-if="testStatus === 'idle'"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center"
          >
            <div class="mx-auto max-w-md">
              <svg
                class="w-24 h-24 mx-auto text-gray-300 dark:text-gray-600 mb-6"
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
              <h3 class="text-xl font-semibold text-gray-800 dark:text-white mb-2">
                准备开始压力测试
              </h3>
              <p class="text-gray-600 dark:text-gray-300 mb-6">
                设置每题时间并添加题目后，点击"开始压力测试"按钮开始训练
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                提示：系统将在设定的时间后自动提醒，请专注口述答案
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // 题目管理
      questions: [],
      newQuestion: {
        id: null,
        text: '',
        reference: '',
        customTime: null, // 新增：题目自定义时间
        showReference: false,
      },
      showAddForm: false,

      // 测试设置
      timePerQuestion: 3, // 默认3分钟
      selectedQuestions: 'all',

      // 测试状态
      testStatus: 'idle', // 'idle' | 'testing' | 'completed'
      testQuestions: [],
      currentQuestionIndex: 0,
      timeLeft: 0,
      timer: null,

      // 测试记录
      testRecords: [],
      startTime: 0,
    }
  },

  computed: {
    currentQuestion() {
      if (this.testQuestions.length > 0 && this.currentQuestionIndex < this.testQuestions.length) {
        return this.testQuestions[this.currentQuestionIndex]
      }
      return { text: '', reference: '', customTime: null }
    },
    completedQuestions() {
      return this.testRecords.length
    },
    // 修改：平均用时计算（总用时/题目数量）
    averageTime() {
      if (this.testRecords.length === 0) return 0
      const total = this.testRecords.reduce((sum, record) => sum + record.timeUsed, 0)
      return Math.round(total / this.testRecords.length)
    },
    // 新增：总用时计算
    totalTime() {
      return this.testRecords.reduce((sum, record) => sum + record.timeUsed, 0)
    },
  },
  watch: {
    timePerQuestion(newVal) {
      if (newVal < 1) this.timePerQuestion = 1
      if (newVal > 30) this.timePerQuestion = 30
      localStorage.setItem('timePerQuestion', newVal)
    },
  },
  mounted() {
    this.loadQuestions()
    const savedTime = localStorage.getItem('timePerQuestion')
    if (savedTime) {
      this.timePerQuestion = parseInt(savedTime)
    }
  },
  methods: {
    // 获取题目时间（优先使用自定义时间）
    getQuestionTime(question) {
      return question.customTime || this.timePerQuestion
    },
    goToPractice() {
      this.$router.push({ name: 'CommonPractice' })
    },

    // 题目管理方法
    addQuestion() {
      if (!this.newQuestion.text.trim()) return

      const newId = Date.now()
      this.questions.push({
        id: newId,
        text: this.newQuestion.text,
        reference: this.newQuestion.reference,
        customTime: this.newQuestion.customTime, // 保存自定义时间
        showReference: false,
      })

      this.saveQuestions()
      this.newQuestion.text = ''
      this.newQuestion.reference = ''
      this.newQuestion.customTime = null // 重置自定义时间
      this.showAddForm = false
    },

    cancelAddQuestion() {
      this.newQuestion.text = ''
      this.newQuestion.reference = ''
      this.newQuestion.customTime = null
      this.showAddForm = false
    },

    deleteQuestion(id) {
      this.questions = this.questions.filter((q) => q.id !== id)
      this.saveQuestions()
    },

    toggleReference(id) {
      this.questions = this.questions.map((q) => {
        if (q.id === id) {
          return { ...q, showReference: !q.showReference }
        }
        return q
      })
      this.saveQuestions()
    },

    saveQuestions() {
      localStorage.setItem('interviewQuestions', JSON.stringify(this.questions))
    },

    loadQuestions() {
      const savedQuestions = localStorage.getItem('interviewQuestions')
      if (savedQuestions) {
        this.questions = JSON.parse(savedQuestions)
      }
    },

    // 测试设置方法
    increaseTime() {
      if (this.timePerQuestion < 30) this.timePerQuestion++
    },

    decreaseTime() {
      if (this.timePerQuestion > 1) this.timePerQuestion--
    },

    // 测试控制方法
    startTest() {
      if (this.questions.length === 0) return

      // 准备测试题目
      this.testQuestions = [...this.questions]

      // 重置测试状态
      this.testStatus = 'testing'
      this.currentQuestionIndex = 0
      this.testRecords = []

      // 开始第一题
      this.startQuestionTimer()
    },

    startQuestionTimer() {
      // 使用题目自定义时间或全局时间
      const questionTime = this.getQuestionTime(this.currentQuestion)
      this.timeLeft = questionTime * 60 // 转换为秒
      this.startTime = Date.now()

      // 清除现有计时器
      if (this.timer) clearInterval(this.timer)

      // 开始新计时器
      this.timer = setInterval(() => {
        this.timeLeft--

        if (this.timeLeft <= 0) {
          clearInterval(this.timer)
          this.timeLeft = 0

          // 播放提示音
          this.playAlertSound()

          // 自动记录当前题目
          this.recordQuestion()

          // 自动进入下一题或结束测试
          if (this.currentQuestionIndex < this.testQuestions.length - 1) {
            setTimeout(() => {
              this.nextQuestion()
            }, 2000)
          } else {
            setTimeout(() => {
              this.completeTest()
            }, 2000)
          }
        }
      }, 1000)
    },

    nextQuestion() {
      // 记录当前题目
      this.recordQuestion()

      // 移动到下一题
      if (this.currentQuestionIndex < this.testQuestions.length - 1) {
        this.currentQuestionIndex++
        this.startQuestionTimer()
      } else {
        this.completeTest()
      }
    },

    prevQuestion() {
      // 移除上一条记录
      if (this.testRecords.length > 0) {
        this.testRecords.pop()
      }

      // 移动到上一题
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
        this.startQuestionTimer()
      }
    },

    recordQuestion() {
      const timeUsed = this.getQuestionTime(this.currentQuestion) * 60 - this.timeLeft
      this.testRecords.push({
        question: { ...this.testQuestions[this.currentQuestionIndex] },
        timeUsed: timeUsed,
        showReference: false,
      })
    },

    completeTest() {
      clearInterval(this.timer)
      this.testStatus = 'completed'

      // 保存测试记录
      this.saveTestRecords()
    },

    resetTest() {
      this.testStatus = 'idle'
      this.testQuestions = []
      this.currentQuestionIndex = 0
      this.testRecords = []
    },

    toggleRecordReference(index) {
      this.testRecords[index].showReference = !this.testRecords[index].showReference
    },

    // 辅助方法
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },

    playAlertSound() {
      // 创建音频上下文
      const context = new (window.AudioContext || window.webkitAudioContext)()
      const oscillator = context.createOscillator()
      const gainNode = context.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(context.destination)

      oscillator.type = 'sine'
      oscillator.frequency.setValueAtTime(440, context.currentTime)
      oscillator.frequency.setValueAtTime(880, context.currentTime + 0.1)

      gainNode.gain.setValueAtTime(0.5, context.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.5)

      oscillator.start()
      oscillator.stop(context.currentTime + 0.5)
    },

    saveTestRecords() {
      // 这里可以扩展为保存历史记录
    },
  },
}
</script>

<style scoped>
/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}
.dark ::-webkit-scrollbar-track {
  background: #374151;
}
::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}
.dark ::-webkit-scrollbar-thumb {
  background: #4b5563;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

/* 题目卡片悬停效果 */
.hover\:shadow {
  transition: box-shadow 0.3s ease;
}
.hover\:shadow:hover {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>
