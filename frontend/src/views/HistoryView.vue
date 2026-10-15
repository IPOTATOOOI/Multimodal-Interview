<template>
  <div class="p-2 max-w-6xl mx-auto">
    <div class="mb-8 bg-white dark:bg-gray-800 rounded-xl shadow p-4">
      <div class="flex flex-col md:flex-row items-center">
        <!-- 折线图 3/4 -->
        <div class="w-full md:w-3/4">
          <apexchart
            type="area"
            height="260"
            :options="lineChartOptions"
            :series="lineChartSeries"
          />
        </div>
        <!-- 仪表图 1/4 -->
        <div class="w-full md:w-1/4 flex flex-col items-center justify-center mt-6 md:mt-0">
          <apexchart
            type="radialBar"
            height="180"
            :options="gaugeOptions"
            :series="[averageScore]"
          />
          <div class="mt-2 text-center">
            <div class="text-gray-400 text-xs">平均分</div>
            <div class="text-2xl font-bold text-blue-500">{{ averageScore }}</div>
          </div>
        </div>
      </div>
    </div>
    <!-- 筛选栏 -->
    <div class="mb-6 flex flex-wrap gap-6 items-center justify-between">
      <div class="flex gap-6 flex-wrap w-full">
        <!-- 领域筛选 -->
        <div class="w-40 relative flex items-center" ref="fieldDropdownRef">
          <label class="inline-block text-gray-400 text-sm font-bold"> 领域 </label>
          <a
            @click.prevent.stop="toggleDropdown('field')"
            class="cursor-pointer inline-flex items-center gap-10 flex-1 px-4 py-2 text-base font-medium text-gray-900 dark:text-gray-100 rounded-lg transition"
          >
            <span class="text-gray-600 dark:text-gray-100">{{ selectedField || '全部' }}</span>
            <svg
              class="duration-200 ease-in-out stroke-current"
              :class="{ 'rotate-180': dropdownOpen === 'field' }"
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
            >
              <path
                d="M4.79199 7.396L10.0003 12.6043L15.2087 7.396"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </a>
          <transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <div
              v-if="dropdownOpen === 'field'"
              v-click-outside="() => closeDropdown('field')"
              class="absolute left-0 top-full z-40 mt-2 w-full min-w-[160px] rounded-2xl border border-gray-200 bg-white p-2 shadow-lg dark:border-gray-800 dark:bg-[#1E2635]"
            >
              <ul class="flex flex-col gap-1">
                <li>
                  <a
                    href="#"
                    @click.prevent="selectField('')"
                    class="flex rounded-lg px-3 py-2.5 text-base font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5"
                    >全部</a
                  >
                </li>
                <li v-for="field in fieldOptions" :key="field">
                  <a
                    href="#"
                    @click.prevent="selectField(field)"
                    class="flex rounded-lg px-3 py-2.5 text-base font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5"
                    >{{ field }}</a
                  >
                </li>
              </ul>
            </div>
          </transition>
        </div>
        <!-- 岗位筛选 -->
        <div class="w-40 relative flex items-center" ref="positionDropdownRef">
          <label class="inline-block text-gray-400 text-sm font-bold">岗位</label>
          <a
            @click.prevent.stop="toggleDropdown('position')"
            class="cursor-pointer inline-flex items-center gap-10 flex-1 px-4 py-2 text-base font-medium text-gray-900 dark:text-gray-100 rounded-lg transition"
          >
            <span class="text-gray-600 dark:text-gray-100">{{ selectedPosition || '全部' }}</span>
            <svg
              class="duration-200 ease-in-out stroke-current"
              :class="{ 'rotate-180': dropdownOpen === 'position' }"
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
            >
              <path
                d="M4.79199 7.396L10.0003 12.6043L15.2087 7.396"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </a>
          <transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <div
              v-if="dropdownOpen === 'position'"
              v-click-outside="() => closeDropdown('position')"
              class="absolute left-0 top-full z-40 mt-2 w-full min-w-[160px] rounded-2xl border border-gray-200 bg-white p-2 shadow-lg dark:border-gray-800 dark:bg-[#1E2635]"
            >
              <ul class="flex flex-col gap-1">
                <li>
                  <a
                    href="#"
                    @click.prevent="selectPosition('')"
                    class="flex rounded-lg px-3 py-2.5 text-base font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5"
                    >全部</a
                  >
                </li>
                <li v-for="position in positionOptions" :key="position">
                  <a
                    href="#"
                    @click.prevent="selectPosition(position)"
                    class="flex rounded-lg px-3 py-2.5 text-base font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5"
                    >{{ position }}</a
                  >
                </li>
              </ul>
            </div>
          </transition>
        </div>
        <!-- 面试时间筛选（element-plus日期选择器） -->
        <div class="w-100 flex items-center">
          <label class="inline-block text-gray-400 text-sm mr-2 font-bold">面试时间</label>
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            :picker-options="pickerOptions"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            popper-class="z-50"
            @change="onDateChange"
          />
        </div>
      </div>
    </div>
    <div v-if="loading" class="text-center py-10 text-gray-500">加载中...</div>
    <div v-else-if="error" class="text-center py-10 text-red-500">{{ error }}</div>
    <div v-else>
      <div v-if="filteredList.length === 0" class="text-center py-10 text-gray-500">
        暂无历史记录
      </div>
      <div class="flex flex-col gap-4">
        <div
          v-for="item in filteredList"
          :key="item.history_id"
          class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-100 dark:border-gray-700 py-4 px-5 flex flex-col md:flex-row md:items-center md:justify-between hover:shadow-md hover:-translate-y-0.5 transition cursor-pointer"
          @click="goToDetail(item.history_id)"
        >
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap gap-4 items-center mb-1">
              <span
                class="inline-block px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-sm font-semibold dark:bg-blue-500/10 dark:text-blue-400"
                >{{ item.field }}</span
              >
            </div>
            <div
              class="text-lg font-bold text-gray-900 dark:text-white mb-1 truncate flex items-center"
            >
              <Icon icon="lucide:land-plot" class="w-5 h-5 mr-2 text-blue-500" />
              {{ item.position }}
            </div>
            <div class="text-gray-500 text-sm mt-1">
              <span v-if="item.feedback_suggestion1">{{
                truncateText(item.feedback_suggestion1, 32) + '...'
              }}</span>
            </div>
            <div class="text-gray-400 text-xs mt-1 font-light flex items-center">
              <Icon icon="lucide:clock" class="w-4 h-4 mr-1 text-gray-500" />
              {{ formatTime(item.interview_time) }} - {{ formatTime(item.end_time) }}
            </div>
          </div>
          <div class="flex flex-col items-end min-w-[140px] ml-6">
            <div class="flex-1 min-w-0 flex items-center gap-8">
              <!-- 小雷达图 -->
              <apexchart
                type="radar"
                width="100"
                height="100"
                :options="getRadarOptions()"
                :series="[
                  {
                    name: '能力',
                    data: [
                      (item.professional_knowledge || 0) * 20,
                      (item.skill_match || 0) * 20,
                      (item.language_expression || 0) * 20,
                      (item.logical_thinking || 0) * 20,
                      (item.innovation_ability || 0) * 20,
                      (item.stress_resistance || 0) * 20,
                    ],
                  },
                ]"
              />
              <!-- 右侧信息 ... -->
              <div class="flex flex-col items-end min-w-[80px] mt-4 md:mt-0">
                <span class="text-gray-400 text-xs">得分</span>
                <span class="text-6xl font-bold text-blue-500">{{ item.score }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getApiUrl } from '@/config/api'
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import apexchart from 'vue3-apexcharts'
import { ElDatePicker } from 'element-plus'
import 'element-plus/es/components/date-picker/style/css'
import { Icon } from '@iconify/vue'
import vClickOutside from '../components/common/v-click-outside.vue'

