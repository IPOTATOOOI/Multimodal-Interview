<template>
  <div class="p-4 md:p-6 lg:p-3 bg-gray-50 dark:bg-gray-900 min-h-screen">
    <div v-if="loading" class="text-center py-10 text-gray-500">加载中...</div>
    <div v-else-if="error" class="text-center py-10 text-red-500">{{ error }}</div>
    <div v-else>
      <div class="max-w-6xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-3 md:p-8">
        <!-- 头部信息 -->
        <div class="flex justify-between items-center mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
              <span class="inline-block w-2 h-6 bg-blue-500 rounded-full mr-2"></span>
              笔试测试
            </h1>
            <div class="text-sm text-gray-500 dark:text-gray-400 mt-2">
              共 {{ questions.length }} 题 | 总分：{{ totalScore }} 分
            </div>
          </div>
          <div class="flex gap-2">
            <Button size="sm" variant="outline" @click="showAllAnswers = !showAllAnswers" v-if="showResult && false">
              <Icon icon="lucide:eye" class="w-4 h-4 mr-1" />
              {{ showAllAnswers ? '隐藏全部答案' : '显示全部答案' }}
            </Button>
          </div>
        </div>

        <!-- 题目列表 -->
        <div class="space-y-8">
          <!-- 选择题部分 -->
          <div v-for="(q, idx) in choiceQuestions" :key="q.record_id" class="border-b pb-6 last:border-b-0 relative">
            <!-- 右上角标记 -->
            <div class="absolute right-2 top-2 flex gap-2">
              <span class="icon-btn" @click="toggleMarked(idx)" :title="isMarked(idx) ? '已标记' : '标记'">
                <Icon icon="lucide:tag" :class="isMarked(idx) ? 'text-blue-500' : 'text-gray-400'" />
              </span>
            </div>

            <!-- 题型标签和分值标签 -->
            <div class="mb-1 flex items-center gap-2">
              <el-tag size="small" effect="plain" :type="getTypeColor(q.question_type)">
                {{ getTypeLabel(q.question_type) }}
              </el-tag>
              <el-tag size="small" effect="plain" type="success">
                {{ q.question_score }}分
              </el-tag>
            </div>

            <!-- 题号和标题 -->
            <div class="flex items-center gap-2 mb-2">
              <span class="text-lg font-bold text-blue-700">{{ idx + 1 }}.</span>
              <div class="text-base font-medium text-gray-800 dark:text-gray-200 flex-1">{{ q.title }}</div>
            </div>

            <!-- 难度和标签 -->
            <div class="flex flex-wrap gap-2 mb-2">
              <Badge :color="getDifficultyColor(q.difficulty)">{{ getDifficultyLabel(q.difficulty) }}</Badge>
              <Badge v-if="q.tag_name" color="info">{{ q.tag_name }}</Badge>
              <Badge v-if="q.knowledgepoint_name" color="info">{{ q.knowledgepoint_name }}</Badge>
            </div>

            <!-- 题目内容 -->
            <div class="mb-2 text-gray-700 dark:text-gray-300" v-html="formatContent(q.content)"></div>

            <!-- 简答题回答框 -->
            <div v-if="q.question_type === 'essay'">
              <textarea
                v-model="userAnswers[idx]"
                :disabled="showResult"
                class="w-full p-2 border rounded min-h-[100px] bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder="请输入你的答案..."
                style="resize: vertical; margin-bottom: 8px"
              ></textarea>
            </div>
            <!-- 选择题选项 -->
            <div v-else-if="q.choice && q.choice.trim()" class="space-y-2 mt-2">
              <div v-for="(opt, optIdx) in parseChoices(q.choice)" :key="optIdx" :class="['flex items-center gap-2 p-2 rounded cursor-pointer border',
                isSelected(idx, opt.label) ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30' : 'border-gray-200',
                showResult ? (opt.label === q.standard_answer ? 'bg-green-100 dark:bg-green-900/40 border-green-500' : '') : ''
              ]" @click="selectOption(idx, opt.label)" style="transition:all 0.2s">
                <span class="font-bold text-lg w-6 text-center">{{ opt.label }}</span>
                <span class="flex-1">{{ opt.text }}</span>
                <span v-if="showResult && isSelected(idx, opt.label) && opt.label === q.standard_answer"
                  class="text-green-600 font-bold ml-2">✔</span>
                <span v-if="showResult && isSelected(idx, opt.label) && opt.label !== q.standard_answer"
                  class="text-red-500 font-bold ml-2">✘</span>
              </div>
            </div>

            <!-- 正确答案显示 -->
            <div v-if="showResult && q.question_type === 'essay'" class="mt-2">
              <div class="px-3 py-1 rounded bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200 font-semibold" style="white-space: pre-line">
                正确答案：
                {{ q.standard_answer ? q.standard_answer.replace(/\\n/g, '\n') : '暂无标准答案' }}
              </div>
            </div>
            <div v-else-if="showResult && userAnswers[idx] && q.question_type !== 'essay'" class="mt-2">
              <span class="inline-block px-3 py-1 rounded bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200 font-semibold">
                正确答案：{{ q.standard_answer }}
              </span>
            </div>
          </div>

          <!-- 编程题部分 -->
          <div v-for="(q, idx) in codeQuestions" :key="q.record_id" class="border-b pb-6 last:border-b-0 relative">
            <!-- 右上角标记 -->
            <div class="absolute right-2 top-2 flex gap-2">
              <span class="icon-btn" @click="toggleMarked(choiceQuestions.length + idx)"
                :title="isMarked(choiceQuestions.length + idx) ? '已标记' : '标记'">
                <Icon icon="lucide:tag"
                  :class="isMarked(choiceQuestions.length + idx) ? 'text-blue-500' : 'text-gray-400'" />
              </span>
            </div>

            <!-- 题型标签和分值标签 -->
            <div class="mb-1 flex items-center gap-2">
              <el-tag size="small" effect="plain" type="warning">编程题</el-tag>
              <el-tag size="small" effect="plain" type="success">
                {{ q.question_score }}分
              </el-tag>
            </div>

            <!-- 题号和标题 -->
            <div class="flex items-center gap-2 mb-2">
              <span class="text-lg font-bold text-blue-700">{{ choiceQuestions.length + idx + 1 }}.</span>
              <div class="text-base font-medium text-gray-800 dark:text-gray-200 flex-1">{{ q.title }}</div>
            </div>

            <!-- 难度和标签 -->
            <div class="flex flex-wrap gap-2 mb-2">
              <Badge :color="getDifficultyColor(q.difficulty)">{{ getDifficultyLabel(q.difficulty) }}</Badge>
              <Badge v-if="q.tag_name" color="info">{{ q.tag_name }}</Badge>
              <Badge v-if="q.knowledgepoint_name" color="info">{{ q.knowledgepoint_name }}</Badge>
            </div>

            <!-- 题目内容 -->
            <div class="mb-4 text-gray-700 dark:text-gray-300" v-html="formatContent(q.content)"></div>

            <!-- 代码编辑框 -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">你的代码：</label>
              <Codemirror v-model="userAnswers[choiceQuestions.length + idx]"
                :extensions="getCodeMirrorExtensions(q.content)"
                :style="{ height: '220px', fontSize: '14px', borderRadius: '8px', overflow: 'hidden', border: showResult ? '1px solid #e5e7eb' : '2px solid #6366f1', background: isDark ? undefined : '#fff' }"
                :disabled="showResult" :lineNumbers="true" placeholder="请在此处编写你的代码..." class="code-editor-block" />
            </div>

            <!-- 标准答案显示 -->
            <div v-if="showResult" class="mt-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">标准答案：</label>
              <Codemirror :model-value="q.standard_answer" :extensions="getCodeMirrorExtensions(q.content)"
                :style="{ height: '220px', fontSize: '14px', borderRadius: '8px', overflow: 'hidden', border: '1px solid #e5e7eb', background: isDark ? undefined : '#fff' }"
                :disabled="true" :lineNumbers="true" class="code-editor-block" />
            </div>
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <div class="flex justify-between items-center mt-10 pt-6 border-t">
          <div class="text-sm text-gray-500 dark:text-gray-400">
            已完成 {{ answeredCount }}/{{ questions.length }} 题
          </div>
          <div class="flex gap-4">
            <Button @click="resetTest" type="info" v-if="!showResult">重置</Button>
            <Button type="primary" @click="submitAnswers" :disabled="showResult">
              提交答案
            </Button>
          </div>
        </div>

        <!-- 成绩展示 -->
        <div v-if="showResult"
          class="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl">
          <h3 class="text-xl font-bold text-gray-800 dark:text-white mb-4 text-center">测试结果</h3>
          <div class="grid grid-cols-3 gap-4 mb-6">
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ questions.length }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-300">题目数量</div>
            </div>
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-green-600 dark:text-green-400">{{ finalScore }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-300">得分</div>
            </div>
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-amber-600 dark:text-amber-400">{{ scorePercentage }}%</div>
              <div class="text-sm text-gray-600 dark:text-gray-300">正确率</div>
            </div>
          </div>
          <div class="text-center">
            <div class="flex justify-center items-center gap-4">
              <!-- 重新开始按钮 -->
              <button
                @click="resetTest"
                class="px-6 py-3 flex items-center text-base font-medium rounded-lg transition-colors bg-blue-500 text-white hover:bg-blue-600 shadow-md"
              >
                <Icon icon="lucide:refresh-cw" class="w-5 h-5 mr-2" />
                重新开始
              </button>

              <!-- 查看面试结果按钮 -->
              <button
                @click="handleViewInterviewResult"
                :disabled="loadingResult"
                class="px-6 py-3 flex items-center text-base font-medium rounded-lg transition-colors bg-green-500 text-white hover:bg-green-600 shadow-md disabled:bg-green-300 disabled:cursor-not-allowed"
              >
                <span v-if="loadingResult" class="flex items-center">
                  <Icon icon="lucide:loader-2" class="w-5 h-5 animate-spin mr-2" />
                  正在获取面试总结...
                </span>
                <span v-else class="flex items-center">
                  <Icon icon="lucide:file-chart-column-increasing" class="w-5 h-5 mr-2" />
                  查看我的面试结果
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Icon } from '@iconify/vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import { Codemirror } from 'vue-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { python } from '@codemirror/lang-python'
import { javascript } from '@codemirror/lang-javascript'
import { getApiUrl } from '@/config/api'

