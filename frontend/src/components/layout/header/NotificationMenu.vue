<template>
  <div class="relative" ref="dropdownRef">
    <button
      class="relative flex items-center justify-center text-gray-500 transition-colors bg-white border border-gray-200 rounded-full hover:text-dark-900 h-11 w-11 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
      @click="toggleDropdown"
    >
      <svg
        class="fill-current"
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M10.75 2.29248C10.75 1.87827 10.4143 1.54248 10 1.54248C9.58583 1.54248 9.25004 1.87827 9.25004 2.29248V2.83613C6.08266 3.20733 3.62504 5.9004 3.62504 9.16748V14.4591H3.33337C2.91916 14.4591 2.58337 14.7949 2.58337 15.2091C2.58337 15.6234 2.91916 15.9591 3.33337 15.9591H4.37504H15.625H16.6667C17.0809 15.9591 17.4167 15.6234 17.4167 15.2091C17.4167 14.7949 17.0809 14.4591 16.6667 14.4591H16.375V9.16748C16.375 5.9004 13.9174 3.20733 10 4.29248C7.30765 4.29248 5.12504 6.47509 5.12504 9.16748V14.4591H14.875ZM14.875 14.4591V9.16748C14.875 6.47509 12.6924 4.29248 10 4.29248C7.30765 4.29248 5.12504 6.47509 5.12504 9.16748V14.4591H14.875ZM8.00004 17.7085C8.00004 18.1228 8.33583 18.4585 8.75004 18.4585H11.25C11.6643 18.4585 12 18.1228 12 17.7085C12 17.2943 11.6643 16.9585 11.25 16.9585H8.75004C8.33583 16.9585 8.00004 17.2943 8.00004 17.7085Z"
          fill=""
        />
      </svg>
      <!-- 未读通知标记 -->
      <span
        v-if="hasUnreadNotifications"
        class="absolute top-0 right-0 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white dark:border-gray-900"
      ></span>
    </button>

    <!-- Dropdown Start -->
    <div
      v-if="dropdownOpen"
      class="absolute -right-[240px] mt-[17px] flex h-[480px] w-[350px] flex-col rounded-2xl border border-gray-200 bg-white p-3 shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark sm:w-[361px] lg:right-0"
    >
      <div
        class="flex items-center justify-between pb-3 mb-3 border-b border-gray-100 dark:border-gray-800"
      >
        <h5 class="text-lg font-semibold text-gray-800 dark:text-white/90">通知</h5>

        <button @click="closeDropdown" class="text-gray-500 dark:text-gray-400">
          <svg
            class="fill-current"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M6.21967 7.28131C5.92678 6.98841 5.92678 6.51354 6.21967 6.22065C6.51256 5.92775 6.98744 5.92775 7.28033 6.22065L11.999 10.9393L16.7176 6.22078C17.0105 5.92789 17.4854 5.92788 17.7782 6.22078C18.0711 6.51367 18.0711 6.98855 17.7782 7.28144L13.0597 12L17.7782 16.7186C18.0711 17.0115 18.0711 17.4863 17.7782 17.7792C17.4854 18.0721 17.0105 18.0721 16.7176 17.7792L11.999 13.0607L7.28033 17.7794C6.98744 18.0722 6.51256 18.0722 6.21967 17.7794C5.92678 17.4865 5.92678 17.0116 6.21967 16.7187L10.9384 12L6.21967 7.28131Z"
              fill=""
            />
          </svg>
        </button>
      </div>

      <ul class="flex flex-col h-auto overflow-y-auto custom-scrollbar">
        <li
          v-for="notification in notifications"
          :key="notification.id"
          @click="(event) => handleItemClick(event, notification)"
        >
          <a
            class="flex gap-3 rounded-lg border-b border-gray-100 p-3 px-4.5 py-3 hover:bg-gray-100 dark:border-gray-800 dark:hover:bg-white/5"
            href="#"
            :class="{ 'cursor-pointer': notification.status === 'completed' }"
          >
            <span class="relative block w-full h-10 rounded-full z-1 max-w-10">
              <img :src="notification.userImage" alt="User" class="overflow-hidden rounded-full" />
              <span
                :class="{
                  'bg-warning-500': notification.status === 'generating',
                  'bg-success-500': notification.status === 'completed',
                  'bg-error-500': notification.status === 'failed',
                  'bg-gray-500': !notification.status,
                }"
                class="absolute bottom-0 right-0 z-10 h-2.5 w-full max-w-2.5 rounded-full border-[1.5px] border-white dark:border-gray-900"
              ></span>
            </span>

            <span class="block">
              <span class="mb-1.5 block text-theme-sm text-gray-500 dark:text-gray-400">
                <span class="font-medium text-gray-800 dark:text-white/90">
                  {{ notification.userName }}
                </span>
                {{ notification.action }}
                <span class="font-medium text-gray-800 dark:text-white/90">
                  {{ notification.project }}
                </span>
              </span>

              <span class="flex items-center gap-2 text-gray-500 text-theme-xs dark:text-gray-400">
                <span
                  :class="{
                    'text-warning-500': notification.status === 'generating',
                    'text-success-500': notification.status === 'completed',
                    'text-error-500': notification.status === 'failed',
                  }"
                >
                  {{
                    notification.status === 'generating'
                      ? '生成中'
                      : notification.status === 'completed'
                        ? '已完成'
                        : notification.status === 'failed'
                          ? '失败'
                          : notification.type
                  }}
                </span>
                <span class="w-1 h-1 bg-gray-400 rounded-full"></span>
                <span>{{ notification.time }}</span>
              </span>
            </span>
          </a>
        </li>
      </ul>

      <router-link
        to="#"
        class="mt-3 flex justify-center rounded-lg border border-gray-300 bg-white p-3 text-theme-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 hover:text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/[0.03] dark:hover:text-gray-200"
        @click="handleViewAllClick"
      >
        已查看所有通知
      </router-link>
    </div>
    <!-- Dropdown End -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { getApiUrl } from '@/config/api'

