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

    <main
      class="relative z-[100] flex flex-col justify-center min-h-screen w-full md:w-[55%] lg:w-[50%] px-6 md:px-12 lg:px-[10%] py-12 md:py-0"
    >
      <h1
        class="title-animation mb-6 md:mb-8 font-extrabold text-5xl md:text-6xl lg:text-7xl font-inter text-[#1E2B3A] leading-tight tracking-tight"
      >
        登录
        <span class="text-[#407BBF]">{{ appStore.appName }}</span>
        <span class="font-inter text-[#407BBF]">.</span>
      </h1>

      <div class="card-animation w-full max-w-lg">
        <div
          class="bg-white/70 dark:bg-gray-900/70 backdrop-blur-2xl rounded-3xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_32px_rgba(0,0,0,0.06)] p-4 sm:p-6 transition-all duration-300"
        >
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

          <form @submit.prevent="handleSubmit" class="space-y-4">
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

            <div class="flex items-center">
              <label
                for="keepLoggedIn"
                class="group flex items-center text-sm font-medium text-gray-600 cursor-pointer select-none hover:text-gray-900 transition-colors dark:text-gray-400 dark:hover:text-gray-200"
              >
                <div class="relative flex items-center justify-center mr-2.5">
                  <input v-model="keepLoggedIn" type="checkbox" id="keepLoggedIn" class="sr-only" />
                  <div
                    :class="
                      keepLoggedIn
                        ? 'border-[#407BBF] bg-[#407BBF]'
                        : 'bg-white/50 border-gray-300 dark:border-gray-600 dark:bg-gray-800/50'
                    "
                    class="flex h-5 w-5 items-center justify-center rounded-md border-[1.5px] transition-all duration-200 group-hover:border-[#407BBF]"
                  >
                    <svg
                      :class="keepLoggedIn ? 'opacity-100 scale-100' : 'opacity-0 scale-50'"
                      class="transition-all duration-200"
                      width="12"
                      height="12"
                      viewBox="0 0 14 14"
                      fill="none"
                    >
                      <path
                        d="M11.6666 3.5L5.24992 9.91667L2.33325 7"
                        stroke="white"
                        stroke-width="2.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </div>
                </div>
                保持登录状态
              </label>
            </div>

            <!-- Cloudflare Turnstile 验证 -->
            <!-- <div class="mt-4">
              <VueTurnstile
                site-key="0x4AAAAAACrSVjKwbFkjLzkZ"
                v-model="turnstileToken"
                @error="handleTurnstileError"
              />
            </div> -->

            <button
              type="submit"
              :disabled="isLoading"
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
                  <span>正在登录...</span>
                </template>
                <template v-else>
                  <span>登录系统</span>
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

          <div class="mt-8 text-center border-t border-gray-200/60 pt-6 dark:border-gray-700/60">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
              还没有账号？
              <router-link
                to="/signup"
                class="text-[#407BBF] hover:text-[#2d5c92] transition-colors font-bold underline-offset-4 hover:underline"
              >
                立即注册
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </main>

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
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { gradient } from '@/components/Gradient'
import { AdminAuthService } from '@/services/adminAuth'
// import VueTurnstile from 'vue-turnstile'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const keepLoggedIn = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const userType = ref('user')
const router = useRouter()
const turnstileToken = ref('')

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// Turnstile 错误处理函数
// const handleTurnstileError = () => {
//   console.error('Turnstile 验证失败')
//   turnstileToken.value = ''
// }

const handleSubmit = async () => {
  errorMessage.value = ''

  // 表单验证
  if (!username.value.trim()) {
    errorMessage.value = '请输入用户名'
    return
  }
  if (!password.value) {
    errorMessage.value = '请输入密码'
    return
  }

  // 检查 Turnstile 令牌是否有效
  // if (!turnstileToken.value) {
  //   errorMessage.value = '请完成人机验证'
  //   return
  // }

  isLoading.value = true
  try {
    if (userType.value === 'user') {
      const form = new FormData()
      form.append('username', username.value)
      form.append('password', password.value)
      // form.append('cf_turnstile_response', turnstileToken.value)

      const response = await axios.post(getApiUrl('/login'), form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      if (response.status === 200) {
        localStorage.setItem('access_token', response.data.access_token)
        localStorage.removeItem('admin_access_token')
        localStorage.setItem('isAuthenticated', 'true')
        localStorage.setItem('username', username.value)
        localStorage.setItem('user_id', response.data.user_id)
        localStorage.setItem('userRole', 'user')

        // 清除 Turnstile 令牌（一次性使用）
        // turnstileToken.value = ''

        ElMessage.success({ message: '登录成功', duration: 1500, showClose: true })
        router.push({ name: 'Welcome' })
      }
    } else {
      const form = new FormData()
      form.append('username', username.value)
      form.append('password', password.value)
      // form.append('cf_turnstile_response', turnstileToken.value)

      const response = await AdminAuthService.login(form)

      if (response.code === 200) {
        const responseAny = response as any
        const adminToken =
          responseAny?.data?.token ||
          responseAny?.data?.access_token ||
          responseAny?.token ||
          responseAny?.access_token ||
          ''

        if (!adminToken) {
          console.error('[AdminSignin] token missing in login response:', response)
          throw new Error('登录成功但未获取到管理员token')
        }

        localStorage.setItem('admin_access_token', adminToken)
        localStorage.setItem('isAuthenticated', 'true')
        localStorage.setItem('username', username.value)
        localStorage.setItem('user_id', response.user_id)
        localStorage.setItem('userRole', 'admin')

        if (keepLoggedIn.value) {
          localStorage.setItem('admin_keep_login', 'true')
        }

        // 清除 Turnstile 令牌（一次性使用）
        // turnstileToken.value = ''

        ElMessage.success({ message: '登录成功', duration: 1500, showClose: true })
        router.push('/admin/users')
      } else {
        throw new Error(response.msg || '登录失败')
      }
    }
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 400:
          // 检查是否是会话令牌无效
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
        case 401:
          errorMessage.value = '用户名或密码错误'
          break
        case 429:
          errorMessage.value = '尝试次数过多，请稍后再试'
          break
        case 500:
          errorMessage.value = '服务器内部错误，请稍后再试'
          break
        default:
          errorMessage.value = '登录失败，请稍后再试'
      }
    } else if (error.request) {
      errorMessage.value = '网络连接失败，请检查网络'
    } else {
      errorMessage.value = error.message || '登录过程中发生错误'
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  // 初始化渐变画布
  if (gradient && typeof gradient.initGradient === 'function') {
    gradient.initGradient('#gradient-canvas')
  }

  // console.log('Turnstile 组件已初始化')
})

onUnmounted(() => {
  // 清理渐变资源
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
