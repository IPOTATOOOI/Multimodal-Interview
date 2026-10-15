<template>
  <div
    class="mb-5 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]"
  >
    <h3 class="mb-3 text-base font-semibold text-gray-800 dark:text-white/90">新增普通用户</h3>
    <form class="grid grid-cols-1 gap-3 md:grid-cols-4" @submit.prevent="handleAddUser">
      <input
        v-model.trim="newUser.username"
        type="text"
        placeholder="用户名"
        class="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-gray-700 dark:bg-gray-900"
      />
      <input
        v-model.trim="newUser.email"
        type="email"
        placeholder="邮箱"
        class="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-gray-700 dark:bg-gray-900"
      />
      <input
        v-model="newUser.password"
        type="password"
        placeholder="初始密码（至少 6 位）"
        class="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-gray-700 dark:bg-gray-900"
      />
      <button
        type="submit"
        :disabled="isSubmitting"
        class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {{ isSubmitting ? '提交中...' : '新增用户' }}
      </button>
    </form>
    <p v-if="formError" class="mt-2 text-sm text-red-600">{{ formError }}</p>
  </div>

  <div class="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <div class="flex w-full items-center gap-2 sm:w-auto">
      <div class="relative w-full sm:w-64">
        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <svg
            class="h-4 w-4 text-gray-500 dark:text-gray-400"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 20 20"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
            />
          </svg>
        </div>
        <input
          v-model.trim="searchKeyword"
          type="text"
          placeholder="搜索用户名..."
          class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 pl-10 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-blue-500 dark:focus:ring-blue-500"
          @keyup.enter="handleSearch"
        />
        <button
          v-if="searchKeyword"
          @click="clearSearch"
          class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>
      <button
        @click="handleSearch"
        class="rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-800 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
      >
        搜索
      </button>
    </div>

    <div class="flex h-10 items-center">
      <transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-1"
      >
        <button
          v-if="selectedIds.length > 0"
          @click="confirmBatchDelete"
          class="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-300 dark:focus:ring-red-900"
        >
          <svg
            class="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            ></path>
          </svg>
          批量删除 ({{ selectedIds.length }})
        </button>
      </transition>
    </div>
  </div>

  <div
    class="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
  >
    <div class="max-w-full overflow-x-auto custom-scrollbar">
      <table class="min-w-full">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <th class="px-2 py-3 w-10 text-center">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="isIndeterminate"
                @change="toggleSelectAll"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
            </th>
            <th class="px-3 py-3 text-left sm:px-4">
              <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">用户信息</p>
            </th>
            <th class="px-3 py-3 text-left sm:px-4">
              <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">创建于</p>
            </th>
            <th class="px-3 py-3 text-left sm:px-4">
              <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">电子邮箱</p>
            </th>
            <th class="px-3 py-3 text-left sm:px-4">
              <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">大学</p>
            </th>
            <th class="px-5 py-3 text-left sm:px-6">
              <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">专业</p>
            </th>
            <th class="px-5 py-3 text-left sm:px-6">
              <p class="font-medium text-gray-500 text-theme-xs dark:text-gray-400">操作</p>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-if="isLoading">
            <td colspan="7" class="px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
              正在加载用户列表...
            </td>
          </tr>
          <tr v-else-if="!users.length">
            <td colspan="7" class="px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
              暂无用户数据
            </td>
          </tr>
          <tr
            v-for="user in users"
            :key="user.id"
            class="border-t border-gray-100 dark:border-gray-800"
          >
            <td class="px-2 py-4 text-center">
              <input
                type="checkbox"
                v-model="selectedIds"
                :value="user.id"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
            </td>
            <td class="px-3 py-4 sm:px-4">
              <div class="flex items-center gap-2">
                <div
                  class="relative flex h-10 w-10 items-center justify-center overflow-hidden rounded-2xl ring-2 ring-white shadow-sm dark:ring-white/10"
                  :class="getAvatarFallbackClass(user.name)"
                >
                  <img
                    v-if="user.avatar && !avatarLoadErrorMap[user.id]"
                    :src="user.avatar"
                    :alt="user.name"
                    class="h-full w-full object-cover"
                    @error="handleAvatarError(user.id)"
                  />
                  <span v-else class="text-sm font-semibold text-white">
                    {{ getUserInitial(user.name) }}
                  </span>
                </div>
                <div>
                  <span class="block font-medium text-gray-800 text-theme-sm dark:text-white/90">
                    {{ user.name }}
                  </span>
                </div>
              </div>
            </td>
            <td class="px-3 py-4 sm:px-4">
              <p class="text-gray-500 text-theme-sm dark:text-gray-400">{{ user.createdAt }}</p>
            </td>
            <td class="px-3 py-4 sm:px-4">
              <p class="text-gray-500 text-theme-sm dark:text-gray-400">{{ user.email }}</p>
            </td>
            <td class="px-3 py-4 sm:px-4">
              <p class="text-gray-500 text-theme-sm dark:text-gray-400">{{ user.university }}</p>
            </td>
            <td class="px-5 py-4 sm:px-6">
              <p class="text-gray-500 text-theme-sm dark:text-gray-400">{{ user.major }}</p>
            </td>
            <td class="px-5 py-4 sm:px-6">
              <div class="flex gap-2">
                <button
                  class="px-2 py-1 text-xs text-red-600 hover:text-red-800"
                  :disabled="isDeleting"
                  @click="deleteUser(user)"
                >
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <ConfirmDialog
    :is-open="showConfirmDialog"
    title="确认删除"
    :message="dialogMessage"
    @confirm="handleConfirmDelete"
    @cancel="showConfirmDialog = false"
  />
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import ConfirmDialog from '../components/dashboard/ConfirmDialog.vue'