const router = useRouter()
const historyList = ref<any[]>([])
const loading = ref(true)
const error = ref('')

const selectedField = ref('')
const selectedPosition = ref('')
const selectedDate = ref<string>('')

const fieldOptions = ref<string[]>([])
const positionOptions = ref<string[]>([])

const dropdownOpen = ref('')
const fieldDropdownRef = ref(null)
const positionDropdownRef = ref(null)

const pickerOptions = {
  disabledDate(time: Date) {
    return time.getTime() > Date.now()
  },
  shortcuts: [
    {
      text: '今天',
      value: new Date(),
    },
    {
      text: '昨天',
      value: (() => {
        const date = new Date()
        date.setDate(date.getDate() - 1)
        return date
      })(),
    },
    {
      text: '一周前',
      value: (() => {
        const date = new Date()
        date.setDate(date.getDate() - 7)
        return date
      })(),
    },
  ],
}

const onDateChange = (val: string) => {
  selectedDate.value = val || ''
}

const toggleDropdown = (type: string) => {
  dropdownOpen.value = dropdownOpen.value === type ? '' : type
}
const closeDropdown = (type: string) => {
  if (dropdownOpen.value === type) dropdownOpen.value = ''
}
const selectField = (field: string) => {
  selectedField.value = field
  dropdownOpen.value = ''
}
const selectPosition = (position: string) => {
  selectedPosition.value = position
  dropdownOpen.value = ''
}

