<template>
  <div class="p-4 md:p-6 lg:p-3 bg-transparent min-h-screen">
    <div v-if="loading" class="text-center py-10 text-gray-500">加载中...</div>
    <div v-else-if="error" class="text-center py-10 text-red-500">{{ error }}</div>
    <div v-else>
      <div class="max-w-6xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-3 md:p-8">
        <!-- 头部信息 -->
        <div class="flex justify-between items-center mb-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
              <span class="inline-block w-2 h-6 bg-orange-500 rounded-full mr-2"></span>
              薄弱点专属训练
            </h1>
            <div class="text-sm text-gray-500 dark:text-gray-400 mt-2">
              共 {{ questions.length }} 题 | 总分：{{ totalScore }} 分
            </div>
          </div>
          <div class="flex gap-2">
            <Button size="sm" variant="outline" @click="toggleAllAnswers" v-if="showResult">
              <Icon :icon="showAllAnswers ? 'lucide:eye-off' : 'lucide:eye'" class="w-4 h-4 mr-1" />
              {{ showAllAnswers ? '隐藏全部答案' : '显示全部答案' }}
            </Button>
          </div>
        </div>

        <!-- 用户画像薄弱点 Banner -->
        <div
          v-if="portrait"
          class="mb-6 rounded-xl border border-orange-200 dark:border-orange-800 overflow-hidden"
        >
          <!-- Banner 头部 -->

          <div class="p-4 bg-orange-50 dark:bg-orange-900/20">
            <!-- 最弱维度 + 统计 -->
            <div class="flex flex-wrap gap-4 mb-3 text-sm">
              <div
                v-if="portrait.interview_performance?.weakest_dimension_label"
                class="flex items-center gap-1"
              >
                <Icon icon="lucide:triangle-alert" class="w-3.5 h-3.5 text-red-500" />
                <span class="text-gray-600 dark:text-gray-300">最弱维度：</span>
                <span class="font-semibold text-red-600 dark:text-red-400">
                  {{ portrait.interview_performance.weakest_dimension_label }}
                </span>
              </div>
              <div
                v-if="portrait.interview_performance?.total_interviews"
                class="flex items-center gap-1"
              >
                <Icon icon="lucide:history" class="w-3.5 h-3.5 text-gray-400" />
                <span class="text-gray-500 dark:text-gray-400">
                  累计 {{ portrait.interview_performance.total_interviews }} 次面试
                </span>
              </div>
              <div v-if="portrait.graph_data?.correct_rate != null" class="flex items-center gap-1">
                <Icon icon="lucide:check-circle" class="w-3.5 h-3.5 text-green-500" />
                <span class="text-gray-500 dark:text-gray-400">
                  答题正确率 {{ (portrait.graph_data.correct_rate * 100).toFixed(0) }}%
                </span>
              </div>
            </div>

            <!-- 薄弱 Tag 强度条 -->
            <div
              v-if="portrait.graph_data?.weak_area_tags?.length"
              class="flex flex-wrap gap-x-4 gap-y-2"
            >
              <div
                v-for="tag in portrait.graph_data.weak_area_tags.slice(0, 6)"
                :key="tag.tag_id"
                class="flex items-center gap-1.5 min-w-[120px]"
              >
                <span
                  class="text-xs px-1.5 py-0.5 rounded"
                  :class="
                    tag.strength >= 3.5
                      ? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
                      : tag.strength >= 2
                        ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300'
                        : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300'
                  "
                >
                  {{ tag.tag_name }}
                </span>
                <div
                  class="flex-1 h-1.5 rounded-full bg-gray-200 dark:bg-gray-600 overflow-hidden min-w-[40px]"
                >
                  <div
                    class="h-full rounded-full transition-all"
                    :class="
                      tag.strength >= 3.5
                        ? 'bg-red-500'
                        : tag.strength >= 2
                          ? 'bg-orange-400'
                          : 'bg-yellow-400'
                    "
                    :style="{ width: Math.min(100, (tag.strength / 5) * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>

            <!-- Qwen 个性化薄弱分析 -->
            <div
              v-if="portrait.recommendation_profile?.weakness_analysis"
              class="mt-3 pt-3 border-t border-orange-200 dark:border-orange-700 text-sm text-orange-800 dark:text-orange-200 leading-relaxed"
            >
              <Icon icon="lucide:sparkles" class="w-3.5 h-3.5 inline mr-1 text-orange-500" />
              {{ portrait.recommendation_profile.weakness_analysis }}
            </div>
          </div>
        </div>

        <!-- 题目列表 — 统一用 questions 扁平数组渲染，分区标题靠第一题检测 -->
        <div class="space-y-8">
          <template v-for="(q, idx) in questions" :key="q.id + '_' + idx">
            <!-- 分区标题：本次面试薄弱点（第一道 source==='history' 的题前显示） -->
            <div
              v-if="
                q.source === 'history' && (idx === 0 || questions[idx - 1].source !== 'history')
              "
              class="flex items-center gap-2 pt-2"
            >
              <span class="inline-block w-1 h-5 bg-orange-500 rounded-full"></span>
              <h2 class="text-base font-semibold text-gray-700 dark:text-gray-200">
                本次面试薄弱点
              </h2>
              <span
                class="text-xs text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full"
              >
                {{ historyCount }} 题
              </span>
            </div>

            <!-- 分区标题：画像推荐补充（第一道 source==='recommend' 的题前显示） -->
            <div
              v-if="
                q.source === 'recommend' && (idx === 0 || questions[idx - 1].source !== 'recommend')
              "
              class="flex items-center gap-2 pt-4"
            >
              <span class="inline-block w-1 h-5 bg-blue-500 rounded-full"></span>
              <h2 class="text-base font-semibold text-gray-700 dark:text-gray-200">画像推荐补充</h2>
              <span
                class="text-xs text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full"
              >
                {{ recommendCount }} 题
              </span>
            </div>

            <!-- 题目卡片 -->
            <div class="border-b pb-6 last:border-b-0 relative">
              <!-- 右上角：长期薄弱徽章 + 标记按钮 -->
              <div class="absolute right-2 top-2 flex gap-1.5 items-center">
                <span
                  v-if="q.isConsistentWeakness"
                  class="text-xs px-1.5 py-0.5 rounded bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-300 font-medium"
                  >长期薄弱</span
                >
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

              <!-- 题型 + 分值 -->
              <div class="mb-1 flex items-center gap-2 flex-wrap">
                <el-tag size="small" effect="plain" :type="getTypeColor(q.type)">
                  {{ getTypeLabel(q.type) }}
                </el-tag>
                <el-tag size="small" effect="plain" type="success">{{ q.score }}分</el-tag>
              </div>

              <!-- 题号 + 标题 -->
              <div class="flex items-center gap-2 mb-2">
                <span class="text-lg font-bold text-blue-700">{{ idx + 1 }}.</span>
                <div class="text-base font-medium text-gray-800 dark:text-gray-200 flex-1">
                  {{ q.title }}
                </div>
              </div>

              <!-- 难度 + Tag + 知识点 -->
              <div class="flex flex-wrap gap-2 mb-2">
                <Badge :color="getDifficultyColor(q.difficulty)">{{
                  getDifficultyLabel(q.difficulty)
                }}</Badge>
                <Badge v-if="q.tag" color="info">{{ q.tag }}</Badge>
                <Badge v-if="q.knowledgePoint" color="info">{{ q.knowledgePoint }}</Badge>
              </div>

              <!-- 题目内容 -->
              <div
                class="mb-2 text-gray-700 dark:text-gray-300"
                v-html="formatContent(q.content)"
              ></div>

              <!-- 答题区：根据题目类型渲染不同组件 -->
              <!-- 简答题 -->
              <div v-if="q.type === 'essay'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                  >你的答案：</label
                >
                <textarea
                  v-model="userAnswers[idx]"
                  :disabled="showResult"
                  rows="4"
                  class="w-full p-3 border rounded-lg bg-white dark:bg-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                  placeholder="请在此处作答..."
                  @focus="activeEssayIdx = idx"
                  @blur="activeEssayIdx = null"
                  :style="activeEssayIdx === idx ? 'border:2px solid #2563eb' : ''"
                ></textarea>
              </div>
              <!-- 选择题选项 -->
              <div v-else-if="q.choice && q.choice.trim()" class="space-y-2 mt-2">
                <div
                  v-for="(opt, optIdx) in parseChoices(q.choice)"
                  :key="optIdx"
                  :class="[
                    'flex items-center gap-2 p-2 rounded cursor-pointer border',
                    isSelected(idx, opt.label)
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                      : 'border-gray-200',
                    showResult
                      ? opt.label === q.answer
                        ? 'bg-green-100 dark:bg-green-900/40 border-green-500'
                        : ''
                      : '',
                  ]"
                  @click="selectOption(idx, opt.label)"
                  style="transition: all 0.2s"
                >
                  <span class="font-bold text-lg w-6 text-center">{{ opt.label }}</span>
                  <span class="flex-1">{{ opt.text }}</span>
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
              <!-- 编程题 -->
              <div v-else-if="q.type === 'code'" class="mt-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                  >你的代码：</label
                >
                <textarea
                  v-model="userAnswers[idx]"
                  :disabled="showResult"
                  rows="8"
                  class="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-900 font-mono text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                  placeholder="请在此处编写你的代码..."
                ></textarea>
              </div>

              <!-- 参考答案 -->
              <div
                v-if="showResult && showAllAnswers"
                class="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg"
              >
                <div class="text-sm text-green-700 dark:text-green-300 font-semibold mb-1">
                  参考答案：
                </div>
                <!-- 简答题答案 -->
                <div
                  v-if="q.type === 'essay'"
                  class="text-gray-700 dark:text-gray-300"
                  v-html="formatContent(q.answer)"
                ></div>
                <!-- 选择题答案 -->
                <div
                  v-else-if="q.type === 'single_choice' || q.type === 'multiple_choice'"
                  class="text-lg font-medium"
                >
                  {{ q.answer }}
                </div>
                <!-- 编程题答案 -->
                <div
                  v-else
                  class="text-gray-700 dark:text-gray-300"
                  v-html="formatContent(q.answer)"
                ></div>
                <div v-if="q.points" class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  <span class="font-medium">得分要点：</span>
                  <ul class="list-disc pl-4 mt-1 space-y-1">
                    <li v-for="(p, pi) in q.points" :key="pi">{{ p }}</li>
                  </ul>
                </div>
                <div v-if="q.explanation" class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  <span class="font-medium">解析：</span>{{ q.explanation }}
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- 底部操作按钮 -->
        <div class="flex justify-between items-center mt-10 pt-6 border-t">
          <div class="text-sm text-gray-500 dark:text-gray-400">
            已完成 {{ answeredCount }}/{{ questions.length }} 题
          </div>
          <div class="flex gap-4">
            <Button @click="resetTest" type="info" v-if="!showResult">重置</Button>
            <Button type="primary" @click="submitAnswers" :disabled="showResult"> 提交答案 </Button>
          </div>
        </div>

        <!-- 成绩展示 -->
        <div
          v-if="showResult"
          class="mt-8 p-6 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl"
        >
          <h3 class="text-xl font-bold text-gray-800 dark:text-white mb-4 text-center">训练结果</h3>
          <div class="grid grid-cols-3 gap-4 mb-6">
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {{ questions.length }}
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">题目数量</div>
            </div>
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-green-600 dark:text-green-400">
                {{ finalScore }}
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">得分</div>
            </div>
            <div class="bg-white dark:bg-gray-700 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-amber-600 dark:text-amber-400">
                {{ scorePercentage }}%
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">完成率</div>
            </div>
          </div>
          <div class="text-center">
            <div class="flex justify-center items-center gap-4">
              <!-- 重新开始按钮 -->
              <button
                @click="resetTest"
                class="px-6 py-3 flex items-center text-base font-medium rounded-lg transition-colors bg-orange-500 text-white hover:bg-orange-600 shadow-md"
              >
                <Icon icon="lucide:refresh-cw" class="w-5 h-5 mr-2" />
                重新训练
              </button>

              <!-- 返回首页按钮 -->
              <button
                @click="backToHome"
                class="px-6 py-3 flex items-center text-base font-medium rounded-lg transition-colors bg-blue-500 text-white hover:bg-blue-600 shadow-md"
              >
                <Icon icon="lucide:home" class="w-5 h-5 mr-2" />
                返回首页
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onActivated, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Icon } from '@iconify/vue'
import axios from 'axios'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import { useSidebar } from '@/composables/useSidebar'
import { getApiUrl } from '@/config/api'

