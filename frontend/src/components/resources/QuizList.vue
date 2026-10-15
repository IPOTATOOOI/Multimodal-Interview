<template>
  <div class="quiz-list-container">
    <!-- Root Category 导航栏 -->
    <div
      class="root-category-bar flex gap-8 px-6 pt-4 pb-2 dark:bg-gray-900 border-b border-gray-100 dark:border-gray-800 relative text-gray-900"
    >
      <!-- 根分类滑动指示器 -->
      <div
        class="root-category-indicator"
        :style="{
          width: rootIndicatorWidth + 'px',
          left: rootIndicatorLeft + 'px',
        }"
      ></div>

      <div
        v-for="root in rootCategories"
        :key="root.name"
        class="root-category-item"
        :class="{ active: rootCategory === root.name }"
        @click="selectRootCategory(root.name)"
        ref="rootCategoryItems"
      >
        {{ root.name }}
      </div>
    </div>

    <!-- 大卡片容器，包含二级分类和题目卡片 -->
    <div
      class="main-content-card mx-3 mt-3 rounded-xl shadow-md bg-white dark:bg-gray-850 overflow-hidden"
    >
      <!-- Sub Category 导航栏 -->
      <div
        class="sub-category-bar flex gap-2 px-6 py-3 bg-gray-30 dark:bg-gray-800 border-b text-gray-900 border-gray-100 dark:border-gray-700"
      >
        <div
          v-for="sub in currentSubCategories"
          :key="sub"
          class="sub-category-item"
          :class="{ active: subCategory === sub }"
          @click="selectSubCategory(sub)"
          ref="subCategoryItems"
        >
          {{ sub }}
        </div>
      </div>

      <!-- 当topic数量大于4个时，显示热门和全部两个区域 -->
      <template v-if="topics.length > 5">
        <!-- 热门 Topic 区域 -->
        <div
          v-if="hotTopics.length > 0"
          class="p-6 border-b border-gray-100 dark:border-gray-700 dark:bg-gray-800"
        >
          <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200 flex items-center">
            <span class="inline-block w-1 h-6 bg-blue-500 rounded-full mr-2"></span>
            <span>热门</span>
          </h3>
          <div
            class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 dark:border-0"
          >
            <el-card
              v-for="topic in hotTopics"
              :key="`hot-${topic.id}`"
              class="cursor-pointer hover:shadow-lg transition-all duration-300"
              @click="goToPractice(topic)"
            >
              <template #header>
                <div class="flex justify-between items-center">
                  <div class="flex items-center gap-3">
                    <!-- 根据topic名称显示对应图标 -->
                    <CustomIcon
                      :name="getIconNameByTopicName(topic.name)"
                      size="xl"
                      class="flex-shrink-0"
                    />
                    <span class="font-medium dark:text-gray-400">{{ topic.name }}</span>
                  </div>
                  <Star
                    :fill="favorites.has(topic.id) ? 'currentColor' : 'none'"
                    :class="favorites.has(topic.id) ? 'text-yellow-400' : ''"
                    :size="18"
                    @click.stop="toggleFavorite(topic.id)"
                    class="cursor-pointer transition-colors duration-300 dark:text-gray-400"
                  />
                </div>
              </template>
              <div class="text-sm text-gray-500 dark:text-gray-400">
                题目数量：{{ topic.question_count }}
              </div>
            </el-card>
          </div>
        </div>

        <!-- 全部 Topic 区域 -->
        <div class="p-6 dark:border-gray-700 dark:bg-gray-800">
          <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200 flex items-center">
            <span class="inline-block w-1 h-6 bg-gray-500 rounded-full mr-2"></span>
            <span>全部</span>
          </h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <el-card
              v-for="topic in topics"
              :key="topic.id"
              class="cursor-pointer hover:shadow-lg transition-all duration-300"
              @click="goToPractice(topic)"
            >
              <template #header>
                <div class="flex justify-between items-center">
                  <div class="flex items-center gap-3">
                    <!-- 根据topic名称显示对应图标 -->
                    <CustomIcon
                      :name="getIconNameByTopicName(topic.name)"
                      size="xl"
                      class="flex-shrink-0"
                    />
                    <span class="font-medium dark:text-gray-400">{{ topic.name }}</span>
                  </div>
                  <Star
                    :fill="favorites.has(topic.id) ? 'currentColor' : 'none'"
                    :class="favorites.has(topic.id) ? 'text-yellow-400' : ''"
                    :size="18"
                    @click.stop="toggleFavorite(topic.id)"
                    class="cursor-pointer transition-colors duration-300 dark:text-gray-400"
                  />
                </div>
              </template>
              <div class="text-sm text-gray-500 dark:text-gray-400">
                题目数量：{{ topic.question_count }}
              </div>
            </el-card>
          </div>
        </div>
      </template>

      <!-- 当topic数量小于等于4个时，直接展示所有topic -->
      <template v-else>
        <div class="p-6 border-b border-gray-100 dark:border-gray-700 dark:bg-gray-800">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <el-card
              v-for="topic in topics"
              :key="topic.id"
              class="cursor-pointer hover:shadow-lg transition-all duration-300"
              @click="goToPractice(topic)"
            >
              <template #header>
                <div class="flex justify-between items-center">
                  <div class="flex items-center gap-3">
                    <!-- 根据topic名称显示对应图标 -->
                    <CustomIcon
                      :name="getIconNameByTopicName(topic.name)"
                      size="xl"
                      class="flex-shrink-0"
                    />
                    <span class="font-medium dark:text-gray-400">{{ topic.name }}</span>
                  </div>
                  <Star
                    :fill="favorites.has(topic.id) ? 'currentColor' : 'none'"
                    :class="favorites.has(topic.id) ? 'text-yellow-400' : ''"
                    :size="18"
                    @click.stop="toggleFavorite(topic.id)"
                    class="cursor-pointer transition-colors duration-300 dark:text-gray-400"
                  />
                </div>
              </template>
              <div class="text-sm text-gray-500 dark:text-gray-400">
                题目数量：{{ topic.question_count }}
              </div>
            </el-card>
          </div>
        </div>
      </template>

      <!-- 加载和空状态显示 -->
      <div v-if="loading" class="p-6 text-center text-gray-400 dark:bg-gray-800 dark:text-gray-200">
        加载中...
      </div>
      <div
        v-if="!loading && topics.length === 0"
        class="p-6 text-center text-gray-400 dark:bg-gray-800 dark:text-gray-200"
      >
        暂无数据
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed, nextTick } from 'vue'
import { Star } from 'lucide-vue-next'
import { ElCard } from 'element-plus'
import { useRouter } from 'vue-router'
import CustomIcon from '../ui/CustomIcon.vue'
import { getApiUrl } from '@/config/api'

