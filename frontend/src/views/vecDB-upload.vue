<template>
  <div class="vector-database-upload p-6 bg-gray-50 dark:bg-gray-900 min-h-screen min-w-[800px]">
    <!-- 标题区域 -->
    <div class="text-center mb-8">
      <h2
        class="text-2xl font-bold text-indigo-700 dark:text-indigo-400 flex items-center justify-center"
      >
        向量数据库文件上传
      </h2>
    </div>

    <!-- 主内容区域 -->
    <div class="max-w-5xl mx-auto space-y-6">
      <!-- 文件上传区域 -->
      <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-indigo-100 dark:border-indigo-900 hover:shadow-md transition-shadow relative"
      >
        <h3
          class="text-lg font-semibold mb-4 flex items-center text-indigo-700 dark:text-indigo-400"
        >
          <FileUploadIcon class="w-10 h-10 mr-2" />
          文件上传
        </h3>

        <div
          class="upload-drop-zone p-8 border-2 border-dashed border-indigo-200 dark:border-indigo-700 rounded-lg hover:border-indigo-400 dark:hover:border-indigo-500 transition-colors bg-indigo-50/30 dark:bg-indigo-900/30"
        >
          <div class="flex flex-col items-center justify-center">
            <File class="w-16 h-16 mb-6" />
            <div class="flex items-center space-x-4 mb-4">
              <p class="text-indigo-600 dark:text-indigo-400 font-medium">拖拽文件到此处或</p>
              <button
                class="bg-indigo-500 dark:bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-600 dark:hover:bg-indigo-700 transition-colors shadow-sm hover:shadow-md"
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
              accept=".txt,.pdf,.doc,.docx,.json,.jsonl"
              multiple
            />
            <p class="text-sm text-indigo-400 dark:text-indigo-500">
              支持的文件格式：TXT, PDF, Word, JSON, JSONL
            </p>
          </div>
        </div>

        <!-- 文件列表 -->
        <div v-if="uploadedFiles.length > 0" class="mt-6">
          <div class="flex justify-between items-center mb-4">
            <h4 class="font-medium text-gray-700 dark:text-gray-300 flex items-center">
              <i class="fas fa-file-alt mr-2 text-indigo-500"></i>
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
                <i
                  :class="[getFileIcon(file.type), 'text-2xl mr-4', getFileIconColor(file.type)]"
                ></i>
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
                    <span class="text-gray-500 dark:text-gray-300">类型：</span>
                    {{ getFileTypeName(file.type) }}
                  </p>
                  <p>
                    <span class="text-gray-500 dark:text-gray-300">上传时间：</span>
                    {{ file.uploadTime }}
                  </p>
                  <p>
                    <span class="text-gray-500 dark:text-gray-300">大小：</span>
                    {{ formatFileSize(file.file.size) }}
                  </p>
                  <p v-if="file.uploadStatus" class="mt-2">
                    <span class="text-gray-500 dark:text-gray-300">状态：</span>
                    <span :class="getStatusClass(file.uploadStatus)">{{ file.uploadStatus }}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 新增：分块配置区域 -->
        <div class="mt-8">
          <h4 class="font-medium text-gray-700 dark:text-gray-300 mb-4 flex items-center">
            <i class="fas fa-cog mr-2 text-indigo-500"></i>
            分块配置
          </h4>
          <div class="space-y-4">
            <!-- 分块方法选择 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                分块方法
              </label>
              <div class="flex flex-wrap gap-4">
                <label class="inline-flex items-center">
                  <input
                    type="radio"
                    class="form-radio text-indigo-600"
                    v-model="chunkMethod"
                    value="fixed"
                  >
                  <span class="ml-2">固定大小分块</span>
                </label>
                <label class="inline-flex items-center">
                  <input
                    type="radio"
                    class="form-radio text-indigo-600"
                    v-model="chunkMethod"
                    value="semantic"
                  >
                  <span class="ml-2">语义分块</span>
                </label>
                <label class="inline-flex items-center">
                  <input
                    type="radio"
                    class="form-radio text-indigo-600"
                    v-model="chunkMethod"
                    value="sliding"
                  >
                  <span class="ml-2">滑动窗口分块</span>
                </label>
                <!-- 新增：问答对专用分块 -->
                <label class="inline-flex items-center">
                  <input
                    type="radio"
                    class="form-radio text-indigo-600"
                    v-model="chunkMethod"
                    value="qa"
                  >
                  <span class="ml-2">问答对</span>
                </label>
              </div>
            </div>

            <!-- 固定大小分块参数 -->
            <div v-if="chunkMethod === 'fixed'" class="ml-6">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                每块字符数
              </label>
              <input
                type="number"
                v-model.number="chunkSize"
                class="w-full max-w-xs p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                min="100"
                max="10000"
              >
            </div>

            <!-- 滑动窗口分块参数 -->
            <div v-if="chunkMethod === 'sliding'" class="ml-6 space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  窗口大小（字符数）
                </label>
                <input
                  type="number"
                  v-model.number="windowSize"
                  class="w-full max-w-xs p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                  min="100"
                  max="10000"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  滑动步长（字符数）
                </label>
                <input
                  type="number"
                  v-model.number="stepSize"
                  class="w-full max-w-xs p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                  min="10"
                  max="5000"
                >
              </div>
            </div>

            <!-- 问答对分块说明 -->
            <div v-if="chunkMethod === 'qa'" class="ml-6 bg-indigo-50 dark:bg-indigo-900/30 p-4 rounded-lg">
              <p class="text-sm text-indigo-700 dark:text-indigo-300">
                <i class="fas fa-info-circle mr-2"></i>
                文件格式要求：每行一个JSON对象，包含"question"和"answer"字段。
              </p>
            </div>
          </div>
        </div>

        <!-- 构建索引按钮 -->
        <div class="absolute top-4 right-4">
          <button
            class="bg-indigo-500 dark:bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-600 dark:hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105 active:scale-95 shadow-sm hover:shadow-md flex items-center text-sm"
            :disabled="!canBuildIndex || isBuilding"
            @click="buildIndex"
          >
            {{ isBuilding ? '构建中...' : '构建索引' }}
          </button>
        </div>
      </div>

      <!-- 上传状态提示 -->
      <div
        v-if="uploadStatus.show"
        class="fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transition-all duration-300"
        :class="{
          'bg-green-100 text-green-700 border border-green-300': uploadStatus.type === 'success',
          'bg-red-100 text-red-700 border border-red-300': uploadStatus.type === 'error'
        }"
      >
        <div class="flex items-center">
          <i
            :class="{
              'fas fa-check-circle mr-2 text-green-500': uploadStatus.type === 'success',
              'fas fa-exclamation-circle mr-2 text-red-500': uploadStatus.type === 'error'
            }"
          ></i>
          <span>{{ uploadStatus.message }}</span>
          <button
            class="ml-4 text-gray-500 hover:text-gray-700"
            @click="closeUploadStatus"
          >
            <i class="fas fa-times"></i>
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
import File from '@/icons/File_1.vue'
import { getApiUrl } from '@/config/api'