const route = useRoute()
const router = useRouter()
const interviewId = ref<string | number>('')
const questions = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const showAllAnswers = ref(false)
const showResult = ref(false)
const userAnswers = ref<string[]>([])
const marked = ref<Set<number>>(new Set())
const loadingResult = ref(false)

// 检测暗色模式
const isDark = ref(document.documentElement.classList.contains('dark'))

// 监听暗色模式变化（适配 Tailwind 的 dark class 切换）
const darkObserver = new MutationObserver(() => {
  isDark.value = document.documentElement.classList.contains('dark')
})
darkObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })

// 计算属性
const choiceQuestions = computed(() => {
  return questions.value.filter(q => q.question_type !== 'code')
})

const codeQuestions = computed(() => {
  return questions.value.filter(q => q.question_type === 'code')
})

const totalScore = computed(() => {
  return questions.value.reduce((sum, q) => sum + q.question_score, 0)
})

const answeredCount = computed(() => {
  return userAnswers.value.filter(answer => answer && answer.trim()).length
})

const allAnswered = computed(() => {
  return userAnswers.value.length === questions.value.length && userAnswers.value.every(Boolean)
})

const finalScore = computed(() => {
  if (!showResult.value) return 0

  let score = 0
  questions.value.forEach((q, idx) => {
    if (q.question_type === 'code') {
      // 编程题默认满分
      score += q.question_score
    } else {
      // 选择题根据答案判断
      if (userAnswers.value[idx] === q.standard_answer) {
        score += q.question_score
      }
    }
  })
  return score
})

