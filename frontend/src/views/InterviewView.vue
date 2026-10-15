<template>
  <div class="text-gray-800 dark:text-gray-400" @click="handleContainerClick">
    <!-- 悬浮跳转按钮 -->
    <transition name="fade">
      <button
        v-if="showPrepareButton"
        @click.stop="goToPrepare"
        class="fixed bottom-8 right-8 z-50 px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-full shadow-lg hover:from-purple-600 hover:to-indigo-700 transition-all transform hover:scale-105 flex items-center"
      >
        <span>还没准备好？点我试试</span>
        <svg
          class="w-5 h-5 ml-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5l7 7-7 7"
          ></path>
        </svg>
      </button>
    </transition>
    <div class="container">
      <div class="content">
        <div class="p-2 sm:p-4">
          <div class="text-center">
            <h1 class="text-2xl sm:text-3xl font-bold mb-2">AI面试助手</h1>
            <p class="text-gray-400 text-sm sm:text-base">
              智能拆解岗位需求，定制「面试官想听的答案公式」
            </p>
          </div>
          <div class="flex justify-center mt-4">
            <div class="flex flex-wrap justify-center gap-2 sm:gap-4">
              <span
                v-for="(category, index) in categories"
                :key="index"
                class="cursor-pointer px-3 sm:px-4 py-2 hover:text-blue-500 hover:border-b-4 hover:border-blue-500 transition duration-300 text-sm sm:text-base lg:text-lg font-bold relative whitespace-nowrap flex items-center gap-1"
                :class="{
                  'text-blue-500 border-b-4 border-blue-500': activeCategory === index,
                }"
                @click="setActiveCategory(index)"
              >
                <!-- 火焰图标 - 仅对热门岗位显示 -->
                <Icon
                  v-if="category.name === '热门岗位'"
                  icon="lucide:flame"
                  class="w-7 h-7 mb-0.5 text-blue-500"
                />
                <Icon
                  v-if="category.name === '人工智能领域'"
                  icon="lucide:bot"
                  class="w-7 h-7 mb-0.5 text-blue-500"
                />
                <Icon
                  v-if="category.name === '大数据领域'"
                  icon="lucide:bar-chart-3"
                  class="w-7 h-7 text-blue-500"
                />
                <Icon
                  v-if="category.name === '物联网领域'"
                  icon="lucide:scan-qr-code"
                  class="w-7 h-7 text-blue-500"
                />
                <Icon
                  v-if="category.name === '软件开发领域'"
                  icon="lucide:square-terminal"
                  class="w-7 h-7 text-blue-500"
                />
                {{ category.name }}
                <span
                  class="absolute -top-1 -right-1 bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
                >
                  {{ category.count }}
                </span>
              </span>
            </div>
          </div>
          <div
            class="mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4"
          >
            <div
              v-for="job in activeJobs"
              :key="job.name"
              @click.stop="selectJob(job, $event)"
              class="bg-white p-3 sm:p-4 rounded-md shadow border-2 border-transparent dark:bg-gray-800 transition-all duration-200 cursor-pointer flex items-center justify-center min-h-[140px] sm:min-h-[160px]"
              :class="{
                'border-blue-600 scale-95': selectedJob === job.name,
                'hover:border-blue-400': true,
                'ring-2 ring-blue-300': selectedJob === job.name,
                'transform transition-transform': true,
              }"
            >
              <div class="text-center w-full">
                <img
                  :src="job.icon"
                  alt="job icon"
                  class="w-10 h-10 sm:w-12 sm:h-12 mb-2 mx-auto"
                />
                <h2 class="text-sm sm:text-base lg:text-lg font-semibold leading-tight">
                  {{ job.name }}
                </h2>
              </div>
            </div>
          </div>
        </div>

        <div class="card mt-8">
          <button
            type="button"
            disabled
            class="flex gap-2 mb-5 shadow-sm text-lg bg-gray-100 backdrop-blur-md lg:font-semibold isolation-auto border-gray-50 before:absolute before:w-full before:transition-all before:duration-700 before:hover:w-full before:-left-full before:hover:left-0 before:rounded-full before:bg-emerald-500 before:-z-10 before:aspect-square before:hover:scale-150 before:hover:duration-700 relative z-10 px-4 py-2 overflow-hidden border-2 rounded-full group dark:bg-gray-700"
          >
            请上传简历文件
            <svg
              class="w-8 h-8 justify-end group-hover:rotate-90 group-hover:bg-gray-50 text-gray-50 ease-linear duration-300 rounded-full border border-gray-700 group-hover:border-none p-2 rotate-45 dark:bg-white"
              viewBox="0 0 16 19"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M7 18C7 18.5523 7.44772 19 8 19C8.55228 19 9 18.5523 9 18H7ZM8.70711 0.292893C8.31658 -0.0976311 7.68342 -0.0976311 7.29289 0.292893L0.928932 6.65685C0.538408 7.04738 0.538408 7.68054 0.928932 8.07107C1.31946 8.46159 1.95262 8.46159 2.34315 8.07107L8 2.41421L13.6569 8.07107C14.0474 8.46159 14.6805 8.46159 15.0711 8.07107C15.4616 7.68054 15.4616 7.04738 15.0711 6.65685L8.70711 0.292893ZM9 18L9 1H7L7 18H9Z"
                class="fill-gray-800 group-hover:fill-gray-800"
              ></path>
            </svg>
          </button>
        </div>
        <div class="file-uploader-container">
          <el-upload
            accept=".pdf, .png, .jpg, .bmp"
            :before-upload="before_upload"
            class="upload-demo"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将简历文件拖拽至此或 <em>点击以上传简历文件</em></div>
            <div class="el-upload__tip">支持pdf/jpg/png/bmp文件</div>
          </el-upload>
        </div>
      </div>
    </div>

    <!-- 温和 / 压力 面试官类型选择部分 -->
    <div class="card mt-8">
      <div class="mb-4">
        <button
          type="button"
          disabled
          class="flex gap-2 mb-4 shadow-sm text-lg bg-gray-100 backdrop-blur-md lg:font-semibold isolation-auto border-gray-50 before:absolute before:w-full before:transition-all before:duration-700 before:hover:w-full before:-left-full before:hover:left-0 before:rounded-full before:bg-emerald-500 before:-z-10 before:aspect-square before:hover:scale-150 before:hover:duration-700 relative z-10 px-4 py-2 overflow-hidden border-2 rounded-full group dark:bg-gray-700"
        >
          面试官类型
          <svg
            class="w-8 h-8 justify-end group-hover:rotate-90 group-hover:bg-gray-50 text-gray-50 ease-linear duration-300 rounded-full border border-gray-700 group-hover:border-none p-2 rotate-45 dark:bg-white"
            viewBox="0 0 16 19"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M7 18C7 18.5523 7.44772 19 8 19C8.55228 19 9 18.5523 9 18H7ZM8.70711 0.292893C8.31658 -0.0976311 7.68342 -0.0976311 7.29289 0.292893L0.928932 6.65685C0.538408 7.04738 0.538408 7.68054 0.928932 8.07107C1.31946 8.46159 1.95262 8.46159 2.34315 8.07107L8 2.41421L13.6569 8.07107C14.0474 8.46159 14.6805 8.46159 15.0711 8.07107C15.4616 7.68054 15.4616 7.04738 15.0711 6.65685L8.70711 0.292893ZM9 18L9 1H7L7 18H9Z"
              class="fill-gray-800 group-hover:fill-gray-800"
            ></path>
          </svg>
        </button>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 w-full">
          <!-- 温和型面试官选项 -->
          <div
            @click.stop="selectInterviewerType('温和')"
            class="interviewer-option flex flex-col items-center p-4 rounded-lg cursor-pointer transition-all duration-300 w-full"
            :class="{
              'bg-green-50 border-2 border-green-200 dark:bg-green-900/20 dark:border-green-700':
                interviewerType === '温和',
              'bg-gray-50 border-2 border-gray-200 hover:border-gray-300 dark:bg-gray-800 dark:border-gray-700 dark:hover:border-gray-600':
                interviewerType !== '温和',
            }"
          >
            <div
              class="w-16 h-16 mb-3 flex items-center justify-center rounded-full"
              :class="
                interviewerType === '温和'
                  ? 'bg-green-100 dark:bg-green-800/30'
                  : 'bg-gray-100 dark:bg-gray-700'
              "
            >
              <Icon
                icon="mdi:emoticon-happy-outline"
                class="w-10 h-10"
                :class="
                  interviewerType === '温和'
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-gray-400 dark:text-gray-500'
                "
              />
            </div>
            <span
              class="font-medium"
              :class="
                interviewerType === '温和'
                  ? 'text-green-700 dark:text-green-300'
                  : 'text-gray-600 dark:text-gray-400'
              "
            >
              温和型
            </span>
            <p class="text-xs mt-2 text-center text-gray-500 dark:text-gray-400">
              友好的面试体验<br />引导式提问
            </p>
          </div>

          <!-- 均衡型面试官选项 -->
          <div
            @click.stop="selectInterviewerType('均衡')"
            class="interviewer-option flex flex-col items-center p-4 rounded-lg cursor-pointer transition-all duration-300 w-full"
            :class="{
              'bg-blue-50 border-2 border-blue-200 dark:bg-blue-900/20 dark:border-blue-700':
                interviewerType === '均衡',
              'bg-gray-50 border-2 border-gray-200 hover:border-gray-300 dark:bg-gray-800 dark:border-gray-700 dark:hover:border-gray-600':
                interviewerType !== '均衡',
            }"
          >
            <div
              class="w-16 h-16 mb-3 flex items-center justify-center rounded-full"
              :class="
                interviewerType === '均衡'
                  ? 'bg-blue-100 dark:bg-blue-800/30'
                  : 'bg-gray-100 dark:bg-gray-700'
              "
            >
              <Icon
                icon="mdi:emoticon-neutral-outline"
                class="w-10 h-10"
                :class="
                  interviewerType === '均衡'
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-400 dark:text-gray-500'
                "
              />
            </div>
            <span
              class="font-medium"
              :class="
                interviewerType === '均衡'
                  ? 'text-blue-700 dark:text-blue-300'
                  : 'text-gray-600 dark:text-gray-400'
              "
            >
              均衡型
            </span>
            <p class="text-xs mt-2 text-center text-gray-500 dark:text-gray-400">
              平衡的面试体验<br />专业评估为主
            </p>
          </div>

          <!-- 压力型面试官选项 -->
          <div
            @click.stop="selectInterviewerType('压力')"
            class="interviewer-option flex flex-col items-center p-4 rounded-lg cursor-pointer transition-all duration-300 w-full"
            :class="{
              'bg-red-50 border-2 border-red-200 dark:bg-red-900/20 dark:border-red-700':
                interviewerType === '压力',
              'bg-gray-50 border-2 border-gray-200 hover:border-gray-300 dark:bg-gray-800 dark:border-gray-700 dark:hover:border-gray-600':
                interviewerType !== '压力',
            }"
          >
            <div
              class="w-16 h-16 mb-3 flex items-center justify-center rounded-full"
              :class="
                interviewerType === '压力'
                  ? 'bg-red-100 dark:bg-red-800/30'
                  : 'bg-gray-100 dark:bg-gray-700'
              "
            >
              <Icon
                icon="mdi:emoticon-sad-outline"
                class="w-10 h-10"
                :class="
                  interviewerType === '压力'
                    ? 'text-red-600 dark:text-red-400'
                    : 'text-gray-400 dark:text-gray-500'
                "
              />
            </div>
            <span
              class="font-medium"
              :class="
                interviewerType === '压力'
                  ? 'text-red-700 dark:text-red-300'
                  : 'text-gray-600 dark:text-gray-400'
              "
            >
              压力型
            </span>
            <p class="text-xs mt-2 text-center text-gray-500 dark:text-gray-400">
              高压面试体验<br />挑战式提问
            </p>
          </div>
        </div>

        <!-- 类型说明 -->
        <div
          class="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
        >
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            面试官类型说明：
          </h4>
          <div
            class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-gray-600 dark:text-gray-400"
          >
            <div
              class="rounded-lg p-3 transition-all duration-300 cursor-pointer"
              :class="
                interviewerType === '温和'
                  ? 'scale-[1.03]'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700/40'
              "
              @click.stop="selectInterviewerType('温和')"
            >
              <div class="flex items-start">
                <div class="w-3 h-3 rounded-full bg-green-500 mt-1 mr-2 flex-shrink-0"></div>
                <div>
                  <span class="font-medium text-green-600 dark:text-green-400">温和型：</span>
                  <p>适合面试新手，面试官会给予更多鼓励和引导，帮助您更好地展示自己。</p>
                </div>
              </div>
            </div>
            <div
              class="rounded-lg p-3 transition-all duration-300 cursor-pointer"
              :class="
                interviewerType === '均衡'
                  ? 'scale-[1.03]'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700/40'
              "
              @click.stop="selectInterviewerType('均衡')"
            >
              <div class="flex items-start">
                <div class="w-3 h-3 rounded-full bg-blue-500 mt-1 mr-2 flex-shrink-0"></div>
                <div>
                  <span class="font-medium text-blue-600 dark:text-blue-400">均衡型：</span>
                  <p>标准面试模式，面试官会平衡提问难度，既评估能力也考察应变能力。</p>
                </div>
              </div>
            </div>
            <div
              class="rounded-lg p-3 transition-all duration-300 cursor-pointer"
              :class="
                interviewerType === '压力'
                  ? 'scale-[1.03]'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700/40'
              "
              @click.stop="selectInterviewerType('压力')"
            >
              <div class="flex items-start">
                <div class="w-3 h-3 rounded-full bg-red-500 mt-1 mr-2 flex-shrink-0"></div>
                <div>
                  <span class="font-medium text-red-600 dark:text-red-400">压力型：</span>
                  <p>适合高阶面试者，面试官会提出挑战性问题，模拟高压面试环境。</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 温和 / 压力  end -->

    <button
      v-if="!isLoading"
      @click="startInterview"
      class="mt-4 px-4 py-2 text-lg font-semibold bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors exclude-deselect flex items-center gap-1"
    >
      <Icon icon="lucide:clipboard-check" class="w-5 h-5" />
      开始面试
    </button>

    <button
      v-else
      disabled
      class="s-button text-white bg-blue-700 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 inline-flex items-center"
    >
      <svg
        aria-hidden="true"
        role="status"
        class="inline w-4 h-4 mr-3 text-white animate-spin"
        viewBox="0 0 100 101"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
          fill="#E5E7EB"
        ></path>
        <path
          d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
          fill="currentColor"
        ></path>
      </svg>
      面试官正在查看您的简历...
    </button>
  </div>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { Icon } from '@iconify/vue'