type DashboardUser = {
  id: string
  name: string
  avatar: string
  createdAt: string
  email: string
  university: string
  major: string
}

import { getApiUrl } from '@/config/api'

const API_URL = getApiUrl('/admin/users')

const users = ref<DashboardUser[]>([])
const isLoading = ref(false)
const isSubmitting = ref(false)
const isDeleting = ref(false)
const formError = ref('')
const avatarLoadErrorMap = ref<Record<string, boolean>>({})

const searchKeyword = ref('')
const selectedIds = ref<string[]>([])
const isBatchMode = ref(false)

const newUser = ref({
  username: '',
  email: '',
  password: '',
})

const isAllSelected = computed(() => {
  return users.value.length > 0 && selectedIds.value.length === users.value.length
})

const isIndeterminate = computed(() => {
  return selectedIds.value.length > 0 && selectedIds.value.length < users.value.length
})

const dialogMessage = computed(() => {
  if (isBatchMode.value) {
    return `确定要删除选中的 ${selectedIds.value.length} 名用户吗？`
  }
  return `确定要删除用户 ${userToDelete.value?.name || ''} 吗？`
})

const getAuthHeader = () => {
  const token = localStorage.getItem('admin_access_token') || ''
  const userRole = localStorage.getItem('userRole')

  if (userRole !== 'admin') {
    console.warn('[AdminUsers] userRole is not admin:', userRole)
  }

  if (!token) {
    throw new Error('管理员登录状态已失效，请重新登录')
  }

  return {
    Authorization: `Bearer ${token}`,
  }
}

const normalizeUsers = (list: any[]): DashboardUser[] => {
  return list.map((item: any) => ({
    id: String(item.id ?? item.user_id ?? item.uid ?? ''),
    name: item.username ?? item.name ?? item.nickname ?? '-',
    avatar: item.avatar || '/images/user/user-default.jpg',
    createdAt: item.created_at ?? item.createdAt ?? '-',
    email: item.email ?? '-',
    university: item.university ?? item.school ?? '-',
    major: item.major ?? item.profession ?? '-',
  }))
}

const avatarFallbackClasses = [
  'bg-gradient-to-br from-sky-500 to-blue-600',
  'bg-gradient-to-br from-emerald-500 to-teal-600',
  'bg-gradient-to-br from-amber-500 to-orange-600',
  'bg-gradient-to-br from-pink-500 to-rose-600',
  'bg-gradient-to-br from-violet-500 to-indigo-600',
]

const getUserInitial = (name: string) => {
  const trimmedName = (name || '').trim()
  return trimmedName ? trimmedName.charAt(0).toUpperCase() : 'U'
}

const getAvatarFallbackClass = (name: string) => {
  const seed = (name || '').split('').reduce((sum, char) => sum + char.charCodeAt(0), 0)
  // Ensure seed is positive before modulo
  const positiveSeed = Math.abs(seed)
  return avatarFallbackClasses[positiveSeed % avatarFallbackClasses.length]
}

const handleAvatarError = (userId: string) => {
  avatarLoadErrorMap.value[userId] = true
}

const resolveUserList = (responseData: any): any[] => {
  const data = responseData?.data
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.list)) return data.list
  if (Array.isArray(data?.users)) return data.users
  if (Array.isArray(data?.items)) return data.items
  if (Array.isArray(responseData?.list)) return responseData.list
  if (Array.isArray(responseData?.users)) return responseData.users
  return []
}

const fetchUsers = async () => {
  isLoading.value = true
  try {
    console.log('[AdminUsers] request GET:', API_URL)
    const authHeader = getAuthHeader()
    const response = await axios.get(API_URL, {
      headers: authHeader,
    })

    console.log('[AdminUsers] response status:', response.status)
    console.log('[AdminUsers] response payload:', response.data)

    if (typeof response.data?.code === 'number' && response.data.code !== 200) {
      throw new Error(response.data?.msg || '获取用户列表失败')
    }

    const list = resolveUserList(response.data)
    users.value = normalizeUsers(list)

    if (!users.value.length) {
      ElMessage.warning('请求成功，但响应中没有可用用户数组，请查看控制台 response payload')
    }
  } catch (error: any) {
    console.error('[AdminUsers] catch message:', error?.message)
    console.error('[AdminUsers] request failed:', {
      url: API_URL,
      message: error?.message,
      code: error?.code,
      status: error?.response?.status,
      data: error?.response?.data,
    })
    const message = error?.response?.data?.detail || error?.message || '获取用户列表失败'
    ElMessage.error(message)
  } finally {
    isLoading.value = false
    selectedIds.value = []
  }
}