// 分类数据
const rootCategories = [
  { name: '软件开发', sub: ['专项练习', '面试真题'] },
  { name: '考公', sub: ['行测', '申论'] },
  { name: '国央企', sub: ['行测', '公共基础题', '性格测试'] },
]

const rootCategory = ref('软件开发')
const subCategory = ref('专项练习')
const topics = ref<any[]>([])
const hotTopics = ref<any[]>([]) // 热门话题（题目数量最多的前6个）
const loading = ref(false)
const favorites = ref<Set<number>>(new Set()) // 收藏的话题ID集合

// 根分类指示器状态
const rootCategoryItems = ref<HTMLElement[]>([])
const rootIndicatorWidth = ref(0)
const rootIndicatorLeft = ref(0)

// 子分类指示器状态
const subCategoryItems = ref<HTMLElement[]>([])
const subIndicatorWidth = ref(0)
const subIndicatorLeft = ref(0)

const currentSubCategories = computed(() => {
  const found = rootCategories.find((r) => r.name === rootCategory.value)
  return found ? found.sub : []
})

const router = useRouter()

// 根据topic名称获取对应的图标名称
function getIconNameByTopicName(topicName: string): string {
  const name = topicName.toLowerCase()

  // 编程语言匹配
  if (name.includes('c语言')) {
    return 'c语言'
  }
  if (name.includes('c++')) {
    return 'c++'
  }
  if (name.includes('java')) {
    return 'java'
  }
  if (name.includes('python')) {
    return 'python'
  }
  if (name.includes('操作系统')) {
    return 'OS'
  }
  if (name.includes('编译原理')) {
    return 'CP'
  }
  if (name.includes('数据库') || name.includes('sql') || name.includes('mysql')) {
    return 'DB'
  }
  if (name.includes('软件工程')) {
    return '软件工程'
  }
  if (name.includes('软件测试')) {
    return 'ST'
  }
  if (name.includes('数据结构')) {
    return 'DS'
  }
  if (name.includes('spring')) {
    return 'spring'
  }
  if (name.includes('redis')) {
    return 'redis'
  }
  if (name.includes('jvm')) {
    return 'JVM'
  }
  if (name.includes('mybatis')) {
    return 'mybatis'
  }

  // 考公相关匹配
  if (name.includes('行测')) {
    return 'exam'
  }
  if (name.includes('申论')) {
    return 'test'
  }
  if (name.includes('面试') || name.includes('真题')) {
    return 'test'
  }
  if (name.includes('公共基础')) {
    return 'book'
  }
  if (name.includes('性格测试')) {
    return 'brain'
  }

  // 默认返回
  return 'default'
}

