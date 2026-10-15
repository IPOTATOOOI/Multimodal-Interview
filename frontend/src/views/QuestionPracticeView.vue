<template>
  <div class="p-4 md:p-6 lg:p-3 min-h-screen">
    <button
      title="返回题库列表"
      @click="backToQuestionBankList"
      class="fixed bottom-8 duration-300 right-10 z-10 flex items-center w-14 h-14 justify-center bg-[#2b7fff] dark:bg-secondary-dark text-white rounded-full shadow-lg hover:bg-[#1a66e6] transition-all transform hover:scale-105 flex items-center"
    >
      <svg
        t="1752736637606"
        class="icon"
        viewBox="0 0 1024 1024"
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        p-id="2684"
        width="30"
        height="30"
      >
        <path
          d="M379.637656 519.019961 803.31583 95.343834c19.469684-19.468661 19.896297-50.606243 0.957576-69.542917l-11.869438-11.874553c-18.94179-18.935652-50.077325-18.508016-69.544964 0.957576L253.75941 483.984555c-1.300298 1.300298-2.508521 2.656864-3.640016 4.053328-7.597177 9.09697-11.342567 20.315748-11.237193 31.510995-0.021484 12.38301 4.598614 24.658599 13.919632 33.979617l11.870461 11.871484c1.270629 1.269606 2.599573 2.446115 3.971484 3.541803l440.803025 440.803025c18.938721 18.936675 49.644575 18.936675 68.587388 0l11.869438-11.872507c18.939744-18.937698 18.939744-49.646621 0-68.586365L379.637656 519.019961z"
          fill="#ffffff"
          p-id="2685"
        ></path>
      </svg>
    </button>
    <div v-if="loading" class="text-center py-10 text-gray-500">加载中...</div>
    <div v-else-if="error" class="text-center py-10 text-red-500">{{ error }}</div>
    <div v-else>
      <div class="max-w-6xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-3 md:p-8">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
              <span class="inline-block w-2 h-6 bg-blue-500 rounded-full mr-2"></span>
              {{ topicName }} 题库练习
            </h1>
            <div class="text-sm text-gray-500 dark:text-gray-400 mt-2">
              共 {{ questions.length }} 题
            </div>
          </div>
          <div class="flex gap-2">
            <Button size="sm" variant="outline" @click="showAllAnswers = !showAllAnswers">
              <Icon icon="lucide:eye" class="w-4 h-4 mr-1" />
              {{ showAllAnswers ? '隐藏全部答案' : '显示全部答案' }}
            </Button>
          </div>
        </div>
        <div class="space-y-8">
          <div
            v-for="(q, idx) in questions"
            :key="q.id"
            class="border-b pb-6 last:border-b-0 relative"
          >
            <!-- 右上角收藏/标记 -->
            <div class="absolute right-2 top-2 flex gap-2">
              <span
                class="icon-btn"
                @click="toggleFavorite(idx)"
                :title="isFavorite(idx) ? '已收藏' : '收藏'"
              >
                <Icon
                  icon="lucide:star"
                  :class="isFavorite(idx) ? 'text-yellow-400' : 'text-gray-400'"
                />
              </span>
              <span
                class="icon-btn"
                @click="toggleMarked(idx)"
                :title="isMarked(idx) ? '已标记' : '标记'"
              >
                <Icon
                  icon="lucide:tag"
                  :class="isMarked(idx) ? 'text-blue-500' : 'text-gray-400'"
                />
              </span>
            </div>
            <!-- 第一行：题型单独一行（type为null或'null'不渲染） -->
            <div v-if="q.type && q.type !== 'null'" class="mb-1">
              <el-tag
                size="small"
                effect="dark"
                :type="typeMap[q.type]?.color || 'info'"
                class="dark:bg-gray-400"
              >
                {{ typeMap[q.type]?.label || q.type }}
              </el-tag>
            </div>
            <!-- 第二行：题号、题目title同一行 -->
            <div class="flex items-center gap-2 mb-2">
              <span class="text-lg font-bold text-blue-700">{{ idx + 1 }}.</span>
              <div class="text-base font-medium text-gray-800 dark:text-gray-200 flex-1">
                {{ q.title }}
              </div>
            </div>
            <!-- 第三行：难度、tags、知识点（difficulty为null或'null'不渲染） -->
            <div v-if="q.difficulty && q.difficulty !== 'null'" class="flex flex-wrap gap-2 mb-2">
              <Badge :color="diffMap[q.difficulty]?.color || 'default'">{{
                diffMap[q.difficulty]?.label || q.difficulty
              }}</Badge>
              <Badge v-for="tag in q.tags" :key="tag.id" color="info">{{ tag.name }}</Badge>
              <Badge v-for="kp in q.knowledgePoints" :key="kp.id" color="info">{{ kp.name }}</Badge>
            </div>
            <!-- 题干内容，支持换行 -->
            <div
              class="mb-2 text-gray-700 dark:text-gray-300"
              v-html="formatContent(q.content)"
            ></div>
            <div v-if="q.type === 'essay'">
              <textarea
                v-model="userAnswers[idx]"
                :disabled="showAllAnswers || showResult"
                class="w-full p-2 border rounded min-h-[100px] bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder="请输入你的答案..."
                style="resize: vertical; margin-bottom: 8px"
              ></textarea>
            </div>
            <div v-else class="space-y-2 mt-2">
              <div
                v-for="(opt, optIdx) in parseChoices(q.choice)"
                :key="optIdx"
                :class="[
                  'flex items-center gap-2 p-2 rounded cursor-pointer border',
                  isSelected(idx, opt.label)
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                    : 'border-gray-200',
                  showAllAnswers || showResult
                    ? opt.label === q.answer
                      ? 'bg-green-100 dark:bg-green-900/40 border-green-500'
                      : ''
                    : '',
                ]"
                @click="selectOption(idx, opt.label)"
                style="transition: all 0.2s"
              >
                <span class="font-bold text-lg w-6 text-center dark:text-gray-300">{{
                  opt.label
                }}</span>
                <span class="flex-1 dark:text-gray-300">{{ opt.text }}</span>
                <span
                  v-if="showResult && isSelected(idx, opt.label) && opt.label === q.answer"
                  class="text-green-600 font-bold ml-2"
                  >✔</span
                >
                <span
                  v-if="showResult && isSelected(idx, opt.label) && opt.label !== q.answer"
                  class="text-red-500 font-bold ml-2"
                  >✘</span
                >
              </div>
            </div>
            <div v-if="showAllAnswers || (showResult && userAnswers[idx])" class="mt-2">
              <div
                v-if="q.type === 'essay'"
                class="px-3 py-1 rounded bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200 font-semibold"
                style="white-space: pre-line"
                v-html="'正确答案：<br>' + formatAnswer(q.answer)"
              ></div>
              <span
                v-else
                class="inline-block px-3 py-1 rounded bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200 font-semibold"
                v-html="'正确答案：' + formatAnswer(q.answer)"
              ></span>
            </div>
          </div>
        </div>
        <div class="flex justify-between items-center mt-10">
          <Button @click="goBackToQuestionBank" variant="outline" size="sm">
            <Icon icon="lucide:arrow-left" class="w-4 h-4 mr-1" />
            返回题库练习
          </Button>
          <div class="flex gap-4">
            <Button type="primary" @click="submitAnswers" :disabled="showResult || !allAnswered"
              >提交答案</Button
            >
            <Button @click="fetchQuestions" type="info">继续练习</Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getApiUrl } from '@/config/api'
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Icon } from '@iconify/vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'

