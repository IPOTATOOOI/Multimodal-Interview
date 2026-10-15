<template>
  <div class="p-4 md:p-6 lg:p-8 bg-gray-50 dark:bg-gray-900 min-h-screen">
    <div v-if="loading" class="flex flex-col items-center justify-center py-32">
      <Icon icon="lucide:loader-2" class="w-12 h-12 animate-spin text-blue-500 mb-4" />
      <div class="text-lg text-gray-600 dark:text-gray-300">评估报告生成中，请稍候...</div>
    </div>
    <div v-else-if="error" class="flex flex-col items-center justify-center py-32">
      <Icon icon="lucide:alert-triangle" class="w-12 h-12 text-red-500 mb-4" />
      <div class="text-lg text-red-600 dark:text-red-400">{{ error }}</div>
    </div>
    <div v-else>
      <div
        ref="interviewResult"
        class="max-w-6xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 md:p-8"
      >
        <div class="flex justify-between items-start mb-6">
          <div>
            <h1
              class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white flex items-center"
            >
              <Icon icon="lucide:file-chart-column-increasing" class="w-8 h-8 mr-2" />
              模拟面试报告
            </h1>
            <div class="text-sm text-gray-500 dark:text-gray-400 mt-2 flex items-center">
              <span class="flex items-center">
                <Icon icon="lucide:land-plot" class="w-5 h-5 mr-2 text-gray-500" />
                {{ interviewData.field }} - {{ interviewData.position }}
              </span>
              <span class="mx-2">|</span>
              <span class="flex items-center">
                <Icon icon="lucide:clock" class="w-4 h-4 mr-1 text-gray-500" />
                {{ new Date(interviewData.interview_time).toLocaleString() }}
              </span>
            </div>
          </div>
          <div class="text-center">
            <p class="text-gray-600 dark:text-gray-300">综合得分</p>
            <p class="text-5xl font-bold text-blue-500">{{ overallScore }}/100</p>
          </div>
        </div>

        <!-- 能力模型 -->
        <div class="mb-8 p-6 bg-gray-50 dark:bg-gray-700/20 rounded-xl">
          <h2 class="text-xl font-semibold text-gray-800 dark:text-white mb-4 flex items-center">
            <Icon icon="lucide:pie-chart" class="w-6 h-6 mr-2 text-blue-700" />
            动态量化评测体系
          </h2>
          <div id="radar-chart">
            <apexchart
              type="radar"
              height="400"
              :options="chartOptions"
              :series="chartSeries"
            ></apexchart>
          </div>
        </div>

        <!-- 反馈建议 -->
        <div class="mb-8">
          <h2 class="text-xl font-semibold text-gray-800 dark:text-white mb-4 flex items-center">
            <Icon icon="lucide:search-slash" class="w-6 h-6 mr-2 text-blue-700" />
            反馈与建议
          </h2>
          <div
            class="p-6 bg-blue-50 border border-blue-200 dark:bg-blue-500/10 dark:border-blue-500/30 rounded-lg"
          >
            <div
              v-for="(suggestion, idx) in suggestions"
              :key="idx"
              class="flex items-start mb-2 last:mb-0"
            >
              <span class="font-bold text-blue-500 mr-2">{{ idx + 1 }}.</span>
              <span class="text-gray-700 dark:text-gray-300">{{ suggestion }}</span>
            </div>
          </div>
        </div>

        <!-- 面试表现图片区块 -->
        <div v-if="landmarkImages.length" class="mb-8">
          <h2 class="text-xl font-semibold text-gray-800 dark:text-white mb-4 flex items-center">
            <Icon icon="lucide:smile" class="w-6 h-6 mr-2 text-blue-700" />
            面试表现
          </h2>
          <div class="flex gap-6 justify-center items-center mb-6">
            <div v-for="(img, idx) in landmarkImages" :key="img" class="landmark-img-box">
              <img
                :src="getApiUrl(`/interview/landmark-image/${img}`)"
                :alt="`面试表现截图${idx + 1}`"
                class="landmark-img"
                loading="lazy"
              />
            </div>
          </div>
          <div
            class="p-6 bg-blue-50 border border-blue-200 dark:bg-blue-500/10 dark:border-blue-500/30 rounded-lg leading-loose"
          >
            <h3
              class="text-lg font-semibold text-blue-700 dark:text-blue-300 mb-2 flex items-center"
            >
              表情神态评价
            </h3>
            <p class="text-gray-700 dark:text-gray-300 whitespace-pre-line">
              {{ (interviewData as any)?.expression_evaluation || '暂无评价' }}
            </p>

            <h3
              class="text-lg font-semibold text-blue-700 dark:text-blue-300 mb-2 flex items-center mt-4"
            >
              肢体动作评价
            </h3>
            <p class="text-gray-700 dark:text-gray-300 whitespace-pre-line">
              {{ (interviewData as any)?.gesture_evaluation || '暂无评价' }}
            </p>
          </div>
        </div>

        <!-- 用户画像薄弱点面板 -->
        <div
          v-if="
            userPortrait &&
            userPortrait.graph_data &&
            userPortrait.graph_data.weak_area_tags &&
            userPortrait.graph_data.weak_area_tags.length
          "
          class="mt-10 p-4 rounded-xl bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800"
        >
          <div class="flex items-center gap-2 mb-3">
            <Icon icon="lucide:user-round-cog" class="w-5 h-5 text-orange-500" />
            <span class="text-base font-semibold text-orange-700 dark:text-orange-300">
              你的薄弱画像
              <span
                v-if="userPortrait.recommendation_profile?.study_focus_label"
                class="ml-2 text-sm font-normal text-orange-500"
              >
                — {{ userPortrait.recommendation_profile.study_focus_label }}
              </span>
            </span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            <div
              v-for="tag in userPortrait.graph_data.weak_area_tags.slice(0, 6)"
              :key="tag.tag_id"
              class="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-gray-800 border border-orange-100 dark:border-orange-800"
            >
              <span class="text-sm text-gray-700 dark:text-gray-300 truncate mr-2">{{
                  tag.tag_name
                }}</span>
              <div class="flex items-center gap-1 flex-shrink-0">
                <div class="w-16 h-1.5 rounded-full bg-gray-200 dark:bg-gray-600 overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all"
                    :class="
                      tag.strength >= 3.5
                        ? 'bg-red-500'
                        : tag.strength >= 2
                          ? 'bg-orange-400'
                          : 'bg-yellow-400'
                    "
                    :style="{ width: Math.min(100, (tag.strength / 5) * 100) + '%' }"
                  ></div>
                </div>
                <span class="text-xs text-gray-400">{{ tag.strength?.toFixed(1) }}</span>
              </div>
            </div>
          </div>
          <div class="mt-3 grid grid-cols-3 gap-3 text-sm text-center">
            <div class="p-2 rounded-lg bg-white dark:bg-gray-800">
              <div class="font-bold text-gray-800 dark:text-white">
                {{ userPortrait.interview_performance?.total_interviews ?? '-' }}
              </div>
              <div class="text-gray-500 text-xs">累计面试</div>
            </div>
            <div class="p-2 rounded-lg bg-white dark:bg-gray-800">
              <div class="font-bold text-gray-800 dark:text-white">
                {{ userPortrait.interview_performance?.weakest_dimension_label ?? '-' }}
              </div>
              <div class="text-gray-500 text-xs">最弱维度</div>
            </div>
            <div class="p-2 rounded-lg bg-white dark:bg-gray-800">
              <div class="font-bold text-gray-800 dark:text-white">
                {{
                  userPortrait.graph_data?.correct_rate != null
                    ? (userPortrait.graph_data.correct_rate * 100).toFixed(0) + '%'
                    : '-'
                }}
              </div>
              <div class="text-gray-500 text-xs">答题正确率</div>
            </div>
          </div>
        </div>

        <!-- 薄弱点动态检索 -->
        <div class="mt-10">
          <div class="flex items-center justify-between gap-4 mb-2">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-white flex items-center">
              <Icon icon="lucide:globe-2" class="w-6 h-6 mr-2 text-[#fb6514]" />
              薄弱点动态检索
            </h2>
            <Button
              size="sm"
              variant="outline"
              :disabled="webSearchLoading"
              @click="searchWeaknessResources"
            >
              <Icon icon="lucide:refresh-cw" class="w-4 h-4" />
              {{ webSearchLoading ? '检索中...' : '刷新检索' }}
            </Button>
          </div>

          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            基于你的薄弱能力项自动检索公开网页学习资源，帮助你快速补强。
          </p>

          <div v-if="webSearchLoading" class="text-sm text-gray-500 dark:text-gray-400">
            正在检索薄弱点相关内容...
          </div>
          <div v-else-if="webSearchError" class="text-sm text-red-500">{{ webSearchError }}</div>
          <div
            v-else-if="!weaknessWebResults.length"
            class="text-sm text-gray-500 dark:text-gray-400"
          >
            暂无检索结果
          </div>
          <div v-else class="space-y-5">
            <div
              v-for="group in weaknessWebResults"
              :key="group.tagName"
              class="p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
            >
              <h3 class="text-base font-semibold text-[#fb6514] mb-1">{{ group.tagName }}</h3>
              <div class="space-y-3">
                <a
                  v-for="item in group.items"
                  :key="item.link"
                  :href="item.link"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="block p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-500 transition-colors"
                >
                  <p class="font-medium text-gray-800 dark:text-gray-100 line-clamp-2">
                    {{ item.title }}
                  </p>
                  <p
                    v-if="item.snippet"
                    class="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-3"
                  >
                    {{ item.snippet }}
                  </p>
                  <p class="text-xs text-[#fb6514] mt-2 truncate">
                    {{ item.source || item.link }}
                  </p>
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- 问答详情 -->
        <div class="mt-8">
          <h2 class="text-xl font-semibold text-gray-800 dark:text-white mb-6 flex items-center">
            <Icon icon="lucide:message-circle-more" class="w-6 h-6 mr-2 text-blue-700" />
            问答详情
          </h2>
          <div
            class="space-y-8"
            @mouseover="handleDetailMouseEnter"
            @mouseout="handleDetailMouseLeave"
          >
            <div
              v-for="(qaPair, index) in qaPairs"
              :key="qaPair.question.qa_id"
              class="border-b pb-8 last:border-b-0"
            >
              <!-- 题目标签和编号 -->
              <div class="flex items-center gap-3 mb-4">
                <span class="text-lg font-bold text-blue-700">{{ index + 1 }}.</span>
                <Badge v-if="qaPair.question.skill" color="primary" size="md">
                  {{ qaPair.question.skill }}
                </Badge>
                <Badge
                  v-if="qaPair.question.difficulty"
                  :color="difficultyColor(qaPair.question.difficulty)"
                  size="md"
                >
                  {{ qaPair.question.difficulty }}
                </Badge>
                <Badge v-if="qaPair.question.category" color="success" size="md">
                  {{ qaPair.question.category }}
                </Badge>
              </div>

              <!-- 问题部分 -->
              <div class="mb-6">
                <div class="flex items-start gap-4">
                  <span
                    class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center font-bold text-gray-600 dark:text-gray-300"
                  >Q</span
                  >
                  <div class="w-full">
                    <div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
                      <p class="text-gray-800 dark:text-gray-200 text-base font-medium">
                        {{ qaPair.question.content }}
                      </p>
                    </div>

                    <div class="flex flex-col gap-3 mt-3">
                      <div class="flex gap-3">
                        <Button
                          v-if="qaPair.answer && qaPair.answer.reference_a"
                          size="sm"
                          variant="outline"
                          @click="toggleReference(index)"
                        >
                          <Icon icon="lucide:eye" class="w-4 h-4 mr-0" />
                          {{ showReference[index] ? '隐藏参考答案' : '查看参考答案' }}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          @click="copyQuestion(qaPair.question.content)"
                        >
                          <Icon icon="lucide:copy" />
                          复制题目
                        </Button>
                        <Button
                          v-if="hasQuestionVideo(qaPair)"
                          size="sm"
                          variant="outline"
                          :class="
                            showQuestionVideo[index]
                              ? 'video-toggle-btn is-open'
                              : 'video-toggle-btn is-closed'
                          "
                          :disabled="questionVideoLoading[index]"
                          @click="toggleQuestionVideo(index, qaPair)"
                        >
                          <Icon
                            :icon="
                              showQuestionVideo[index] ? 'lucide:video-off' : 'lucide:video'
                            "
                            class="w-4 h-4 mr-0"
                          />
                          {{
                            questionVideoLoading[index]
                              ? '加载回放中...'
                              : showQuestionVideo[index]
                                ? '隐藏视频回放'
                                : '查看视频回放'
                          }}
                        </Button>
                      </div>

                      <div
                        v-if="qaPair.question.key_words"
                        class="flex flex-wrap gap-2 items-center"
                      >
                        <span class="text-sm font-bold text-gray-500 mr-1"
                        >回答要点关键词：</span
                        >
                        <Badge
                          v-for="(kw, kidx) in parseKeywords(qaPair.question.key_words)"
                          :key="kidx"
                          color="info"
                          size="md"
                        >
                          {{ kw }}
                        </Badge>
                      </div>

                      <!-- 语音指标 -->
                      <div v-if="qaPair.answer" class="flex flex-wrap gap-2 items-center">
                        <div
                          class="flex items-center gap-1 px-2 py-1 bg-purple-50 dark:bg-purple-500/10 rounded-md border border-purple-200 dark:border-purple-500/30"
                        >
                          <Icon icon="lucide:gauge" class="w-4 h-4 text-purple-500" />
                          <span class="text-xs text-gray-600 dark:text-gray-400">语速</span>
                          <span class="text-xs font-semibold text-purple-600 dark:text-purple-400">
                            {{
                              qaPair.answer.speech_rate != null
                                ? qaPair.answer.speech_rate + ' SPM'
                                : '- SPM'
                            }}
                          </span>
                        </div>
                        <div
                          class="flex items-center gap-1 px-2 py-1 bg-cyan-50 dark:bg-cyan-500/10 rounded-md border border-cyan-200 dark:border-cyan-500/30"
                        >
                          <Icon icon="lucide:audio-waveform" class="w-4 h-4 text-cyan-500" />
                          <span class="text-xs text-gray-600 dark:text-gray-400">清晰度</span>
                          <span class="text-xs font-semibold text-cyan-600 dark:text-cyan-400">
                            {{
                              qaPair.answer.clarity != null
                                ? qaPair.answer.clarity + '%'
                                : '-%'
                            }}
                          </span>
                        </div>
                        <div
                          class="flex items-center gap-1 px-2 py-1 bg-orange-50 dark:bg-orange-500/10 rounded-md border border-orange-200 dark:border-orange-500/30"
                        >
                          <Icon icon="lucide:sparkles" class="w-4 h-4 text-orange-500" />
                          <span class="text-xs text-gray-600 dark:text-gray-400">自信度</span>
                          <span class="text-xs font-semibold text-orange-600 dark:text-orange-400">
                            {{
                              qaPair.answer.confidence != null
                                ? qaPair.answer.confidence + '%'
                                : '-%'
                            }}
                          </span>
                        </div>
                      </div>

                      <transition name="fade">
                        <div
                          v-if="showReference[index] && qaPair.answer && qaPair.answer.reference_a"
                          class="mt-2 p-3 rounded bg-[#ECFDF3] border border-[#8CD9A8] text-[#1E3A3A] dark:bg-[#A6F4C5]/20 dark:border-[#A6F4C5]/50 dark:text-[#A6F4C5]"
                        >
                          <span class="font-bold text-green-800 dark:text-green-100"
                          >参考答案：</span
                          >{{ qaPair.answer.reference_a }}
                        </div>
                      </transition>

                      <transition name="fade">
                        <div
                          v-if="showQuestionVideo[index]"
                          class="mt-2 p-3 rounded bg-blue-50 border border-blue-200 dark:bg-blue-500/10 dark:border-blue-500/30"
                        >
                          <p
                            v-if="questionVideoLoading[index]"
                            class="text-sm text-blue-600 dark:text-blue-300"
                          >
                            视频加载中...
                          </p>
                          <p
                            v-else-if="questionVideoError[index]"
                            class="text-sm text-red-600 dark:text-red-300"
                          >
                            {{ questionVideoError[index] }}
                          </p>
                          <video
                            v-else-if="questionVideoUrl[index]"
                            :src="questionVideoUrl[index]"
                            controls
                            preload="metadata"
                            class="w-full max-w-2xl rounded-lg border border-blue-200 dark:border-blue-500/30"
                            @error="onQuestionVideoError(index)"
                          ></video>
                        </div>
                      </transition>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 回答部分 -->
              <div v-if="qaPair.answer" class="mb-6">
                <div class="flex items-start gap-4">
                  <span
                    class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold"
                  >A</span
                  >
                  <div class="w-full">
                    <!-- 录音播放区域 -->
                    <div
                      v-if="getAudioFilename(qaPair.answer.audio_file)"
                      class="mb-4"
                    >
                      <div class="audio-player-container">
                        <div
                          class="audio-player"
                          @click="
                            playAudio(
                              getAudioFilename(qaPair.answer.audio_file)!,
                              index,
                            )
                          "
                        >
                          <div class="audio-controls">
                            <div
                              class="play-button"
                              :class="{ playing: audioStates[index]?.isPlaying }"
                            >
                              <Icon
                                :icon="
                                  audioStates[index]?.isPlaying
                                    ? 'lucide:pause'
                                    : 'lucide:play'
                                "
                                class="w-4 h-4"
                              />
                            </div>
                            <div class="audio-title" style="margin-right: 10px">
                              语音回答
                            </div>
                            <div class="audio-waveform">
                              <div
                                v-for="(bar, barIndex) in waveformBars"
                                :key="barIndex"
                                class="wave-bar"
                                :class="{ active: audioStates[index]?.isPlaying }"
                                :style="{ height: `${bar.height}px` }"
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="bg-blue-50 dark:bg-blue-500/20 rounded-lg p-4 mb-3">
                      <p
                        class="text-gray-800 dark:text-gray-200 break-words whitespace-pre-wrap"
                        v-html="formatAnswerWithMarks(qaPair.answer.content)"
                      ></p>
                    </div>

                    <div
                      class="bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg p-4"
                    >
                      <div class="flex items-center gap-3 mb-3">
                        <Badge
                          v-if="
                            qaPair.answer.answer_rating !== undefined &&
                            qaPair.answer.answer_rating !== null
                          "
                          color="error"
                          size="md"
                        >
                          评分：{{ qaPair.answer.answer_rating }}/5.0
                        </Badge>
                      </div>
                      <h4
                        class="font-semibold text-green-600 dark:text-green-400 mb-2 flex items-center"
                      >
                        <Icon
                          icon="lucide:square-dashed-bottom-code"
                          class="w-6 h-6 mr-2 text-green-600 dark:text-green-400"
                        />
                        答题评价
                      </h4>
                      <p class="text-gray-600 dark:text-gray-300 mb-4">
                        {{ qaPair.answer.evaluation }}
                      </p>
                      <h4
                        class="font-semibold text-orange-500 dark:text-orange-400 mb-2 flex items-center"
                      >
                        <Icon
                          icon="lucide:panel-bottom-close"
                          class="w-6 h-6 mr-2 text-orange-500 dark:text-orange-400"
                        />
                        改进建议
                      </h4>
                      <p class="text-gray-600 dark:text-gray-300">
                        {{ qaPair.answer.feedback }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="!qaPair.answer" class="mb-6">
                <div class="flex items-start gap-4">
                  <span
                    class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-400 text-white flex items-center justify-center font-bold"
                  >A</span
                  >
                  <div class="w-full">
                    <div
                      class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border-2 border-dashed border-gray-300 dark:border-gray-600"
                    >
                      <p class="text-gray-500 dark:text-gray-400 text-center italic">
                        该问题未作答
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="max-w-6xl mx-auto mt-6 flex justify-center gap-4">
        <button
          @click="goToWeaknessTraining"
          class="flex items-center justify-center gap-2 px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors shadow-md"
        >
          <Icon icon="lucide:target" class="w-5 h-5" />
          <span>薄弱点专属训练</span>
        </button>
        <button
          @click="backToInterview"
          class="flex items-center justify-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow-md"
        >
          <Icon icon="lucide:arrow-left" class="w-5 h-5" />
          <span>返回面试列表</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apexchart from 'vue3-apexcharts'
import { Icon } from '@iconify/vue'
import { ElMessage } from 'element-plus'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import { getApiUrl } from '@/config/api'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const interviewResult = ref(null)

const loading = ref(true)
const polling = ref(false)
const error = ref('')
const processId = ref('')

const interviewData = ref<any>({})
const qaData = ref<any[]>([])
const suggestions = ref<string[]>([])
const overallScore = ref(0)
const showReference = ref<{ [key: number]: boolean }>({})
const landmarkImages = ref<string[]>([])
const showQuestionVideo = ref<{ [key: number]: boolean }>({})
const questionVideoLoading = ref<{ [key: number]: boolean }>({})
const questionVideoError = ref<{ [key: number]: string }>({})
const questionVideoUrl = ref<{ [key: number]: string }>({})

// 新增状态
const userPortrait = ref<any>(null)
const weaknessTags = ref<string[]>([])
const webSearchLoading = ref(false)
const webSearchError = ref('')
const weaknessWebResults = ref<
  { tagName: string; query: string; items: { title: string; link: string; snippet: string; source: string }[] }[]
>([])

const serpApiKey = import.meta.env.VITE_SERPAPI_KEY || ''

const audioStates = ref<
  Record<
    number,
    {
      isPlaying: boolean
      currentTime: number
      duration: number
      progress: number
      audio: HTMLAudioElement | null
    }
  >
>({})

const waveformBars = ref([
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
  { height: 9 },
  { height: 13 },
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
  { height: 9 },
  { height: 13 },
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
  { height: 9 },
  { height: 13 },
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
  { height: 9 },
  { height: 13 },
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
  { height: 9 },
  { height: 13 },
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
  { height: 9 },
  { height: 13 },
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
  { height: 9 },
  { height: 13 },
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
  { height: 9 },
  { height: 13 },
  { height: 8 },
  { height: 12 },
  { height: 6 },
  { height: 10 },
  { height: 14 },
  { height: 7 },
  { height: 11 },
])

import type { ApexOptions } from 'apexcharts'
const chartOptions = ref<ApexOptions>({})
const chartSeries = ref<{ name: string; data: number[] }[]>([])

const qaPairs = computed(() => {
  const pairs: Array<{ question: any; answer: any | null }> = []
  const questions = qaData.value.filter((item) => item.role === 0)
  const answers = qaData.value.filter((item) => item.role === 1)

  questions.forEach((question, index) => {
    const answer = answers[index] || null
    // 合并参考答案
    if (!question.reference_a && answer && answer.reference_a) {
      question.reference_a = answer.reference_a
    }
    pairs.push({ question, answer })
  })

  return pairs
})

function parseResultData(result: any) {
  if (!result || !result.interview_history) {
    error.value = '面试结果数据格式错误'
    loading.value = false
    return
  }

  interviewData.value = result.interview_history || {}
  qaData.value = result.qa_log || []
  interviewData.value.recommended_questions = result.recommended_questions || []
  suggestions.value = [
    result.interview_history?.feedback_suggestion1,
    result.interview_history?.feedback_suggestion2,
    result.interview_history?.feedback_suggestion3,
  ].filter(Boolean)
  overallScore.value = result.interview_history?.score || 0

  landmarkImages.value = result.landmark_images || []

  // 初始化状态
  const questionCount = qaData.value.filter((item) => item.role === 0).length
  showReference.value = new Array(questionCount).fill(false)
  showQuestionVideo.value = {}
  questionVideoLoading.value = {}
  questionVideoError.value = {}
  questionVideoUrl.value = {}

  // 初始化音频状态
  qaPairs.value.forEach((pair, index) => {
    const filename = getAudioFilename(pair.answer?.audio_file)
    if (filename) {
      audioStates.value[index] = {
        isPlaying: false,
        currentTime: 0,
        duration: 0,
        progress: 0,
        audio: null,
      }
    }
  })

  chartOptions.value = {
    chart: { toolbar: { show: false } },
    xaxis: {
      categories: ['专业知识', '技能匹配', '语言表达', '逻辑思维', '创新能力', '抗压能力'],
    },
    yaxis: { min: 0, max: 5 },
    stroke: { show: true, width: 2 },
    fill: { opacity: 0.2 },
    markers: { size: 4 },
    colors: ['#465fff'],
    dataLabels: { enabled: true },
    tooltip: { enabled: true },
  }
  chartSeries.value = [
    {
      name: '能力得分',
      data: [
        result.interview_history?.professional_knowledge || 0,
        result.interview_history?.skill_match || 0,
        result.interview_history?.language_expression || 0,
        result.interview_history?.logical_thinking || 0,
        result.interview_history?.innovation_ability || 0,
        result.interview_history?.stress_resistance || 0,
      ],
    },
  ]

  // 获取额外数据
  fetchExtraData()
}

async function fetchExtraData() {
  // 提取 historyId（假设 interviewData 中为 history_id 或 id）
  const historyId = interviewData.value?.history_id || interviewData.value?.id;
  if (!historyId) {
    console.warn('未获取到 historyId，跳过附加数据加载');
    return;
  }

  // 1. 获取语音指标（原接口）
  try {
    const metricsRes = await axios.get(getApiUrl(`/qa/speech-metrics/${historyId}`));
    const metricsList = metricsRes.data?.data || [];
    const metricsMap = new Map<number, any>();
    metricsList.forEach((item: any) => {
      metricsMap.set(item.qa_id, {
        speech_rate: item.speech_rate,
        clarity: item.clarity,
        confidence: item.confidence,
      });
    });
    // 合并到 qaData
    qaData.value = qaData.value.map((item) => {
      if (item.role === 1 && metricsMap.has(item.qa_id)) {
        const m = metricsMap.get(item.qa_id)!;
        return { ...item, speech_rate: m.speech_rate, clarity: m.clarity, confidence: m.confidence };
      }
      return item;
    });
  } catch (e) {
    console.warn('获取语音指标失败:', e);
  }

  // 2. 获取图片评价（原接口）
  if (landmarkImages.value.length) {
    try {
      const evalRes = await axios.get(getApiUrl(`/history/${historyId}/image-evaluation`));
      if (evalRes.data) {
        interviewData.value = {
          ...interviewData.value,
          expression_evaluation: evalRes.data.expression_evaluation || '',
          gesture_evaluation: evalRes.data.gesture_evaluation || '',
        };
      }
    } catch (e) {
      console.warn('获取图片评价失败:', e);
    }
  }

  // 3. 用户画像（原接口，保持不变）
  const userId = localStorage.getItem('user_id');
  if (userId) {
    try {
      const portraitRes = await axios.get(getApiUrl(`/user/portrait/${userId}`));
      userPortrait.value = portraitRes.data?.data || null;
    } catch (pe) {
      console.warn('用户画像加载失败:', pe);
    }
  }

  await fetchWeaknessTags();
  void searchWeaknessResources();
}

async function fetchWeaknessTags() {
  // 优先使用用户画像的累积薄弱 Tag
  const portraitTags = userPortrait.value?.graph_data?.weak_area_tags
  if (portraitTags && portraitTags.length > 0) {
    weaknessTags.value = portraitTags
      .slice(0, 3)
      .map((t: any) => String(t?.tag_name || '').trim())
      .filter(Boolean)
    if (weaknessTags.value.length > 0) return
  }

  // 兜底：基于本次面试数据（可扩展）
  weaknessTags.value = []
}

async function searchWeaknessResources() {
  webSearchError.value = ''
  weaknessWebResults.value = []

  if (!serpApiKey) {
    webSearchError.value = '未配置 SerpAPI，请设置 VITE_SERPAPI_KEY'
    return
  }

  if (!weaknessTags.value.length) {
    webSearchError.value = '未获取到薄弱点标签，无法检索'
    return
  }

  webSearchLoading.value = true
  try {
    for (const tagName of weaknessTags.value) {
      const query = `计算机 ${tagName} (site:csdn.net OR site:zhihu.com)`
      const response = await axios.get('/serpapi/search.json', {
        params: {
          engine: 'google',
          q: query,
          api_key: serpApiKey,
          hl: 'zh-cn',
          gl: 'cn',
          num: 5,
        },
      })

      const organic = response.data?.organic_results || []
      const allowHosts = ['csdn.net', 'zhihu.com']
      const items = organic
        .slice(0, 8)
        .map((item: any) => {
          const link = String(item?.link || '')
          const source = String(item?.source || item?.displayed_link || '')
          let host = ''
          try {
            host = new URL(link).hostname
          } catch {
            host = ''
          }

          const isAllowed = allowHosts.some(
            (allowed) => host === allowed || host.endsWith(`.${allowed}`),
          )
          if (!isAllowed) return null

          return {
            title: item?.title || '未命名结果',
            link,
            snippet: item?.snippet || '',
            source,
          }
        })
        .filter((item: any) => Boolean(item))
        .slice(0, 2)

      if (items.length > 0) {
        weaknessWebResults.value.push({ tagName, query, items })
      }
    }

    if (!weaknessWebResults.value.length) {
      webSearchError.value = '检索完成，但没有匹配到可展示的结果'
    }
  } catch (e: any) {
    console.error('SerpAPI 检索失败:', e)
    webSearchError.value = e?.response?.data?.error || e?.message || '检索失败，请稍后重试'
  } finally {
    webSearchLoading.value = false
  }
}

// 音频播放逻辑
const getAudioFilename = (audioFile: any): string | null => {
  if (!audioFile) return null
  if (typeof audioFile === 'string') return audioFile
  if (typeof audioFile === 'object' && typeof audioFile.filename === 'string') {
    return audioFile.filename
  }
  return null
}

const playAudio = async (audioFile: string, index: number) => {
  const audioState = audioStates.value[index]
  if (!audioState) return

  try {
    if (audioState.isPlaying && audioState.audio) {
      audioState.audio.pause()
      audioState.isPlaying = false
      return
    }

    if (!audioState.audio) {
      const audioUrl = getApiUrl(`/interview/audio/${audioFile}`)
      audioState.audio = new Audio(audioUrl)

      audioState.audio.addEventListener('loadedmetadata', () => {
        audioState.duration = audioState.audio!.duration || 0
      })
      audioState.audio.addEventListener('timeupdate', () => {
        audioState.currentTime = audioState.audio!.currentTime
        audioState.progress = (audioState.currentTime / audioState.duration) * 100
      })
      audioState.audio.addEventListener('ended', () => {
        audioState.isPlaying = false
        audioState.currentTime = 0
        audioState.progress = 0
      })
      audioState.audio.addEventListener('error', (e) => {
        console.error('音频播放错误:', e)
        audioState.isPlaying = false
      })
    }

    await audioState.audio.play()
    audioState.isPlaying = true

    Object.keys(audioStates.value).forEach((key) => {
      const keyIndex = parseInt(key)
      if (keyIndex !== index && audioStates.value[keyIndex]?.isPlaying) {
        audioStates.value[keyIndex].audio?.pause()
        audioStates.value[keyIndex].isPlaying = false
      }
    })
  } catch (error) {
    console.error('播放音频失败:', error)
    audioState.isPlaying = false
  }
}

// 轮询逻辑保持不变
async function pollStatus() {
  if (!processId.value) return
  loading.value = true
  polling.value = true
  error.value = ''
  let finished = false
  let pollCount = 0
  const MAX_POLL_COUNT = 30

  while (!finished && pollCount < MAX_POLL_COUNT) {
    pollCount++

    try {
      const res = await fetch(getApiUrl(`/interview/end/status/${processId.value}`))
      const data = await res.json()
      if (data.code === 200) {
        if (data.data.status === 'completed') {
          if (data.data.result) {
            console.log('Received result data:', JSON.stringify(data.data.result, null, 2))
            parseResultData(data.data.result)
            loading.value = false
            polling.value = false
            finished = true
          } else {
            error.value = '报告数据为空'
            loading.value = false
            polling.value = false
            finished = true
          }
        } else if (data.data.status === 'failed') {
          error.value = data.data.error || '评估失败，请稍后重试'
          loading.value = false
          polling.value = false
          finished = true
        } else {
          loading.value = true
          await new Promise((r) => setTimeout(r, 3000))
        }
      } else {
        error.value = data.message || '请求失败'
        loading.value = false
        polling.value = false
        finished = true
      }
    } catch (e: any) {
      error.value = e.message || '网络错误'
      loading.value = false
      polling.value = false
      finished = true
    }
  }

  if (!finished && pollCount >= MAX_POLL_COUNT) {
    error.value = '评估报告生成时间较长，请稍后查看'
    loading.value = false
    polling.value = false
  }
}

const difficultyColor = (difficulty: string) => {
  const colorMap: Record<string, 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark'> = {
    easy: 'success',
    medium: 'warning',
    hard: 'error',
  }
  return colorMap[difficulty] || 'info'
}

