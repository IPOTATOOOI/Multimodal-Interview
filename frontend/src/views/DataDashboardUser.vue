<template>
  <div
    class="p-8 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-700 dark:text-slate-300 relative overflow-x-hidden font-sans bg-tech-pattern transition-colors duration-300"
  >
    <div class="flex items-center mb-6">
      <el-button
        @click="goBack"
        :icon="ArrowLeft"
        circle
        class="mr-4 dark:!bg-slate-800 dark:!border-slate-700 dark:!text-slate-300"
      />
      <div>
        <h1
          class="text-left mb-2 text-4xl font-extrabold tracking-tight flex items-center gap-4 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent drop-shadow-sm"
        >
          {{ userInfo ? `${userInfo.name} 的面试数据` : '加载中...' }}
        </h1>
        <p
          class="text-left text-slate-500 dark:text-slate-400 mb-3 text-sm ml-1 flex items-center gap-2 before:content-[''] before:block before:w-5 before:h-0.5 before:bg-slate-300 dark:before:bg-slate-600"
        >
          <span v-if="userInfo">{{ userInfo.school }} · {{ userInfo.province }}</span>
        </p>
      </div>
    </div>

    <div class="mb-4">
      <span v-if="isLoading" class="text-blue-500 dark:text-blue-400 text-sm">数据加载中...</span>
      <span v-if="errorMsg" class="text-red-500 dark:text-red-400 text-sm">{{ errorMsg }}</span>
    </div>

    <div v-if="userInfo" class="grid gap-6">
      <div
        class="bg-white/80 dark:bg-slate-800/80 rounded-2xl p-6 shadow-sm mb-6 backdrop-blur-md border border-white/60 dark:border-slate-700/60 transition-colors duration-300"
      >
        <div class="flex gap-6 mb-6 text-base font-semibold text-slate-600 dark:text-slate-300">
          <span>历史记录数：{{ historyList.length }}</span>
          <span>平均分：{{ averageScore }}</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-6 mb-6">
          <div class="flex flex-col">
            <h3 class="flex items-center gap-2 mb-4 pl-2">
              <span
                class="w-1 h-[18px] rounded-sm bg-gradient-to-b from-indigo-500 to-purple-500"
              ></span>
              <span class="text-lg font-bold text-slate-800 dark:text-slate-100 tracking-wide"
                >各次面试分数趋势</span
              >
            </h3>
            <div class="h-[300px] w-full">
              <v-chart v-if="historyList.length" :option="scoreTrendOption" autoresize />
              <el-empty v-else description="暂无数据" :image-size="60"></el-empty>
            </div>
          </div>

          <div class="flex flex-col">
            <h3 class="flex items-center gap-2 mb-4 pl-2">
              <span
                class="w-1 h-[18px] rounded-sm bg-gradient-to-b from-pink-500 to-rose-500"
              ></span>
              <span class="text-lg font-bold text-slate-800 dark:text-slate-100 tracking-wide"
                >最近面试各维度得分</span
              >
            </h3>
            <div class="h-[300px] w-full">
              <v-chart v-if="historyList.length" :option="dimensionScoresOption" autoresize />
              <el-empty v-else description="暂无数据" :image-size="60"></el-empty>
            </div>
          </div>

          <div class="col-span-1 lg:col-span-full mt-6">
            <h3 class="flex items-center gap-2 mb-4 pl-2">
              <span
                class="w-1 h-[18px] rounded-sm bg-gradient-to-b from-emerald-500 to-teal-500"
              ></span>
              <span class="text-lg font-bold text-slate-800 dark:text-slate-100 tracking-wide"
                >历史记录（点击查看详情）</span
              >
            </h3>

            <div
              v-if="historyList.length"
              class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-4"
            >
              <div
                v-for="item in historyList"
                :key="item.id"
                class="group relative flex justify-between items-center bg-white/70 dark:bg-slate-800/70 backdrop-blur-md border border-slate-200/80 dark:border-slate-700/80 rounded-2xl p-4 cursor-pointer transition-all duration-300 ease-out overflow-hidden hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-500/10 dark:hover:shadow-blue-900/20 hover:bg-white/95 dark:hover:bg-slate-700/95 hover:border-blue-200 dark:hover:border-blue-700 before:absolute before:top-0 before:left-0 before:w-1 before:h-full before:bg-gradient-to-b before:from-blue-100 before:to-blue-50 dark:before:from-blue-900 dark:before:to-slate-800 before:transition-colors before:duration-300 hover:before:from-blue-500 hover:before:to-blue-400"
                @click="openHistoryDetail(item)"
              >
                <div class="flex-1 flex flex-col gap-2 z-10 text-left pl-2">
                  <div
                    class="font-bold text-base text-slate-800 dark:text-slate-100 flex items-center gap-2"
                  >
                    <el-icon class="text-amber-500"><Trophy /></el-icon>
                    <span>{{ item.position }}</span>
                  </div>
                  <div class="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
                    <span
                      class="bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded font-semibold text-slate-500 dark:text-slate-300"
                      >{{ item.domain }}</span
                    >
                    <el-icon><Clock /></el-icon>
                    <span>{{ item.date || '未知日期' }}</span>
                  </div>
                </div>

                <div
                  class="flex flex-col items-center justify-center bg-gradient-to-br from-sky-50 to-sky-100 dark:from-sky-900/30 dark:to-sky-800/30 rounded-xl py-2 px-3 min-w-[60px] shadow-[inset_0_2px_4px_rgba(255,255,255,0.8)] dark:shadow-[inset_0_2px_4px_rgba(255,255,255,0.05)] border border-sky-200 dark:border-sky-800/50 mr-3"
                >
                  <div
                    class="font-[DIN_Alternate,Inter,sans-serif] text-2xl font-extrabold text-sky-600 dark:text-sky-400 leading-none"
                  >
                    {{ item.totalScore }}
                  </div>
                  <div class="text-[10px] text-sky-500 dark:text-sky-400 font-semibold mt-0.5">
                    总得分
                  </div>
                </div>

                <el-icon
                  class="text-slate-300 dark:text-slate-500 transition-transform duration-300 shrink-0 group-hover:text-blue-500 dark:group-hover:text-blue-400 group-hover:translate-x-1"
                  :size="20"
                  ><ArrowRight
                /></el-icon>
              </div>
            </div>
            <el-empty v-else description="该用户暂无历史记录" :image-size="80"></el-empty>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// (保持原有的 imports 不变)
