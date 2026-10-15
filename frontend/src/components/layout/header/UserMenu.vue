<template>
  <div class="relative" ref="dropdownRef">
    <button
      class="flex items-center text-gray-700 dark:text-gray-400"
      @click.prevent="toggleDropdown"
    >
      <span class="mr-3 overflow-hidden rounded-full h-11 w-11">
        <img src="/images/example-user-image.png" alt="User" />
      </span>

      <span class="block mr-1 font-medium text-theme-sm">{{ userInfo.username }}</span>

      <ChevronDownIcon :class="{ 'rotate-180': dropdownOpen }" />
    </button>

    <!-- Dropdown Start -->
    <div
      v-if="dropdownOpen"
      class="absolute right-0 mt-[17px] flex w-[260px] flex-col rounded-2xl border border-gray-200 bg-white p-3 shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark"
    >
      <div class="ml-3">
        <span class="block font-medium text-gray-700 text-theme-sm dark:text-gray-400">
          {{ username }}
        </span>
        <span
          v-if="userInfo.name"
          class="mt-0.5 block text-theme-xs text-gray-500 dark:text-gray-400"
        >
          姓名： {{ userInfo.name }}
        </span>
        <span
          v-if="userInfo.gender && userInfo.gender !== '未知'"
          class="mt-0.5 block text-theme-xs text-gray-500 dark:text-gray-400"
        >
          性别：{{ userInfo.gender }}
        </span>

        <span
          v-if="userInfo.age > 0"
          class="mt-0.5 block text-theme-xs text-gray-500 dark:text-gray-400"
        >
          年龄：{{ userInfo.age }}岁
        </span>
        <span
          v-if="userInfo.university"
          class="mt-0.5 block text-theme-xs text-gray-500 dark:text-gray-400"
        >
          大学： {{ userInfo.university }}
        </span>
        <span
          v-if="userInfo.major"
          class="mt-0.5 block text-theme-xs text-gray-500 dark:text-gray-400"
        >
          专业： {{ userInfo.major }}
        </span>
      </div>

      <!-- 添加个人信息按钮 -->
      <button
        v-if="!isAdmin"
        @click="openProfileForm"
        class="flex dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300 items-center gap-3 px-3 py-2 mt-1 font-medium text-gray-700 rounded-lg group text-theme-sm hover:bg-gray-100"
      >
        <UserCircleIcon class="text-gray-500 group-hover:text-gray-700" />
        修改个人信息
      </button>

      <!-- 更新人脸照片按钮（已注释停用）
      <button
        @click="openFaceDialog"
        class="flex dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300 items-center gap-3 px-3 py-2 mt-1 font-medium text-gray-700 rounded-lg group text-theme-sm hover:bg-gray-100"
      >
        <Icon icon="mdi:face-recognition" class="text-gray-500 group-hover:text-gray-700 w-5 h-5" />
        更新人脸照片
      </button>
      -->

      <button
        @click="handleSignOut"
        class="flex items-center gap-3 px-3 py-2 mt-1 font-medium text-gray-700 rounded-lg group text-theme-sm hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300"
      >
        <LogoutIcon
          class="text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300"
        />
        退出登录
      </button>
    </div>

    <!-- 个人信息表单弹窗 -->
    <el-dialog v-model="showProfileForm" title="编辑个人信息" width="30%">
      <el-form :model="profileForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="profileForm.name" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="profileForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
            <el-radio label="未知">未知</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input v-model.number="profileForm.age" type="number" min="0" max="150" />
        </el-form-item>
        <el-form-item label="大学">
          <el-input v-model="profileForm.university" />
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="profileForm.major" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showProfileForm = false">取消</el-button>
          <el-button type="primary" @click="submitProfile">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 人脸照片更新弹窗（已注释停用）
    <el-dialog v-model="showFaceDialog" title="更新人脸照片" width="60%" :before-close="handleFaceDialogClose" class="face-dialog">
      <div class="flex flex-col md:flex-row gap-6 items-start">
        <div class="w-full md:w-1/2 bg-gray-50 dark:bg-gray-800 rounded-2xl p-5 shadow-md">
          <div class="mb-3 font-bold text-lg text-gray-800 dark:text-gray-200">当前人脸照片</div>
          <div class="flex items-center justify-center h-64 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-2xl bg-white dark:bg-gray-900">
            <template v-if="faceLoading">
              <div class="text-theme-sm text-gray-500 flex flex-col items-center">
                <svg class="animate-spin h-8 w-8 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                加载中...
              </div>
            </template>
            <template v-else>
              <img v-if="faceImageUrl" :src="faceImageUrl" alt="face" class="max-h-60 rounded-xl object-contain shadow-md" />
              <div v-else class="text-center text-theme-sm text-gray-500 p-4">
                <svg class="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
                暂时没有人脸识别照片，请上传。
              </div>
            </template>
          </div>
        </div>

        <div class="w-full md:w-1/2 bg-gray-50 dark:bg-gray-800 rounded-2xl p-5 shadow-md">
          <div class="mb-3 font-bold text-lg text-gray-800 dark:text-gray-200">拍照上传</div>
          <div class="flex flex-col gap-4">
            <video v-show="cameraActive" ref="videoRef" autoplay playsinline class="rounded-2xl border-2 border-gray-300 dark:border-gray-600 shadow-md w-full h-60 object-cover bg-black"></video>
            <div v-show="!cameraActive" class="rounded-2xl border-2 border-gray-300 dark:border-gray-600 shadow-md w-full h-60 bg-black"></div>
            <canvas ref="canvasRef" class="hidden"></canvas>
            <div class="flex flex-wrap gap-2 justify-center">
              <button
                :disabled="cameraActive || faceUploading"
                @click="startCamera"
                class="px-5 py-2.5 rounded-xl bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                :class="{ 'opacity-50 cursor-not-allowed': cameraActive || faceUploading }"
              >
                <svg class="w-5 h-5 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                打开摄像头
              </button>
              <button
                :disabled="!cameraActive || faceUploading"
                @click="capturePhoto"
                class="px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-medium transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transform hover:-translate-y-0.5"
                :class="{ 'opacity-50 cursor-not-allowed': !cameraActive || faceUploading }"
              >
                <svg class="w-5 h-5 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                拍摄
              </button>
              <button
                @click="stopCamera"
                :disabled="!cameraActive"
                class="px-5 py-2.5 rounded-xl bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                :class="{ 'opacity-50 cursor-not-allowed': !cameraActive }"
              >
                <svg class="w-5 h-5 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"></path>
                </svg>
                停止
              </button>
            </div>

            <div v-if="previewDataUrl" class="mt-2">
              <div class="mb-2 font-medium text-gray-700 dark:text-gray-300">预览：</div>
              <div class="border-2 border-gray-300 dark:border-gray-600 rounded-2xl p-3 bg-white dark:bg-gray-900">
                <img :src="previewDataUrl" alt="preview" class="max-h-44 rounded-xl border shadow-md mx-auto" />
                <div class="mt-4 flex flex-wrap gap-2 justify-center">
                  <button
                    :loading="faceUploading"
                    @click="uploadFacePhoto"
                    class="px-5 py-2.5 rounded-xl bg-green-500 hover:bg-green-600 text-white font-medium transition-all duration-200 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                  >
                    <svg v-if="!faceUploading" class="w-5 h-5 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <svg v-else class="animate-spin h-5 w-5 inline mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ faceUploading ? '上传中...' : '上传照片' }}
                  </button>
                  <button
                    @click="clearPreview"
                    class="px-5 py-2.5 rounded-xl bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium transition-all duration-200 shadow-md hover:shadow-lg"
                  >
                    <svg class="w-5 h-5 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1v3M4 7h16"></path>
                    </svg>
                    取消
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer flex justify-end">
          <button
            @click="showFaceDialog = false"
            class="px-6 py-2.5 rounded-xl bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium transition-all duration-200 shadow-md hover:shadow-lg"
          >
            关闭
          </button>
        </span>
      </template>
    </el-dialog>
    -->
  </div>