const toggleReference = (index: number) => {
  showReference.value[index] = !showReference.value[index]
}

const copyQuestion = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('题目已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

const parseKeywords = (keywords: string) => {
  if (!keywords) return []
  return keywords
    .split(',')
    .map((k) => k.trim())
    .filter((k) => k)
}

const getQuestionId = (question: any): string | null => {
  const rawId = question?.qa_id ?? question?.question_id ?? question?.id
  if (rawId === undefined || rawId === null || rawId === '') return null
  return String(rawId)
}

const getQuestionVideoUrl = (questionId: string): string => {
  return getApiUrl(`/interview/video/question/${encodeURIComponent(questionId)}`)
}

const hasQuestionVideo = (qaPair: any): boolean => {
  return Boolean(getQuestionId(qaPair?.question))
}

const resolveQuestionVideoUrl = async (qaPair: any): Promise<string | null> => {
  const questionId = getQuestionId(qaPair?.question)
  if (!questionId) return null
  return getQuestionVideoUrl(questionId)
}

const toggleQuestionVideo = async (index: number, qaPair: any) => {
  showQuestionVideo.value[index] = !showQuestionVideo.value[index]

  if (!showQuestionVideo.value[index]) return
  if (questionVideoUrl.value[index]) return

  questionVideoLoading.value[index] = true
  questionVideoError.value[index] = ''

  const url = await resolveQuestionVideoUrl(qaPair)
  if (!url) {
    questionVideoError.value[index] = '该题暂无视频回放'
    questionVideoLoading.value[index] = false
    return
  }

  questionVideoUrl.value[index] = url
  questionVideoLoading.value[index] = false
}

const onQuestionVideoError = (index: number) => {
  questionVideoError.value[index] = '视频加载失败或文件不存在'
}

const goToWeaknessTraining = () => {
  router.push({
    name: 'WeaknessTraining',
    query: { process_id: processId.value },
    state: {
      recommendedQuestions: interviewData.value.recommended_questions || [],
    },
  })
}

const backToInterview = () => {
  router.push({ name: 'Interview' })
}

// 回答高亮与悬停提示
const formatAnswerWithMarks = (answer: string) => {
  if (!answer) return ''

  let result = answer

  // 绿色高亮 /+文本+/
  result = result.replace(/\/\+(.+?)\+\//g, (_m, content) => {
    return `<mark class="highlight-green">${escapeHtml(content)}</mark>`
  })

  // 红色高亮 /-文本-/
  result = result.replace(/\/-(.+?)-\//g, (_m, content) => {
    return `<mark class="highlight-red">${escapeHtml(content)}</mark>`
  })

  // 符号标记 [✅❗]（括号内容）
  const symbolRegex = /([✅❗])[（(]([^）)]+)[）)]/g
  let symbolMatch: RegExpExecArray | null
  const symbolParts: string[] = []
  let symbolLastIndex = 0

  while ((symbolMatch = symbolRegex.exec(result)) !== null) {
    if (symbolMatch.index > symbolLastIndex) {
      symbolParts.push(result.substring(symbolLastIndex, symbolMatch.index))
    }

    const symbol = symbolMatch[1]
    const content = symbolMatch[2]
    symbolParts.push(
      `<span class="detail-toggle" data-content="${escapeHtml(content)}">${symbol}</span>`,
    )

    symbolLastIndex = symbolRegex.lastIndex
  }

  if (symbolParts.length > 0) {
    if (symbolLastIndex < result.length) {
      symbolParts.push(result.substring(symbolLastIndex))
    }
    result = symbolParts.join('')
  }

  return result
}