export default {
  name: 'VectorDatabaseUpload',
  components: {
    FileUploadIcon,
    Setting,
    Preview,
    File,
  },
  setup() {
    const uploadedFiles = ref([])
    const isBuilding = ref(false)
    const uploadStatus = ref({
      show: false,
      type: 'success',
      message: '',
      timer: null,
    })

    // 分块配置参数
    const chunkMethod = ref('fixed') // 默认固定大小分块
    const chunkSize = ref(1000) // 默认每块1000字符
    const windowSize = ref(1000) // 默认窗口大小
    const stepSize = ref(500) // 默认步长

    const canBuildIndex = computed(() => {
      return uploadedFiles.value.length > 0 && !isBuilding.value
    })

    const getFileIcon = (type) => {
      const iconMap = {
        txt: 'fas fa-file-alt',
        pdf: 'fas fa-file-pdf',
        doc: 'fas fa-file-word',
        docx: 'fas fa-file-word',
        json: 'fas fa-file-code',
        jsonl: 'fas fa-file-code',
      }
      return iconMap[type] || 'fas fa-file'
    }

    const getFileTypeName = (type) => {
      const typeMap = {
        txt: '文本文件',
        pdf: 'PDF文档',
        doc: 'Word文档',
        docx: 'Word文档',
        json: 'JSON文件',
        jsonl: 'JSONL文件',
      }
      return typeMap[type] || type.toUpperCase()
    }

    const handleFileDrop = (event) => {
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
        if (['txt', 'pdf', 'doc', 'docx', 'json', 'jsonl'].includes(extension)) {
          const fileObj = {
            id: Date.now() + Math.random(),
            name: file.name,
            type: extension,
            uploadTime: dayjs().format('YYYY-MM-DD HH:mm'),
            file: file,
            uploadStatus: '等待上传',
          }
          uploadedFiles.value.push(fileObj)
          showUploadStatus('success', `文件已添加：${file.name}`)
        } else {
          showUploadStatus('error', `不支持的文件类型：${extension}`)
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

    const uploadFileToBackend = async (file) => {
      try {
        // 更新文件状态为上传中
        file.uploadStatus = '上传中...'

        const formData = new FormData()
        formData.append('files', file.file, file.name)

        // 添加分块参数到请求
        formData.append('chunk_method', chunkMethod.value)
        formData.append('chunk_size', chunkMethod.value === 'fixed' ? chunkSize.value : '')
        formData.append('window_size', chunkMethod.value === 'sliding' ? windowSize.value : '')
        formData.append('step_size', chunkMethod.value === 'sliding' ? stepSize.value : '')

        const response = await fetch(getApiUrl('/upload/'), {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error(`上传失败: ${response.statusText}`)
        }

        const result = await response.json()
        file.uploadStatus = '上传成功'
        return result
      } catch (error) {
        file.uploadStatus = '上传失败'
        throw error
      }
    }

    const buildIndex = async () => {
      isBuilding.value = true
      try {
        // 根据选择的分块方法调用不同的接口
        let endpoint = '';
        let formData = new FormData();

        // 添加所有文件
        uploadedFiles.value.forEach(file => {
          formData.append('files', file.file, file.name);
          // 更新文件状态为上传中
          file.uploadStatus = '上传中...';
        });

        // 根据分块方法设置端点和参数
        switch (chunkMethod.value) {
          case 'fixed':
            endpoint = '/upload/fixed/';
            formData.append('chunk_size', chunkSize.value);
            break;
          case 'semantic':
            endpoint = '/upload/semantic/';
            formData.append('chunk_size', chunkSize.value);
            break;
          case 'sliding':
            endpoint = '/upload/sliding/';
            formData.append('window_size', windowSize.value);
            formData.append('step_size', stepSize.value);
            break;
          case 'qa':
            // 保持原有的问答对分块接口
            endpoint = '/upload/';
            // 添加原有的分块参数
            formData.append('chunk_method', chunkMethod.value);
            formData.append('chunk_size', chunkMethod.value === 'fixed' ? chunkSize.value : '');
            formData.append('window_size', chunkMethod.value === 'sliding' ? windowSize.value : '');
            formData.append('step_size', chunkMethod.value === 'sliding' ? stepSize.value : '');
            break;
        }

        const response = await fetch(getApiUrl(endpoint), {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error(`上传失败: ${response.statusText}`);
        }

        const result = await response.json();

        // 更新文件状态为上传成功
        uploadedFiles.value.forEach(file => {
          file.uploadStatus = '上传成功';
        });

        showUploadStatus('success', '索引构建成功！');

      } catch (error) {
        console.error('构建索引时出错:', error);
        // 更新文件状态为上传失败
        uploadedFiles.value.forEach(file => {
          file.uploadStatus = '上传失败';
        });
        showUploadStatus('error', `索引构建失败: ${error.message}`);
      } finally {
        isBuilding.value = false;
      }
    }

    const previewFile = ref(null)
    const isPreviewVisible = ref(false)
    let previewTimer = null

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

    const getFileIconColor = (type) => {
      const colorMap = {
        txt: 'text-gray-500',
        pdf: 'text-red-500',
        doc: 'text-blue-500',
        docx: 'text-blue-500',
        json: 'text-yellow-500',
        jsonl: 'text-yellow-500',
      }
      return colorMap[type] || 'text-gray-500'
    }

    const getStatusClass = (status) => {
      switch (status) {
        case '上传成功':
          return 'text-green-500'
        case '上传失败':
          return 'text-red-500'
        case '上传中...':
          return 'text-yellow-500'
        default:
          return 'text-gray-500'
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
    }

    return {
      uploadedFiles,
      isBuilding,
      uploadStatus,
      canBuildIndex,
      getFileIcon,
      getFileTypeName,
      handleFileDrop,
      handleFileSelect,
      removeFile,
      removeAllFiles,
      closeUploadStatus,
      buildIndex,
      previewFile,
      isPreviewVisible,
      showPreview,
      hidePreview,
      getFileIconColor,
      getStatusClass,
      formatFileSize,
      // 分块配置参数
      chunkMethod,
      chunkSize,
      windowSize,
      stepSize,
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
  width: 100%;
  height: 4px;
  background: #ddd;
  border-radius: 2px;
  outline: none;
}

.form-range::-webkit-slider-thumb {
  -webkit-appearance: none;
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
  width: 100%;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  outline: none;
}

.custom-range::-webkit-slider-thumb {
  -webkit-appearance: none;
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

.animate-bounce {
  animation: bounce 1s infinite;
}

/* 添加阴影过渡效果 */
.hover\:shadow-md:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
  0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>

<style scoped>
.custom-range {
  -webkit-appearance: none;
  width: 100%;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  outline: none;
}

.custom-range::-webkit-slider-thumb {
  -webkit-appearance: none;
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
