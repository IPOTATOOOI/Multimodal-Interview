<template>
  <div
    class="min-h-screen w-full flex flex-col md:flex-row relative bg-[#F2F3F5] font-inter overflow-hidden selection:bg-[#407BBF] selection:text-white"
  >
    <svg
      style="filter: contrast(125%) brightness(110%)"
      class="fixed z-[1] w-full h-full opacity-[35%] pointer-events-none"
    >
      <filter id="noise">
        <feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="3" stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#noise)" />
    </svg>

    <!-- 左侧主要内容区域（注册表单） -->
    <main
      class="relative z-[100] flex flex-col justify-center min-h-screen w-full md:w-[55%] lg:w-[50%] px-6 md:px-12 lg:px-[10%] py-12 md:py-0"
    >
      <h1
        class="title-animation mb-6 md:mb-8 font-extrabold text-5xl md:text-6xl lg:text-7xl font-inter text-[#1E2B3A] leading-tight tracking-tight"
      >
        注册
        <span class="text-[#407BBF]">{{ appStore.appName }}</span>
        <span class="font-inter text-[#407BBF]">.</span>
      </h1>

      <!-- 注册成功弹出层 -->
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 flex items-center justify-center z-50 bg-black/30"
      >
        <div
          class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl rounded-2xl shadow-2xl p-8 max-w-md w-full"
        >
          <div class="text-center">
            <svg
              class="w-16 h-16 mx-auto text-green-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
            <h3 class="mt-4 text-xl font-bold text-gray-800 dark:text-white">注册成功!</h3>
            <p class="mt-2 text-gray-600 dark:text-gray-300">
              您的账号已成功创建，请使用您的凭证登录系统。
            </p>
          </div>
          <div class="mt-6 flex justify-center">
            <button
              @click="redirectToLogin"
              class="px-6 py-2.5 bg-[#1E2B3A] text-white rounded-full hover:bg-[#2d3f52] transition font-semibold shadow-lg"
            >
              前往登录
            </button>
          </div>
        </div>
      </div>

      <!-- 注册表单卡片区域 -->
      <div class="card-animation w-[120%] max-w-lg">
        <div
          class="bg-white/70 dark:bg-gray-900/70 backdrop-blur-2xl rounded-3xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_32px_rgba(0,0,0,0.06)] p-3 sm:p-6 transition-all duration-300"
        >
          <!-- 错误提示 -->
          <transition name="fade">
            <div
              v-if="errorMessage"
              class="mb-6 p-3.5 text-sm text-red-600 bg-red-50/90 border border-red-100 rounded-xl dark:bg-red-500/20 dark:border-red-500/30 flex items-center shadow-sm"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-5 h-5 mr-2.5 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{{ errorMessage }}</span>
            </div>
          </transition>

          <!-- 表单 -->
          <form @submit.prevent="handleSubmit" class="space-y-3">
            <!-- 用户类型选择 -->
            <div
              class="flex items-center justify-between border-b border-gray-200/60 pb-5 dark:border-gray-700/60"
            >
              <label class="text-sm font-semibold text-gray-800 dark:text-gray-200">用户类型</label>
              <div class="flex items-center space-x-5">
                <label class="flex items-center space-x-2 cursor-pointer group">
                  <input
                    v-model="userType"
                    type="radio"
                    value="user"
                    class="h-4.5 w-4.5 accent-[#407BBF] cursor-pointer transition-all"
                  />
                  <span
                    class="text-sm font-medium text-gray-600 group-hover:text-[#407BBF] transition-colors dark:text-gray-400"
                    >普通用户</span
                  >
                </label>
                <label class="flex items-center space-x-2 cursor-pointer group">
                  <input
                    v-model="userType"
                    type="radio"
                    value="admin"
                    class="h-4.5 w-4.5 accent-[#407BBF] cursor-pointer transition-all"
                  />
                  <span
                    class="text-sm font-medium text-gray-600 group-hover:text-[#407BBF] transition-colors dark:text-gray-400"
                    >管理员</span
                  >
                </label>
              </div>
            </div>

            <!-- 用户名 -->
            <div class="space-y-1.5">
              <label
                for="username"
                class="block text-sm font-semibold text-gray-800 dark:text-gray-200"
              >
                用户名 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="username"
                type="text"
                id="username"
                placeholder="请输入用户名"
                class="h-11 w-full rounded-xl border border-white/60 bg-white/60 px-4 py-2 text-sm text-gray-800 shadow-sm placeholder:text-gray-400 focus:border-[#407BBF] focus:bg-white focus:outline-none focus:ring-4 focus:ring-[#407BBF]/15 transition-all duration-300 dark:border-gray-700 dark:bg-gray-800/60 dark:text-white dark:focus:bg-gray-800"
              />
            </div>

            <!-- 邮箱 -->
            <div class="space-y-1.5">
              <label
                for="email"
                class="block text-sm font-semibold text-gray-800 dark:text-gray-200"
              >
                邮箱 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="email"
                type="email"
                id="email"
                placeholder="请输入邮箱"
                class="h-11 w-full rounded-xl border border-white/60 bg-white/60 px-4 py-2 text-sm text-gray-800 shadow-sm placeholder:text-gray-400 focus:border-[#407BBF] focus:bg-white focus:outline-none focus:ring-4 focus:ring-[#407BBF]/15 transition-all duration-300 dark:border-gray-700 dark:bg-gray-800/60 dark:text-white dark:focus:bg-gray-800"
              />
            </div>

            <!-- 密码 -->
            <div class="space-y-1.5">
              <label
                for="password"
                class="block text-sm font-semibold text-gray-800 dark:text-gray-200"
              >
                密码 <span class="text-red-500">*</span>
              </label>
              <div class="relative group">
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  placeholder="请输入密码"
                  class="h-11 w-full rounded-xl border border-white/60 bg-white/60 py-2 pl-4 pr-12 text-sm text-gray-800 shadow-sm placeholder:text-gray-400 focus:border-[#407BBF] focus:bg-white focus:outline-none focus:ring-4 focus:ring-[#407BBF]/15 transition-all duration-300 dark:border-gray-700 dark:bg-gray-800/60 dark:text-white dark:focus:bg-gray-800"
                />
                <button
                  type="button"
                  @click="togglePasswordVisibility"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#407BBF] transition-colors focus:outline-none p-1"
                >
                  <svg v-if="!showPassword" class="w-5 h-5 fill-current" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      clip-rule="evenodd"
                      d="M10.0002 13.8619C7.23361 13.8619 4.86803 12.1372 3.92328 9.70241C4.86804 7.26761 7.23361 5.54297 10.0002 5.54297C12.7667 5.54297 15.1323 7.26762 16.0771 9.70243C15.1323 12.1372 12.7667 13.8619 10.0002 13.8619ZM10.0002 4.04297C6.48191 4.04297 3.49489 6.30917 2.4155 9.4593C2.3615 9.61687 2.3615 9.78794 2.41549 9.94552C3.49488 13.0957 6.48191 15.3619 10.0002 15.3619C13.5184 15.3619 16.5055 13.0957 17.5849 9.94555C17.6389 9.78797 17.6389 9.6169 17.5849 9.45932C16.5055 6.30919 13.5184 4.04297 10.0002 4.04297ZM9.99151 7.84413C8.96527 7.84413 8.13333 8.67606 8.13333 9.70231C8.13333 10.7286 8.96527 11.5605 9.99151 11.5605H10.0064C11.0326 11.5605 11.8646 10.7286 11.8646 9.70231C11.8646 8.67606 11.0326 7.84413 10.0064 7.84413H9.99151Z"
                    />
                  </svg>
                  <svg v-else class="w-5 h-5 fill-current" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      clip-rule="evenodd"
                      d="M4.63803 3.57709C4.34513 3.2842 3.87026 3.2842 3.57737 3.57709C3.28447 3.86999 3.28447 4.34486 3.57737 4.63775L4.85323 5.91362C3.74609 6.84199 2.89363 8.06395 2.4155 9.45936C2.3615 9.61694 2.3615 9.78801 2.41549 9.94558C3.49488 13.0957 6.48191 15.3619 10.0002 15.3619C11.255 15.3619 12.4422 15.0737 13.4994 14.5598L15.3625 16.4229C15.6554 16.7158 16.1302 16.7158 16.4231 16.4229C16.716 16.13 16.716 15.6551 16.4231 15.3622L4.63803 3.57709ZM12.3608 13.4212L10.4475 11.5079C10.3061 11.5423 10.1584 11.5606 10.0064 11.5606H9.99151C8.96527 11.5606 8.13333 10.7286 8.13333 9.70237C8.13333 9.5461 8.15262 9.39434 8.18895 9.24933L5.91885 6.97923C5.03505 7.69015 4.34057 8.62704 3.92328 9.70247C4.86803 12.1373 7.23361 13.8619 10.0002 13.8619C10.8326 13.8619 11.6287 13.7058 12.3608 13.4212ZM16.0771 9.70249C15.7843 10.4569 15.3552 11.1432 14.8199 11.7311L15.8813 12.7925C16.6329 11.9813 17.2187 11.0143 17.5849 9.94561C17.6389 9.78803 17.6389 9.61696 17.5849 9.45938C16.5055 6.30925 13.5184 4.04303 10.0002 4.04303C9.13525 4.04303 8.30244 4.17999 7.52218 4.43338L8.75139 5.66259C9.1556 5.58413 9.57311 5.54303 10.0002 5.54303C12.7667 5.54303 15.1323 7.26768 16.0771 9.70249Z"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 管理员注册码 -->
            <div v-if="userType === 'admin'" class="space-y-1.5">
              <label
                for="adminCode"
                class="block text-sm font-semibold text-gray-800 dark:text-gray-200"
              >
                管理员注册码 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="adminCode"
                type="text"
                id="adminCode"
                placeholder="注册码由超级管理员提供下发"
                class="h-11 w-full rounded-xl border border-white/60 bg-white/60 px-4 py-2 text-sm text-gray-800 shadow-sm placeholder:text-gray-400 focus:border-[#407BBF] focus:bg-white focus:outline-none focus:ring-4 focus:ring-[#407BBF]/15 transition-all duration-300 dark:border-gray-700 dark:bg-gray-800/60 dark:text-white dark:focus:bg-gray-800"
              />
            </div>

            <!-- Cloudflare Turnstile 验证 -->
            <!-- <div class="mt-4">
              <VueTurnstile
                site-key="0x4AAAAAACrSVjKwbFkjLzkZ"
                v-model="turnstileToken"
                @error="handleTurnstileError"
              />
            </div> -->

            <!-- 注册按钮 -->
            <button
              type="submit"
              :disabled="isLoading || showSuccessModal"
              class="group relative w-full rounded-xl overflow-hidden bg-[#1E2B3A] px-4 py-3 text-base font-semibold text-white shadow-lg shadow-[#1E2B3A]/20 transition-all hover:bg-[#2A3B4C] hover:shadow-xl hover:shadow-[#1E2B3A]/30 hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:translate-y-0"
            >
              <div class="flex items-center justify-center gap-2">
                <template v-if="isLoading">
                  <svg
                    class="w-5 h-5 text-white/80 animate-spin"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    />
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  <span>正在注册...</span>
                </template>
                <template v-else>
                  <span>创建账号</span>
                  <svg
                    class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M13.75 6.75L19.25 12L13.75 17.25"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M19 12H4.75"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </template>
              </div>
            </button>
          </form>

          <!-- 登录跳转 -->
          <div class="mt-1 text-center border-t border-gray-200/60 dark:border-gray-700/60">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
              已有账号？
              <router-link
                to="/signin"
                class="text-[#407BBF] hover:text-[#2d5c92] transition-colors font-bold underline-offset-4 hover:underline"
              >
                立即登录
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </main>

    <!-- 右侧动态渐变 Canvas -->
    <div
      class="fixed top-0 right-0 w-[80%] md:w-1/2 h-screen bg-[#1F2B3A]/20"
      :style="{
        clipPath: 'polygon(100px 0,100% 0,calc(100% + 225px) 100%, 480px 100%)',
      }"
    ></div>
    <canvas
      id="gradient-canvas"
      data-transition-in
      class="z-50 fixed top-0 right-[-2px] w-[10%] md:w-1/2 h-screen"
      :style="{
        clipPath: 'polygon(100px 0,100% 0,calc(100% + 225px) 100%, 300px 100%)',
      }"
    ></canvas>

    <div
      class="h-[20px] bg-[#1D2B3A] fixed bottom-0 z-20 w-full flex flex-row items-center justify-evenly"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { getApiUrl } from '@/config/api'