const escapeHtml = (text: string): string => {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }
  return text.replace(/[&<>"']/g, (m) => map[m])
}

// 提示框逻辑
const showDetail = (content: string, element: HTMLElement) => {
  const existingBox = document.querySelector('.detail-box')
  if (existingBox) {
    document.body.removeChild(existingBox)
  }

  const box = document.createElement('div')
  box.className = 'detail-box'
  box.textContent = content

  if (document.documentElement.classList.contains('dark')) {
    box.classList.add('dark')
  }

  document.body.appendChild(box)

  const rect = element.getBoundingClientRect()
  const boxWidth = box.offsetWidth
  const boxHeight = box.offsetHeight
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight

  let left = rect.right + 8
  let top = rect.top + (rect.height - boxHeight) / 2

  if (left + boxWidth > windowWidth - 16) {
    left = rect.left - boxWidth - 8
  }
  if (top < 16) {
    top = 16
  }
  if (top + boxHeight > windowHeight - 16) {
    top = windowHeight - boxHeight - 16
  }

  box.style.top = `${top}px`
  box.style.left = `${left}px`

  setTimeout(() => box.classList.add('show'), 10)
}

const hideDetail = () => {
  const box = document.querySelector('.detail-box')
  if (box) {
    box.classList.remove('show')
    setTimeout(() => {
      if (box.parentNode) {
        document.body.removeChild(box)
      }
    }, 300)
  }
}

const handleDetailMouseEnter = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  const toggle = target.closest('.detail-toggle')

  if (toggle) {
    const content = toggle.getAttribute('data-content')
    if (content) {
      showDetail(content, toggle)
    }
  }
}