import { defineComponent, reactive, toRefs, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  PolarComponent,
  RadarComponent,
  SingleAxisComponent,
  AxisPointerComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ArrowLeft, ArrowRight, Clock, Trophy } from '@element-plus/icons-vue'
import { getApiUrl } from '@/config/api'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  PolarComponent,
  RadarComponent,
  SingleAxisComponent,
  AxisPointerComponent,
  BarChart,
  LineChart,
  RadarChart,
  CanvasRenderer,
])

export default defineComponent({
  name: 'DataDashboardUser',
  components: { VChart, ArrowRight, Clock, Trophy },
  setup() {
    const route = useRoute()
    const router = useRouter()

    const USERS_API_URL = getApiUrl('/admin/users')
    const getHistoryByUserApi = (uid) => getApiUrl(`/history/user/${uid}`)

    const state = reactive({
      userInfo: null,
      interviews: [],
      isLoading: false,
      errorMsg: '',
    })

    const getAuthHeader = () => {
      const token =
        localStorage.getItem('admin_access_token') || localStorage.getItem('access_token') || ''
      return token ? { Authorization: `Bearer ${token}` } : {}
    }

    const resolveUserList = (responseData) => {
      const data = responseData?.data
      if (Array.isArray(data)) return data
      if (Array.isArray(data?.list)) return data.list
      if (Array.isArray(data?.users)) return data.users
      if (Array.isArray(data?.items)) return data.items
      if (Array.isArray(responseData?.list)) return responseData.list
      if (Array.isArray(responseData?.users)) return responseData.users
      return []
    }

    const normalizeUsers = (list) => {
      return list
        .map((item) => {
          const id = item?.id ?? item?.user_id ?? item?.uid
          if (id === undefined || id === null || id === '') return null
          return {
            id: String(id),
            name: item?.username ?? item?.name ?? item?.nickname ?? `用户${id}`,
            school: item?.school ?? item?.university ?? '-',
            province: item?.province || item?.prov || item?.city || item?.address || '未知地区',
          }
        })
        .filter(Boolean)
    }

    const normalizeHistory = (history, user) => {
      const parseDate = (raw) => {
        if (!raw) return null
        const normalized = String(raw).replace(' ', 'T')
        const date = new Date(normalized)
        return Number.isNaN(date.getTime()) ? null : date
      }

      const interviewTime = history?.interview_time || history?.date || history?.created_at || ''
      const parsedInterviewTime = parseDate(interviewTime)
      const scoreFields = [
        ['专业知识', history?.professional_knowledge],
        ['技能匹配', history?.skill_match],
        ['语言表达', history?.language_expression],
        ['逻辑思维', history?.logical_thinking],
        ['创新能力', history?.innovation_ability],
        ['抗压能力', history?.stress_resistance],
      ]
      const dimensionScores = scoreFields.map(([name, value]) => ({
        name,
        score: Math.round((Number(value) || 0) * 20),
      }))

      const historyId =
        history?.history_id ??
        history?.historyId ??
        history?.interview_history_id ??
        history?.hid ??
        history?.id ??
        null

      return {
        id: String(historyId ?? `${user.id}-${interviewTime}`),
        historyId,
        userId: user.id,
        userName: user.name,
        domain: history?.field ?? history?.domain ?? '未知领域',
        position: history?.position ?? '未知岗位',
        date: parsedInterviewTime
          ? parsedInterviewTime.toISOString().split('T')[0]
          : interviewTime
            ? String(interviewTime).slice(0, 10)
            : '',
        interviewTime,
        interviewTimestamp: parsedInterviewTime?.getTime() || 0,
        totalScore: Number(history?.score ?? 0),
        dimensionScores,
        raw: history,
      }
    }

    const fetchData = async () => {
      const userId = route.params.userId
      if (!userId) return

      state.isLoading = true
      state.errorMsg = ''
      try {
        const usersAppResponse = await axios.get(USERS_API_URL, { headers: getAuthHeader() })
        const userList = normalizeUsers(resolveUserList(usersAppResponse.data))
        const targetUser = userList.find((u) => u.id === String(userId))

        if (targetUser) {
          state.userInfo = targetUser
        } else {
          state.userInfo = { id: userId, name: `用户${userId}`, school: '未知', province: '未知' }
        }

        const historyResponse = await axios.get(getHistoryByUserApi(userId), {
          headers: getAuthHeader(),
        })
        const list =
          historyResponse?.data?.history_list || historyResponse?.data?.data?.history_list || []
        state.interviews = list
          .map((h) => normalizeHistory(h, state.userInfo))
          .sort((a, b) => (b.interviewTimestamp || 0) - (a.interviewTimestamp || 0))
      } catch (err) {
        console.error(err)
        state.errorMsg = '获取数据失败'
      } finally {
        state.isLoading = false
      }
    }

    onMounted(() => fetchData())

    watch(
      () => route.params.userId,
      (newId) => {
        if (newId) fetchData()
      },
    )

    const goBack = () => router.push({ name: 'AdminDashboard' })

    const openHistoryDetail = (item) => {
      const historyId = item?.historyId
      if (!historyId) return
      router.push({ name: 'AdminHistoryDetail', params: { history_id: historyId } })
    }

    const historyList = computed(() => state.interviews)

    const averageScore = computed(() => {
      if (!state.interviews.length) return 0
      const total = state.interviews.reduce((sum, item) => sum + (Number(item.totalScore) || 0), 0)
      return Math.round(total / state.interviews.length)
    })

    const scoreTrendOption = computed(() => {
      if (!state.interviews.length) return {}
      const sortedInterviews = [...state.interviews].sort(
        (a, b) => (a.interviewTimestamp || 0) - (b.interviewTimestamp || 0),
      )
      const dates = sortedInterviews.map((interview, index) => interview.date || `第${index + 1}次`)
      const scores = sortedInterviews.map((interview) => interview.totalScore)
      const positions = sortedInterviews.map((interview) => interview.position)

      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'line',
            lineStyle: { color: 'rgba(148, 163, 184, 0.5)', width: 1, type: 'dashed' },
          },
          // 移除硬编码的纯白色背景，使用半透明以兼容暗黑模式
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          textStyle: { color: '#334155' },
          extraCssText:
            'box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 8px; backdrop-filter: blur(4px);',
          formatter: (params) => {
            const index = params[0].dataIndex
            return `
                    <div style="font-weight: 600; margin-bottom: 4px;">${dates[index]}</div>
                    <div style="color: #64748b; font-size: 12px; margin-bottom: 2px;">岗位: ${positions[index]}</div>
                    <div style="color: #ec4899; font-weight: bold;">分数: ${scores[index]}</div>
                    `
          },
        },
        grid: { left: '2%', right: '5%', bottom: '10%', top: '15%', containLabel: true },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates,
          axisLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.3)' } },
          axisLabel: { color: '#64748b' },
          axisTick: { show: false },
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
          splitLine: { lineStyle: { type: 'dashed', color: 'rgba(148, 163, 184, 0.2)' } },
          axisLabel: { color: '#94a3b8' },
        },
        series: [
          {
            name: '面试分数',
            type: 'line',
            data: scores,
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: { color: '#ec4899', borderWidth: 2, borderColor: '#ffffff' },
            lineStyle: { width: 4, color: '#ec4899' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(236, 72, 153, 0.2)' },
                { offset: 1, color: 'rgba(236, 72, 153, 0.0)' },
              ]),
            },
          },
        ],
      }
    })

    const dimensionScoresOption = computed(() => {
      if (!state.interviews.length) return {}
      const latestInterview = state.interviews[0]
      const dimensions = latestInterview.dimensionScores.map((item) => item.name)
      const scores = latestInterview.dimensionScores.map((item) => item.score)

      return {
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          textStyle: { color: '#334155' },
          extraCssText: 'backdrop-filter: blur(4px);',
        },
        radar: {
          indicator: dimensions.map((dim) => ({ name: dim, max: 100 })),
          center: ['50%', '50%'],
          // 配合暗黑模式，使用半透明替代纯色
          splitArea: {
            areaStyle: { color: ['rgba(148, 163, 184, 0.05)', 'rgba(255, 255, 255, 0)'] },
          },
          splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.2)' } },
          axisLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.2)' } },
        },
        series: [
          {
            type: 'radar',
            data: [
              {
                value: scores,
                name: '得分',
                itemStyle: { color: '#3b82f6' },
                areaStyle: { color: 'rgba(59, 130, 246, 0.2)' },
              },
            ],
          },
        ],
      }
    })

    return {
      ...toRefs(state),
      historyList,
      averageScore,
      scoreTrendOption,
      dimensionScoresOption,
      goBack,
      openHistoryDetail,
      ArrowLeft,
      ArrowRight,
      Clock,
      Trophy,
    }
  },
})
</script>

