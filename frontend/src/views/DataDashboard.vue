<template>
  <div
    class="data-dashboard relative min-h-screen p-4 md:p-8 font-sans overflow-x-hidden text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-950 transition-colors duration-300"
  >
    <div class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between mb-6">
      <div>
        <h1
          class="m-0 text-2xl md:text-3xl font-semibold text-slate-950 dark:text-white tracking-normal"
        >
          {{ appStore.appName }}系统数据看板
        </h1>
        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
          汇总面试表现、岗位分布与人才地域数据，辅助管理员快速判断训练情况。
        </p>
      </div>
    </div>

    <div
      class="flex flex-wrap items-center gap-4 mb-6 p-4 md:px-5 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 shadow-sm"
    >
      <div class="w-full md:w-[280px]">
        <el-input
          v-model="searchUsername"
          placeholder="按用户名搜索..."
          class="tech-input-search w-full"
          @keyup.enter="handleSearchUser"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearchUser" :loading="isSearching" />
          </template>
        </el-input>
      </div>
      <div class="w-full md:w-[280px]">
        <el-select
          v-model="selectedUserId"
          placeholder="跳转至用户详情"
          @change="handleUserChange"
          class="user-select w-full md:w-[240px]"
          popper-class="glass-popper dark:glass-popper-dark"
        >
          <template #prefix>
            <el-icon class="text-slate-400 text-lg ml-0.5"><User /></el-icon>
          </template>
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="user.name"
            :value="user.id"
          ></el-option>
        </el-select>
      </div>
      <span
        v-if="isLoadingUsers || isLoadingInterviews"
        class="ml-auto text-sm font-medium text-slate-500 dark:text-slate-400 flex items-center gap-2"
        >数据加载中...</span
      >
      <span v-if="loadError" class="ml-auto text-sm font-medium text-red-500">{{ loadError }}</span>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
      <div v-for="item in overviewCards" :key="item.label" class="metric-card">
        <span class="metric-label">{{ item.label }}</span>
        <strong class="metric-value">{{ item.value }}</strong>
        <span class="metric-note">{{ item.note }}</span>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 max-w-full">
      <div class="dashboard-card">
        <h2 class="dashboard-card-title">面试分数汇总</h2>
        <div class="w-full h-[320px] relative z-10">
          <v-chart :option="scoreDistributionOption" autoresize />
        </div>
      </div>

      <div class="dashboard-card">
        <h2 class="dashboard-card-title">面试领域分布</h2>
        <div class="w-full h-[320px] relative z-10">
          <v-chart :option="domainDistributionOption" autoresize />
        </div>
      </div>

      <div class="dashboard-card">
        <h2 class="dashboard-card-title">岗位类型占比</h2>
        <div class="w-full h-[320px] relative z-10">
          <v-chart :option="positionDistributionOption" autoresize />
        </div>
      </div>

      <div class="dashboard-card">
        <h2 class="dashboard-card-title">人才地域分布</h2>
        <div class="w-full h-[320px] relative z-10">
          <v-chart v-if="isMapLoaded" :option="mapDistributionOption" autoresize />
          <div
            v-else
            class="w-full h-full flex flex-col justify-center items-center text-slate-400 dark:text-slate-500 gap-3 uppercase tracking-widest text-xs"
          >
            <el-icon class="is-loading text-2xl"><Loading /></el-icon>
            <span>地图数据加载中...</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAppStore } from '@/store/app'
import { getApiUrl } from '@/config/api'
import { defineComponent, reactive, toRefs, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import {
  BarChart,
  LineChart,
  PieChart,
  RadarChart,
  MapChart,
  EffectScatterChart,
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  PolarComponent,
  RadarComponent,
  SingleAxisComponent,
  AxisPointerComponent,
  GeoComponent,
  VisualMapComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { Loading, Search, User, Sunny, Moon } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useDark, useToggle } from '@vueuse/core'
import 'element-plus/theme-chalk/dark/css-vars.css'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  PolarComponent,
  RadarComponent,
  SingleAxisComponent,
  AxisPointerComponent,
  GeoComponent,
  VisualMapComponent,
  BarChart,
  LineChart,
  PieChart,
  RadarChart,
  MapChart,
  EffectScatterChart,
  CanvasRenderer,
])