// 切换收藏状态
function toggleFavorite(topicId: number) {
  if (favorites.value.has(topicId)) {
    favorites.value.delete(topicId)
  } else {
    favorites.value.add(topicId)
  }
  // 触发响应式更新
  favorites.value = new Set(favorites.value)
}

function selectRootCategory(name: string) {
  if (rootCategory.value !== name) {
    rootCategory.value = name
    const found = rootCategories.find((r) => r.name === name)
    subCategory.value = found?.sub[0] || ''
    nextTick(() => {
      updateRootIndicatorPosition()
      updateSubIndicatorPosition()
    })
  }
}

function selectSubCategory(name: string) {
  if (subCategory.value !== name) {
    subCategory.value = name
    nextTick(() => updateSubIndicatorPosition())
  }
}

// 更新根分类指示器位置
function updateRootIndicatorPosition() {
  const activeIndex = rootCategories.findIndex((r) => r.name === rootCategory.value)
  if (activeIndex !== -1 && rootCategoryItems.value[activeIndex]) {
    const rect = rootCategoryItems.value[activeIndex].getBoundingClientRect()
    const barRect = (
      rootCategoryItems.value[0].parentElement as HTMLElement
    ).getBoundingClientRect()
    rootIndicatorWidth.value = rect.width
    rootIndicatorLeft.value = rect.left - barRect.left
  }
}

// 更新子分类指示器位置
function updateSubIndicatorPosition() {
  const activeIndex = currentSubCategories.value.findIndex((s) => s === subCategory.value)
  if (activeIndex !== -1 && subCategoryItems.value[activeIndex]) {
    const rect = subCategoryItems.value[activeIndex].getBoundingClientRect()
    const barRect = (subCategoryItems.value[0].parentElement as HTMLElement).getBoundingClientRect()
    subIndicatorWidth.value = rect.width
    subIndicatorLeft.value = rect.left - barRect.left
  }
}