import { useAppStore } from '@/store/app'

const appStore = useAppStore()
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { gradient } from '@/components/Gradient' // 导入WebGL渐变控制器
import axios from 'axios'
// import VueTurnstile from 'vue-turnstile'

const username = ref('')
const email = ref('')
const password = ref('')
const showPassword = ref(false)

const errorMessage = ref('')
const isLoading = ref(false)
const successMessage = ref('') // 新增成功消息提示
const userType = ref('user') // 默认普通用户
const adminCode = ref('') // 管理员注册码
const turnstileToken = ref('')

const router = useRouter()
const showSuccessModal = ref(false)
const countdown = ref(5) // 倒计时 5 秒

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// Turnstile 错误处理函数
// const handleTurnstileError = () => {
//   console.error('Turnstile 验证失败')
//   turnstileToken.value = ''
// }

const handleSubmit = async () => {
  // 重置错误消息
  errorMessage.value = ''
  successMessage.value = ''

  // 表单验证
  if (!username.value || !email.value || !password.value) {
    errorMessage.value = '所有字段都是必填的'
    return
  }

  if (userType.value === 'admin' && !adminCode.value) {
    errorMessage.value = '请输入管理员注册码'
    return
  }

  // 检查 Turnstile 令牌是否有效
  // if (!turnstileToken.value) {
  //   errorMessage.value = '请完成人机验证'
  //   return
  // }

  // 简单的邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }

  // 密码长度验证
  if (password.value.length < 6) {
    errorMessage.value = '密码长度至少为 6 个字符'
    return
  }

  try {
    isLoading.value = true
    successMessage.value = '正在创建您的账号...'

    // 构造 multipart/form-data
    const form = new FormData()
    form.append('username', username.value)
    form.append('password', password.value)
    if (email.value) form.append('email', email.value)
    if (userType.value === 'admin') form.append('admin_code', adminCode.value)
    // form.append('cf_turnstile_response', turnstileToken.value)

    // 发送注册请求
    let response
    if (userType.value === 'user') {
      response = await fetch(getApiUrl('/register'), {
        method: 'POST',
        body: form,
      })

      if (response.status === 201 || response.status === 200) {
        // 注册成功
        showSuccessModal.value = true
        successMessage.value = '注册成功！'

        // 清除 Turnstile 令牌（一次性使用）
        // turnstileToken.value = ''

        // 启动倒计时跳转登录
        const timer = setInterval(() => {
          countdown.value--
          if (countdown.value <= 0) {
            clearInterval(timer)
            redirectToLogin()
          }
        }, 1000)
      } else {
        // 解析错误返回，后端可能返回 JSON
        let errorData: any = null
        try {
          errorData = await response.json()
        } catch (e) {
          errorData = { detail: await response.text() }
        }

        if (response.status === 409) {
          errorMessage.value = errorData.detail || errorData.message || '用户名已经注册'
        } else if (response.status === 400) {
          // 检查是否是 Turnstile 验证无效
          // if (errorData.detail === '验证无效' || errorData.detail?.includes('turnstile')) {
          //   errorMessage.value = '验证已过期，请重新完成人机验证'
          //   // 重置 Turnstile 让用户重新验证
          //   turnstileToken.value = ''
          // } else {
          //   errorMessage.value = errorData.detail || errorData.message || '请求数据无效'
          // }
          errorMessage.value = errorData.detail || errorData.message || '请求数据无效'
        } else {
          errorMessage.value =
            errorData.detail || errorData.message || `注册失败：${response.status}`
        }
      }
    } else {
      try {
        // 导入 AdminAuthService
        const { AdminAuthService } = await import('@/services/adminAuth')
        const response = await AdminAuthService.register(form)

        if (response.code === 200) {
          // 注册成功
          showSuccessModal.value = true
          successMessage.value = '注册成功！'

          // 清除 Turnstile 令牌（一次性使用）
          // turnstileToken.value = ''

          // 启动倒计时跳转登录
          const timer = setInterval(() => {
            countdown.value--
            if (countdown.value <= 0) {
              clearInterval(timer)
              redirectToLogin()
            }
          }, 1000)
        } else {
          throw new Error(response.msg || '注册失败')
        }
      } catch (error: any) {
        if (error.response) {
          const status = error.response.status
          switch (status) {
            case 400:
              // 检查是否是 Turnstile 验证无效
              // if (
              //   error.response.data?.detail === '验证无效' ||
              //   error.response.data?.detail?.includes('turnstile')
              // ) {
              //   errorMessage.value = '验证已过期，请重新完成人机验证'
              //   // 重置 Turnstile 让用户重新验证
              //   turnstileToken.value = ''
              // } else {
              //   errorMessage.value = '请求参数错误，请检查输入'
              // }
              errorMessage.value = '请求参数错误，请检查输入'
              break
            case 409:
              errorMessage.value = '用户名已经注册'
              break
            case 429:
              errorMessage.value = '尝试次数过多，请稍后再试'
              break
            case 500:
              errorMessage.value = '服务器内部错误，请稍后再试'
              break
            default:
              errorMessage.value = '注册失败，请稍后再试'
          }
        } else if (error.request) {
          errorMessage.value = '网络连接失败，请检查网络'
        } else {
          errorMessage.value = error.message || '注册过程中发生错误'
        }
      }
    }
  } catch (error: any) {
    console.error('注册请求失败:', error)
    if (error.response && error.response.data) {
      // 检查是否是 Turnstile 验证无效
      // if (
      //   error.response.data.detail === '验证无效' ||
      //   error.response.data.detail?.includes('turnstile')
      // ) {
      //   errorMessage.value = '验证已过期，请重新完成人机验证'
      //   // 重置 Turnstile 让用户重新验证
      //   turnstileToken.value = ''
      // } else {
      //   errorMessage.value = error.response.data.detail || '网络错误，请稍后重试'
      // }
      errorMessage.value = error.response.data.detail || '网络错误，请稍后重试'
    } else {
      errorMessage.value = '网络错误，请稍后重试'
    }
  } finally {
    isLoading.value = false
  }
}

const redirectToLogin = () => {
  showSuccessModal.value = false
  router.push('/signin')
}

// ---------- WebGL 渐变背景初始化（与文档 1 行为一致）-----------
onMounted(() => {
  // 初始化渐变画布
  gradient.initGradient('#gradient-canvas')

  // console.log('Turnstile 组件已初始化')
})

onUnmounted(() => {
  // 清理渐变资源（gradient内部有disconnect方法）
  if (gradient && typeof gradient.disconnect === 'function') {
    gradient.disconnect()
  }
})
</script>

<style scoped>
/* 渐变画布基础色 */
#gradient-canvas {
  --gradient-color-1: #87cefa;
  --gradient-color-2: #f0f8ff;
  --gradient-color-3: #b0e0e6;
  --gradient-color-4: #e6f7ff;
  background-color: #f8fcff;
}

/* 错误提示淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 进场动画 */
@keyframes slideDownFade {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.title-animation {
  animation: slideDownFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.card-animation {
  animation: slideDownFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: 0.1s;
  animation-fill-mode: backwards;
}
</style>