export default defineComponent({
  name: 'InterviewDashboard',
  components: { VChart, Loading, Sunny, Moon },
  setup() {
    const appStore = useAppStore()
    const router = useRouter()

    const DASHBOARD_API_URL = getApiUrl('/admin/dashboard/interviews')
    const IP_API_URL = getApiUrl('/ip')

    const state = reactive({
      users: [],
      selectedUserId: null,
      allInterviews: [],
      isMapLoaded: false,
      isLoadingUsers: false,
      isLoadingInterviews: false,
      loadError: '',
      ipProvince: '',
      searchUsername: '',
      isSearching: false,
    })

    const getAuthHeader = () => {
      const token =
        localStorage.getItem('admin_access_token') || localStorage.getItem('access_token') || ''
      return token ? { Authorization: `Bearer ${token}` } : {}
    }

    const inferProvinceFromText = (rawText) => {
      const text = String(rawText || '')
      if (!text) return ''
      const provinceRegex =
        /(北京|上海|天津|重庆|河北|山西|辽宁|吉林|黑龙江|江苏|浙江|安徽|福建|江西|山东|河南|湖北|湖南|广东|海南|四川|贵州|云南|陕西|甘肃|青海|台湾|内蒙古|广西|西藏|宁夏|新疆|香港|澳门)(省|市|自治区|特别行政区)?/
      const match = text.match(provinceRegex)
      return match?.[1] || ''
    }

    const isDarkMode = useDark()
    const toggleDarkMode = useToggle(isDarkMode)

    const inferProvinceFromUser = (item) => {
      const schoolText = item?.school || item?.university || ''
      if (schoolText) {
        const province = inferProvinceFromText(schoolText)
        if (province) return province
      }
      return state.ipProvince || ''
    }

    const fetchCurrentIpProvince = async () => {
      try {
        const response = await axios.get(IP_API_URL, { headers: getAuthHeader() })
        const payload = response?.data || {}
        const textSource = [
          payload?.province,
          payload?.city,
          payload?.address,
          payload?.region,
          payload?.region_name,
          payload?.location,
          payload?.ip_location,
          payload?.data?.province,
          payload?.data?.city,
          payload?.data?.address,
        ]
          .filter(Boolean)
          .join(' ')
        let province = inferProvinceFromText(textSource)
        if (!province) {
          const ip = payload.ip || payload.client_ip
          let queryUrl = 'http://ip-api.com/json/?lang=zh-CN'
          if (
            ip &&
            ip !== '127.0.0.1' &&
            ip !== 'localhost' &&
            !ip.startsWith('192.168.') &&
            !ip.startsWith('10.')
          ) {
            queryUrl = `http://ip-api.com/json/${ip}?lang=zh-CN`
          }
          try {
            const geoRes = await axios.get(queryUrl)
            const geoData = geoRes.data || {}
            if (geoData.status === 'success') {
              province = inferProvinceFromText(`${geoData.regionName} ${geoData.city}`)
            }
          } catch (externErr) {}
        }
        state.ipProvince = province
      } catch (error) {
        state.ipProvince = ''
      }
    }

    const fetchDashboardData = async () => {
      state.isLoadingUsers = true
      state.isLoadingInterviews = true
      state.loadError = ''
      try {
        await fetchCurrentIpProvince()
        const response = await axios.get(DASHBOARD_API_URL, { headers: getAuthHeader() })
        if (response.data?.code === 200) {
          const data = response.data.data
          state.users = (data?.users || []).map((u) => ({
            ...u,
            province: inferProvinceFromUser(u),
          }))
          state.allInterviews = data?.interviews || []

          if (!state.users.length && !state.allInterviews.length) {
            state.loadError = '数据接口返回为空，请检查管理员接口数据。'
          }
        } else {
          state.loadError = response.data?.message || '获取数据失败'
        }
      } catch (error) {
        state.loadError = '获取大屏数据失败，请检查管理员登录状态或接口可用性。'
      } finally {
        state.isLoadingUsers = false
        state.isLoadingInterviews = false
      }
    }

    const loadChinaMap = () => {
      fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
        .then((res) => res.json())
        .then((data) => {
          echarts.registerMap('china', data)
          state.isMapLoaded = true
        })
        .catch((err) => console.error('Failed to load map data:', err))
    }

    onMounted(async () => {
      loadChinaMap()
      await fetchDashboardData()
    })

    const handleUserChange = (userId) => {
      if (userId) router.push({ name: 'AdminDashboardUser', params: { userId: String(userId) } })
    }

    const handleSearchUser = async () => {
      if (!state.searchUsername.trim()) {
        ElMessage.warning('请输入用户名')
        return
      }
      state.isSearching = true
      try {
        const response = await axios.get(
          getApiUrl(`/admin/users/by-username/${encodeURIComponent(state.searchUsername)}`),
          { headers: getAuthHeader() },
        )
        if (response.data?.code === 200 && response.data.data) {
          const user = response.data.data
          const userId = user.id || user.user_id || user.uid
          if (userId) {
            ElMessage.success('找到用户，正在跳转...')
            handleUserChange(userId)
          } else {
            ElMessage.warning('未找到有效的用户ID')
          }
        } else {
          ElMessage.warning(response.data.message || '未找到该用户')
        }
      } catch (error) {
        if (error.response?.status === 404) ElMessage.warning('用户不存在')
        else ElMessage.error(error.message || '搜索失败')
      } finally {
        state.isSearching = false
      }
    }

    const getStableOffset = (text, amplitude = 1.2) => {
      let hash = 0
      for (let i = 0; i < String(text || '').length; i++)
        hash = (hash * 31 + String(text || '').charCodeAt(i)) % 100000
      return ((hash % 1000) / 1000 - 0.5) * amplitude
    }

    const getTooltipTheme = () =>
      isDarkMode.value
        ? {
            backgroundColor: 'rgba(30, 41, 59, 0.95)',
            borderColor: '#334155',
            textStyle: { color: '#f8fafc' },
          }
        : {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e2e8f0',
            textStyle: { color: '#334155' },
          }

    const overviewCards = computed(() => {
      const interviewCount = state.allInterviews.length
      const scoredInterviews = state.allInterviews.filter((item) =>
        Number.isFinite(Number(item.totalScore)),
      )
      const averageScore = scoredInterviews.length
        ? Math.round(
            scoredInterviews.reduce((sum, item) => sum + Number(item.totalScore || 0), 0) /
              scoredInterviews.length,
          )
        : 0
      const domainMap = {}
      state.allInterviews.forEach((item) => {
        if (item.domain) domainMap[item.domain] = (domainMap[item.domain] || 0) + 1
      })
      const topDomain = Object.entries(domainMap).sort((a, b) => b[1] - a[1])?.[0]?.[0] || '暂无'

      return [
        { label: '用户总数', value: state.users.length, note: '已纳入统计的用户' },
        { label: '面试记录', value: interviewCount, note: '累计训练与评测次数' },
        { label: '平均分', value: scoredInterviews.length ? `${averageScore} 分` : '暂无', note: '按有效总分计算' },
        { label: '主要领域', value: topDomain, note: '出现频次最高的方向' },
      ]
    })

    const mapDistributionOption = computed(() => {
      const provinceCounts = {}
      state.users.forEach((user) => {
        if (user.province) provinceCounts[user.province] = (provinceCounts[user.province] || 0) + 1
      })
      const mapData = Object.keys(provinceCounts).map((prov) => ({
        name: prov,
        value: provinceCounts[prov],
      }))
      return {
        tooltip: {
          trigger: 'item',
          ...getTooltipTheme(),
          extraCssText: 'box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08); border-radius: 8px;',
        },
        geo: {
          map: 'china',
          roam: true,
          zoom: 1.2,
          label: { show: true, color: isDarkMode.value ? '#94a3b8' : '#64748b', fontSize: 10 },
          itemStyle: {
            areaColor: isDarkMode.value ? '#1f2937' : '#f8fafc',
            borderColor: isDarkMode.value ? '#334155' : '#cbd5e1',
            borderWidth: 1,
          },
          emphasis: {
            itemStyle: { areaColor: isDarkMode.value ? '#334155' : '#e0f2fe' },
            label: { show: true, color: isDarkMode.value ? '#f8fafc' : '#334155' },
          },
        },
        series: [
          {
            name: '用户分布热力',
            type: 'map',
            geoIndex: 0,
            data: mapData,
          },
        ],
      }
    })

    const scoreDistributionOption = computed(() => {
      const rangeCounts = [0, 0, 0, 0]
      state.allInterviews.forEach((i) => {
        if (i.totalScore >= 60 && i.totalScore < 70) rangeCounts[0]++
        else if (i.totalScore >= 70 && i.totalScore < 80) rangeCounts[1]++
        else if (i.totalScore >= 80 && i.totalScore < 90) rangeCounts[2]++
        else if (i.totalScore >= 90) rangeCounts[3]++
      })
      return {
        tooltip: {
          trigger: 'item',
          ...getTooltipTheme(),
          extraCssText: 'box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08); border-radius: 8px;',
        },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: [
          {
            type: 'category',
            data: ['60-69', '70-79', '80-89', '90-100'],
            axisTick: { show: false },
            axisLine: { show: false },
            axisLabel: { color: isDarkMode.value ? '#94a3b8' : '#64748b' },
          },
        ],
        yAxis: [
          {
            type: 'value',
            name: '面试数量',
            nameTextStyle: { color: isDarkMode.value ? '#64748b' : '#94a3b8' },
            splitLine: {
              lineStyle: { type: 'dashed', color: isDarkMode.value ? '#334155' : '#f1f5f9' },
            },
            axisLabel: { color: isDarkMode.value ? '#94a3b8' : '#94a3b8' },
          },
        ],
        series: [
          {
            type: 'bar',
            barWidth: '40%',
            data: rangeCounts,
            itemStyle: {
              borderRadius: [6, 6, 0, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#2563eb' },
                { offset: 1, color: '#93c5fd' },
              ]),
            },
            showBackground: true,
            backgroundStyle: {
              color: isDarkMode.value ? '#1e293b' : '#f8fafc',
              borderRadius: [6, 6, 0, 0],
            },
          },
        ],
      }
    })

    const domainDistributionOption = computed(() => {
      const domainMap = {}
      state.allInterviews.forEach((i) => {
        domainMap[i.domain] = (domainMap[i.domain] || 0) + 1
      })
      const domains = Object.keys(domainMap)
      const counts = domains.map((d) => domainMap[d])
      const colors = ['#2563eb', '#0891b2', '#16a34a', '#d97706', '#475569', '#7c3aed', '#dc2626']
      return {
        tooltip: {
          trigger: 'item',
          ...getTooltipTheme(),
          extraCssText: 'box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08); border-radius: 8px;',
        },
        legend: {
          orient: 'vertical',
          right: 20,
          top: 'center',
          textStyle: { color: isDarkMode.value ? '#94a3b8' : '#64748b' },
          icon: 'circle',
        },
        series: [
          {
            type: 'pie',
            radius: ['50%', '75%'],
            center: ['40%', '50%'],
            itemStyle: {
              borderRadius: 8,
              borderColor: isDarkMode.value ? '#1e293b' : '#fff',
              borderWidth: 3,
            },
            label: { show: false },
            emphasis: {
              label: {
                show: true,
                fontSize: 18,
                fontWeight: 'bold',
                color: isDarkMode.value ? '#f8fafc' : '#334155',
              },
            },
            data: domains.map((d, i) => ({
              name: d,
              value: counts[i],
              itemStyle: { color: colors[i % colors.length] },
            })),
          },
        ],
      }
    })

    const positionDistributionOption = computed(() => {
      const positionMap = {}
      state.allInterviews.forEach((i) => {
        positionMap[i.position] = (positionMap[i.position] || 0) + 1
      })
      const sorted = Object.entries(positionMap)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
      return {
        tooltip: {
          trigger: 'item',
          ...getTooltipTheme(),
          extraCssText: 'box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08); border-radius: 8px;',
        },
        grid: { left: '3%', right: '8%', bottom: '3%', top: '3%', containLabel: true },
        xAxis: {
          type: 'value',
          splitLine: { show: false },
          axisLabel: { show: false },
          axisLine: { show: false },
        },
        yAxis: {
          type: 'category',
          data: sorted.map((s) => s[0]),
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: {
            color: isDarkMode.value ? '#cbd5e1' : '#475569',
            fontWeight: 500,
            fontSize: 13,
            width: 90,
            overflow: 'truncate',
          },
          inverse: true,
        },
        series: [
          {
            type: 'bar',
            data: sorted.map((s) => s[1]),
            barWidth: 16,
            itemStyle: {
              borderRadius: [0, 8, 8, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#0f766e' },
                { offset: 1, color: '#5eead4' },
              ]),
            },
            showBackground: true,
            backgroundStyle: {
              color: isDarkMode.value ? '#1e293b' : '#f8fafc',
              borderRadius: [0, 8, 8, 0],
            },
            label: {
              show: true,
              position: 'right',
              color: isDarkMode.value ? '#94a3b8' : '#64748b',
              fontWeight: 'bold',
            },
          },
        ],
      }
    })

    return {
      appStore,
      ...toRefs(state),
      handleUserChange,
      handleSearchUser,
      Search,
      User,
      Sunny,
      Moon,
      overviewCards,
      scoreDistributionOption,
      domainDistributionOption,
      positionDistributionOption,
      mapDistributionOption,
      isDarkMode,
      toggleDarkMode,
    }
  },
})
</script>