const fetchHistory = async () => {
  loading.value = true
  error.value = ''
  try {
    // 动态获取user_id
    const userId = localStorage.getItem('user_id')
    if (!userId) {
      error.value = '未获取到用户ID，请重新登录'
      loading.value = false
      return
    }
    // 使用动态userId拼接请求
    const res = await axios.get(getApiUrl(`/history/user/${userId}`))

    // 根据后端接口文档，数据在 res.data.data.historyList 中
    const historyData = res.data.history_list || []

    // 直接使用后端返回的数据，保持字段名一致
    historyList.value = historyData

    // 按时间从最近到最远排序
    historyList.value.sort((a, b) => {
      const timeA = new Date(a.interview_time).getTime()
      const timeB = new Date(b.interview_time).getTime()
      return timeB - timeA // 降序排列，最近的在前面
    })

    // 提取所有领域和岗位选项
    const fields = new Set<string>()
    const positions = new Set<string>()
    historyList.value.forEach((item) => {
      if (item.field) fields.add(item.field)
      if (item.position) positions.add(item.position)
    })
    fieldOptions.value = Array.from(fields)
    positionOptions.value = Array.from(positions)
    await nextTick()
    updateLineChart()
  } catch (e) {
    console.error('获取历史记录失败:', e)
    error.value = '获取历史记录失败'
  } finally {
    loading.value = false
  }
}
const filteredList = computed(() => {
  return historyList.value.filter((item) => {
    const matchField = !selectedField.value || item.field === selectedField.value
    const matchPosition = !selectedPosition.value || item.position === selectedPosition.value
    const matchDate =
      !selectedDate.value ||
      (item.interview_time && item.interview_time.startsWith(selectedDate.value))
    return matchField && matchPosition && matchDate
  })
})

