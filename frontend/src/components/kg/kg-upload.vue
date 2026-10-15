<template>
  <div
    class="vector-database-upload p-6 bg-gray-50 dark:bg-gray-900 min-h-screen min-w-[800px]"
    @dragover.prevent
    @dragenter.prevent
    @drop.prevent
  >
    <!-- 标题区域 -->
    <div class="text-center mb-8">
      <h2
        class="text-2xl font-bold text-orange-500 dark:text-orange-400 flex items-center justify-center"
      >
        知识图谱文件上传
      </h2>
    </div>

    <!-- 主内容区域 -->
    <div class="max-w-5xl mx-auto space-y-6">
      <!-- 加载动画 -->
      <div v-if="isBuilding" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fade-in">
        <div class="flex flex-col items-center mb-20">
          <div class="w-12 h-12 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin mb-4"></div>
          <div class="loading-text text-white text-lg font-medium animate-pulse">正在处理文件并导入图谱，请稍候...</div>
        </div>
      </div>

      <!-- 状态提示 -->
      <div
        v-if="uploadStatus.show"
        class="fixed top-4 right-4 z-50 max-w-md animate-slide-in"
        :class="{
          'bg-green-500': uploadStatus.type === 'success',
          'bg-red-500': uploadStatus.type === 'error',
          'bg-blue-500': uploadStatus.type === 'info'
        }"
      >
        <div class="flex items-center p-4 text-white rounded-lg shadow-lg">
          <i
            class="mr-3 text-xl"
            :class="{
              'fas fa-check-circle': uploadStatus.type === 'success',
              'fas fa-exclamation-circle': uploadStatus.type === 'error',
              'fas fa-info-circle': uploadStatus.type === 'info'
            }"
          ></i>
          <div class="flex-1">
            <p class="font-medium">{{ uploadStatus.message }}</p>
          </div>
          <button
            @click="closeUploadStatus"
            class="ml-3 text-white hover:text-gray-200 transition-colors"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      <!-- 领域名称输入框区域 -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-orange-100 dark:border-orange-900 mb-4">
        <div class="flex items-center justify-between mb-4">
          <label for="domain-input" class="text-lg font-semibold text-orange-500 dark:text-orange-400 flex-shrink-0">
            主题名称
          </label>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            <i class="fas fa-info-circle mr-1"></i>
            <span v-if="isAdmin">管理员模式：数据将作为公共数据共享</span>
            <span v-else>普通用户模式：数据将归属于您的账户</span>
          </div>
        </div>
        <input
          id="domain-input"
          v-model="domainName"
          type="text"
          placeholder="请输入图数据的主题名称，如：Java面试题、Python基础等"
          class="w-full px-4 py-2 rounded-lg border border-orange-200 dark:border-orange-700 focus:outline-none focus:border-orange-400 dark:focus:border-orange-500 bg-orange-50/30 dark:bg-orange-900/30 text-gray-800 dark:text-white transition-colors shadow-sm"
        />
      </div>
  <!-- 文件上传区域 -->
      <!-- 关键修改 1: 添加 relative 定位 -->
      <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-orange-100 dark:border-orange-900 hover:shadow-md transition-shadow relative min-h-100"
      >
        <h3
          class="text-lg font-semibold mb-4 flex items-center text-orange-500 dark:text-orange-400"
        >
          <FileUploadIcon class="w-10 h-10 mr-2 text-orange-500 dark:text-orange-400" />
          文件上传
        </h3>

        <div
          class="upload-drop-zone p-8 border-2 border-dashed border-orange-200 dark:border-orange-700 rounded-lg hover:border-orange-400 dark:hover:border-orange-500 transition-colors bg-orange-50/30 dark:bg-orange-900/30"
          @dragover.prevent
          @dragenter.prevent
          @drop.prevent.stop="handleFileDrop"
        >
          <div class="flex flex-col items-center justify-center">
            <File_2 class="w-16 h-16 mb-6" />
            <div class="flex items-center space-x-4 mb-4">
              <p class="text-orange-600 dark:text-orange-400 font-medium">拖拽文件到此处或</p>
              <button
                class="bg-orange-500 dark:bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-600 dark:hover:bg-orange-700 transition-colors shadow-sm hover:shadow-md"
                @click="$refs.fileInput.click()"
              >
                选择文件
              </button>
            </div>
            <input
              type="file"
              ref="fileInput"
              class="hidden"
              @change="handleFileSelect"
              accept=".csv,.docx,.txt,.xlsx"
              multiple
            />
            <p class="text-sm text-orange-400 dark:text-orange-500">
              支持的文件格式：CSV、DOCX、TXT、XLSX
            </p>
          </div>
        </div>

        <!-- 文件列表 -->
        <div v-if="uploadedFiles.length > 0" class="mt-6">
          <div class="flex justify-between items-center mb-4">
            <h4 class="font-medium text-gray-700 dark:text-gray-300 flex items-center">
              <i class="fas fa-file-alt mr-2 text-orange-500"></i>
              已上传文件
            </h4>
            <button
              class="text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-500 flex items-center"
              @click="removeAllFiles"
            >
              <i class="fas fa-trash-alt mr-1"></i>
              删除全部
            </button>
          </div>
          <div class="space-y-3">
            <div
              v-for="file in uploadedFiles"
              :key="file.id"
              class="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-indigo-200 transition-all relative group"
              @mouseenter="showPreview(file)"
              @mouseleave="hidePreview"
            >
              <div class="flex items-center">
                <div>
                  <p class="font-medium text-gray-800 dark:text-white">{{ file.name }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    <i class="far fa-clock mr-1"></i>
                    {{ file.uploadTime }}
                  </p>
                </div>
              </div>
              <button
                class="text-red-400 hover:text-red-500 dark:text-red-300 dark:hover:text-red-400 transition-colors"
                @click="removeFile(file.id)"
              >
                <i class="fas fa-trash-alt"></i>
              </button>

              <!-- 文件预览弹窗 -->
              <div
                v-if="previewFile?.id === file.id"
                class="absolute left-full ml-4 top-0 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 transition-opacity duration-300 z-10"
                :class="{ 'opacity-100': isPreviewVisible, 'opacity-0': !isPreviewVisible }"
              >
                <div class="text-sm">
                  <h5 class="font-bold mb-2 text-gray-800 dark:text-white">文件详情</h5>
                  <p>
                    <span class="text-gray-500 dark:text-gray-300">文件名：</span>{{ file.name }}
                  </p>
                  <p>
                    <span class="text-gray-500 dark:text-gray-300">类型：</span
                    >{{ file.type.toUpperCase() }}
                  </p>
                  <p>
                    <span class="text-gray-500 dark:text-gray-300">上传时间：</span
                    >{{ file.uploadTime }}
                  </p>
                  <p>
                    <span class="text-gray-500 dark:text-gray-300">大小：</span
                    >{{ formatFileSize(file.file.size) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 处理结果表格展示 -->
        <div v-if="resultData && resultData.csv_data && resultData.csv_data.length > 0" class="mt-8">
          <h3 class="text-lg font-semibold mb-4 text-orange-500 dark:text-orange-400">处理结果预览</h3>
          <div class="overflow-x-auto rounded-xl shadow border border-orange-100 dark:border-orange-900 bg-white dark:bg-gray-800">
            <table class="min-w-full divide-y divide-orange-200 dark:divide-orange-700">
              <thead class="bg-orange-50 dark:bg-orange-900">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-orange-600 dark:text-orange-400">题库主题</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-orange-600 dark:text-orange-400">题目标题</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-orange-600 dark:text-orange-400">题目内容</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-orange-600 dark:text-orange-400">参考答案</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-orange-600 dark:text-orange-400">标签</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-orange-100 dark:divide-orange-900">
                <tr v-for="(row, idx) in resultData.csv_data" :key="idx" class="hover:bg-orange-50 dark:hover:bg-orange-900">
                  <td class="px-4 py-2 text-gray-700 dark:text-gray-200">{{ row.Topic }}</td>
                  <td class="px-4 py-2 text-gray-700 dark:text-gray-200">{{ row.title }}</td>
                  <td class="px-4 py-2 text-gray-700 dark:text-gray-200">{{ row.content }}</td>
                  <td class="px-4 py-2 text-gray-700 dark:text-gray-200">{{ row.answer }}</td>
                  <td class="px-4 py-2 text-gray-700 dark:text-gray-200">{{ row.Tag }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="absolute top-4 right-4">
          <button
            class="bg-orange-500 dark:bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-600 dark:hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105 active:scale-95 shadow-sm hover:shadow-md flex items-center text-sm"
            :disabled="!canBuildIndex || isBuilding"
            @click="goToUpload"
          >
            {{ isBuilding ? '上传中...' : '确认上传' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import dayjs from 'dayjs'
import FileUploadIcon from '@/icons/FileUploadIcon.vue'
import Setting from '@/icons/Setting.vue'
import Preview from '@/icons/Preview.vue'
import File_2 from '@/icons/File_2.vue'
import { getApiUrl } from '@/config/api'

export default {
  name: 'KG-Upload',
  components: {
    FileUploadIcon,
    Setting,
    Preview,
    File_2,
  },
  setup() {
    const uploadedFiles = ref([])
    const isBuilding = ref(false)
    const domainName = ref("")
    const resultData = ref(null)
    const uploadStatus = ref({
      show: false,
      type: 'success',
      message: '',
      timer: null,
    })
    const getFileIcon = (type) => {
      const iconMap = {
        pdf: 'fas fa-file-pdf',
        docx: 'fas fa-file-word',
        txt: 'fas fa-file-alt',
      }
      return iconMap[type] || 'fas fa-file'
    }

    const previewFile = ref(null)
    const isPreviewVisible = ref(false)
    let previewTimer = null
    const canBuildIndex = computed(() => {
      return uploadedFiles.value.length > 0 && !isBuilding.value
    })

    const isAdmin = computed(() => {
      return localStorage.getItem('userRole') === 'admin'
    })
    // 添加文件预览相关的方法
    const showPreview = (file) => {
      previewFile.value = file
      // 延迟显示以实现渐入效果
      setTimeout(() => {
        isPreviewVisible.value = true
      }, 100)
    }

    const hidePreview = () => {
      isPreviewVisible.value = false
      // 延迟清除预览文件以确保渐出动画完成
      setTimeout(() => {
        previewFile.value = null
      }, 300)
    }

    // 添加文件图标颜色方法
    const getFileIconColor = (type) => {
      const colorMap = {
        pdf: 'text-red-500',
        docx: 'text-blue-500',
        txt: 'text-gray-500',
        csv: 'text-green-500',
        xlsx: 'text-green-600',
      }
      return colorMap[type] || 'text-gray-500'
    }

    // 添加文件大小格式化方法
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
    }

    const handleFileDrop = (event) => {
      event.preventDefault()
      const files = Array.from(event.dataTransfer.files)
      processFiles(files)
    }

    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      processFiles(files)
    }

    const processFiles = (files) => {
      files.forEach((file) => {
        const extension = file.name.split('.').pop().toLowerCase()
        if (['csv', 'docx', 'txt', 'xlsx'].includes(extension)) {
          const fileObj = {
            id: Date.now() + Math.random(),
            name: file.name,
            type: extension,
            uploadTime: dayjs().format('YYYY-MM-DD HH:mm'),
            file: file,
          }
          uploadedFiles.value.push(fileObj)
          showUploadStatus('success', `上传成功：${file.name}`)
        } else {
          showUploadStatus('error', `上传失败：不支持的文件格式`)
        }
      })
    }

    const removeFile = (id) => {
      uploadedFiles.value = uploadedFiles.value.filter((file) => file.id !== id)
    }

    const removeAllFiles = () => {
      uploadedFiles.value = []
    }

    const showUploadStatus = (type, message) => {
      if (uploadStatus.value.timer) {
        clearTimeout(uploadStatus.value.timer)
      }
      uploadStatus.value = {
        show: true,
        type,
        message,
        timer: setTimeout(() => {
          uploadStatus.value.show = false
        }, 3000),
      }
    }

    const closeUploadStatus = () => {
      if (uploadStatus.value.timer) {
        clearTimeout(uploadStatus.value.timer)
      }
      uploadStatus.value.show = false
    }

    // 上传方法
    const goToUpload = async () => {
      if (!domainName.value) {
        showUploadStatus('error', '请填写题目领域名称')
        return
      }
      if (uploadedFiles.value.length === 0) {
        showUploadStatus('error', '请先选择文件')
        return
      }
      isBuilding.value = true
      resultData.value = null
      try {
        // 获取用户ID和角色信息
        const userId = localStorage.getItem('user_id')
        const isAdmin = localStorage.getItem('userRole') === 'admin'

        if (!userId) {
          throw new Error('未获取到用户ID，请重新登录')
        }

        // 只上传第一个文件，如需批量可遍历
        const fileObj = uploadedFiles.value[0]
        const formData = new FormData()
        formData.append('Topic', domainName.value)
        formData.append('file', fileObj.file)
        formData.append('user_id', userId)
        formData.append('is_admin', isAdmin.toString())

        console.log('上传文件到图谱:', {
          Topic: domainName.value,
          fileName: fileObj.name,
          userId: userId,
          isAdmin: isAdmin
        })

        const response = await fetch(getApiUrl('/graph/upload'), {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`上传失败: HTTP ${response.status} - ${errorText}`)
        }

        const result = await response.json()
        console.log('上传结果:', result)

        if (result.success) {
          resultData.value = result
          showUploadStatus('success', `上传成功！处理了 ${result.csv_data?.length || 0} 条数据`)
          // 清空文件列表
          uploadedFiles.value = []
          domainName.value = ''
        } else {
          throw new Error('服务器处理失败')
        }
      } catch (err) {
        console.error('上传失败:', err)
        showUploadStatus('error', err.message || '上传失败')
      } finally {
        isBuilding.value = false
      }
    }
    return {
      uploadedFiles,
      isBuilding,
      domainName,
      uploadStatus,
      resultData,
      // 添加所有在模板中使用的变量和函数
      canBuildIndex,
      isAdmin,
      previewFile,
      isPreviewVisible,
      showPreview,
      hidePreview,
      getFileIconColor,
      formatFileSize,
      getFileIcon,
      handleFileDrop,
      handleFileSelect,
      removeFile,
      removeAllFiles,
      closeUploadStatus,
      goToUpload,
    }
  },
}
</script>

<style scoped>
.upload-drop-zone {
  min-height: 200px;
}

.form-range {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  background: #ddd;
  border-radius: 2px;
  outline: none;
}

.form-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}
</style>

<style scoped>
.upload-drop-zone {
  min-height: 200px;
}

.custom-range {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  outline: none;
}

.custom-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #10b981;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.custom-range::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  background: #059669;
}

/* 添加过渡效果 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* 添加动画效果 */
@keyframes bounce {
  0%,
  100% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-bounce {
  animation: bounce 1s infinite;
}

.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* 添加阴影过渡效果 */
.hover\:shadow-md:hover {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>

<style scoped>
.custom-range {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  outline: none;
}

.custom-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #10b981;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

/* Dark mode styles */
:root.dark .custom-range {
  background: #374151;
}

:root.dark .custom-range::-webkit-slider-thumb {
  background: #059669;
  border-color: #1f2937;
}

/* Other styles remain unchanged */
</style>
