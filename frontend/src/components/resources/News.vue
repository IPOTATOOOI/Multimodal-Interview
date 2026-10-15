<template>
  <div>
    <div class="container mx-auto px-4 py-8">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 transition-all duration-300">
        <div class="space-y-6">
          <!-- 头部区域 -->
          <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-400 rounded-lg flex items-center justify-center"
              >
                <Icon icon="lucide:newspaper" class="text-white text-lg w-6 h-6" />
              </div>
              <div>
                <h2 class="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  互联网新闻资讯聚合
                </h2>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">实时获取最新技术资讯</p>
              </div>
            </div>

            <!-- 筛选和操作区域 -->
            <div
              class="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full lg:w-auto"
            >
              <!-- 级联选择器 -->
              <div class="flex items-center gap-3 w-full sm:w-auto">
                <div class="flex items-center gap-2">
                  <Icon icon="lucide:filter" class="text-gray-500 dark:text-gray-400" />
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">分类筛选</span>
                </div>
                <el-cascader
                  v-model="selectedCategories"
                  :options="categoryOptions"
                  :props="cascaderProps"
                  placeholder="请选择分类"
                  clearable
                  collapse-tags
                  collapse-tags-tooltip
                  class="w-full sm:w-64"
                  popperClass="my-cascader"
                  size="default"
                  @change="handleCategoryChange"
                >
                  <template #default="{ node, data }">
                    <span class="flex items-center gap-2">
                      <i :class="getCategoryIcon(data.value)" class="text-sm"></i>
                      <span>{{ data.label }}</span>
                      <span v-if="data.count" class="text-xs text-gray-400"
                        >({{ data.count }})</span
                      >
                    </span>
                  </template>
                </el-cascader>
              </div>

              <!-- 刷新按钮 -->
              <el-button
                type="primary"
                :icon="Refresh"
                @click="refreshFeed"
                :loading="loading"
                class="w-full sm:w-auto"
              >
                刷新资讯
              </el-button>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="flex justify-center items-center py-12">
            <div
              class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"
            ></div>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">加载新闻失败: {{ error.message }}</p>
                <p class="mt-2 text-sm">
                  <button
                    class="text-blue-500 hover:text-blue-600 font-medium"
                    @click="refreshFeed"
                  >
                    点击重试
                  </button>
                </p>
              </div>
            </div>
          </div>

          <!-- 新闻列表 -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <article
              v-for="item in filteredNewsItems"
              :key="item.id"
              class="bg-white dark:bg-gray-700 rounded-lg overflow-hidden shadow hover:shadow-lg transition-shadow duration-300"
            >
              <a
                :href="item.link"
                target="_blank"
                rel="noopener noreferrer"
                class="block h-full p-5"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="mb-2">
                      <span
                        class="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs px-2 py-1 rounded-full"
                      >
                        {{ item.source }}
                      </span>
                    </div>

                    <h3
                      class="font-semibold text-lg text-gray-900 dark:text-white line-clamp-2 mb-3"
                    >
                      {{ item.title }}
                    </h3>

                    <p class="text-sm text-gray-600 dark:text-gray-300 line-clamp-3 mb-4">
                      {{ item.description || '暂无内容摘要' }}
                    </p>

                    <div
                      class="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400"
                    >
                      <div>
                        <i class="far fa-clock mr-1"></i>
                        {{ formatDate(item.pubDate) }}
                      </div>
                      <div>
                        <i class="far fa-user mr-1"></i>
                        {{ item.author || item.source }}
                      </div>
                    </div>
                  </div>
                </div>
              </a>
            </article>
          </div>

          <!-- 分页控制 -->
          <div
            v-if="filteredNewsItems.length && !loading"
            class="flex justify-between items-center mt-6"
          >
            <button
              :disabled="currentPage <= 1"
              @click="prevPage"
              class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              <Icon icon="lucide:chevron-left" class="mr-1" />
              上一页
            </button>

            <div class="text-sm text-gray-700 dark:text-gray-300">
              第 {{ currentPage }} 页，共 {{ totalPages }} 页
            </div>

            <button
              :disabled="currentPage >= totalPages"
              @click="nextPage"
              class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              下一页
              <Icon icon="lucide:chevron-right" class="ml-1" />
            </button>
          </div>

          <!-- 无数据提示 -->
          <div
            v-if="!loading && !error && filteredNewsItems.length === 0"
            class="text-center py-12"
          >
            <div class="text-gray-400 dark:text-gray-500 mb-4">
              <i class="fas fa-newspaper text-4xl"></i>
            </div>
            <p class="text-gray-500 dark:text-gray-400">没有找到符合条件的新闻</p>
            <button
              @click="resetFilters"
              class="mt-4 text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
            >
              重置筛选条件
            </button>
          </div>
        </div>
      </div>

      <footer class="mt-12 text-center text-gray-500 dark:text-gray-400 text-sm">
        <p>新闻资讯数据来源：InfoQ中文站、开源中国等</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { Refresh } from '@element-plus/icons-vue'