const route = useRoute()
const router = useRouter()
const topicId = ref((route.query.topic_id as string) || '')
const topicName = ref((route.query.topic_name as string) || '')
const questions = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const showAllAnswers = ref(false)
const showResult = ref(false)
const userAnswers = ref<string[]>([])
const favorites = ref<Set<number>>(new Set())
const marked = ref<Set<number>>(new Set())

type BadgeColor = 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark'

const typeMap: Record<string, { label: string; color: BadgeColor }> = {
  single_choice: { label: '单选题', color: 'primary' },
  multiple_choice: { label: '多选题', color: 'info' },
  essay: { label: '简答题', color: 'warning' },
}
const diffMap: Record<string, { label: string; color: BadgeColor }> = {
  easy: { label: '简单', color: 'success' },
  medium: { label: '中等', color: 'warning' },
  hard: { label: '困难', color: 'error' },
}

function parseChoices(choice: string) {
  // 支持A.B.等紧凑格式
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

const backToQuestionBankList = () => {
  router.push({ name: 'QuizList' })
}

function selectOption(qIdx: number, label: string) {
  if (showAllAnswers.value || showResult.value) return
  userAnswers.value[qIdx] = label
}

const allAnswered = computed(() => {
  return userAnswers.value.length === questions.value.length && userAnswers.value.every(Boolean)
})

function isFavorite(idx: number) {
  return favorites.value.has(idx)
}
function toggleFavorite(idx: number) {
  if (favorites.value.has(idx)) {
    favorites.value.delete(idx)
  } else {
    favorites.value.add(idx)
  }
  favorites.value = new Set(favorites.value)
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

async function fetchQuestions() {
  loading.value = true
  error.value = ''
  showAllAnswers.value = false
  showResult.value = false
  userAnswers.value = []
  favorites.value = new Set()
  marked.value = new Set()
  try {
    const url = getApiUrl(`/questionBank/questions?topic_id=${encodeURIComponent(topicId.value)}`)
    const res = await fetch(url)
    if (!res.ok) throw new Error('请求失败')
    const data = await res.json()

    // 兼容两种返回结构：{ questions: [] } 和 { data: { questions: [] } }
    const rawQuestions = data.questions || data.data?.questions || []
    questions.value = rawQuestions.map((q: any) => ({
      ...q,
      tags: Array.isArray(q.tags) ? q.tags : [],
      knowledgePoints: Array.isArray(q.knowledgePoints)
        ? q.knowledgePoints
        : Array.isArray(q.knowledge_points)
          ? q.knowledge_points
          : [],
    }))

    // 滚动到页面顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e: any) {
    console.error('获取题目列表失败:', e)
    error.value = e.message || '加载失败'
    questions.value = []
  } finally {
    loading.value = false
  }
}

function submitAnswers() {
  if (!allAnswered.value) {
    ElMessage.warning('请先完成所有题目作答')
    return
  }
  showResult.value = true
}

function formatContent(content: string) {
  if (!content) return ''
  // 替换\n和\\n为<br>，防止XSS
  return content.replace(/\\n/g, '<br>').replace(/\n/g, '<br>')
}

function formatAnswer(answer: string) {
  if (!answer) return ''
  // 支持 \n、\r\n 和 \n 换行，统一替换为 <br>
  return answer.replace(/\\r\\n|\\n|\n|\r\n/g, '<br>')
}
function goBackToQuestionBank() {
  router.push({ name: 'QuizList' })
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
</style>