async function fetchTopics() {
  loading.value = true
  topics.value = []
  hotTopics.value = []

  try {
    const url = getApiUrl(`/questionBank/topics?root_category_name=${encodeURIComponent(rootCategory.value)}&sub_category_name=${encodeURIComponent(subCategory.value)}`)
    const res = await fetch(url)
    if (!res.ok) throw new Error('请求失败')
    const data = await res.json()

    // 兼容两种返回结构：{ topics: [] } 和 { data: { topics: [] } }
    let allTopics = data.topics || data.data?.topics || []

    // 处理questionCount为0的情况，随机赋值30-200
    allTopics = allTopics.map((topic: any) => ({
      ...topic,
      question_count:
        topic.question_count ?? topic.questionCount ?? 0,
    }))

    // 根据topic数量决定显示方式
    if (allTopics.length > 4) {
      // 数量大于4个时，按题目数量排序，取前6个作为热门话题
      const sortedTopics = [...allTopics].sort((a, b) => b.question_count - a.question_count)
      hotTopics.value = sortedTopics.slice(0, 6)
      topics.value = allTopics
    } else {
      // 数量小于等于4个时，直接展示所有topic
      hotTopics.value = []
      topics.value = allTopics
    }
  } catch (e) {
    console.error('获取题库列表失败:', e)
    topics.value = []
    hotTopics.value = []
  } finally {
    loading.value = false
  }
}

// 监听分类变化自动请求
watch([rootCategory, subCategory], fetchTopics, { immediate: true })

function goToPractice(topic: any) {
  router.push({
    name: 'QuestionPractice',
    query: {
      topic_id: topic.id,
      topic_name: topic.name,
    },
  })
}

onMounted(() => {
  nextTick(() => {
    updateRootIndicatorPosition()
    updateSubIndicatorPosition()
  })
})
</script>

<style scoped>
/* 样式部分保持不变，除了已在模板中修改的部分 */
.root-category-bar {
  font-size: 18px;
  font-weight: 500;
  position: relative; /* 为指示器提供定位参考 */
}

/* 根分类指示器 */
.root-category-indicator {
  position: absolute;
  height: 6px; /* 蓝条高度 */
  bottom: 4px; /* 贴近底部，靠近文字 */
  z-index: 1;
  background: linear-gradient(135deg, #3641f5 0%, #5a65ff 100%);
  border-radius: 8px 8px 8px 8px; /* 右上和左下圆角 */
  transition: all 0.3s ease-out; /* 平滑过渡动画 */
}

/* 根分类菜单项 */
.root-category-item {
  padding: 8px 18px 4px 18px;
  cursor: pointer;
  color: #475467;
  transition: all 0.3s;
  position: relative;
  transform-origin: bottom center; /* 缩放原点设为左下角，确保蓝条对齐 */
}

/* 根分类活跃状态 */
.root-category-item.active {
  color: #3641f5;
  transform: scale(1.15);
}

/* 主内容卡片样式 */
.main-content-card {
  transition: all 0.3s ease;
}

.main-content-card:hover {
  box-shadow:
    0 10px 25px -5px rgba(0, 0, 0, 0.05),
    0 8px 10px -6px rgba(0, 0, 0, 0.02);
}

.sub-category-bar {
  font-size: 17px;
  font-weight: 500;
  flex-wrap: wrap; /* 允许在小屏幕上换行 */
}

/* 子分类菜单项 - 美化样式 */
.sub-category-item {
  padding: 6px 16px;
  cursor: pointer;
  color: #475467;
  transition: all 0.3s ease;
  border-radius: 20px; /* 完整的圆角设计 */
  margin: 2px 0;
}

/* 子分类活跃状态 */
.sub-category-item.active {
  color: white;
  background: linear-gradient(135deg, #3641f5 0%, #5a65ff 100%);
  box-shadow: 0 4px 12px rgba(54, 65, 245, 0.2);
}

/* 子分类悬停效果 */
.sub-category-item:not(.active):hover {
  background-color: #f1f5f9;
  color: #334155;
}

/* 移除Element UI卡片的默认边距和阴影 */
:deep(.el-card) {
  margin: 0;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  background: transparent !important;
}

:deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-card__body) {
  padding: 16px;
}
</style>