</template>

<script setup>
import { UserCircleIcon, ChevronDownIcon, LogoutIcon, SettingsIcon, InfoCircleIcon } from '@/icons'
// import { Icon } from '@iconify/vue'
import { RouterLink } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { getApiUrl } from '@/config/api'
import {
  ElMessage,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElButton,
  ElDialog,
} from 'element-plus'
import axios from 'axios'

const { logout } = useAuth()
const dropdownOpen = ref(false)
const dropdownRef = ref(null)

const isAdmin = localStorage.getItem('userRole') === 'admin'

const showProfileForm = ref(false)
const username = localStorage.getItem('username')
const userInfo = ref({
  username: '',
  name: '',
  gender: '',
  age: '',
  university: '',
  major: '',
})

const profileForm = ref({
  name: '',
  gender: '',
  age: '',
  university: '',
  major: '',
})

const openProfileForm = () => {
  showProfileForm.value = true
}

const genderMap = {
  男: 1,
  女: 2,
  未知: 0,
}

const genderReverseMap = {
  1: '男',
  2: '女',
  0: '未知',
}

const transformFormData = (formData) => {
  return {
    ...formData,
    age: formData.age ? parseInt(formData.age) : 0,
    gender: genderMap[formData.gender] ?? 0, // 字符串转整数
  }
}
const submitProfile = async () => {
  if (profileForm.value.age && (isNaN(profileForm.value.age) || profileForm.value.age < 0)) {
    ElMessage.error('年龄必须是有效的正数')
    return
  }
  try {
    const username = localStorage.getItem('username')
    const transformedData = transformFormData(profileForm.value)
    const response = await axios.put(getApiUrl('/update-profile'), {
      username: username,
      ...transformedData,
    })

    if (response.status === 200) {
      ElMessage.success('个人信息更新成功')
      // 保持 userInfo 中 gender 为中文字符串（用于展示）
      userInfo.value = {
        ...userInfo.value,
        ...profileForm.value, // profileForm 中 gender 已是中文字符串
      }
      showProfileForm.value = false
    }
  } catch (error) {
    ElMessage.error('更新失败：' + error.message)
  }
}