const dropdownOpen = ref(false)
const notifying = ref(false)
const dropdownRef = ref(null)
const router = useRouter()
const pollingTimer = ref(null)

const notifications = ref([])

// 计算属性：检查是否有未读通知
const hasUnreadNotifications = computed(() => {
  return notifications.value.some((notification) => !notification.read)
})

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
  if (dropdownOpen.value) {
    // 打开通知时立即刷新状态
    loadNotifications()
    checkReportStatus()
  }
}

const closeDropdown = () => {
  dropdownOpen.value = false
}

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    closeDropdown()
  }
}

const handleItemClick = (event, notification) => {
  event.preventDefault()
  // 处理通知点击
  if (notification.status === 'completed' && notification.processId) {
    // 跳转到面试结果页面
    router.push({
      name: 'InterviewResult',
      query: { process_id: notification.processId },
    })
  }

  // 标记通知为已读
  notification.read = true

  // 更新localStorage中的通知状态
  const storedNotifications = JSON.parse(localStorage.getItem('interview_notifications') || '[]')
  const updatedNotifications = storedNotifications.map((item) => {
    if (item.id === notification.id) {
      return { ...item, read: true }
    }
    return item
  })
  localStorage.setItem('interview_notifications', JSON.stringify(updatedNotifications))

  closeDropdown()
}

const handleViewAllClick = (event) => {
  event.preventDefault()
  // 标记所有通知为已读
  notifications.value.forEach((notification) => {
    notification.read = true
  })

  // 更新localStorage中的通知状态
  const storedNotifications = JSON.parse(localStorage.getItem('interview_notifications') || '[]')
  const updatedNotifications = storedNotifications.map((item) => ({
    ...item,
    read: true,
  }))
  localStorage.setItem('interview_notifications', JSON.stringify(updatedNotifications))

  closeDropdown()
}

// 从 localStorage 加载通知
const loadNotifications = () => {
  const storedNotifications = JSON.parse(localStorage.getItem('interview_notifications') || '[]')
  notifications.value = storedNotifications
    .map((item) => ({
      id: item.id,
      userName: '系统',
      action: item.status === 'completed' ? '你的面试报告已生成完成' : '正在生成你的面试报告',
      project: '',
      type: '面试报告',
      time: formatTime(item.createdAt),
      createdAt: item.createdAt, // 保留原始时间戳用于排序
      status: item.status,
      processId: item.processId,
      read: item.read || false, // 确保read状态正确加载
      userImage:
        'https://ai.lanzidian.com/uploads/images/20240531/b15ea65a6bdea2aa71b43feaf45b26f1.png',
    }))
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()) // 按时间降序排列，最新的在前
}

// 格式化时间
const formatTime = (createdAt) => {
  const now = new Date()
  const created = new Date(createdAt)
  const diff = now.getTime() - created.getTime()

  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return `${Math.floor(diff / 86400000)}天前`
  }
}

// 检查面试报告状态
const checkReportStatus = async () => {
  const storedNotifications = JSON.parse(localStorage.getItem('interview_notifications') || '[]')
  let hasChanges = false

  for (const item of storedNotifications) {
    if (item.status === 'generating' && item.processId) {
      try {
        const res = await fetch(getApiUrl(`/interview/end/status/${item.processId}`))
        const data = await res.json()

        // 添加 code 检查和状态处理
        if (data.code === 200) {
          if (data.data.status === 'completed') {
            // 报告生成完成
            item.status = 'completed'
            hasChanges = true
            notifying.value = true
          } else if (data.data.status === 'failed') {
            // 报告生成失败
            item.status = 'failed'
            hasChanges = true
            notifying.value = true
          }
          // processing 状态保持不变，继续轮询
        } else {
          console.error('检查报告状态失败:', data.message)
        }
      } catch (e) {
        console.error('检查报告状态失败:', e)
      }
    }
  }

  if (hasChanges) {
    // 保存更新后的状态
    localStorage.setItem('interview_notifications', JSON.stringify(storedNotifications))
    // 重新加载通知列表
    loadNotifications()
  }
}

// 启动轮询
const startPolling = () => {
  // 每 5 秒检查一次报告状态
  pollingTimer.value = setInterval(() => {
    checkReportStatus()
  }, 5000)
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // 加载本地存储的通知
  loadNotifications()
  // 启动轮询
  startPolling()
  // 组件挂载时检查面试报告状态
  checkReportStatus()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  // 清理轮询定时器
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
})
</script>