const handleDetailMouseLeave = () => {
  hideDetail()
}

// 暗黑模式适配
const updateChartForTheme = (isDark: boolean) => {
  const textColor = isDark ? '#E5E7EB' : '#374151'
  const polygonStrokeColor = isDark ? '#4B5563' : '#E5E7EB'
  const polygonFillColors = isDark ? ['#374151', '#1F2937'] : ['#f8f8f8', '#fff']

  chartOptions.value = {
    ...chartOptions.value,
    xaxis: {
      ...chartOptions.value.xaxis,
      labels: {
        style: {
          ...chartOptions.value.xaxis?.labels?.style,
          colors: textColor,
        },
      },
    },
    yaxis: {
      ...chartOptions.value.yaxis,
      labels: {
        style: {
          colors: [isDark ? '#9CA3AF' : '#6B7280'],
        },
      },
    },
    plotOptions: {
      radar: {
        polygons: {
          strokeColors: polygonStrokeColor,
          fill: {
            colors: polygonFillColors,
          },
        },
      },
    },
  }
}

onMounted(() => {
  processId.value =
    (route.query.process_id as string) || localStorage.getItem('interview_process_id') || ''
  if (!processId.value) {
    error.value = '未获取到面试评估进程ID，无法查询结果。'
    loading.value = false
    return
  }
  pollStatus()

  const isDark = document.documentElement.classList.contains('dark')
  updateChartForTheme(isDark)

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.attributeName === 'class') {
        const isDark = (mutation.target as HTMLElement).classList.contains('dark')
        updateChartForTheme(isDark)
      }
    }
  })

  observer.observe(document.documentElement, { attributes: true })
})