<style scoped>
@reference "@/assets/main.css";
.data-dashboard {
  letter-spacing: 0;
}

.metric-card,
.dashboard-card {
  @apply bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm;
}

.metric-card {
  @apply rounded-lg px-5 py-4 flex flex-col gap-1;
}

.metric-label {
  @apply text-xs font-medium text-slate-500 dark:text-slate-400;
}

.metric-value {
  @apply text-2xl font-semibold text-slate-950 dark:text-white leading-tight truncate;
}

.metric-note {
  @apply text-xs text-slate-400 dark:text-slate-500 truncate;
}

.dashboard-card {
  @apply relative rounded-lg p-5 overflow-hidden;
}

.dashboard-card-title {
  @apply m-0 mb-5 text-base font-semibold text-slate-900 dark:text-white tracking-normal flex items-center;
}

.dashboard-card-title::before {
  content: '';
  @apply block w-1 h-5 rounded-full bg-blue-600 mr-3;
}

.tech-input-search :deep(.el-input__wrapper),
.user-select :deep(.el-input__wrapper) {
  @apply bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 shadow-none rounded-lg px-4 py-1.5 transition-colors duration-200;
  clip-path: none !important;
}

.tech-input-search :deep(.el-input__wrapper:hover),
.user-select :deep(.el-input__wrapper:hover) {
  @apply border-slate-300 dark:border-slate-600;
}