const scorePercentage = computed(() => {
  if (totalScore.value === 0) return 0
  return Math.round((finalScore.value / totalScore.value) * 100)
})

// 工具函数
function parseChoices(choice: string) {
  if (!choice || !choice.trim()) return []
  const regex = /([A-D])\.(.*?)(?=[A-D]\.|$)/g
  const result = []
  let match
  while ((match = regex.exec(choice)) !== null) {
    result.push({ label: match[1], text: match[2].trim() })
  }
  return result
}

function isSelected(qIdx: number, label: string) {
  return userAnswers.value[qIdx] === label
}

function selectOption(qIdx: number, label: string) {
  if (showResult.value) return
  userAnswers.value[qIdx] = label
}

function isMarked(idx: number) {
  return marked.value.has(idx)
}

function toggleMarked(idx: number) {
  if (marked.value.has(idx)) {
    marked.value.delete(idx)
  } else {
    marked.value.add(idx)
  }
  marked.value = new Set(marked.value)
}

function getTypeColor(type: string): 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark' {
  const colorMap: Record<string, 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark'> = {
    single_choice: 'primary',
    multiple_choice: 'info',
    essay: 'success',
    code: 'warning'
  }
  return colorMap[type] || 'info'
}

function getTypeLabel(type: string): string {
  const labelMap: Record<string, string> = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    essay: '简答题',
    code: '编程题'
  }
  return labelMap[type] || type
}