const getUserProfile = async () => {
  const username = localStorage.getItem('username')
  if (username) {
    userInfo.value.username = username
    try {
      const isAdmin = localStorage.getItem('userRole') === 'admin'
      const response = await axios.get(getApiUrl(`/user-profile/${username}?isAdmin=${isAdmin}`))

      if (response.status === 200) {
        // 修复 1：FastAPI 返回的数据直接在 response.data 中，不需要再 .data
        const raw = response.data || {}

        const userData = {
          ...raw,
          // 修复 2：兼容处理。如果后端传来的是数字，用 map 转换；如果是字符串，直接使用
          gender:
            typeof raw.gender === 'number'
              ? (genderReverseMap[raw.gender] ?? '未知')
              : raw.gender || '未知',
        }

        userInfo.value = { ...userInfo.value, ...userData }
        profileForm.value = { ...userData }
      }
    } catch (error) {
      ElMessage.error('获取用户信息失败：' + error.message)
    }
  }
}

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

const closeDropdown = () => {
  dropdownOpen.value = false
}

const handleSignOut = () => {
  logout()
  closeDropdown()
}

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    closeDropdown()
  }
}

onMounted(() => {
  getUserProfile()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// ----------------- 人脸照片逻辑（已注释停用） -----------------
// const showFaceDialog = ref(false)
// const faceImageUrl = ref('')
// const faceLoading = ref(false)
// const faceUploading = ref(false)
//
// const videoRef = ref(null)
// const canvasRef = ref(null)
// let mediaStream = null
// const cameraActive = ref(false)
// const previewDataUrl = ref('')
//
// const openFaceDialog = async () => {
//   showFaceDialog.value = true
//   await fetchFaceImage()
// }
//
// const handleFaceDialogClose = () => {
//   stopCamera()
//   showFaceDialog.value = false
// }
//
// const fetchFaceImage = async () => {
//   // 尝试从多个位置获取 userid，增加回退与日志以便调试
//   // 支持两种 localStorage 键：'userid' 和 'user_id'（不同页面可能使用不同命名）
//   let userid = localStorage.getItem('userid') || localStorage.getItem('user_id')
//   if (!userid && userInfo && userInfo.value) {
//     // 常见后端字段名回退：userid / user_id / id
//     userid = userInfo.value.userid || userInfo.value.user_id || userInfo.value.id || ''
//   }
//
//   if (!userid) {
//     // 在无法获得 userid 时记录详细信息，避免静默失败
//     // 这将帮助开发者在浏览器控制台中快速定位问题
//     // 例如：localStorage 中没有 userid，或 getUserProfile 还未完成
//     // 不发出网络请求以避免无效的后端调用
//     // eslint-disable-next-line no-console
//     console.warn('[UserMenu] fetchFaceImage: missing userid, skipping request', {
//       localStorage_userid: localStorage.getItem('userid'),
//       localStorage_user_id: localStorage.getItem('user_id'),
//       userInfo: userInfo ? userInfo.value : null,
//     })
//     faceImageUrl.value = ''
//     return
//   }
//
//   // 判断是否为管理员
//   const isAdmin = localStorage.getItem('userRole') === 'admin'
//
//   faceLoading.value = true
//   // 调试信息：将要请求的完整 URL
//   // eslint-disable-next-line no-console
//   console.debug('[UserMenu] fetchFaceImage: fetching face image for userid', userid, 'isAdmin:', isAdmin)
//   try {
//     const resp = await axios.get(`http://localhost:8000/api/face/face-photo/${userid}?is_admin=${isAdmin}`, { responseType: 'blob' })
//     if (resp.status === 200 && resp.data && resp.data.size > 0) {
//       const url = URL.createObjectURL(resp.data)
//       faceImageUrl.value = url
//     } else {
//       faceImageUrl.value = ''
//     }
//   } catch (err) {
//     // 如果后端返回404或没有图片也进入这里
//     // eslint-disable-next-line no-console
//     console.error('[UserMenu] fetchFaceImage: request failed', err)
//     faceImageUrl.value = ''
//   } finally {
//     faceLoading.value = false
//   }
// }
//
// const startCamera = async () => {
//   try {
//     mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
//     if (videoRef.value) {
//       videoRef.value.srcObject = mediaStream;
//       cameraActive.value = true;
//       // 确保视频开始播放
//       try {
//         await videoRef.value.play();
//         videoRef.value.onloadeddata = () => {
//           cameraActive.value = true; // 确保摄像头状态更新
//         };
//       } catch (playError) {
//         console.warn('视频播放失败:', playError);
//       }
//     }
//   } catch (err) {
//     ElMessage.error('无法打开摄像头：' + (err.message || err));
//   }
// }
//
// const stopCamera = () => {
//   if (mediaStream) {
//     mediaStream.getTracks().forEach((t) => t.stop())
//     mediaStream = null
//   }
//   cameraActive.value = false
// }
//
// const capturePhoto = () => {
//   if (!videoRef.value) return
//   const video = videoRef.value
//   const canvas = canvasRef.value || document.createElement('canvas')
//   canvas.width = video.videoWidth || 640
//   canvas.height = video.videoHeight || 480
//   const ctx = canvas.getContext('2d')
//   ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
//   const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
//   previewDataUrl.value = dataUrl
// }
//
// const clearPreview = () => {
//   previewDataUrl.value = ''
// }
//
// const uploadFacePhoto = async () => {
//   if (!previewDataUrl.value) {
//     ElMessage.warning('请先拍摄照片')
//     return
//   }
//   faceUploading.value = true
//   try {
//     const blob = dataURLtoBlob(previewDataUrl.value)
//     const form = new FormData()
//     // 优先从 localStorage 获取 userid，若没有则回退到 userInfo 中的字段
//     // 支持 localStorage 中 user_id（HistoryView 使用）或 userid
//     let userid = localStorage.getItem('userid') || localStorage.getItem('user_id')
//     if (!userid && userInfo && userInfo.value) {
//       userid = userInfo.value.userid || userInfo.value.user_id || userInfo.value.id || ''
//     }
//
//     if (!userid) {
//       // eslint-disable-next-line no-console
//       console.warn('[UserMenu] uploadFacePhoto: userid is null or empty, aborting upload', {
//         localStorage_userid: localStorage.getItem('userid'),
//         localStorage_user_id: localStorage.getItem('user_id'),
//         userInfo: userInfo ? userInfo.value : null,
//       })
//       ElMessage.error('无法获取用户 ID，无法上传人脸照片')
//       faceUploading.value = false
//       return
//     }
//
//     // 判断是否为管理员
//     const isAdmin = localStorage.getItem('userRole') === 'admin'
//
//     form.append('userid', userid)
//     form.append('face', blob, 'face.jpg')
//     form.append('is_admin', isAdmin.toString())
//
//     // 调试：记录将要发送的 userid 与 URL
//     // eslint-disable-next-line no-console
//     console.debug('[UserMenu] uploadFacePhoto: uploading face for userid', userid, 'isAdmin:', isAdmin)
//
//     // 后端会返回处理后的二进制图片流（最新图片），我们直接将其用于预览
//     const resp = await axios.post('http://localhost:8000/api/face/face-photo', form, {
//       headers: { 'Content-Type': 'multipart/form-data' },
//       responseType: 'blob',
//     })
//
//     if ((resp.status === 200 || resp.status === 201) && resp.data && resp.data.size > 0) {
//       ElMessage.success('上传成功')
//       // 使用后端返回的二进制流直接更新展示
//       const url = URL.createObjectURL(resp.data)
//       faceImageUrl.value = url
//       // 清除预览
//       previewDataUrl.value = ''
//     } else {
//       ElMessage.error('上传失败')
//     }
//   } catch (err) {
//     ElMessage.error('上传失败：' + (err.message || err))
//   } finally {
//     faceUploading.value = false
//   }
// }
//
// function dataURLtoBlob(dataurl) {
//   const arr = dataurl.split(',')
//   const mime = arr[0].match(/:(.*?);/)[1]
//   const bstr = atob(arr[1])
//   let n = bstr.length
//   const u8arr = new Uint8Array(n)
//   while (n--) {
//     u8arr[n] = bstr.charCodeAt(n)
//   }
//   return new Blob([u8arr], { type: mime })
// }
</script>

<style scoped>
.el-radio /deep/ .el-radio__label {
  font-size: 16px;
}

.el-form-item /deep/ .el-form-item__label {
  padding: 0 30px 0 0;
}

/* 添加人脸对话框的样式 */
.face-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #e5e7eb;
  padding: 20px 20px 15px;
}

.face-dialog :deep(.el-dialog__title) {
  font-weight: 600;
  font-size: 18px;
}

.face-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.face-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid #e5e7eb;
  padding: 15px 20px;
}

@media (max-width: 768px) {
  .face-dialog :deep(.el-dialog) {
    width: 90% !important;
    margin-top: 20px !important;
  }

  .face-dialog :deep(.el-dialog__body) {
    padding: 15px;
  }
}
</style>