const formatTime = (t: string) => {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const truncateText = (text: string, max: number) => {
  if (!text) return ''
  return text.length > max ? text.slice(0, max) + '…' : text
}

const goToDetail = (historyId: number) => {
  router.push({ name: 'HistoryDetail', params: { history_id: historyId } })
}

// 折线图数据
const lineChartSeries = ref<any[]>([])
const lineChartOptions = ref<any>({
  chart: {
    type: 'area',
    toolbar: { show: false },
    zoom: { enabled: false },
    fontFamily: 'inherit',
    foreColor: '#64748b',
    background: 'transparent',
  },
  stroke: { curve: 'smooth', width: 3 },
  markers: { size: 5, colors: ['#465fff'], strokeColors: '#fff', strokeWidth: 2 },
  xaxis: {
    type: 'category',
    labels: {
      style: { fontSize: '13px', fontWeight: 500, colors: ['#64748b'] },
      rotate: -30,
      formatter: function (value: string | number) {
        // 将值转换为Date对象（假设value是时间戳或ISO格式字符串）
        const date = new Date(value)

        // 月份英文缩写数组
        const monthNames = [
          'Jan',
          'Feb',
          'Mar',
          'Apr',
          'May',
          'Jun',
          'Jul',
          'Aug',
          'Sep',
          'Oct',
          'Nov',
          'Dec',
        ]

        // 获取月份缩写和日期（补零）
        const monthAbbr = monthNames[date.getMonth()]
        const day = String(date.getDate()).padStart(2, '0')

        // 返回格式化后的字符串
        return `${monthAbbr} ${day}` // 例如："Jan 01"
      },
    },
    tooltip: { enabled: false },
  },
  yaxis: {
    min: 0,
    max: 100,
    tickAmount: 5,
    labels: { style: { fontSize: '13px', fontWeight: 500, colors: ['#64748b'] } },
  },
  grid: { borderColor: '#e5e7eb', strokeDashArray: 4 },
  tooltip: { theme: 'light' },
  colors: ['#465fff'],
  fill: {
    type: 'gradient',
    gradient: {
      shade: 'light',
      type: 'vertical',
      shadeIntensity: 0.5,
      gradientToColors: ['#a5b4fc'],
      inverseColors: false,
      opacityFrom: 0.5,
      opacityTo: 0.1,
    },
  },
  legend: { show: false },
})

function updateLineChart() {
  // 按时间排序（升序，从早到晚，用于折线图）
  const sorted = [...historyList.value].sort(
    (a, b) => new Date(a.interview_time).getTime() - new Date(b.interview_time).getTime(),
  )
  lineChartSeries.value = [
    {
      name: '分数',
      data: sorted.map((item) => item.score),
    },
  ]
  lineChartOptions.value = {
    ...lineChartOptions.value,
    xaxis: {
      ...lineChartOptions.value.xaxis,
      categories: sorted.map((item) => formatTime(item.interview_time)),
    },
  }
}

function getRadarOptions() {
  return {
    chart: {
      type: 'radar',
      toolbar: { show: false },
      sparkline: { enabled: true },
      background: 'transparent',
    },
    xaxis: {
      categories: ['', '', '', '', '', ''],
      labels: { show: false },
      axisTicks: { show: false },
      axisBorder: { show: false },
    },
    yaxis: { show: false, min: 0, max: 100, labels: { show: false } },
    stroke: { width: 2, colors: ['#465fff'] },
    fill: { opacity: 0.15, colors: ['#465fff'] },
    markers: { size: 0 },
    dataLabels: { enabled: false },
    grid: { show: false },
    tooltip: { enabled: false },
    plotOptions: {
      radar: { polygons: { strokeColors: '#f3f4f6', fill: { colors: ['#f8f8f8', '#fff'] } } },
    },
    legend: { show: false },
  }
}

onMounted(fetchHistory)

const averageScore = computed(() => {
  if (!historyList.value.length) return 0
  const sum = historyList.value.reduce((acc, cur) => acc + (cur.score || 0), 0)
  return Math.round(sum / historyList.value.length)
})

const gaugeOptions = {
  chart: {
    type: 'radialBar',
    height: 180,
    offsetY: 0,
    sparkline: { enabled: true },
  },
  plotOptions: {
    radialBar: {
      startAngle: -135,
      endAngle: 135,
      track: {
        background: '#f3f4f6',
        startAngle: -135,
        endAngle: 135,
        strokeWidth: '90%',
        margin: -5,
      },
      hollow: {
        margin: 0,
        size: '70%',
        background: '#fff',
      },
      dataLabels: {
        show: false,
      },
    },
  },
  fill: {
    type: 'gradient',
    gradient: {
      shade: 'light',
      type: 'horizontal',
      shadeIntensity: 0.5,
      gradientToColors: ['#465fff'],
      inverseColors: false,
      opacityFrom: 0.8,
      opacityTo: 1,
      stops: [0, 100],
    },
  },
  stroke: {
    lineCap: 'round',
  },
  labels: ['平均分'],
  colors: ['#465fff'],
  grid: { show: false },
  tooltip: { enabled: false },
}
</script>

<style scoped>
::v-deep .el-input__wrapper {
  background-color: transparent !important;
}
</style>