const router = useRouter()
const route = useRoute()
const questions = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const showAllAnswers = ref(false)
const showResult = ref(false)
const userAnswers = ref<string[]>([])
const marked = ref<Set<number>>(new Set())
const activeEssayIdx = ref<number | null>(null)
const portrait = ref<any>(null)
const dataSource = ref<'history' | 'recommend' | 'fallback'>('fallback')
// 用于缓存检查，避免重复请求
const lastHistoryId = ref<string>('')
const lastUserId = ref<string>('')

// 分区计数（用于标题显示）
const historyCount = computed(
  () => questions.value.filter((q: any) => q.source === 'history').length,
)
const recommendCount = computed(
  () => questions.value.filter((q: any) => q.source === 'recommend').length,
)

// 将 weakness 表记录转为训练题目格式
function transformWeaknessItem(item: any, idx: number) {
  return {
    id: String(item.question_id || `h_${idx}`),
    title: item.title || '薄弱点练习',
    content: item.content || '',
    answer: item.standard_answer || '',
    score: item.question_score != null ? Number(item.question_score) : 5,
    difficulty: item.difficulty || 'medium',
    tag: item.tag_name || '',
    knowledgePoint: item.knowledgepoint_name || '',
    source: 'history' as const,
    isConsistentWeakness: false,
    type: item.question_type || item.type || 'essay',
    choice: item.choice || '',
  }
}