const resetForm = () => {
  newUser.value.username = ''
  newUser.value.email = ''
  newUser.value.password = ''
}

const handleAddUser = async () => {
  formError.value = ''

  if (!newUser.value.username || !newUser.value.password) {
    formError.value = '请填写用户名和初始密码'
    return
  }

  if (newUser.value.password.length < 6) {
    formError.value = '密码长度至少为 6 位'
    return
  }

  isSubmitting.value = true
  try {
    const payload: { username: string; password: string; email?: string } = {
      username: newUser.value.username,
      password: newUser.value.password,
    }

    if (newUser.value.email) {
      payload.email = newUser.value.email
    }

    await axios.post(API_URL, payload, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    })

    ElMessage.success('新增用户成功')
    resetForm()
    await fetchUsers()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.response?.data?.msg || '新增用户失败'
    formError.value = message
  } finally {
    isSubmitting.value = false
  }
}

//删除用户
const showConfirmDialog = ref(false)
const userToDelete = ref<DashboardUser | null>(null)

const clearSearch = () => {
  searchKeyword.value = ''
  fetchUsers()
}

const handleSearch = async () => {
  if (!searchKeyword.value) {
    fetchUsers()
    return
  }

  isLoading.value = true
  try {
    const authHeader = getAuthHeader()
    const response = await axios.get(getApiUrl(`/admin/users/by-username/${searchKeyword.value}`), {
      headers: authHeader,
    })

    if (response.data?.code === 200 && response.data?.data) {
      users.value = normalizeUsers([response.data.data])
    } else {
      users.value = []
      ElMessage.info('未找到该用户')
    }
  } catch (error: any) {
    if (error.response && error.response.status === 404) {
      users.value = []
      ElMessage.info('未找到该用户')
    } else {
      const message = error?.response?.data?.detail || error?.message || '搜索失败'
      ElMessage.error(message)
    }
  } finally {
    isLoading.value = false
    selectedIds.value = []
  }
}

const toggleSelectAll = (e: Event) => {
  const checkbox = e.target as HTMLInputElement
  if (checkbox.checked) {
    selectedIds.value = users.value.map((u) => u.id)
  } else {
    selectedIds.value = []
  }
}

const confirmBatchDelete = () => {
  if (selectedIds.value.length === 0) return
  isBatchMode.value = true
  showConfirmDialog.value = true
}

const deleteUser = (user: DashboardUser) => {
  userToDelete.value = user
  isBatchMode.value = false
  showConfirmDialog.value = true
}

const handleConfirmDelete = async () => {
  if (isBatchMode.value) {
    if (selectedIds.value.length === 0) {
      ElMessage.warning('未选择用户')
      showConfirmDialog.value = false
      return
    }
  } else {
    if (!userToDelete.value?.id) {
      ElMessage.error('缺少用户ID，无法删除')
      showConfirmDialog.value = false
      return
    }
  }

  isDeleting.value = true

  try {
    const authHeader = getAuthHeader()
    if (isBatchMode.value) {
      const deletePromises = selectedIds.value.map((id) =>
        axios
          .delete(`${API_URL}/${id}`, { headers: authHeader })
          .then(() => id)
          .catch((err) => {
            console.error(`Failed to delete user ${id}`, err)
            return null
          }),
      )

      const results = await Promise.all(deletePromises)
      const successfulIds = results.filter((id): id is string => id !== null)

      if (successfulIds.length > 0) {
        users.value = users.value.filter((u) => !successfulIds.includes(u.id))
        selectedIds.value = selectedIds.value.filter((id) => !successfulIds.includes(id))
        if (successfulIds.length === results.length) {
          ElMessage.success(`成功删除 ${successfulIds.length} 名用户`)
        } else {
          ElMessage.warning(
            `成功删除 ${successfulIds.length} 名用户，${results.length - successfulIds.length} 名删除失败`,
          )
        }
      } else {
        ElMessage.error('所有选中的用户删除失败')
      }
    } else {
      await axios.delete(`${API_URL}/${userToDelete.value!.id}`, {
        headers: authHeader,
      })

      users.value = users.value.filter((u) => u.id !== userToDelete.value?.id)
      ElMessage.success('删除用户成功')
    }
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.response?.data?.msg || '操作失败'
    ElMessage.error(message)
  } finally {
    isDeleting.value = false
    showConfirmDialog.value = false
    userToDelete.value = null
    isBatchMode.value = false
  }
}

onMounted(() => {
  console.log('[AdminUsers] onMounted triggered')
  console.log('[AdminUsers] storage snapshot:', {
    admin_access_token: !!localStorage.getItem('admin_access_token'),
    userRole: localStorage.getItem('userRole'),
  })
  fetchUsers()
})

onActivated(() => {
  console.log('[AdminUsers] onActivated triggered')
  fetchUsers()
})
</script>

<style scoped></style>