.tech-input-search :deep(.el-input__wrapper.is-focus),
.user-select :deep(.el-input__wrapper.is-focus) {
  @apply border-blue-500 dark:border-blue-400 ring-2 ring-blue-500/10 dark:ring-blue-400/10;
}

.tech-input-search :deep(.el-input-group__append) {
  @apply bg-blue-600 border-none rounded-r-lg overflow-hidden shadow-none p-0;
}

.tech-input-search :deep(.el-input-group__append .el-button) {
  @apply text-white border-none rounded-none px-5 py-3 h-full m-0 transition-colors duration-200 hover:bg-blue-700 active:bg-blue-800;
}

.user-select :deep(.el-input__inner),
.tech-input-search :deep(.el-input__inner) {
  @apply font-medium text-slate-700 dark:text-slate-200 h-9 bg-transparent focus:outline-hidden;
}
</style>

<style>
@reference "@/assets/main.css";
/* 全局 Popper 样式 */
.glass-popper.el-popper {
  @apply bg-white border border-slate-200 shadow-lg rounded-lg p-1.5;
}

html.dark .glass-popper-dark.el-popper {
  @apply bg-slate-900 border-slate-700 shadow-2xl;
}

.glass-popper .el-select-dropdown__item {
  @apply rounded-md my-1 h-10 leading-10 text-slate-600 font-medium transition-colors duration-200;
}

html.dark .glass-popper-dark .el-select-dropdown__item {
  @apply text-slate-300;
}

.glass-popper .el-select-dropdown__item.hover,
.glass-popper .el-select-dropdown__item:hover {
  @apply bg-slate-100 text-slate-900;
}

html.dark .glass-popper-dark .el-select-dropdown__item.hover,
html.dark .glass-popper-dark .el-select-dropdown__item:hover {
  @apply bg-slate-800 text-white;
}

.glass-popper .el-select-dropdown__item.selected {
  @apply bg-blue-600 text-white font-semibold shadow-none;
}

.glass-popper .el-popper__arrow::before {
  @apply bg-white border border-slate-200;
}

html.dark .glass-popper-dark .el-popper__arrow::before {
  @apply bg-slate-900 border-slate-700;
}

.glass-popper .el-select-dropdown__wrap::-webkit-scrollbar {
  width: 6px;
}
.glass-popper .el-select-dropdown__wrap::-webkit-scrollbar-thumb {
  @apply bg-slate-400/30 rounded-full;
}
.glass-popper .el-select-dropdown__wrap::-webkit-scrollbar-track {
  background: transparent;
}
</style>