import { Icon } from '@iconify/vue'

// 配置信息
const ITEMS_PER_PAGE = 9
const newsSources = [
  {
    name: 'InfoQ中文站',
    url: '/rss-proxy/infoq',
    category: ['软件开发', '架构', 'AI'],
  },
  {
    name: '开源中国-最新资讯',
    url: '/rss-proxy/oschina',
    category: ['开源', '技术'],
  },
  {
    name: '开源中国-大模型',
    url: '/rss-proxy/oschina-llm',
    category: ['AI', '大模型'],
  },
  {
    name: '开源中国-大前端',
    url: '/rss-proxy/oschina-front',
    category: ['前端', '开发'],
  },
  {
    name: '开源中国-开发技能',
    url: '/rss-proxy/oschina-skill',
    category: ['开发', '编程'],
  },
  {
    name: '开源中国-数据库',
    url: '/rss-proxy/oschina-db',
    category: ['数据库', '开发'],
  },
  {
    name: '开源中国-软件架构',
    url: '/rss-proxy/oschina-arch',
    category: ['架构', '开发'],
  },
  {
    name: '开源中国-AI大数据',
    url: '/rss-proxy/oschina-ai',
    category: ['AI', '大数据'],
  },
  {
    name: '开源中国-运维',
    url: '/rss-proxy/oschina-ops',
    category: ['运维', '开发'],
  },
  {
    name: '开源中国-测试',
    url: '/rss-proxy/oschina-test',
    category: ['测试', '开发'],
  },
  {
    name: '开源中国-网络',
    url: '/rss-proxy/oschina-network',
    category: ['网络', '开发'],
  },
  {
    name: '开源中国-游戏',
    url: '/rss-proxy/oschina-game',
    category: ['游戏', '开发'],
  },
  {
    name: '开源中国-区块链',
    url: '/rss-proxy/oschina-blockchain',
    category: ['区块链', '开发'],
  },
  {
    name: '36氪',
    url: '/rss-proxy/36kr',
    category: ['互联网', '科技'],
  },
  {
    name: '极客公园',
    url: '/rss-proxy/geekpark',
    category: ['科技', '互联网'],
  },
  {
    name: '虎嗅网',
    url: '/rss-proxy/huxiu',
    category: ['互联网', '科技'],
  },
]