</script>

<script lang="ts">
import { getApiUrl } from '@/config/api'
import axios from 'axios'

import { useInterviewStore } from '@/store/interview'
import Calendar2Line from '@/icons/Calendar2Line.vue'

export default {
  components: { Calendar2Line },
  data() {
    return {
      interviewerType: '温和',
      categories: [
        {
          name: '热门岗位',
          count: '热',
          jobs: [
            {
              name: '深度学习算法工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/c5b7a68f1dc30519a10df2dd7b59159d.png',
              field: '人工智能领域',
            },
            {
              name: '计算机视觉工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/4f15e2b2a8bc02e838d3bc998ea48a58.png',
              field: '人工智能领域',
            },

            {
              name: '数据分析师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/a5e348d179f5f8e38405db69d879e34d.png',
              field: '大数据领域',
            },
            {
              name: '大数据运维工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/e1b4336d8257f32c610d0154936bf9d0.png',
              field: '大数据领域',
            },
            {
              name: '嵌入式系统开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/955e6e2bc5a331a355d49a271e4a5f2f.png',
              field: '物联网领域',
            },
            {
              name: '前端开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/e494b568ca43eb3d4caa98f84e4570f4.png',
              field: '软件开发领域',
            },
            {
              name: '后端开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/3e8720258dba22c518ddd5889ae01523.png',
              field: '软件开发领域',
            },
            {
              name: '全栈开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/430fc28a03339e5fe7ee95bf2be928a9.png',
              field: '软件开发领域',
            },
            {
              name: 'Android开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/201fbb2f41829a670da6ac7387c1bf11.png',
              field: '软件开发领域',
            },
            {
              name: 'iOS开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/54c5dabf9d918a75e5a70412dc148847.png',
              field: '软件开发领域',
            },
            {
              name: '项目经理',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/8fff15d43dc37ced0db2604948c7b210.png',
              field: '软件开发领域',
            },
          ],
        },
        {
          name: '人工智能领域',
          count: 6,
          jobs: [
            {
              name: '机器学习算法工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/05f63762f7ac7aebf667018d76cbff69.png',
            },
            {
              name: '深度学习算法工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/c35df531c4953e88c082ce841885a65e.png',
            },

            {
              name: '计算机视觉工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/5000b580b92f1bc0f0d147e9448d2ee8.png',
            },
            {
              name: 'AI系统架构师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/a2db7ff6dce5e06405740b9e368fafe2.png',
            },
            {
              name: '机器人算法工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/c6f5431280f86b37a65567f5ba07c4ac.png',
            },
            {
              name: 'AI产品经理',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/43ceee2dca48fc14465529abe87581b7.png',
            },
          ],
        },
        {
          name: '大数据领域',
          count: 6,
          jobs: [
            {
              name: '大数据开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/3c3e425bab9d406710bc0f54575f013a.png',
            },
            {
              name: '数据工程师（ETL）',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/eed2c2d9c4d78425315c771c66c11bab.png',
            },
            {
              name: '数据分析师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/77387aea2da7aadc48f5db96599ed820.png',
            },
            {
              name: '商业智能（BI）分析师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/d62e976ae80c2774813a4847a46adf0a.png',
            },
            {
              name: '大数据运维工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/8ee08fe34233812137a905fca9f9caab.png',
            },
            {
              name: '数据安全工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/9d4dc799b6232e501f2b5dec58da29fd.png',
            },
          ],
        },
        {
          name: '物联网领域',
          count: 6,
          jobs: [
            {
              name: '物联网工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/0393c637cc2147179f27ebac22b0f95e.png',
            },
            {
              name: '嵌入式系统开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/65482df031e9085a8732ddc209e4d4dd.png',
            },
            {
              name: '传感器工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/8c7fcc5c3a064c040978bb506baff348.png',
            },
            {
              name: '物联网解决方案架构师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/1b189d3e4c7eb79bcb73a55591e04e11.png',
            },
            {
              name: '边缘计算工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/e7bc20c9f98c6fc79343b168dc3da855.png',
            },
            {
              name: '物联网产品经理',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/f80fe8da0158c3fd6802e5d079b920e9.png',
            },
          ],
        },
        {
          name: '软件开发领域',
          count: 9,
          jobs: [
            {
              name: '前端开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/c63211f89cff2667b78400c3fa65fb11.png',
            },
            {
              name: 'UI/UX设计师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/9cad9dd07df20744f63003eb90c8ae00.png',
            },
            {
              name: '后端开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/35b71c5299c4348be51fed6b150a660e.png',
            },
            {
              name: '全栈开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/438c218a05818aee028cb77a37fb9088.png',
            },
            {
              name: 'Android开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/73d3e24ce7cbb6da202c4cff62d89aee.png',
            },
            {
              name: 'iOS开发工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/395091167844dfa0eb9d1e3d0de9360a.png',
            },
            {
              name: '软件测试工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/4fe2ed0ad6e58d3167a637e8a60d1fc3.png',
            },
            {
              name: '质量保证（QA）工程师',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/e9e2d4d59ca5dde49c448fb4230c8c3c.png',
            },
            {
              name: '项目经理',
              icon: 'https://ai.lanzidian.com/uploads/images/20240531/ba7ceb3fcf542772d709d96f59ff2197.png',
            },
          ],
        },
      ],
      activeCategory: 0,
      selectedJob: null,
      selectedCategory: '人工智能领域',
      resumeFile: null,
      isLoading: false, // 用于控制加载状态

      showPrepareButton: false,
      resumeTimer: null,
      hasPositionData: false, // 新增：标记是否有岗位数据
    }
  },

  activated() {
    this.restoreState()
  },

  deactivated() {},
  mounted() {
    this.restoreState()
  },

  beforeDestroy() {},
  computed: {
    activeJobs() {
      return this.categories[this.activeCategory].jobs
    },
    selectedJobInfo() {
      if (!this.selectedJob) return null
      return {
        category: this.selectedCategory,
        job: this.selectedJob,
      }
    },
  },
  methods: {
    restoreState() {
      const savedJob = sessionStorage.getItem('interview_selectedJob')
      const savedCategory = sessionStorage.getItem('interview_selectedCategory')
      const savedActiveCategory = sessionStorage.getItem('interview_activeCategory')
      const savedInterviewerType = sessionStorage.getItem('interview_interviewerType')

      if (savedJob && savedCategory && savedActiveCategory) {
        this.selectedJob = savedJob
        this.selectedCategory = savedCategory
        this.activeCategory = parseInt(savedActiveCategory)
      }

      if (savedInterviewerType) {
        this.interviewerType = savedInterviewerType
      }
    },

    before_upload(file) {
      const isPDF = file.type === 'application/pdf'
      const isImage = ['image/png', 'image/jpeg', 'image/bmp'].includes(file.type)

      if (!isPDF && !isImage) {
        ElMessage.error('只支持上传PDF、PNG、JPG、BMP格式的简历文件')
        return false
      }
      return true
    },
    async pollProcessStatus(processId, maxAttempts = 200) {
      return new Promise((resolve, reject) => {
        let attempts = 0
        const interval = setInterval(async () => {
          try {
            const response = await axios.get(getApiUrl(`/resume/status/${processId}`))
            const interviewStore = useInterviewStore()
            const { code, data } = response.data

            if (code !== 200) {
              clearInterval(interval)
              reject(new Error(response.data.message || '查询处理状态失败'))
              return
            }

            const { status, result, error } = data

            if (status === 'completed' && result) {
              interviewStore.setHistoryId(response.data.data.result.history_id)
              clearInterval(interval)
              resolve(result)
            } else if (status === 'failed') {
              clearInterval(interval)
              reject(new Error(error || '处理失败'))
            }
            attempts++
            if (attempts >= maxAttempts) {
              clearInterval(interval)
              reject(new Error('处理超时，请重试'))
            }
          } catch (error) {
            clearInterval(interval)
            reject(error)
          }
        }, 5000)
      })
    },

    // 新增容器点击处理方法
    handleContainerClick(event) {
      // 检查点击是否发生在排除元素内
      const isExcluded =
        event.target.closest('.exclude-deselect') ||
        event.target.closest('.el-upload') ||
        event.target.closest('.flex.space-x-4') ||
        event.target.closest('.interviewer-option') ||
        event.target.closest('[class*="job"]')

      if (!isExcluded && this.selectedJob !== null) {
        this.selectedJob = null
        this.selectedCategory = null
        // 清除 sessionStorage
        sessionStorage.removeItem('interview_selectedJob')
        sessionStorage.removeItem('interview_selectedCategory')

        // 清除定时器和隐藏按钮
        this.clearResumeTimer()
        this.showPrepareButton = false
        this.hasPositionData = false // 重置岗位数据状态
      }
    },

    setActiveCategory(index) {
      this.activeCategory = index
      this.selectedJob = null // 切换领域时清空选中状态
      this.selectedCategory = null // 切换领域时清空选中的领域

      sessionStorage.removeItem('interview_selectedJob')
      sessionStorage.removeItem('interview_selectedCategory')
      sessionStorage.setItem('interview_activeCategory', index.toString())

      // 清除定时器和隐藏按钮
      this.clearResumeTimer()
      this.showPrepareButton = false
      this.hasPositionData = false // 重置岗位数据状态
    },
    async selectJob(job, event) {
      if (event) {
        event.stopPropagation()
      }

      this.selectedJob = job.name
      if (this.activeCategory === 0) {
        this.selectedCategory = job.field
      } else {
        this.selectedCategory = this.categories[this.activeCategory].name
      }

      // 保存完整状态
      sessionStorage.setItem('interview_selectedJob', job.name)
      sessionStorage.setItem('interview_selectedCategory', this.selectedCategory)
      sessionStorage.setItem('interview_activeCategory', this.activeCategory.toString())

      // 验证岗位数据
      this.hasPositionData = true

      // 清除现有定时器并设置新定时器
      this.clearResumeTimer()
      if (!this.resumeFile) {
        this.resumeTimer = setTimeout(() => {
          this.showPrepareButton = this.hasPositionData
        }, 5000)
      }
      console.log('选中的领域:', this.selectedCategory)
      console.log('选中的岗位:', job.name)
      console.log('完整选中信息:', this.selectedJobInfo) // 这里会使用修改后的计算属性
    },
    handleFileChange(file) {
      this.resumeFile = file.raw
      this.clearResumeTimer()
      this.showPrepareButton = false
    },
    clearResumeTimer() {
      if (this.resumeTimer) {
        clearTimeout(this.resumeTimer)
        this.resumeTimer = null
      }
      this.showPrepareButton = false
    },
    goToPrepare() {
      if (!this.hasPositionData) {
        ElMessage.warning('未选中岗位')
        return
      }
      // 使用命名路由并传递 params 参数
      this.$router.push({
        name: 'PrepareDetail',
        params: {
          category: this.selectedCategory, // 注意参数名与路由配置一致
          job: this.selectedJob,
        },
      })
    },
    async startInterview() {
      // 验证用户是否选择了岗位
      const isJobSelected = this.selectedJob !== null
      // 验证用户是否上传了简历
      const isResumeUploaded = this.resumeFile !== null

      // 处理各种验证情况
      if (!isJobSelected && !isResumeUploaded) {
        ElMessage({
          message: '请选择进行AI模拟面试的岗位并上传简历文件',
          type: 'error',
          duration: 3000,
          top: '150px',
          offset: 100,
        })
        return
      }

      if (!isJobSelected) {
        ElMessage({
          message: '请选择进行AI模拟面试的岗位',
          type: 'error',
          duration: 3000,
          top: '150px',
          offset: 100,
        })
        return
      }

      if (!isResumeUploaded) {
        ElMessage({
          message: '请上传简历文件',
          type: 'error',
          duration: 3000,
          top: '150px',
          offset: 100,
        })
        return
      }
      try {
        this.isLoading = true // 激活加载状态
        // 创建FormData对象
        const formData = new FormData()
        formData.append('file', this.resumeFile)
        formData.append('domain', this.selectedCategory)
        formData.append('position', this.selectedJob)
        formData.append('interviewer_type', this.interviewerType) // 新增：添加面试官类型

        const userId = localStorage.getItem('user_id') || ''
        formData.append('user_id', userId)

        // 发送上传请求
        const uploadResponse = await axios.post(getApiUrl('/resume/upload'), formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        if (uploadResponse.data.code !== 202) {
          throw new Error(uploadResponse.data.message || '上传失败')
        }

        const { process_id } = uploadResponse.data.data

        // 开始轮询处理状态
        const result = await this.pollProcessStatus(process_id)

        // 从简历处理结果中获取面试初始化数据（后端已在简历处理成功后自动创建面试记录）
        const interviewStore = useInterviewStore()
        if (!result?.first_question || !result?.question_qa_id) {
          throw new Error('面试初始化数据不完整，请重试')
        }
        interviewStore.setInterviewStartData(result)

        // 处理成功，显示成功消息并跳转
        ElMessage({
          message: '简历处理完成，即将进入面试',
          type: 'success',
          duration: 2000,
        })

        this.$router.push('/interview/dialoging')
      } catch (error) {
        console.error('处理失败:', error)
        ElMessage({
          message: error.message || '处理失败，请重试',
          type: 'error',
          duration: 3000,
          top: '150px',
          offset: 100,
        })
      } finally {
        this.isLoading = false
      }
    },

    selectInterviewerType(type) {
      this.interviewerType = type
      // 保存到sessionStorage
      sessionStorage.setItem('interview_interviewerType', type)
    },
  },
}
</script>

<style scoped>
/* 添加淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.5s,
    transform 0.5s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
s-button {
  color: white;
  background-color: #1d4ed8;
  --ring-color: #93c5fd;
  font-weight: 500;
  border-radius: 0.5rem;
  font-size: 1rem;
  line-height: 2rem;
  padding-left: 2rem;
  padding-right: 2rem;
  padding-top: 0.7rem;
  padding-bottom: 0.7rem;
  text-align: center;
  margin-right: 0.5rem;
  display: inline-flex;
  align-items: center;
  border: none;
}

s-button:hover {
  background-color: #1e40af;
}

s-button:focus {
  box-shadow: var(--tw-ring-inset) 0 0 0 calc(4px + var(--tw-ring-offset-width))
    var(--tw-ring-color);
}

s-button svg {
  display: inline;
  width: 1.3rem;
  height: 1.3rem;
  margin-right: 0.75rem;
  color: white;
  animation: spin_357 1s linear infinite;
}

@keyframes spin_357 {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

:root {
  --el-upload-bg-color: #fff;
}

:dark {
  --el-upload-bg-color: #333;
}

:deep(.el-upload-dragger) {
  background-color: var(--el-upload-bg-color);
}

.interviewer-option {
  min-height: 180px;
  transition:
    transform 0.3s ease,
    border-color 0.3s ease,
    background-color 0.3s ease,
    box-shadow 0.3s ease;
}

.interviewer-option:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}
</style>