// 静态兜底题目（仅在 API 完全失败时使用）
const initQuestions = () => {
  return [
    {
      id: '1',
      title: 'HashMap 深度解析',
      content:
        '请详细说明 JDK1.8 中 HashMap 的扩容机制（包括触发条件、扩容流程、负载因子的作用），并解释其在 JDK1.7 到 JDK1.8 中从"头插法"改为"尾插法"的原因及其解决的问题。',
      answer:
        '1. 扩容机制：当HashMap中元素数量超过"容量 * 负载因子(默认0.75)"时触发。扩容会创建一个新的2倍大小的数组，并对所有元素进行rehash，重新计算索引位置。负载因子0.75是在时间和空间成本上的一个折中权衡。\n\n2. 头插法变尾插法：JDK1.7在链表扩容时采用头插法，在多线程并发rehash时可能形成环形链表，导致CPU 100%的严重问题。JDK1.8改为尾插法，避免了此问题，但HashMap本身仍是非线程安全的，并发场景应使用ConcurrentHashMap。',
      points: [
        '明确说出扩容触发条件（容量*负载因子）',
        '解释负载因子0.75的权衡意义',
        '指出JDK1.7头插法在多线程下可能导致环形链表',
        '说明JDK1.8改为尾插法是为了解决此并发问题',
      ],
      explanation:
        '本题针对面试中未提及HashMap具体扩容机制和头插法改进的缺陷，帮助深入理解HashMap的线程安全问题。',
      score: 10,
      difficulty: 'medium',
      tag: 'Java',
      knowledgePoint: 'HashMap原理',
    },
    {
      id: '2',
      title: '缓存穿透高级解决方案',
      content:
        '为防止缓存穿透，除了缓存空值，布隆过滤器（Bloom Filter）是如何工作的？请对比"缓存空值"与"布隆过滤器"两种方案的优缺点，并说明在何种业务场景下应优先选择后者。',
      answer:
        '布隆过滤器是一个二进制向量（位数组）和一系列哈希函数构成的空间高效数据结构，用于判断一个元素是否一定不存在于集合中（可能有误判，但不会漏判）。\n\nvs 缓存空值：\n1. 空值缓存：实现简单，但可能因大量不同的非法Key耗尽内存，且需为每个Key设置较短的TTL。\n2. 布隆过滤器：内存占用极低，与非法Key数量无关。缺点是存在一定的误判率，且无法删除元素（可使用Counting Bloom Filter变体）。\n\n优先使用场景：当业务存在海量、不可预测的非法查询请求（如恶意遍历、爬虫），且可接受极低概率的误判（将合法请求误认为非法）时，应优先使用布隆过滤器前置拦截，以保护数据库和Redis内存。',
      points: [
        '描述布隆过滤器的基本原理（位数组、多个哈希函数、判断"一定不存在"）',
        '对比两者在内存消耗和应对海量非法Key上的核心差异',
        '指出布隆过滤器的缺点（误判、删除困难）',
        '给出合理的适用场景（海量不可预测请求）',
      ],
      explanation: '本题针对面试中缓存穿透解决方案比较基础，未提及布隆过滤器这种更高效方案的缺陷。',
      score: 10,
      difficulty: 'hard',
      tag: 'Redis',
      knowledgePoint: '缓存穿透',
    },
    {
      id: '3',
      title: '互斥锁实现缓存击穿的健壮性设计',
      content:
        '在实现基于Redis SETNX的分布式锁来解决缓存击穿时，为了防止死锁，必须设置锁的超时时间。但这会引入"锁过期但业务未执行完"的新问题。请描述一个更健壮的分布式锁实现方案（可参考Redlock思想或Redisson库），并说明其如何保证原子性、锁续期和释放锁的安全性。',
      answer:
        '一个健壮的方案需包含：\n\n1. 加锁原子性：使用"SET lock_name unique_value NX PX 30000"命令，将设置值和过期时间在一个原子操作中完成。\n\n2. 锁续期（Watchdog）：业务执行时间可能超过锁过期时间。解决方案是启动一个"看门狗"线程，在业务执行期间定期（如过期时间的1/3）对锁进行续期，避免业务未完成锁被释放。\n\n3. 释放锁的安全性：释放锁时，需先判断锁的unique_value（如UUID+线程ID）是否与当前客户端设置的值一致，一致时才删除。这需要使用Lua脚本保证判断和删除的原子性，防止误删其他客户端的锁。',
      points: [
        '提到加锁命令必须是原子的（SET ... NX PX）',
        '提出"锁续期"概念及解决方案（看门狗线程）',
        '强调释放锁时需验证锁持有者，并通过Lua脚本保证原子性',
      ],
      explanation:
        '本题针对面试中互斥锁实现未提到设置过期时间防止死锁，也没提到锁等待的具体策略，生产环境意识较弱的缺陷。',
      score: 10,
      difficulty: 'medium',
      tag: '分布式系统',
      knowledgePoint: '分布式锁',
    },
    {
      id: '4',
      title: 'MySQL索引优化深度实践',
      content:
        '你提到了"覆盖索引"可以避免回表。请具体说明如何创建一个覆盖索引，并解释最左前缀原则。请结合一个具体的SQL查询示例（例如：SELECT name, price FROM products WHERE category = "电子" AND price > 1000 ORDER BY create_time DESC;），设计一个最优的复合索引，并阐述其如何满足查询条件、排序和覆盖索引的要求。',
      answer:
        '覆盖索引创建：索引包含了查询所需的所有字段（WHERE、ORDER BY、SELECT中的列），使得查询可以直接在索引中完成。例如，对于上述查询，最优索引可以是：(category, price, create_time DESC, name)。其中：\n\n1. category, price 用于WHERE条件过滤。\n2. create_time 用于满足ORDER BY排序，避免文件排序（filesort）。\n3. name 是查询的字段，加入索引后即可实现覆盖索引，无需回表。\n\n最左前缀原则：索引从最左列开始匹配。上述索引能高效匹配WHERE category = "电子"，也能匹配WHERE category = "电子" AND price > 1000，但无法单独加速WHERE price > 1000的查询。',
      points: [
        '创建的复合索引应包含WHERE、ORDER BY和SELECT中的字段',
        '明确解释索引字段的排序顺序（create_time DESC）是为了优化ORDER BY',
        '清楚阐述"最左前缀原则"的含义及限制',
        '指出该索引如何实现覆盖查询，避免回表',
      ],
      explanation:
        '本题针对面试中未提及覆盖索引的具体创建策略，对于最左前缀原则等索引失效场景未涉及的缺陷。',
      score: 10,
      difficulty: 'medium',
      tag: 'MySQL',
      knowledgePoint: '索引优化',
    },
    {
      id: '5',
      title: 'WebSocket长连接的高可用保障',
      content:
        '在实现WebSocket来单提醒时，仅依赖协议层的ping/pong和前端重连是不够的。请描述在服务端应如何实现应用层的心跳机制来检测连接假死，以及如何设计一个用户在线状态管理系统。当服务端向已断开的连接发送消息失败时，除了记录日志，应有哪些补偿或降级方案来确保消息必达（请列举至少两种）？',
      answer:
        '1. 应用层心跳：客户端定期（如30秒）向服务端发送自定义心跳包（如{type:"heartbeat"}）。服务端维护一个"最后活跃时间"，若超时未收到任何消息（数据或心跳），则判定连接已断，主动关闭并清理会话。\n\n2. 在线状态管理：在Redis中维护一个在线用户集合或哈希表，键为用户ID，值为连接信息（如连接ID、节点IP）。连接建立/断开时更新此集合。\n\n3. 消息保障机制：\n   - 消息持久化与重试队列：发送消息前，先将其持久化到数据库或消息队列（如RocketMQ/Kafka）。发送失败后，由后台任务从队列中取出重试，或转移到延迟队列稍后重试。\n   - 多通道降级：当WebSocket多次重试失败后，触发降级逻辑，通过App推送、短信或站内信等备用通道补发通知，确保关键信息触达。',
      points: [
        '提出在应用层自定协议进行心跳保活，并说明如何判断假死',
        '提出利用Redis等外部存储管理全局在线状态',
        '提出消息先持久化，后发送的核心思想',
        '给出至少一种具体的补偿方案（如重试队列）和一种降级方案（如短信通知）',
      ],
      explanation: '本题针对面试中WebSocket回答缺乏在线状态管理，高并发下可能导致消息丢失的缺陷。',
      score: 10,
      difficulty: 'hard',
      tag: '网络编程',
      knowledgePoint: 'WebSocket高可用',
    },
  ]
}