// 关键词列表用于筛选新闻
const keywords = [
  // 通用技术术语
  'AI',
  '人工智能',
  '机器学习',
  '深度学习',
  '神经网络',
  // 自然语言处理相关
  '自然语言处理',
  'NLP',
  '文本分析',
  '语义理解',
  // 计算机视觉相关
  '计算机视觉',
  'CV',
  '图像识别',
  '视频分析',
  // 模型相关
  '大语言模型',
  'LLM',
  '生成式AI',
  '多模态模型',
  '预训练模型',
  '微调模型',
  '模型部署',
  '模型训练',
  // 开发与编程
  '前端开发',
  'Web开发',
  '移动端开发',
  'React',
  'Vue',
  'Angular',
  '跨平台开发',
  'H5',
  '前端框架',
  '前端工程化',
  '组件化开发',
  '编程',
  '编码',
  '算法',
  '数据结构',
  '设计模式',
  '开发工具',
  'IDE',
  '版本控制',
  'Git',
  '调试',
  '重构',
  // 数据库
  'MySQL',
  'PostgreSQL',
  'MongoDB',
  'Redis',
  '数据库设计',
  '数据存储',
  'SQL',
  'NoSQL',
  '数据查询',
  '事务处理',
  '数据备份',
  // 架构
  '微服务',
  '分布式架构',
  '单体架构',
  'SOA',
  'API设计',
  '架构设计',
  '服务治理',
  // 云原生与容器化
  '容器化',
  'Kubernetes',
  '云原生',
  '服务注册发现',
  // 大数据
  'Hadoop',
  'Spark',
  'Flink',
  '数据挖掘',
  '数据分析',
  '数据湖',
  '数据仓库',
  '大数据平台',
  '实时计算',
  '离线计算',
  '数据清洗',
  // DevOps与运维
  'DevOps',
  'CI/CD',
  '监控',
  '告警',
  '自动化运维',
  '服务器管理',
  '云运维',
  '容器运维',
  '日志分析',
  '性能优化',
  '故障排查',
  // 测试
  '单元测试',
  '集成测试',
  '自动化测试',
  '性能测试',
  '压力测试',
  '测试用例',
  '测试工具',
  'Selenium',
  'Jest',
  '测试驱动开发',
  'TDD',
  // 网络
  'TCP/IP',
  'HTTP',
  'HTTPS',
  '网络协议',
  '网络安全',
  '防火墙',
  '负载均衡',
  'CDN',
  '网络架构',
  '带宽',
  '网络诊断',
  // 游戏开发
  'Unity',
  'Unreal',
  '游戏引擎',
  '3D建模',
  '游戏逻辑',
  '角色设计',
  '游戏测试',
  '游戏运营',
  '手游开发',
  '端游开发',
  '游戏美术',
  // 区块链
  '比特币',
  '以太坊',
  '智能合约',
  '加密货币',
  '分布式账本',
  'NFT',
  '共识机制',
  '区块链开发',
  '链上数据',
  '去中心化',
  '区块链安全',
  // 其他补充的基础词汇
  'AI伦理',
  'AI训练',
  'AI推理',
]

// 状态管理
const loading = ref(false)
const error = ref(null)
const rawNewsItems = ref([])
const currentPage = ref(1)

const categories = ref([
  'AI',
  '前端',
  '开发',
  '数据库',
  '架构',
  '大数据',
  '互联网',
  '区块链',
  '运维',
  '测试',
  '网络',
  '游戏',
  '人工智能',
  '机器学习',
  '深度学习',
  '自然语言处理',
  '计算机视觉',
  '模型训练',
  '微服务',
  '容器化',
  '云原生',
  'DevOps',
  '自动化测试',
  '网络安全',
  '游戏开发',
  '智能合约',
])
const darkMode = ref(false)

const filteredNewsItems = computed(() => {
  const filtered = applyAllFilters()
  const start = (currentPage.value - 1) * ITEMS_PER_PAGE
  return filtered.slice(start, start + ITEMS_PER_PAGE)
})