onBeforeUnmount(() => {
  Object.values(audioStates.value).forEach((state) => {
    if (state.audio) {
      state.audio.pause()
      state.audio.src = ''
    }
  })
})
</script>

<style scoped>
/* 保留原有样式，新增以下样式 */

/* 高亮样式 */
.highlight-green {
  background: linear-gradient(120deg, #86efac 0%, #4ade80 100%);
  background-size: 100% 35%;
  background-repeat: no-repeat;
  background-position: center bottom;
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 500;
  color: #166534;
  display: inline;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}
.dark .highlight-green {
  background: linear-gradient(120deg, #166534 0%, #14532d 100%);
  color: #86efac;
}

.highlight-red {
  background: linear-gradient(120deg, #fca5a5 0%, #f87171 100%);
  background-size: 100% 35%;
  background-repeat: no-repeat;
  background-position: center bottom;
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 500;
  color: #991b1b;
  display: inline;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}
.dark .highlight-red {
  background: linear-gradient(120deg, #991b1b 0%, #7f1d1d 100%);
  color: #fca5a5;
}

/* 符号悬停 */
.detail-toggle {
  cursor: pointer;
  display: inline-block;
  position: relative;
  margin: 0 2px;
  transition: all 0.2s ease;
}
.detail-toggle:hover {
  transform: scale(1.2);
}

/* 提示框 */
.detail-box {
  position: fixed;
  z-index: 9999;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-width: 300px;
  word-break: break-word;
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  pointer-events: none;
  font-size: 14px;
  line-height: 1.5;
  color: #374151;
}
.detail-box.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
.detail-box.dark {
  background: #1f2937;
  border-color: #374151;
  color: #f3f4f6;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* 音频播放器样式（与之前一致） */
.audio-player-container {
  margin-bottom: 16px;
}
.audio-player {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.dark .audio-player {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-color: #475569;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
.audio-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0;
  min-height: 40px;
}
.play-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
  aspect-ratio: 1;
  min-width: 40px;
  min-height: 40px;
}
.play-button:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}
.play-button.playing {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}
.play-button.playing:hover {
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}
.audio-title {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  margin-right: 10px;
  white-space: nowrap;
  line-height: 1;
}
.dark .audio-title {
  color: #e5e7eb;
}
.audio-waveform {
  display: flex;
  align-items: center;
  gap: 1px;
  height: 30px;
  width: 100%;
  justify-content: flex-start;
}
.wave-bar {
  width: 3px;
  background: linear-gradient(to top, #3b82f6, #1d4ed8);
  border-radius: 2px;
  transition: all 0.3s ease;
  opacity: 0.6;
}
.wave-bar.active {
  animation: waveAnimation 1.5s infinite ease-in-out;
}
@keyframes waveAnimation {
  0%,
  100% {
    transform: scaleY(1);
    opacity: 0.6;
  }
  50% {
    transform: scaleY(1.5);
    opacity: 1;
  }
}
.wave-bar:nth-child(1) {
  animation-delay: 0s;
}
.wave-bar:nth-child(2) {
  animation-delay: 0.1s;
}

.wave-bar:nth-child(3) {
  animation-delay: 0.2s;
}

.wave-bar:nth-child(4) {
  animation-delay: 0.3s;
}

.wave-bar:nth-child(5) {
  animation-delay: 0.4s;
}

.wave-bar:nth-child(6) {
  animation-delay: 0.5s;
}

.wave-bar:nth-child(7) {
  animation-delay: 0.6s;
}

.wave-bar:nth-child(8) {
  animation-delay: 0.7s;
}

.wave-bar:nth-child(9) {
  animation-delay: 0.8s;
}

.wave-bar:nth-child(10) {
  animation-delay: 0.9s;
}

.wave-bar:nth-child(11) {
  animation-delay: 1s;
}

.wave-bar:nth-child(12) {
  animation-delay: 1.1s;
}

.wave-bar:nth-child(13) {
  animation-delay: 1.2s;
}

.wave-bar:nth-child(14) {
  animation-delay: 1.3s;
}

.wave-bar:nth-child(15) {
  animation-delay: 1.4s;
}

.wave-bar:nth-child(16) {
  animation-delay: 1.5s;
}

.landmark-img-box {
  width: 240px;
  height: 240px;
  border-radius: 16px;
  overflow: hidden;
  background: #f3f6fa;
  box-shadow: 0 2px 8px rgba(70, 95, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: box-shadow 0.2s;
}

.landmark-img-box:hover {
  box-shadow: 0 6px 24px rgba(70, 95, 255, 0.18);
}
.landmark-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.dark .landmark-img-box {
  background: #23272f;
  box-shadow: 0 2px 8px rgba(70, 95, 255, 0.18);
}

.video-toggle-btn.is-closed {
  color: #2563eb;
  border-color: #93c5fd;
  background-color: #eff6ff;
}
.video-toggle-btn.is-open {
  color: #b91c1c;
  border-color: #fca5a5;
  background-color: #fef2f2;
}
.dark .video-toggle-btn.is-closed {
  color: #93c5fd;
  border-color: #1d4ed8;
  background-color: rgba(37, 99, 235, 0.16);
}
.dark .video-toggle-btn.is-open {
  color: #fca5a5;
  border-color: #dc2626;
  background-color: rgba(185, 28, 28, 0.2);
}
</style>

<style>
/* 全局/穿透样式：用于 v-html 和 body 动态元素 */
.highlight-green {
  background: linear-gradient(120deg, #86efac 0%, #4ade80 100%);
  background-size: 100% 35%;
  background-repeat: no-repeat;
  background-position: center bottom;
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 500;
  color: #166534;
  display: inline;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}
.dark .highlight-green {
  background: linear-gradient(120deg, #166534 0%, #14532d 100%);
  color: #86efac;
}

.highlight-red {
  background: linear-gradient(120deg, #fca5a5 0%, #f87171 100%);
  background-size: 100% 35%;
  background-repeat: no-repeat;
  background-position: center bottom;
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 500;
  color: #991b1b;
  display: inline;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}
.dark .highlight-red {
  background: linear-gradient(120deg, #991b1b 0%, #7f1d1d 100%);
  color: #fca5a5;
}

.detail-toggle {
  cursor: pointer;
  display: inline-block;
  position: relative;
  margin: 0 2px;
  transition: all 0.2s ease;
}
.detail-toggle:hover {
  transform: scale(1.2);
}

.detail-box {
  position: fixed;
  z-index: 9999;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  max-width: 300px;
  word-break: break-word;
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  pointer-events: none;
  font-size: 14px;
  line-height: 1.5;
  color: #374151;
}
.detail-box.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
.detail-box.dark {
  background: #1f2937;
  border-color: #374151;
  color: #f3f4f6;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
</style>