// 计算属性
const totalScore = computed(() => {
  return questions.value.reduce((sum, q) => sum + q.score, 0)
})

const answeredCount = computed(() => {
  return userAnswers.value.filter((answer) => answer && answer.trim()).length
})

const finalScore = computed(() => {
  if (!showResult.value) return 0

  let score = 0
  questions.value.forEach((q, idx) => {
    if (q.type === 'code') {
      // 编程题默认满分
      score += q.score
    } else if (q.type === 'single_choice' || q.type === 'multiple_choice') {
      // 选择题根据答案判断
      if (userAnswers.value[idx] === q.answer) {
        score += q.score
      }
    } else {
      // 简答题：只要作答就给满分
      if (userAnswers.value[idx] && userAnswers.value[idx].trim()) {
        score += q.score
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

function toggleAllAnswers() {
  showAllAnswers.value = !showAllAnswers.value
}

function selectOption(qIdx: number, label: string) {
  if (showResult.value) return
  userAnswers.value[qIdx] = label
}

function getDifficultyColor(
  difficulty: string,
): 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark' {
  const colorMap: Record<
    string,
    'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark'
  > = {
    easy: 'success',
    medium: 'warning',
    hard: 'error',
  }
  return colorMap[difficulty] || 'info'
}

function getDifficultyLabel(difficulty: string): string {
  const labelMap: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难',
  }
  return labelMap[difficulty] || difficulty
}

function getTypeColor(
  type: string,
): 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark' {
  const colorMap: Record<
    string,
    'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark'
  > = {
    single_choice: 'primary',
    multiple_choice: 'info',
    essay: 'success',
    code: 'warning',
  }
  return colorMap[type] || 'info'
}

function getTypeLabel(type: string): string {
  const labelMap: Record<string, string> = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    essay: '简答题',
    code: '编程题',
  }
  return labelMap[type] || type
}

function parseChoices(choice: string): { label: string; text: string }[] {
  if (!choice || !choice.trim()) return []
  const regex = /([A-D])\.(.*?)(?=[A-D]\.|$)/g
  const result: { label: string; text: string }[] = []
  let match
  while ((match = regex.exec(choice)) !== null) {
    result.push({ label: match[1], text: match[2].trim() })
  }
  return result
}

function isSelected(qIdx: number, label: string) {
  return userAnswers.value[qIdx] === label
}

function formatContent(content: string) {
  if (!content) return ''
  return content.replace(/\\n/g, '<br>').replace(/\n/g, '<br>')
}

function submitAnswers() {
  showResult.value = true
  showAllAnswers.value = true
  ElMessage.success(`训练完成！得分：${finalScore.value}/${totalScore.value}`)
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function resetTest() {
  showResult.value = false
  showAllAnswers.value = false
  userAnswers.value = new Array(questions.value.length).fill('')
  marked.value = new Set()
}

function backToHome() {
  router.push({ name: 'Interview' })
}

const { isMobileOpen, toggleMobileSidebar } = useSidebar()

// 将 /api/recommend 返回的题目转为训练题目格式
function transformRecommendItem(item: any, idx: number) {
  return {
    id: String(item.question_id || item.id || `r_${idx}`),
    title: item.title || '推荐练习',
    content: item.content || '',
    answer: item.standard_answer || item.answer || '',
    score: item.difficulty === 'hard' ? 10 : item.difficulty === 'medium' ? 5 : 3,
    difficulty: item.difficulty || 'medium',
    tag:
      Array.isArray(item.tag_names) && item.tag_names.length > 0
        ? item.tag_names[0]
        : item.tag_name || '',
    knowledgePoint: item.knowledgepoint_name || item.kp_name || '',
    source: 'recommend' as const,
    isConsistentWeakness: false,
    type: item.question_type || item.type || 'essay',
    choice: item.choice || '',
  }
}

// 用画像的薄弱 Tag 对题目进行"长期薄弱"标注
function annotateWithPortrait(qs: any[], weakTagNames: Set<string>) {
  for (const q of qs) {
    q.isConsistentWeakness = q.tag ? weakTagNames.has(q.tag) : false
  }
  return qs
}

async function loadTrainingData() {
  const historyId = route.query.history_id as string
  const userId = localStorage.getItem('user_id')

  // 缓存检查：参数未变化则不重新请求
  if (
    lastHistoryId.value === historyId &&
    lastUserId.value === userId &&
    questions.value.length > 0
  ) {
    console.log('参数未变化，使用缓存数据')
    return
  }

  // 更新缓存标识
  lastHistoryId.value = historyId
  lastUserId.value = userId

  questions.value = []
  portrait.value = null
  dataSource.value = 'fallback'
  showResult.value = false
  showAllAnswers.value = false
  marked.value = new Set()
  loading.value = true

  try {
    // Step 1：先取画像 — 需要 priority_tag_ids 才能构造 tagHints
    let portraitData: any = null
    if (userId) {
      try {
        const pRes = await axios.get(getApiUrl(`/user/portrait/${userId}`))
        portraitData = pRes.data?.data ?? null
        portrait.value = portraitData
      } catch (e) {
        console.warn('画像加载失败（不影响主流程）:', e)
      }
    }

    // 从画像提取 tagHints（含笔试失败 tag，补充 WEAK_AT 之外的信号）
    const priorityTagIds: string[] = portraitData?.recommendation_profile?.priority_tag_ids ?? []
    const tagHintsParam = priorityTagIds.length > 0 ? `&tagHints=${priorityTagIds.join(',')}` : ''

    // 薄弱 tag 名称集合，用于"长期薄弱"标注
    const weakTagNames = new Set<string>(
      (portraitData?.graph_data?.weak_area_tags ?? []).map((t: any) => t.tag_name as string),
    )

    // Step 2：并发调用 recommend（始终）+ history weakness（条件）
    const [recommendResult, historyResult] = await Promise.allSettled([
      userId
        ? axios.get(getApiUrl(`/recommend?userId=${userId}${tagHintsParam}`))
        : Promise.resolve(null),
      historyId ? axios.get(getApiUrl(`/history/${historyId}/weakness`)) : Promise.resolve(null),
    ])

    // 解析 recommend 结果（始终尝试）
    let recommendQs: any[] = []
    if (recommendResult.status === 'fulfilled' && recommendResult.value) {
      const raw: any[] = recommendResult.value.data?.data?.questions ?? []
      recommendQs = annotateWithPortrait(raw.map(transformRecommendItem), weakTagNames)
    }

    // 解析 history weakness 结果（仅当 historyId 存在）
    let historyQs: any[] = []
    if (historyResult.status === 'fulfilled' && historyResult.value) {
      const raw: any[] =
        historyResult.value.data?.weakness ?? historyResult.value.data?.data?.weakness ?? []
      historyQs = annotateWithPortrait(raw.map(transformWeaknessItem), weakTagNames)
    }

    // Step 3：去重 — recommend 已有题不在 history 中重复展示（优先保留 recommend）
    if (historyQs.length > 0 && recommendQs.length > 0) {
      const recommendIds = new Set(recommendQs.map((q: any) => q.id))
      historyQs = historyQs.filter((q: any) => !recommendIds.has(q.id))
    }

    dataSource.value = recommendQs.length > 0 ? 'recommend' : historyId ? 'history' : 'fallback'

    // 合并：recommend 分区在前（优先），history 分区在后
    const merged = [...recommendQs, ...historyQs]
    questions.value =
      merged.length > 0
        ? merged
        : initQuestions().map((q: any) => ({
            ...q,
            source: 'fallback',
            isConsistentWeakness: false,
          }))

    userAnswers.value = new Array(questions.value.length).fill('')
  } catch (e) {
    console.error('加载薄弱点训练数据失败:', e)
    questions.value = initQuestions().map((q: any) => ({
      ...q,
      source: 'fallback',
      isConsistentWeakness: false,
    }))
    userAnswers.value = new Array(questions.value.length).fill('')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (isMobileOpen.value) toggleMobileSidebar()
  // loadTrainingData 由 onActivated 统一调用（首次挂载时也会执行）
})

// keep-alive 重新激活时检查参数是否变化，只有变化才重新加载
onActivated(() => {
  loadTrainingData()
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

/* 文本域样式 */
textarea {
  font-family:
    'Inter',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    sans-serif;
  line-height: 1.5;
  resize: vertical;
  min-height: 100px;
}
</style>