// 计算总页数 - 修复分页计算问题
const totalPages = computed(() => {
  const filtered = applyAllFilters()
  return Math.ceil(filtered.length / ITEMS_PER_PAGE)
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 解析RSS XML数据 - 支持多种格式
const parseRSS = (xml, sourceName) => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(xml, 'text/xml')

  // 检查是否是有效的 XML
  const parseError = doc.querySelector('parsererror')
  if (parseError) {
    console.error(`${sourceName} 返回无效的 XML 内容`)
    return []
  }

  const items = doc.querySelectorAll('item')
  const parsedItems = []

  Array.from(items).forEach((item) => {
    try {
      let title = ''
      let link = ''
      let pubDate = ''
      let author = sourceName
      let description = ''
      let source = sourceName

      // 36氪特殊处理
      if (sourceName === '36氪') {
        title = item.querySelector('title')?.textContent || ''
        link = item.querySelector('link')?.textContent || ''
        pubDate = item.querySelector('pubDate')?.textContent || ''

        // 处理CDATA格式的描述
        const descElement = item.querySelector('description')
        if (descElement) {
          const cdataContent = descElement.innerHTML
          // 提取CDATA内容并移除HTML标签
          const cdataMatch = cdataContent.match(/<!\[CDATA\[(.*?)\]\]>/s)
          if (cdataMatch) {
            description = cdataMatch[1].replace(/<[^>]+>/g, '').substring(0, 200) + '...'
          } else {
            description = descElement.textContent.replace(/<[^>]+>/g, '').substring(0, 200) + '...'
          }
        }

        // 提取来源
        const sourceElement = item.querySelector('source')
        if (sourceElement) {
          source = sourceElement.textContent || sourceName
        }
      }
      // 开源中国特殊处理
      else if (sourceName.startsWith('开源中国')) {
        title = item.querySelector('title')?.textContent || ''
        link = item.querySelector('link')?.textContent || ''
        pubDate = item.querySelector('pubDate')?.textContent || ''

        // 处理描述
        const descElement = item.querySelector('description')
        if (descElement) {
          description = descElement.textContent.replace(/<[^>]+>/g, '').substring(0, 200) + '...'
        }

        // 提取分类
        const categoryElement = item.querySelector('category')
        if (categoryElement) {
          author = categoryElement.textContent || sourceName
        }
      }
      // 其他标准RSS源
      else {
        title = item.querySelector('title')?.textContent || ''
        link = item.querySelector('link')?.textContent || ''
        pubDate = item.querySelector('pubDate')?.textContent || ''
        author = item.querySelector('creator')?.textContent || sourceName

        const descElement = item.querySelector('description')
        if (descElement) {
          description = descElement.textContent.replace(/<[^>]+>/g, '').substring(0, 200) + '...'
        }
      }

      parsedItems.push({
        id: item.querySelector('guid')?.textContent || Math.random().toString(36).substring(7),
        title,
        link,
        pubDate,
        author,
        description,
        source,
      })
    } catch (error) {
      console.error('解析新闻项失败:', error)
    }
  })

  return parsedItems
}

// 获取新闻数据
const fetchNews = async () => {
  loading.value = true
  error.value = null

  try {
    // 从本地存储获取缓存数据
    const cachedData = localStorage.getItem('internet-news-cache')
    const cacheTime = localStorage.getItem('internet-news-cache-time')
    const now = Date.now()

    // 如果缓存存在且未过期(10分钟)，使用缓存数据
    if (cachedData && cacheTime && now - parseInt(cacheTime) < 600000) {
      rawNewsItems.value = JSON.parse(cachedData)
      loading.value = false
      return
    }

    // 从多个来源获取数据
    const allNews = []

    // 创建带有自定义头部的axios实例
    const rssFetcher = axios.create({
      headers: {
        Accept:
          'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      },
      timeout: 10000, // 10秒超时
    })

    // 并发获取所有新闻源数据
    const fetchPromises = newsSources.map(async (source) => {
      try {
        const response = await rssFetcher.get(source.url)

        // 检查响应内容类型
        const contentType = response.headers['content-type'] || ''
        if (!contentType.includes('xml') && !contentType.includes('rss')) {
          console.warn(`从 ${source.name} 获取到非XML响应: ${contentType}`)
        }

        // 检查是否是有效的XML
        if (
          typeof response.data !== 'string' ||
          (!response.data.includes('<rss') &&
            !response.data.includes('<feed') &&
            !response.data.includes('<?xml'))
        ) {
          console.error(`从 ${source.name} 获取到无效的XML内容`)
          return
        }

        const parsedItems = parseRSS(response.data, source.name)
        allNews.push(...parsedItems)
        console.log(`从 ${source.name} 获取 ${parsedItems.length} 条新闻`)
      } catch (err) {
        console.error(`从 ${source.name} 获取新闻失败:`, err)
      }
    })

    await Promise.all(fetchPromises)

    // 按发布日期排序 (最新的在前)
    allNews.sort((a, b) => {
      return new Date(b.pubDate) - new Date(a.pubDate)
    })

    // 去重处理 (基于链接，避免重复卡片)
    const uniqueNews = []
    const seenLinks = new Set()

    allNews.forEach((item) => {
      // 使用链接作为唯一标识
      if (item.link && !seenLinks.has(item.link)) {
        seenLinks.add(item.link)
        uniqueNews.push(item)
      }
    })

    rawNewsItems.value = uniqueNews

    // 更新缓存
    localStorage.setItem('internet-news-cache', JSON.stringify(rawNewsItems.value))
    localStorage.setItem('internet-news-cache-time', now.toString())
  } catch (err) {
    console.error('获取新闻失败:', err)
    error.value = { message: '无法加载新闻数据，请稍后重试' }
  } finally {
    loading.value = false
  }
}

// 页面控制
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const refreshFeed = () => {
  // 清除缓存并重新加载
  localStorage.removeItem('internet-news-cache')
  localStorage.removeItem('internet-news-cache-time')
  currentPage.value = 1
  fetchNews()
}

const toggleDarkMode = () => {
  darkMode.value = !darkMode.value
  if (darkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// 级联选择器相关数据
const selectedCategories = ref([])

// 级联选择器配置
const cascaderProps = {
  expandTrigger: 'hover',
  multiple: true,
  checkStrictly: false,
  emitPath: true,
}

// 分类选项数据
const categoryOptions = ref([
  {
    value: 'ai',
    label: '人工智能',
    children: [
      { value: 'ai-basic', label: 'AI基础', count: 45 },
      { value: 'machine-learning', label: '机器学习', count: 32 },
      { value: 'deep-learning', label: '深度学习', count: 28 },
      { value: 'nlp', label: '自然语言处理', count: 25 },
      { value: 'computer-vision', label: '计算机视觉', count: 18 },
      { value: 'llm', label: '大语言模型', count: 35 },
    ],
  },
  {
    value: 'development',
    label: '开发技术',
    children: [
      { value: 'frontend', label: '前端开发', count: 42 },
      { value: 'backend', label: '后端开发', count: 38 },
      { value: 'mobile', label: '移动开发', count: 22 },
      { value: 'fullstack', label: '全栈开发', count: 15 },
      { value: 'devops', label: 'DevOps', count: 20 },
    ],
  },
  {
    value: 'database',
    label: '数据库',
    children: [
      { value: 'mysql', label: 'MySQL', count: 18 },
      { value: 'postgresql', label: 'PostgreSQL', count: 12 },
      { value: 'mongodb', label: 'MongoDB', count: 15 },
      { value: 'redis', label: 'Redis', count: 10 },
      { value: 'nosql', label: 'NoSQL', count: 8 },
    ],
  },
  {
    value: 'architecture',
    label: '架构设计',
    children: [
      { value: 'microservices', label: '微服务', count: 25 },
      { value: 'distributed', label: '分布式', count: 20 },
      { value: 'cloud-native', label: '云原生', count: 18 },
      { value: 'api-design', label: 'API设计', count: 12 },
    ],
  },
  {
    value: 'bigdata',
    label: '大数据',
    children: [
      { value: 'hadoop', label: 'Hadoop', count: 15 },
      { value: 'spark', label: 'Spark', count: 12 },
      { value: 'flink', label: 'Flink', count: 8 },
      { value: 'data-analysis', label: '数据分析', count: 20 },
    ],
  },
  {
    value: 'internet',
    label: '互联网',
    children: [
      { value: 'tech-news', label: '科技资讯', count: 30 },
      { value: 'startup', label: '创业公司', count: 18 },
      { value: 'product', label: '产品设计', count: 15 },
    ],
  },
  {
    value: 'blockchain',
    label: '区块链',
    children: [
      { value: 'bitcoin', label: '比特币', count: 8 },
      { value: 'ethereum', label: '以太坊', count: 10 },
      { value: 'smart-contract', label: '智能合约', count: 12 },
      { value: 'defi', label: 'DeFi', count: 6 },
    ],
  },
  {
    value: 'testing',
    label: '测试',
    children: [
      { value: 'unit-test', label: '单元测试', count: 15 },
      { value: 'integration-test', label: '集成测试', count: 12 },
      { value: 'automation-test', label: '自动化测试', count: 18 },
    ],
  },
  {
    value: 'network',
    label: '网络',
    children: [
      { value: 'network-security', label: '网络安全', count: 20 },
      { value: 'protocol', label: '网络协议', count: 15 },
      { value: 'cdn', label: 'CDN', count: 8 },
    ],
  },
  {
    value: 'game',
    label: '游戏开发',
    children: [
      { value: 'unity', label: 'Unity', count: 12 },
      { value: 'unreal', label: 'Unreal', count: 8 },
      { value: 'game-design', label: '游戏设计', count: 10 },
    ],
  },
])

// 获取分类图标
const getCategoryIcon = (value) => {
  const iconMap = {
    ai: 'fas fa-brain',
    development: 'fas fa-code',
    database: 'fas fa-database',
    architecture: 'fas fa-sitemap',
    bigdata: 'fas fa-chart-bar',
    internet: 'fas fa-globe',
    blockchain: 'fas fa-link',
    testing: 'fas fa-vial',
    network: 'fas fa-network-wired',
    game: 'fas fa-gamepad',
  }
  return iconMap[value] || 'fas fa-tag'
}

// 处理分类变化
const handleCategoryChange = (value) => {
  selectedCategories.value = value
  currentPage.value = 1
}

// 修改筛选逻辑以支持级联选择器
const applyAllFilters = () => {
  return rawNewsItems.value
    .filter((item) => {
      // 开源中国新闻直接保留
      if (item.source.startsWith('开源中国')) {
        return true
      }
      // 其他来源关键词过滤
      return keywords.some((k) => item.title.includes(k) || item.description?.includes(k))
    })
    .filter((item) => {
      // 如果没有选择分类，显示所有
      if (!selectedCategories.value || selectedCategories.value.length === 0) {
        return true
      }

      // 检查是否匹配选中的分类
      return selectedCategories.value.some((categoryPath) => {
        const categoryValue = Array.isArray(categoryPath)
          ? categoryPath[categoryPath.length - 1]
          : categoryPath
        return item.title.includes(categoryValue) || item.description?.includes(categoryValue)
      })
    })
}

// 修改重置筛选函数
const resetFilters = () => {
  selectedCategories.value = []
  currentPage.value = 1
}

// 监听分类变化
watch(selectedCategories, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    currentPage.value = 1
  }
})

// 组件挂载时获取新闻
onMounted(() => {
  fetchNews()

  // 初始检查系统主题
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    darkMode.value = true
    document.documentElement.classList.add('dark')
  }

  // 设置定时刷新（每10分钟）
  setInterval(
    () => {
      if (!document.hidden) {
        refreshFeed()
      }
    },
    10 * 60 * 1000,
  )
})
</script>

<style>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<style scoped>
::v-deep .el-input__wrapper {
  background-color: transparent !important;
}
</style>