function getDifficultyColor(difficulty: string): 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark' {
  const colorMap: Record<string, 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark'> = {
    easy: 'success',
    medium: 'warning',
    hard: 'error'
  }
  return colorMap[difficulty] || 'info'
}

function getDifficultyLabel(difficulty: string): string {
  const labelMap: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return labelMap[difficulty] || difficulty
}

function formatContent(content: string) {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

// 判断题目内容适合的语言
function getCodeLang(content: string) {
  if (/python|py|def |def\(|:$|#/.test(content)) {
    return python()
  }
  return javascript()
}

function getCodeMirrorExtensions(content: string) {
  const lang = getCodeLang(content)
  return isDark.value ? [lang, oneDark] : [lang]
}

// API调用
async function fetchQuestions() {
  loading.value = true
  error.value = ''
  showResult.value = false
  userAnswers.value = []
  marked.value = new Set()

  try {
    interviewId.value = route.query.interviewId as string
    const url = getApiUrl(`/written-test/questions?history_id=${interviewId.value}`)

    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    if (data.code === 200) {
      questions.value = data.data.questions || []
      userAnswers.value = new Array(questions.value.length).fill('')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      throw new Error(data.message || '获取题目失败')
    }
  } catch (e: any) {
    error.value = e.message || '加载失败'
    questions.value = []
  } finally {
    loading.value = false
  }
}

function submitAnswers() {
  showResult.value = true
  ElMessage.success(`测试完成！得分：${finalScore.value}/${totalScore.value}`)
}

function resetTest() {
  showResult.value = false
  userAnswers.value = new Array(questions.value.length).fill('')
  marked.value = new Set()
  showAllAnswers.value = false
}

async function handleViewInterviewResult() {
  loadingResult.value = true
  let processId = localStorage.getItem('interview_process_id') || ''

  if (!processId) {
    ElMessage.warning('面试评估任务尚未启动，正在启动中...')
    // 尝试启动面试评估任务
    try {
      const formData = new FormData()
      formData.append('history_id', String(interviewId.value))
      const res = await fetch(getApiUrl('/interview/end'), {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      if (data.code === 202 && data.data.process_id) {
        processId = data.data.process_id
        localStorage.setItem('interview_process_id', processId)
        ElMessage.success('面试评估任务已启动')
      } else {
        ElMessage.error(data.message || '启动面试评估任务失败')
        loadingResult.value = false
        return
      }
    } catch (e: any) {
      ElMessage.error('启动面试评估任务失败')
      loadingResult.value = false
      return
    }
  }

  // 轮询接口
  let finished = false
  let retryCount = 0
  const maxRetries = 20 // 最多等待60秒

  while (!finished && retryCount < maxRetries) {
    try {
      const res = await fetch(getApiUrl(`/interview/end/status/${processId}`))
      const data = await res.json()
      if (data.code === 200 && data.data.status === 'completed') {
        loadingResult.value = false
        router.push({ name: 'InterviewResult', query: { process_id: processId } })
        finished = true
      } else if (data.data.status === 'failed') {
        ElMessage.error(data.data.error || '评估失败，请稍后重试')
        loadingResult.value = false
        finished = true
      } else {
        retryCount++
        await new Promise(r => setTimeout(r, 3000))
      }
    } catch (e: any) {
      retryCount++
      if (retryCount >= maxRetries) {
        ElMessage.error('查询面试结果超时，请稍后手动查看')
        loadingResult.value = false
        finished = true
      } else {
        await new Promise(r => setTimeout(r, 3000))
      }
    }
  }

  if (retryCount >= maxRetries && !finished) {
    ElMessage.warning('面试评估仍在进行中，请稍后再试')
    loadingResult.value = false
  }
}

onMounted(() => {
  fetchQuestions()
})
</script>

<style scoped>
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.2s;
  background: transparent;
  font-size: 20px;
}

.icon-btn:hover {
  background: #f1f5f9;
}

/* 代码编辑器样式 */
textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.5;
}

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

.code-editor-block {
  margin-bottom: 0.5rem;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.04);
}
</style>