<style scoped>
/* 由于背景结构过于复杂（多层渐变），保留在 CSS 中维持代码可读性，并注入暗黑模式变量 */
.bg-tech-pattern {
  background-image: linear-gradient(rgba(99, 102, 241, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.025) 1px, transparent 1px),
    radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.05), transparent 40%),
    radial-gradient(circle at 100% 100%, rgba(236, 72, 153, 0.05), transparent 40%);
  background-size:
    40px 40px,
    40px 40px,
    100% 100%,
    100% 100%;
}

/* 适配暗黑模式的背景色 */
:global(.dark) .bg-tech-pattern {
  background-image: linear-gradient(rgba(99, 102, 241, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.05) 1px, transparent 1px),
    radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.1), transparent 40%),
    radial-gradient(circle at 100% 100%, rgba(236, 72, 153, 0.1), transparent 40%);
}

/* 顶部滑动渐变装饰线 */
.dashboard-top-border::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #ec4899, #6366f1);
  background-size: 200% 100%;
  animation: bgSlide 4s linear infinite;
  z-index: 10;
}

@keyframes bgSlide {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 200% 0%;
  }
}

/* 用来修正父级渐变字体引起的子元素透明化问题 */
.text-fill-initial {
  -webkit-text-fill-color: initial;
}
</style>
