<template>
  <div
    class="interview-container relative w-full h-screen overflow-hidden flex flex-col bg-cover transition-colors duration-300"
    :class="{ 'light-mode': !isDarkMode }"
  >
    <div
      class="interview-header shrink-0 flex flex-col md:flex-row justify-between items-center py-[8px] px-[15px] border-b border-[rgba(59,108,225,0.2)] shadow-sm z-10"
    >
      <div class="logo flex items-center gap-[12px]">
        <img
          src="/images/logo/logo2.png"
          alt="Logo"
          class="logo-icon w-[44px] h-[44px] md:w-[50px] md:h-[50px] object-contain"
        />
        <img
          src="/images/名称2.png"
          alt="App Name"
          class="logo-text h-[36px] md:h-[42px] object-contain"
        />
      </div>

      <div
        class="timer flex flex-col items-center md:items-end w-full md:w-[30%] min-w-[220px] mt-[5px] md:mt-0"
      >
        <div class="time-remaining text-[12px] mb-[4px] font-medium tracking-[0.5px]">
          距离面试结束 {{ formatTime(remainingTime) }}
        </div>
        <el-progress
          :percentage="progressPercentage"
          :show-text="false"
          stroke-linecap="round"
          class="progress-bar w-full h-[6px] rounded-[4px] overflow-hidden"
        />
        <div class="time-used text-[12px] mt-[4px] font-medium">
          {{ formatTime(timeUsed) }} / {{ formatTime(totalTime) }}
        </div>
      </div>
    </div>

    <div
      class="content-wrapper flex-1 flex flex-col md:flex-row overflow-hidden p-[10px] gap-[10px]"
    >
      <div
        class="avatar-section flex-none w-full md:w-[25%] min-w-[240px] flex flex-col p-[10px] rounded-[10px] overflow-y-auto custom-scrollbar"
      >
        <div class="ai-section flex flex-col items-center w-full shrink-0">
          <div
            class="camera-container relative mx-auto w-full aspect-video rounded-[10px] overflow-hidden transition-transform duration-300 hover:scale-[1.02]"
          >
            <img
              :src="currentAiAvatar"
              alt="AI 面试官"
              class="w-full h-full object-cover"
              style="view-transition-name: ai-avatar-switch"
            />
            <div
              class="camera-status absolute bottom-[6px] left-0 right-0 text-center text-[11px] py-[2px] px-[6px]"
            >
              <div class="flex items-center justify-center gap-[4px]">
                <div
                  :class="aiSpeaking ? 'pulse bg-[#6d9cff]' : 'bg-gray-400'"
                  class="w-[6px] h-[6px] rounded-full"
                ></div>
                <span>{{ aiSpeaking ? 'AI 正在讲话...' : 'AI 正在聆听' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="camera-section flex flex-col items-center mt-[10px] w-full shrink-0">
          <div
            class="camera-container relative mx-auto w-full aspect-video rounded-[10px] overflow-hidden"
          >
            <video
              ref="cameraVideo"
              class="camera-view w-full h-full object-cover transition-all duration-500"
              autoplay
              playsinline
              :class="{ 'scale-[1.02]': cameraActive }"
            ></video>

            <div
              class="camera-status absolute bottom-[6px] left-0 right-0 text-center text-[11px] py-[2px] px-[6px]"
            >
              <div
                v-if="cameraActive"
                class="camera-active-indicator flex items-center justify-center gap-[4px]"
              >
                <div class="pulse w-[6px] h-[6px] rounded-full"></div>
                <span>摄像头工作中</span>
              </div>
              <div v-else class="camera-inactive flex items-center justify-center gap-[4px]">
                <el-icon class="icon text-[12px]">
                  <VideoCameraFilled />
                </el-icon>
                <span>摄像头未启用</span>
              </div>
            </div>
          </div>
        </div>

        <div
          class="behavior-analysis mt-[10px] flex-1 flex flex-col rounded-[8px] p-[10px] w-full min-h-[160px]"
        >
          <div class="metrics-panel flex flex-col gap-[6px] w-full shrink-0 mb-[6px]">
            <div class="metric-item flex items-center w-full">
              <span class="metric-label text-[12px] font-medium min-w-[70px]">表情自然度:</span>
              <el-progress
                :percentage="expressionScore"
                :color="getScoreColor(expressionScore)"
                :stroke-width="8"
                :show-text="false"
                class="flex-1 mx-[8px]"
              />
              <span class="metric-value text-[12px] font-semibold min-w-[35px] text-right"
              >{{ expressionScore }}%</span
              >
            </div>

            <div class="metric-item flex items-center w-full">
              <span class="metric-label text-[12px] font-medium min-w-[70px]">目光接触:</span>
              <el-progress
                :percentage="eyeContactScore"
                :color="getScoreColor(eyeContactScore)"
                :stroke-width="8"
                :show-text="false"
                class="flex-1 mx-[8px]"
              />
              <span class="metric-value text-[12px] font-semibold min-w-[35px] text-right"
              >{{ eyeContactScore }}%</span
              >
            </div>

            <div class="metric-item flex items-center w-full">
              <span class="metric-label text-[12px] font-medium min-w-[70px]">肢体表达:</span>
              <el-progress
                :percentage="poseScore"
                :color="getScoreColor(poseScore)"
                :stroke-width="8"
                :show-text="false"
                class="flex-1 mx-[8px]"
              />
              <span class="metric-value text-[12px] font-semibold min-w-[35px] text-right"
              >{{ poseScore }}%</span
              >
            </div>

          </div>

          <div
            class="feedback-tags flex-1 flex flex-wrap content-start gap-[6px] overflow-y-auto custom-scrollbar pt-[4px]"
          >
            <el-tag
              v-for="(feedback, index) in activeFeedbacks"
              :key="index"
              :type="feedbackType(feedback.level)"
              class="feedback-tag rounded-[12px] py-[2px] px-[8px] text-[11px] transition-all duration-300"
            >
              {{ feedback.message }}
            </el-tag>
          </div>
        </div>
      </div>

      <div class="dialogue-section flex-1 flex flex-col overflow-hidden rounded-[10px] w-full">
        <div
          class="dialogue-wrapper flex-1 overflow-y-auto p-[15px] rounded-t-[10px] custom-scrollbar"
          ref="dialogueContainer"
        >
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message-group mb-[15px]"
            @click="toggleAiSpeech(msg, index)"
          >
            <!-- AI 消息 -->
            <div v-if="msg.role === 'ai'" class="message ai-message flex mb-[15px] justify-start">
              <div class="avatar shrink-0 mr-[12px]">
                <div
                  class="avatar-small w-[38px] h-[38px] rounded-full flex items-center justify-center overflow-hidden border border-[rgba(91,124,250,0.3)]"
                >
                  <img
                    src="https://ai.lanzidian.com/uploads/images/20240531/b15ea65a6bdea2aa71b43feaf45b26f1.png"
                    alt="AI面试官"
                    class="w-full h-full object-cover block"
                  />
                </div>
              </div>
              <div
                class="bubble relative py-[10px] px-[14px] rounded-[14px] rounded-tl-[4px] min-h-[60px] flex flex-col max-w-[90%] md:max-w-[85%]"
              >
                <div
                  class="content leading-[1.6] text-[14px] md:text-[15px] tracking-[0.2px] font-normal whitespace-pre-wrap"
                >
                  {{ msg.content
                  }}<span v-if="msg.streaming" class="streaming-cursor inline-block ml-[2px]">▋</span>
                </div>
                <div class="timestamp text-[12px] text-right mt-[6px] opacity-80 font-medium">
                  {{ msg.timestamp }}
                </div>
                <div
                  class="audio-indicator mt-[4px] flex items-center gap-[4px] text-[12px] opacity-80"
                  v-if="msg.speaking"
                >
                  <el-icon :size="16">
                    <VideoPlay />
                  </el-icon>
                  <span>正在播放...</span>
                </div>
              </div>
            </div>

            <!-- 用户消息 -->
            <div
              v-else-if="msg.role === 'user'"
              class="message user-message flex mb-[15px] justify-end"
            >
              <div
                class="bubble relative py-[10px] px-[14px] rounded-[14px] rounded-tr-[4px] min-h-[60px] flex flex-col max-w-[90%] items-end"
              >
                <div
                  class="content w-full leading-[1.6] text-[14px] md:text-[15px] tracking-[0.2px] font-normal"
                >
                  <div
                    v-if="msg.type === 'audio'"
                    class="audio-message flex flex-row items-center justify-between w-full min-w-0 md:min-w-[220px] py-[6px] px-[12px] rounded-[12px] transition-all duration-300 cursor-pointer"
                    @click="playAudio(msg)"
                  >
                    <div
                      class="waveform flex items-center justify-start h-[30px] w-full gap-[3px] mr-[10px]"
                    >
                      <div
                        class="wave-bar w-[3px] rounded-[3px] transition-all duration-300 ease-in-out"
                        v-for="(bar, barIndex) in animatedBars"
                        :key="barIndex"
                        :class="{ playing: msg.playing }"
                      ></div>
                    </div>
                    <div
                      class="audio-duration text-[13px] font-semibold min-w-[50px] text-right pl-[10px]"
                    >
                      <span v-if="!msg.playing">{{ msg.duration }}</span>
                      <span v-else>播放中 {{ formatPlayTime(msg.currentTime) }}</span>
                    </div>
                  </div>
                  <div class="whitespace-pre-wrap" v-else>{{ msg.content }}</div>
                </div>
                <div class="timestamp text-[12px] text-right mt-[6px] opacity-80 font-medium">
                  {{ msg.timestamp }}
                </div>
              </div>
              <div class="avatar shrink-0 ml-[12px]">
                <div
                  class="avatar-small w-[38px] h-[38px] rounded-full flex items-center justify-center overflow-hidden border border-[rgba(91,124,250,0.3)]"
                >
                  <img
                    src="https://ai.lanzidian.com/uploads/images/20240531/777372dbcb071cc3a082e34a2784c841.png"
                    alt="面试者"
                    class="w-full h-full object-cover block"
                  />
                </div>
              </div>
            </div>

            <!-- processing 消息：回答后的加载动画 -->
            <div
              v-else-if="msg.type === 'processing'"
              class="message processing-message flex mb-[15px] justify-start"
            >
              <div class="avatar shrink-0 mr-[12px]">
                <div
                  class="avatar-small w-[38px] h-[38px] rounded-full flex items-center justify-center overflow-hidden border border-[rgba(91,124,250,0.3)]"
                >
                  <img
                    src="https://ai.lanzidian.com/uploads/images/20240531/b15ea65a6bdea2aa71b43feaf45b26f1.png"
                    alt="AI面试官"
                    class="w-full h-full object-cover block"
                  />
                </div>
              </div>
              <div
                class="bubble relative py-[10px] px-[14px] rounded-[14px] rounded-tl-[4px] min-h-[60px] flex flex-col max-w-[90%] md:max-w-[85%]"
              >
                <div class="processing-card">
                  <div class="card-header">
                    <div class="header-left">
                      <el-icon class="spinner-icon spinning"><Loading /></el-icon>
                      <span class="header-title">正在分析回答内容</span>
                    </div>
                    <span class="step-count">{{ currentStep }}/3</span>
                  </div>
                  <p class="card-desc">请稍候，系统正在处理本轮回答并准备下一步反馈。</p>
                  <div class="steps-list">
                    <div class="step-item" :class="getStepClass(1)">
                      <div class="step-number">{{ getStepNumberDisplay(1) }}</div>
                      <div class="step-content">
                        <div class="step-title">正在分析回答内容</div>
                        <div class="step-status">{{ getStepStatusText(1) }}</div>
                      </div>
                    </div>
                    <div class="step-item" :class="getStepClass(2)">
                      <div class="step-number">{{ getStepNumberDisplay(2) }}</div>
                      <div class="step-content">
                        <div class="step-title">正在生成反馈结论</div>
                        <div class="step-status">{{ getStepStatusText(2) }}</div>
                      </div>
                    </div>
                    <div class="step-item" :class="getStepClass(3)">
                      <div class="step-number">{{ getStepNumberDisplay(3) }}</div>
                      <div class="step-content">
                        <div class="step-title">正在准备下一题</div>
                        <div class="step-status">{{ getStepStatusText(3) }}</div>
                      </div>
                    </div>
                  </div>
                  <div class="progress-area">
                    <div class="progress-label-row">
                      <span class="progress-label">处理进度</span>
                      <span class="progress-value">{{ loadingProgress }}%</span>
                    </div>
                    <div class="progress-track">
                      <div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <transition name="eval-fade">
          <div
            v-if="lastEvaluation"
            class="evaluation-card mx-[15px] mb-[8px] p-[10px] rounded-[8px] border text-[12px]"
          >
            <div class="flex items-center justify-between mb-[4px]">
              <span class="font-semibold">上题评分：{{ lastEvaluation.answer_rating }} / 5</span>
              <el-tag size="small" type="info">{{ lastEvaluation.skill }}</el-tag>
              <button
                class="text-[12px] opacity-60 hover:opacity-100 ml-[8px]"
                @click="lastEvaluation = null"
              >
                关闭
              </button>
            </div>
            <p class="mb-[2px]">
              <span class="font-medium">评价：</span>{{ lastEvaluation.evaluation }}
            </p>
            <p class="mb-[2px]">
              <span class="font-medium">建议：</span>{{ lastEvaluation.feedback }}
            </p>
            <details class="mt-[2px]">
              <summary class="cursor-pointer opacity-70 select-none">参考答案</summary>
              <p class="mt-[2px] opacity-80">{{ lastEvaluation.reference_a }}</p>
            </details>
          </div>
        </transition>

        <div class="input-section shrink-0 p-[10px]">
          <div
            class="prompt px-[10px] py-[10px] rounded-[10px] text-[13px] md:text-[14px] mb-[10px] flex leading-[1.4] items-center border-l-4"
            v-if="nextQuestion && showPrompt"
          >
            <el-icon class="icon mr-[10px] text-[18px]">
              <ChatRound />
            </el-icon>
            <span>{{ nextQuestion }}</span>
          </div>
          <div class="text-input-row flex items-end gap-[10px] mb-[10px]">
            <el-input
              v-model="textInput"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 4 }"
              resize="none"
              class="text-input custom-scrollbar flex-1"
              :placeholder="isEnded ? '面试已结束' : '请输入你的回答（文本）'"
              @keydown.enter.exact.prevent="sendTextMessage"
              :disabled="isEnded || isSubmittingAnswer"
            />
            <button
              class="action-button end-button text-send-button shrink-0"
              @click="sendTextMessage"
              :disabled="isEnded || isSubmittingAnswer"
            >
              发送
            </button>
          </div>

          <div class="voice-controls">
            <div class="controls-row flex justify-between items-center w-full">
              <div class="record-container flex items-center gap-[12px]">
                <button
                  class="record-button w-[44px] h-[44px] rounded-full flex items-center justify-center cursor-pointer border-[1.5px]"
                  :class="{
                    recording: isRecording,
                    paused: recordingPaused,
                  }"
                  :disabled="isEnded"
                  @click="toggleRecording"
                >
                  <el-icon class="icon text-[20px] font-bold text-white" v-if="!isRecording">
                    <Microphone />
                  </el-icon>
                  <div v-else class="stop-icon w-[14px] h-[14px] bg-white rounded-[2px]"></div>
                </button>

                <button
                  class="theme-toggle-button w-[28px] h-[28px] rounded-full flex items-center justify-center cursor-pointer border transition-all duration-300"
                  @click="toggleTheme"
                >
                  <el-icon class="icon" v-if="isDarkMode">
                    <Sunny />
                  </el-icon>
                  <el-icon class="icon" v-else>
                    <Moon />
                  </el-icon>
                </button>

                <div class="assistant-controls flex gap-[6px] ml-[4px]">
                  <button
                    class="assistant-button w-[32px] h-[32px] rounded-full flex items-center justify-center relative cursor-pointer border transition-all duration-300"
                    @click="openNoteDialog"
                  >
                    <el-icon class="icon">
                      <Notebook />
                    </el-icon>
                    <span
                      class="tooltip absolute bottom-[120%] left-1/2 transform -translate-x-1/2 bg-[rgba(0,0,0,0.7)] text-white py-[4px] px-[8px] rounded-[4px] text-[12px] whitespace-nowrap opacity-0 pointer-events-none transition-opacity duration-300"
                    >笔记</span
                    >
                  </button>

                  <button
                    class="assistant-button w-[32px] h-[32px] rounded-full flex items-center justify-center relative cursor-pointer border transition-all duration-300"
                    @click="togglePrompt"
                  >
                    <el-icon class="icon">
                      <ChatLineRound v-if="showPrompt" />
                      <ChatDotSquare v-else />
                    </el-icon>
                    <span
                      class="tooltip absolute bottom-[120%] left-1/2 transform -translate-x-1/2 bg-[rgba(0,0,0,0.7)] text-white py-[4px] px-[8px] rounded-[4px] text-[12px] whitespace-nowrap opacity-0 pointer-events-none transition-opacity duration-300"
                    >{{ showPrompt ? '隐藏提示' : '显示提示' }}</span
                    >
                  </button>
                </div>

                <div
                  class="recording-info flex items-center text-[12px] font-semibold py-[6px] px-[12px] rounded-full border"
                  v-if="isRecording"
                >
                  <div class="pulse w-[8px] h-[8px] rounded-full mr-[8px]"></div>
                  <span>录音中... {{ formatTime(recordingDuration) }}</span>
                </div>
              </div>

              <button
                class="action-button end-button py-[8px] px-[16px] text-[13px] rounded-[24px] flex items-center gap-[6px] border cursor-pointer transition-all duration-300 font-medium shrink-0"
                @click="endInterview"
              >
                <el-icon class="text-[14px]">
                  <SwitchButton />
                </el-icon>
                <span>结束面试</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="endDialogVisible"
      title=""
      width="400px"
      center
      :show-header="false"
      class="theme-aware-dialog end-interview-dialog"
    >
      <div
        class="dialog-content-wrapper"
        :class="isDarkMode ? 'dark-mode-dialog' : 'light-mode-dialog'"
      >
        <div class="warning-icon">
          <el-icon class="icon"><Warning /></el-icon>
        </div>
        <h3 class="dialog-title">确认结束面试</h3>
        <p class="dialog-desc">您确定要结束面试吗？未完成进度将会丢失。</p>
        <div class="button-group flex gap-[12px] justify-center mt-[24px]">
          <button class="btn-custom btn-cancel" @click="endDialogVisible = false">取消</button>
          <button
            class="btn-custom btn-primary flex items-center justify-center gap-[6px]"
            @click="goToWrittenTest"
          >
            <el-icon><Notebook /></el-icon>进入笔试
          </button>
          <button
            class="btn-custom btn-danger flex items-center justify-center gap-[6px]"
            @click="confirmEndInterview"
          >
            <el-icon><SwitchButton /></el-icon>直接结束
          </button>
        </div>
      </div>
    </el-dialog>

    <audio ref="audioPlayer" style="display: none"></audio>
  </div>

  <el-dialog
    v-model="noteDialogVisible"
    title="面试笔记"
    width="40%"
    center
    class="theme-aware-dialog"
  >
    <div class="note-dialog-content px-[10px]">
      <el-input
        type="textarea"
        :autosize="{ minRows: 6, maxRows: 10 }"
        placeholder="记录重要内容..."
        v-model="noteContent"
        resize="none"
        class="note-textarea mb-[10px] custom-scrollbar"
      ></el-input>
      <div class="note-character-count text-right text-[13px] mt-[8px]">
        已输入 {{ noteContent.length }} 个字符
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer flex gap-[12px] justify-center">
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNote"> 保存笔记 </el-button>
      </span>
    </template>
  </el-dialog>

  <el-dialog
    v-model="showResultOptionDialog"
    title=""
    width="420px"
    :show-header="false"
    center
    class="theme-aware-dialog result-option-dialog"
  >
    <div
      class="dialog-content-wrapper result-option-content text-center"
      :class="isDarkMode ? 'dark-mode-dialog' : 'light-mode-dialog'"
    >
      <div class="completion-icon">
        <el-icon class="check-icon"><Select /></el-icon>
      </div>
      <h3 class="dialog-title completion-title">面试完成</h3>
      <p class="dialog-desc completion-desc mb-6">您的面试数据已提交，是否等待评估报告生成？</p>
      <div class="button-group flex justify-center gap-[12px] mt-[24px]">
        <button class="btn-custom btn-primary" @click="waitForResult">等待报告生成</button>
        <button class="btn-custom btn-secondary" @click="viewLater">稍后查看</button>
      </div>
    </div>
  </el-dialog>

  <a ref="downloadLink" style="display: none"></a>
</template>

<script setup>
// ==================== 加载状态（processing 消息）====================
const loadingProgress = ref(0)
const currentStep = ref(1)
const LOADING_MIN_DURATION = 1800 // 最小显示 1.8 秒
let loadingTimer = null
let loadingFillTimer = null
let processingMsgId = null // 当前 processing 消息的 id

// 是否有 processing 消息
const hasProcessingMessage = computed(() => {
  return messages.value.some(m => m.type === 'processing')
})

// 获取步骤状态
const getStepClass = (step) => {
  if (loadingProgress.value >= step * 33) {
    return 'completed'
  }
  if (loadingProgress.value >= (step - 1) * 33) {
    return 'active'
  }
  return 'pending'
}

const getStepNumberDisplay = (step) => {
  if (loadingProgress.value >= step * 33) {
    return '✓'
  }
  return step
}

const getStepStatusText = (step) => {
  if (loadingProgress.value >= step * 33) {
    return '已完成'
  }
  if (loadingProgress.value >= (step - 1) * 33) {
    return '进行中'
  }
  return '等待中'
}

// 启动加载进度
const startLoadingProgress = () => {
  loadingProgress.value = 0
  currentStep.value = 1

  if (loadingTimer) {
    clearInterval(loadingTimer)
    loadingTimer = null
  }

  // 每 50ms 增加 1%，约 5 秒到 100%
  loadingTimer = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += 1
      if (loadingProgress.value >= 66) {
        currentStep.value = 3
      } else if (loadingProgress.value >= 33) {
        currentStep.value = 2
      }
    } else {
      if (loadingTimer) {
        clearInterval(loadingTimer)
        loadingTimer = null
      }
    }
  }, 50)
}

// 停止加载并移除 processing 消息
const stopLoadingAndHide = () => {
  if (loadingTimer) {
    clearInterval(loadingTimer)
    loadingTimer = null
  }
  if (loadingFillTimer) {
    clearInterval(loadingFillTimer)
    loadingFillTimer = null
  }

  if (processingMsgId !== null) {
    const idx = messages.value.findIndex(m => m.id === processingMsgId)
    if (idx !== -1) {
      messages.value.splice(idx, 1)
    }
    processingMsgId = null
  }
}

// 快速填充进度到 100% 然后移除
const fastFillAndHide = () => {
  return new Promise((resolve) => {
    // 如果已经100%，直接移除并返回
    if (loadingProgress.value >= 100) {
      stopLoadingAndHide()
      resolve()
      return
    }

    // 清除旧的填充定时器
    if (loadingFillTimer) {
      clearInterval(loadingFillTimer)
      loadingFillTimer = null
    }

    // 快速填充进度到100%
    loadingFillTimer = setInterval(() => {
      if (loadingProgress.value < 100) {
        loadingProgress.value += 3
        if (loadingProgress.value >= 66) {
          currentStep.value = 3
        } else if (loadingProgress.value >= 33) {
          currentStep.value = 2
        }
      } else {
        // 已到100%，清除定时器
        clearInterval(loadingFillTimer)
        loadingFillTimer = null
        // 延迟300ms后移除卡片，给用户视觉停留
        setTimeout(() => {
          stopLoadingAndHide()
          resolve()
        }, 300)
      }
    }, 30)
  })
}

import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/store/app'
import { getApiUrl, getWsUrl } from '@/config/api'
import { ElProgress, ElMessage } from 'element-plus'
import {
  Microphone,
  VideoPause,
  VideoPlay,
  SwitchButton,
  ChatRound,
  Warning,
  Sunny,
  Moon,
  Notebook,
  Star,
  Select,
  ChatLineRound,
  ChatDotSquare,
  VideoCameraFilled,
  Loading,
} from '@element-plus/icons-vue'

import CryptoJS from 'crypto-js'
import { useInterviewStore } from '@/store/interview'
import { storeToRefs } from 'pinia'

const appStore = useAppStore()
const interviewStore = useInterviewStore()
const {
  historyId,
  firstQuestion,
  questionQaId: storeQuestionQaId,
  currentTopic,
} = storeToRefs(interviewStore)



const aiStaticImg = '/images/static.gif'
const aiDynamicImg = '/images/dynamic.gif'

const currentAiAvatar = ref(aiStaticImg)
const avatarTransitioning = ref(false)

const preloadImages = () => {
  const staticImg = new Image()
  staticImg.src = aiStaticImg

  const dynamicImg = new Image()
  dynamicImg.src = aiDynamicImg
}

const switchAvatar = (isSpeaking) => {
  if (avatarTransitioning.value) return

  const nextImg = isSpeaking ? aiDynamicImg : aiStaticImg

  if (document.startViewTransition) {
    avatarTransitioning.value = true

    const transition = document.startViewTransition(() => {
      currentAiAvatar.value = nextImg
    })

    transition.ready.then(() => {
      const transitionElements = document.querySelectorAll(
        '::view-transition-new(ai-avatar-switch), ::view-transition-old(ai-avatar-switch)',
      )
      transitionElements.forEach((el) => {
        el.style.animation = 'avatarMotionBlur 0.5s ease-in-out'
      })
    })

    transition.finished.then(() => {
      avatarTransitioning.value = false
    })
  } else {
    avatarTransitioning.value = true

    const imgElement = document.querySelector('[style*="view-transition-name: ai-avatar-switch"]')
    if (imgElement) {
      imgElement.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
      imgElement.style.filter = 'blur(4px)'
      imgElement.style.transform = 'scale(1.05)'

      setTimeout(() => {
        currentAiAvatar.value = nextImg
        imgElement.style.filter = 'blur(0px)'
        imgElement.style.transform = 'scale(1)'

        setTimeout(() => {
          imgElement.style.transition = ''
          avatarTransitioning.value = false
        }, 300)
      }, 150)
    } else {
      currentAiAvatar.value = nextImg
      avatarTransitioning.value = false
    }
  }
}

const router = useRouter()
const route = useRoute()

const currentQuestionQaId = ref(null)
const isSubmittingAnswer = ref(false)
const isEnded = ref(false)
const lastEvaluation = ref(null)

const noteDialogVisible = ref(false)
const noteContent = ref('')

const textInput = ref('')

const audioIdCounter = ref(1)
const mediaRecorder = ref(null)
const userAudioChunks = ref([])
const downloadLink = ref(null)

const getValidHistoryId = () => {
  const numericHistoryId = Number(historyId.value)
  return Number.isInteger(numericHistoryId) && numericHistoryId > 0 ? numericHistoryId : null
}

const aiSpeaking = ref(false)
const ttsWebSocket = ref(null)
const ttsAudioChunks = ref([])
watch(aiSpeaking, (isSpeaking) => {
  switchAvatar(isSpeaking)
})

const endProcessing = ref(false)

const cameraVideo = ref(null)
const cameraActive = ref(false)
const cameraStream = ref(null)

const expressionScore = ref(0)
const eyeContactScore = ref(0)
const poseScore = ref(0)
const activeFeedbacks = ref([])
const behaviorWs = ref(null)
let behaviorFrameTimer = null

const showPrompt = ref(true)

const imgCounter = ref(0)
const imageCaptureTimer = ref(null)

const questionVideoRecorder = ref(null)
const questionVideoChunks = ref([])
const questionVideoStarted = ref(false)
const questionVideoId = ref('')
const questionVideoMimeType = ref('video/webm')

const getQuestionId = (question) => {
  const rawId = question?.qa_id ?? question?.question_id ?? question?.id
  if (rawId === undefined || rawId === null || rawId === '') return null
  return String(rawId)
}

const getPreferredVideoMimeType = () => {
  const mimeTypes = ['video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm']
  for (const mimeType of mimeTypes) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(mimeType)) {
      return mimeType
    }
  }
  return ''
}

const resetQuestionVideoState = () => {
  if (questionVideoRecorder.value) {
    questionVideoRecorder.value.ondataavailable = null
    questionVideoRecorder.value.onstop = null
    questionVideoRecorder.value.onerror = null
  }
  questionVideoRecorder.value = null
  questionVideoChunks.value = []
  questionVideoStarted.value = false
  questionVideoId.value = ''
  questionVideoMimeType.value = 'video/webm'
}

const startQuestionVideoRecording = async (question) => {
  const questionId = getQuestionId(question)
  if (!questionId || !historyId.value || !cameraStream.value || !window.MediaRecorder) return

  if (questionVideoStarted.value) {
    await stopQuestionVideoRecording(true)
  }

  try {
    const formData = new FormData()
    formData.append('history_id', String(historyId.value))
    formData.append('question_qa_id', questionId)

    const startRes = await fetch(getApiUrl('/interview/video/start'), {
      method: 'POST',
      body: formData,
    })

    if (!startRes.ok) {
      throw new Error(`HTTP ${startRes.status}`)
    }

    const startData = await startRes.json()
    if (startData?.code !== 200) {
      throw new Error(startData?.message || 'video start failed')
    }

    const preferredMimeType = getPreferredVideoMimeType()
    let recorder = null

    try {
      recorder = preferredMimeType
        ? new MediaRecorder(cameraStream.value, { mimeType: preferredMimeType })
        : new MediaRecorder(cameraStream.value)
    } catch {
      recorder = new MediaRecorder(cameraStream.value)
    }

    questionVideoRecorder.value = recorder
    questionVideoChunks.value = []
    questionVideoStarted.value = true
    questionVideoId.value = questionId
    questionVideoMimeType.value = recorder.mimeType || preferredMimeType || 'video/webm'

    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        questionVideoChunks.value.push(event.data)
      }
    }

    recorder.onerror = (event) => {
      console.error('题目视频录制错误:', event)
    }

    recorder.start(1000)
  } catch (error) {
    console.error('启动题目视频录制失败:', error)
    resetQuestionVideoState()
  }
}

const stopQuestionVideoRecording = async (silent = false) => {
  const started = questionVideoStarted.value
  const questionId = questionVideoId.value
  const recorder = questionVideoRecorder.value

  if (!started || !questionId || !recorder) {
    resetQuestionVideoState()
    return
  }

  try {
    const blob = await new Promise((resolve, reject) => {
      const finalize = () => {
        const merged = new Blob(questionVideoChunks.value, {
          type: questionVideoMimeType.value || 'video/webm',
        })
        resolve(merged)
      }

      recorder.onstop = finalize
      recorder.onerror = (event) => reject(event)

      if (recorder.state !== 'inactive') {
        recorder.stop()
      } else {
        finalize()
      }
    })

    if (!blob || blob.size === 0) {
      throw new Error('empty video blob')
    }

    const ext = (questionVideoMimeType.value || '').includes('mp4') ? 'mp4' : 'webm'
    const formData = new FormData()
    formData.append('history_id', String(historyId.value))
    formData.append('question_qa_id', questionId)
    formData.append('file', blob, `${questionId}.${ext}`)

    const stopRes = await fetch(getApiUrl('/interview/video/end'), {
      method: 'POST',
      body: formData,
    })

    if (!stopRes.ok) {
      throw new Error(`HTTP ${stopRes.status}`)
    }

    const stopData = await stopRes.json()
    if (stopData?.code !== 200 && stopData?.code !== 202) {
      throw new Error(stopData?.message || 'video end failed')
    }
  } catch (error) {
    console.error('结束题目视频录制失败:', error)
    if (!silent) {
      ElMessage.warning('视频保存失败，不影响当前作答')
    }
  } finally {
    resetQuestionVideoState()
  }
}

const captureAndSaveImage = async () => {
  const validHistoryId = getValidHistoryId()
  if (!validHistoryId) {
    console.warn('historyId无效，跳过截图保存')
    return
  }

  if (!cameraActive.value || !cameraVideo.value) {
    console.warn('摄像头未启动，无法捕获图片')
    return
  }

  try {
    const canvas = document.createElement('canvas')
    const video = cameraVideo.value
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    canvas.toBlob(
      async (blob) => {
        if (!blob) {
          console.error('图片转换失败')
          return
        }

        const formData = new FormData()
        formData.append('image', blob, 'capture.jpg')
        formData.append('history_id', String(validHistoryId))

        try {
          const response = await fetch(getApiUrl('/save-image'), {
            method: 'POST',
            body: formData,
          })

          const result = await response.json()
          if (result.success) {
            console.log('图片保存成功:', result.filename)
            imgCounter.value = result.counter
          } else {
            console.error('图片保存失败:', result.error)
          }
        } catch (e) {
          console.error('请求失败:', e)
        }
      },
      'image/jpeg',
      0.9,
    )
  } catch (error) {
    console.error('捕获图片失败:', error)
  }
}

const scheduleImageCapture = () => {
  if (imageCaptureTimer.value) {
    clearTimeout(imageCaptureTimer.value)
    imageCaptureTimer.value = null
  }

  imageCaptureTimer.value = setTimeout(() => {
    void captureAndSaveImage()
    imageCaptureTimer.value = null
  }, 2000)
}

const getScoreColor = (score) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const feedbackType = (level) => {
  switch (level) {
    case 'positive':
      return 'success'
    case 'warning':
      return 'warning'
    case 'critical':
      return 'danger'
    default:
      return ''
  }
}

const startCamera = async () => {
  try {
    cameraStream.value = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user',
      },
      audio: false,
    })

    cameraVideo.value.srcObject = cameraStream.value
    cameraActive.value = true
  } catch (error) {
    console.error('摄像头启动失败:', error)
    ElMessage.error('无法启动摄像头: ' + error.message)
    cameraActive.value = false
  }
}

const stopCamera = () => {
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach((track) => track.stop())
    cameraStream.value = null
  }
  if (cameraVideo.value) {
    cameraVideo.value.srcObject = null
  }
  cameraActive.value = false
}

const totalTime = ref(28 * 60)
const timeUsed = ref(0)
const remainingTime = computed(() => totalTime.value - timeUsed.value)
const progressPercentage = computed(() => (timeUsed.value / totalTime.value) * 100)

const formatCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

const generateAuthUrl = () => {
  const APIKey = import.meta.env.VITE_XUNFEI_API_KEY
  const APISecret = import.meta.env.VITE_XUNFEI_API_SECRET
  if (!APIKey || !APISecret) {
    return ''
  }
  const url = 'wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6'

  const host = 'cbm01.cn-huabei-1.xf-yun.com'

  const date = new Date().toGMTString()

  const algorithm = 'hmac-sha256'
  const headers = 'host date request-line'

  const signatureOrigin = `host: ${host}\ndate: ${date}\nGET /v1/private/mcd9m97e6 HTTP/1.1`

  const signature = CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(signatureOrigin, APISecret))

  const authorizationOrigin = `api_key="${APIKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`

  const authorization = btoa(unescape(encodeURIComponent(authorizationOrigin)))

  return `${url}?authorization=${authorization}&date=${encodeURIComponent(date)}&host=${encodeURIComponent(host)}`
}

const speakText = (text, index) => {
  const appId = import.meta.env.VITE_XUNFEI_APPID
  const apiKey = import.meta.env.VITE_XUNFEI_API_KEY
  const apiSecret = import.meta.env.VITE_XUNFEI_API_SECRET
  if (!appId || !apiKey || !apiSecret) {
    ElMessage.warning('语音播报跳过：讯飞鉴权配置缺失')
    return
  }

  if (aiSpeaking.value) stopAiSpeech()

  const authUrl = generateAuthUrl()
  if (!authUrl) {
    ElMessage.warning('语音播报跳过：鉴权URL生成失败')
    return
  }
  ttsWebSocket.value = new WebSocket(authUrl)

  ttsAudioChunks.value = []

  const connectTimeout = setTimeout(() => {
    if (ttsWebSocket.value.readyState === WebSocket.CONNECTING) {
      ttsWebSocket.value.close()
      aiSpeaking.value = false
      messages.value[index].speaking = false
      ElMessage.error('语音合成连接超时，请重试')
    }
  }, 5000)

  ttsWebSocket.value.onopen = () => {
    clearTimeout(connectTimeout)
    console.log('TTS WebSocket连接已打开')
    aiSpeaking.value = true

    messages.value[index].speaking = true

    const encoder = new TextEncoder()
    const textBytes = encoder.encode(text)
    let binaryText = ''
    for (let i = 0; i < textBytes.length; i++) {
      binaryText += String.fromCharCode(textBytes[i])
    }
    const base64Text = btoa(binaryText)

    const requestData = {
      header: {
        app_id: appId,
        status: 2,
      },
      parameter: {
        tts: {
          vcn: 'x6_lingfeiyi_pro',
          speed: 50,
          volume: 50,
          pitch: 50,
          bgs: 0,
          reg: 0,
          rdn: 0,
          rhy: 0,
          audio: {
            encoding: 'lame',
            sample_rate: 24000,
            channels: 1,
            bit_depth: 16,
            frame_size: 0,
          },
        },
      },
      payload: {
        text: {
          encoding: 'utf8',
          compress: 'raw',
          format: 'plain',
          status: 2,
          seq: 0,
          text: base64Text,
        },
      },
    }

    ttsWebSocket.value.send(JSON.stringify(requestData))
  }

  ttsWebSocket.value.onmessage = (event) => {
    try {
      const response = JSON.parse(event.data)

      if (response.header.code !== 0) {
        console.error('TTS错误:', response.header)
        ElMessage.error(`语音合成失败: ${response.header.message || '未知错误'}`)
        return
      }

      if (response.payload && response.payload.audio) {
        const audioData = atob(response.payload.audio.audio)
        const arrayBuffer = new ArrayBuffer(audioData.length)
        const uintArray = new Uint8Array(arrayBuffer)

        for (let i = 0; i < audioData.length; i++) {
          uintArray[i] = audioData.charCodeAt(i)
        }

        ttsAudioChunks.value.push(arrayBuffer)

        if (response.header.status === 2) {
          playAiSpeech(index)
        }
      }
    } catch (error) {
      console.error('处理TTS响应失败:', error)
      ElMessage.error('处理语音合成响应时出错')
    }
  }

  ttsWebSocket.value.onerror = (error) => {
    clearTimeout(connectTimeout)
    console.error('TTS WebSocket错误:', error)
    aiSpeaking.value = false
    messages.value[index].speaking = false
    ElMessage.error('语音合成连接错误，请检查网络')
  }

  ttsWebSocket.value.onclose = (event) => {
    clearTimeout(connectTimeout)
    console.log('TTS WebSocket连接已关闭', event)
  }
}

const playAiSpeech = (index) => {
  if (ttsAudioChunks.value.length === 0) {
    ElMessage.warning('未收到音频数据')
    return
  }

  try {
    const totalLength = ttsAudioChunks.value.reduce((acc, chunk) => acc + chunk.byteLength, 0)
    const combinedBuffer = new Uint8Array(totalLength)
    let offset = 0

    ttsAudioChunks.value.forEach((chunk) => {
      combinedBuffer.set(new Uint8Array(chunk), offset)
      offset += chunk.byteLength
    })

    const blob = new Blob([combinedBuffer], { type: 'audio/mp3' })
    const audioUrl = URL.createObjectURL(blob)

    const audio = new Audio(audioUrl)
    audio.play()

    messages.value[index].audioUrl = audioUrl
    messages.value[index].speaking = true

    audio.onended = () => {
      aiSpeaking.value = false
      messages.value[index].speaking = false
      URL.revokeObjectURL(audioUrl)
      ttsAudioChunks.value = []
    }

    audio.onerror = (error) => {
      console.error('音频播放错误:', error)
      aiSpeaking.value = false
      messages.value[index].speaking = false
    }
  } catch (error) {
    console.error('播放音频失败:', error)
    ElMessage.error('处理音频数据时出错')
    aiSpeaking.value = false
    messages.value[index].speaking = false
  }
}

const stopAiSpeech = () => {
  if (ttsWebSocket.value && ttsWebSocket.value.readyState === WebSocket.OPEN) {
    ttsWebSocket.value.close()
  }
  aiSpeaking.value = false
  ttsAudioChunks.value = []
}

const messages = ref([])
const nextQuestion = ref('')

const aiListening = ref(false)

const interviewPosition = ref('')

const isRecording = ref(false)
const isSpeaking = ref(false)
const recordingPaused = ref(false)
const recordingDuration = ref(0)
const recordingTimer = ref(null)

const audioPlayer = ref(null)

const endDialogVisible = ref(false)

const animatedBars = ref([])
const waveAnimationInterval = ref(null)

const isDarkMode = ref(false)

const createWaveBars = () => {
  const bars = []
  for (let i = 0; i < 16; i++) {
    bars.push({
      height: Math.floor(Math.random() * 15) + 5,
    })
  }
  animatedBars.value = bars
}

const animateWaveBars = () => {
  waveAnimationInterval.value = setInterval(() => {
    animatedBars.value.forEach((bar, index) => {
      bar.height = Math.max(
        5,
        Math.min(25, bar.height + (Math.random() > 0.5 ? 1 : -1) * Math.random() * 4),
      )
    })
  }, 200)
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatPlayTime = (seconds) => {
  const secs = Math.floor(seconds % 60)
  return `0:${secs.toString().padStart(2, '0')}`
}

// ==================== 发送文本消息 ====================
const sendTextMessage = async () => {
  const content = textInput.value.trim()
  if (!content) {
    ElMessage.warning('请输入内容后再发送')
    return
  }

  if (isRecording.value) {
    ElMessage.warning('录音中，请先停止录音再发送文本')
    return
  }

  if (isEnded.value) {
    ElMessage.warning('面试已结束，无法继续作答')
    return
  }

  if (isSubmittingAnswer.value) {
    ElMessage.warning('正在提交上一个回答，请稍候')
    return
  }

  scheduleImageCapture()

  // 添加用户消息
  messages.value.push({
    role: 'user',
    type: 'text',
    content,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  })

  const qaId = currentQuestionQaId.value
  textInput.value = ''
  scrollToBottom()

  await stopQuestionVideoRecording()

  await submitAnswer({ type: 'text', content, qaId })
}

// ==================== 录音控制 ====================
const toggleRecording = async () => {
  if (isEnded.value) {
    ElMessage.warning('面试已结束，无法继续作答')
    return
  }
  if (isRecording.value) {
    await stopRecording()
  } else {
    try {
      await startRecording()
    } catch (error) {
      console.error('录音启动失败:', error)
      ElMessage.error('无法启动录音，请检查麦克风权限')
    }
  }
}

const startRecording = async () => {
  if (isRecording.value) return

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    mediaRecorder.value = new MediaRecorder(stream)
    userAudioChunks.value = []

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        userAudioChunks.value.push(event.data)
      }
    }

    mediaRecorder.value.onstop = () => {
      const audioBlob = new Blob(userAudioChunks.value, { type: 'audio/wav' })
      saveAudioFile(audioBlob)

      stream.getTracks().forEach((track) => track.stop())
    }

    mediaRecorder.value.start()

    isRecording.value = true
    isSpeaking.value = true
    aiListening.value = true
    recordingPaused.value = false
    recordingDuration.value = 0

    nextQuestion.value = '回答中...'

    recordingTimer.value = setInterval(() => {
      recordingDuration.value += 1
    }, 1000)

    animateWaveBars()

    scheduleImageCapture()
  } catch (err) {
    console.error('麦克风访问失败:', err)
    ElMessage.error('麦克风访问被拒绝，请允许使用麦克风')
    return Promise.reject(err)
  }
}

const stopRecording = async () => {
  if (!isRecording.value || !mediaRecorder.value) return
  if (recordingDuration.value < 1) return

  if (mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
  }

  isRecording.value = false
  isSpeaking.value = false
  aiListening.value = false
  clearInterval(recordingTimer.value)
  clearInterval(waveAnimationInterval.value)

  if (imageCaptureTimer.value) {
    clearTimeout(imageCaptureTimer.value)
    imageCaptureTimer.value = null
  }

  await stopQuestionVideoRecording()
}

// 语音转写并提交（保留原有后端调用）
const transcribeAndSubmitAudio = async (fileName, audioBlob, qaId) => {
  const validHistoryId = getValidHistoryId();
  if (!validHistoryId) {
    // 不弹框，不报错，直接提交答案（硬编码模式不需要 historyId）
    console.warn('historyId无效，跳过语音转写，直接提交答案');
    await submitAnswer({ type: 'audio', qaId });
    return;
  }

  // 原有转录请求逻辑保持不变
  const formData = new FormData();
  formData.append('file', audioBlob, fileName);
  formData.append('history_id', String(validHistoryId));
  if (qaId !== null && qaId !== undefined) {
    formData.append('question_qa_id', String(qaId));
  }
  try {
    const response = await fetch(getApiUrl('/voice/transcribe'), {
      method: 'POST',
      body: formData,
    });
    const result = await response.json();
    if (!result.success) {
      console.error('音频转录失败:', result.error || result.message);
      ElMessage.warning('语音上传失败，不影响继续作答');
      return;
    }
    await submitAnswer({ type: 'audio', qaId });
  } catch (error) {
    console.error('保存请求失败:', error);
    ElMessage.warning('语音上传失败，请检查网络');
  }
};

const saveAudioFile = async (audioBlob) => {
  const fileName = `his-${historyId.value}-audioid-${audioIdCounter.value}.wav`
  audioIdCounter.value++

  const audioUrl = URL.createObjectURL(audioBlob)

  const userMessage = {
    role: 'user',
    type: 'audio',
    audioUrl: audioUrl,
    duration: recordingDuration.value,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    playing: false,
    currentTime: 0,
    filename: fileName,
  }

  messages.value.push(userMessage)

  const qaId = currentQuestionQaId.value
  scrollToBottom()

  await transcribeAndSubmitAudio(fileName, audioBlob, qaId)
}

// ==================== 提交答案（由后端生成下一题） ====================
const submitAnswer = async ({ type, content = null, qaId }) => {
  if (isEnded.value || isSubmittingAnswer.value) return

  const validHistoryId = getValidHistoryId()
  if (!validHistoryId || qaId === null || qaId === undefined) {
    ElMessage.warning('面试记录尚未初始化，请返回准备页重新开始')
    return
  }

  isSubmittingAnswer.value = true
  let streamingMsgIdx = -1

  try {
    const formData = new FormData()
    formData.append('history_id', String(validHistoryId))
    formData.append('question_qa_id', String(qaId))
    if (type === 'text' && content) {
      formData.append('answer_content', content)
    }

    const response = await fetch(getApiUrl('/interview/answer/stream'), {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('响应流不可用')

    const decoder = new TextDecoder()
    let buffer = ''
    let currentEvent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''

      for (const line of lines) {
        if (!line) {
          currentEvent = ''
          continue
        }
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
          continue
        }
        if (!line.startsWith('data: ')) continue

        let data
        try {
          data = JSON.parse(line.slice(6))
        } catch {
          continue
        }

        if (currentEvent === 'metadata' && data.action !== 'end') {
          nextQuestion.value = data.current_topic || '正在生成下一题…'
          messages.value.push({
            role: 'ai',
            content: '',
            streaming: true,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            speaking: false,
            audioUrl: null,
          })
          streamingMsgIdx = messages.value.length - 1
          scrollToBottom()
        } else if (currentEvent === 'token' && streamingMsgIdx >= 0 && data.content) {
          messages.value[streamingMsgIdx].content += data.content
          scrollToBottom()
        } else if (currentEvent === 'done') {
          if (data.action === 'end') {
            isEnded.value = true
            currentQuestionQaId.value = null
            const endContent = '感谢你的回答，本次面试已结束。请点击“结束面试”生成评估报告。'
            if (streamingMsgIdx >= 0) {
              messages.value[streamingMsgIdx].content = endContent
              messages.value[streamingMsgIdx].streaming = false
            } else {
              messages.value.push({
                role: 'ai',
                content: endContent,
                streaming: false,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                speaking: false,
                audioUrl: null,
              })
            }
            nextQuestion.value = '面试已结束，请生成评估报告'
          } else if (streamingMsgIdx >= 0) {
            const finalQuestion = data.next_question || messages.value[streamingMsgIdx].content
            messages.value[streamingMsgIdx].content = finalQuestion
            messages.value[streamingMsgIdx].streaming = false
            currentQuestionQaId.value = data.question_qa_id
            interviewStore.setQuestionQaId(data.question_qa_id)
            nextQuestion.value = data.current_topic || finalQuestion
            void startQuestionVideoRecording({ qa_id: String(data.question_qa_id) })
            try {
              speakText(finalQuestion, streamingMsgIdx)
            } catch (ttsError) {
              console.warn('语音播报失败:', ttsError)
            }
          }
          scrollToBottom()
        } else if (currentEvent === 'error') {
          throw new Error(data.message || '生成下一题失败')
        }
      }
    }
  } catch (error) {
    console.error('提交回答失败:', error)
    ElMessage.error(`提交回答失败：${error instanceof Error ? error.message : '未知错误'}`)
    if (streamingMsgIdx >= 0 && messages.value[streamingMsgIdx]?.streaming) {
      messages.value.splice(streamingMsgIdx, 1)
    }
  } finally {
    isSubmittingAnswer.value = false
  }
}

const displayNextQuestion = (questionText, qaId, topicHint = '') => {
  currentQuestionQaId.value = qaId
  interviewStore.setQuestionQaId(qaId)
  nextQuestion.value = topicHint || questionText

  setTimeout(() => {
    const newMsg = {
      role: 'ai',
      content: questionText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      speaking: false,
      audioUrl: null,
    }
    messages.value.push(newMsg)
    const msgIndex = messages.value.length - 1

    void startQuestionVideoRecording({ qa_id: String(qaId) })
    try {
      speakText(questionText, msgIndex)
    } catch (ttsError) {
      console.warn('语音播报失败:', ttsError)
    }
    scrollToBottom()
  }, 1000)
}

const toggleAiSpeech = (msg, index) => {
  if (msg.role !== 'ai') return

  if (msg.speaking) {
    stopAiSpeech()
    msg.speaking = false
  } else if (msg.audioUrl) {
    const audio = new Audio(msg.audioUrl)
    audio.play()
    msg.speaking = true

    audio.onended = () => {
      msg.speaking = false
    }
  } else {
    speakText(msg.content, index)
  }
}

const playAudio = (msg) => {
  if (msg.playing) {
    msg.playing = false
    audioPlayer.value.pause()
    clearInterval(msg.playTimer)
    return
  }

  messages.value.forEach((m) => {
    if (m.playing) {
      m.playing = false
      clearInterval(m.playTimer)
    }
  })

  msg.playing = true
  msg.currentTime = 0
  audioPlayer.value.src = msg.audioUrl
  audioPlayer.value.play().catch((e) => {
    console.error('音频播放失败:', e)
    ElMessage.error('音频播放失败')
    clearInterval(msg.playTimer)
    msg.playing = false
  })

  msg.playTimer = setInterval(() => {
    if (msg.currentTime < msg.duration) {
      msg.currentTime += 1
      if (msg.currentTime / msg.duration > 0.05) {
        audioPlayer.value.currentTime = msg.currentTime
      }
    } else {
      clearInterval(msg.playTimer)
      msg.playing = false
      audioPlayer.value.pause()
    }
  }, 1000)
}

const dialogueContainer = ref(null)
const scrollToBottom = () => {
  nextTick(() => {
    if (dialogueContainer.value) {
      dialogueContainer.value.scrollTop = dialogueContainer.value.scrollHeight
    }
  })
}

const endInterview = async () => {
  await stopQuestionVideoRecording(true)
  endDialogVisible.value = true
}

const showResultOptionDialog = ref(false)
const processId = ref('')
const reportPollingTimer = ref(null)
const reportPollingCount = ref(0)
const MAX_POLLING_COUNT = 30

const confirmEndInterview = async () => {
  if (endProcessing.value) return
  endProcessing.value = true
  endDialogVisible.value = false
  try {
    await stopQuestionVideoRecording(true)

    const formData = new FormData()
    formData.append('history_id', historyId.value)
    const res = await fetch(getApiUrl('/interview/end'), {
      method: 'POST',
      body: formData,
    })
    const data = await res.json()
    if (data.code === 202 && data.data.process_id) {
      processId.value = data.data.process_id
      localStorage.setItem('interview_process_id', processId.value)
      showResultOptionDialog.value = true
    } else {
      ElMessage.error(data.message || '结束面试失败')
    }
  } catch (e) {
    ElMessage.error('网络错误，结束面试失败')
  } finally {
    endProcessing.value = false
  }
}

const waitForResult = () => {
  showResultOptionDialog.value = false
  ElMessage.success('正在生成评估报告，请稍候...')
  reportPollingCount.value = 0
  startReportPolling()
}

const startReportPolling = () => {
  if (!processId.value) {
    ElMessage.error('未获取到面试评估进程 ID')
    return
  }

  const pollReportStatus = async () => {
    reportPollingCount.value++

    if (reportPollingCount.value > MAX_POLLING_COUNT) {
      if (reportPollingTimer.value) {
        clearInterval(reportPollingTimer.value)
        reportPollingTimer.value = null
      }
      ElMessage.warning('评估报告生成时间较长，请稍后查看')
      return
    }

    try {
      const res = await fetch(getApiUrl(`/interview/end/status/${processId.value}`))
      const data = await res.json()

      if (data.code === 200) {
        if (data.data.status === 'completed') {
          if (reportPollingTimer.value) {
            clearInterval(reportPollingTimer.value)
            reportPollingTimer.value = null
          }
          ElMessage.success('评估报告已生成')
          router.push({
            name: 'InterviewResult',
            query: { process_id: processId.value },
          })
        } else if (data.data.status === 'failed') {
          if (reportPollingTimer.value) {
            clearInterval(reportPollingTimer.value)
            reportPollingTimer.value = null
          }
          ElMessage.error('评估报告生成失败，请稍后重试')
        }
      } else {
        console.error('轮询报告状态失败:', data.message)
      }
    } catch (e) {
      console.error('轮询报告状态失败:', e)
    }
  }

  pollReportStatus()
  reportPollingTimer.value = setInterval(pollReportStatus, 3000)
}

const viewLater = () => {
  showResultOptionDialog.value = false
  if (processId.value) {
    const existingNotifications = JSON.parse(
      localStorage.getItem('interview_notifications') || '[]',
    )
    existingNotifications.push({
      id: Date.now(),
      processId: processId.value,
      status: 'generating',
      createdAt: new Date().toISOString(),
      read: false,
    })
    localStorage.setItem('interview_notifications', JSON.stringify(existingNotifications))
  }
  ElMessage.success('面试报告生成中，请稍后于本站通知中查看')
  router.push({ name: 'Interview' })
}

const goToWrittenTest = async () => {
  if (endProcessing.value) return
  endProcessing.value = true
  endDialogVisible.value = false
  ElMessage.info('正在跳转至笔试环节...')
  try {
    await stopQuestionVideoRecording(true)

    const formData = new FormData()
    formData.append('history_id', historyId.value)
    const res = await fetch(getApiUrl('/interview/end'), {
      method: 'POST',
      body: formData,
    })
    const data = await res.json()
    if (data.code === 202 && data.data.process_id) {
      const processId = data.data.process_id
      localStorage.setItem('interview_process_id', processId)

      router.push({
        name: 'WrittenTest',
        query: {
          interviewId: historyId.value,
          process_id: processId,
        },
      })
    } else {
      ElMessage.error(data.message || '启动面试评估任务失败')
      endProcessing.value = false
      return
    }
  } catch (e) {
    ElMessage.error('跳转笔试失败')
  } finally {
    endProcessing.value = false
  }
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  document.body.classList.toggle('dark-mode', isDarkMode.value)
}




let interviewTimer = null
onMounted(async () => {
  // 预加载图片（保留原有逻辑）
  const img1 = new Image()
  img1.src = aiStaticImg
  const img2 = new Image()
  img2.src = aiDynamicImg

  if (storeQuestionQaId.value && firstQuestion.value) {
    currentQuestionQaId.value = storeQuestionQaId.value
    nextQuestion.value = currentTopic.value || firstQuestion.value
    displayNextQuestion(firstQuestion.value, storeQuestionQaId.value, currentTopic.value)
  } else {
    nextQuestion.value = '缺少面试初始化数据，请返回面试准备页重新开始'
    ElMessage.warning(nextQuestion.value)
  }

  createWaveBars()
  scrollToBottom()

  interviewTimer = setInterval(() => {
    if (timeUsed.value < totalTime.value) {
      timeUsed.value += 1
    } else {
      clearInterval(interviewTimer)
      ElMessage.warning('面试时间已到！')
      setTimeout(() => {
        endDialogVisible.value = true
      }, 1000)
    }
  }, 1000)

  try {
    await startCamera()
  } catch (error) {
    console.error('摄像头初始化失败:', error)
  }

  await startBehaviorAnalysis()

})

const startBehaviorAnalysis = async () => {
  try {
    const stream = cameraStream.value
    if (!stream) return

    behaviorWs.value = new WebSocket(getWsUrl('/behavior-analysis'))

    // 平滑参数：EMA 的 alpha 值，越小越平滑，但响应真实变化越慢
    const EMA_ALPHA = 0.25
    let smoothExp = null
    let smoothEye = null
    let smoothPose = null

    behaviorWs.value.onopen = () => {
      console.log('行为分析连接已建立')
      if (!cameraVideo.value) return
      behaviorWs.value.send(
        JSON.stringify({
          type: 'init',
          width: cameraVideo.value.videoWidth,
          height: cameraVideo.value.videoHeight,
          historyId: historyId.value,
        })
      )
    }

    behaviorWs.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'metrics') {
          // 获取原始数值（容错处理）
          const rawExp = parseFloat(data.expression) || 0
          const rawEye = parseFloat(data.eyeContact) || 0
          const rawPose = parseFloat(data.pose) || 0

          // 指数移动平均平滑
          smoothExp = smoothExp === null ? rawExp : EMA_ALPHA * rawExp + (1 - EMA_ALPHA) * smoothExp
          smoothEye = smoothEye === null ? rawEye : EMA_ALPHA * rawEye + (1 - EMA_ALPHA) * smoothEye
          smoothPose = smoothPose === null ? rawPose : EMA_ALPHA * rawPose + (1 - EMA_ALPHA) * smoothPose

          // 更新界面指标
          expressionScore.value = Math.floor(smoothExp+10)
          eyeContactScore.value = Math.floor(smoothEye)
          poseScore.value = Math.floor(smoothPose-10)

          if (data.feedbacks && data.feedbacks.length) {
            activeFeedbacks.value = data.feedbacks.slice(-10)
          }
        }
      } catch (error) {
        console.error('处理行为分析响应失败:', error)
      }
    }

    behaviorWs.value.onerror = (error) => {
      console.error('行为分析连接错误:', error)
      ElMessage.error('行为分析服务连接失败')
    }

    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    const sendFrame = () => {
      if (!behaviorWs.value || behaviorWs.value.readyState !== WebSocket.OPEN) return
      if (!cameraVideo.value || !ctx) return
      if (!cameraVideo.value.videoWidth || !cameraVideo.value.videoHeight) return

      canvas.width = cameraVideo.value.videoWidth
      canvas.height = cameraVideo.value.videoHeight
      ctx.drawImage(cameraVideo.value, 0, 0, canvas.width, canvas.height)

      canvas.toBlob(
        (blob) => {
          if (!blob) return
          if (!behaviorWs.value || behaviorWs.value.readyState !== WebSocket.OPEN) return
          behaviorWs.value.send(blob)
        },
        'image/jpeg',
        0.8
      )
    }

    const fps = 5
    if (behaviorFrameTimer) {
      clearInterval(behaviorFrameTimer)
    }
    behaviorFrameTimer = setInterval(sendFrame, 1000 / fps)
  } catch (error) {
    console.error('启动行为分析失败:', error)
    ElMessage.error('无法启动行为分析')
  }
}

const addActiveFeedback = (feedback) => {
  if (activeFeedbacks.value.length >= 4) {
    activeFeedbacks.value.shift()
  }

  activeFeedbacks.value.push({
    message: feedback.message,
    level: feedback.level,
    timestamp: Date.now(),
  })

  setTimeout(() => {
    activeFeedbacks.value = activeFeedbacks.value.filter((f) => f.timestamp !== feedback.timestamp)
  }, 3000)
}

onBeforeUnmount(() => {
  void stopQuestionVideoRecording(true)

  if (behaviorFrameTimer) {
    clearInterval(behaviorFrameTimer)
    behaviorFrameTimer = null
  }
  if (behaviorWs.value) {
    behaviorWs.value.close()
    behaviorWs.value = null
  }

  stopCamera()
  clearInterval(interviewTimer)
  clearInterval(recordingTimer.value)
  clearInterval(waveAnimationInterval.value)

  // 清理加载定时器
  if (loadingTimer) {
    clearInterval(loadingTimer)
    loadingTimer = null
  }
  if (loadingFillTimer) {
    clearInterval(loadingFillTimer)
    loadingFillTimer = null
  }

  if (reportPollingTimer.value) {
    clearInterval(reportPollingTimer.value)
    reportPollingTimer.value = null
  }

  if (reportPollingTimer.value) {
    clearInterval(reportPollingTimer.value)
    reportPollingTimer.value = null
  }

  messages.value.forEach((msg) => {
    if (msg.type === 'audio' && msg.audioUrl) {
      URL.revokeObjectURL(msg.audioUrl)
    }
  })

  if (ttsWebSocket.value && ttsWebSocket.value.readyState === WebSocket.OPEN) {
    ttsWebSocket.value.close()
  }
  messages.value.forEach((msg) => {
    if (msg.audioUrl) {
      URL.revokeObjectURL(msg.audioUrl)
    }
  })

  if (imageCaptureTimer.value) {
    clearTimeout(imageCaptureTimer.value)
    imageCaptureTimer.value = null
  }


})

const togglePrompt = () => {
  showPrompt.value = !showPrompt.value
}

const openNoteDialog = () => {
  noteDialogVisible.value = true
}

const saveNote = () => {
  if (noteContent.value.length > 0) {
    ElMessage.success('笔记已保存')
  } else {
    ElMessage.warning('未输入任何内容')
  }
  noteDialogVisible.value = false
}
</script>

<style>
/* Unscoped global overrides for dialog themes (ensures deep elements get styled) */
body:not(.dark-mode) .theme-aware-dialog.el-dialog {
  background: #ffffff;
  border: 1px solid rgba(190, 210, 240, 0.8);
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.1);
}

body:not(.dark-mode) .theme-aware-dialog .el-dialog__title {
  color: #1f2937;
}

body:not(.dark-mode) .theme-aware-dialog .el-dialog__body {
  color: #4b5563;
}

body.dark-mode .theme-aware-dialog.el-dialog {
  background: linear-gradient(135deg, rgba(20, 30, 50, 0.98), rgba(15, 25, 45, 0.99));
  border: 1px solid rgba(59, 108, 225, 0.35);
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
}

body.dark-mode .theme-aware-dialog .el-dialog__title {
  color: #f9fafb;
}

body.dark-mode .theme-aware-dialog .el-dialog__body {
  color: #d1d5db;
}
</style>

<style scoped>
.streaming-cursor {
  animation: blink-cursor 0.7s step-end infinite;
  color: inherit;
  opacity: 0.8;
}

@keyframes blink-cursor {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.eval-fade-enter-active,
.eval-fade-leave-active {
  transition: opacity 0.3s;
}

.eval-fade-enter-from,
.eval-fade-leave-to {
  opacity: 0;
}

.camera-container {
  box-shadow: 0 0 25px rgba(91, 124, 250, 0.35);
  border: 2px solid rgba(109, 156, 255, 0.6);
  background: rgba(10, 20, 40, 0.7);
}

.camera-view {
  background: linear-gradient(45deg, #1e293b, #0f172a);
}

.camera-status {
  color: #9ab4ff;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
}

.camera-inactive .icon {
  color: #ff6d6d;
}

.pulse {
  background: #6d9cff;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(109, 156, 255, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(109, 156, 255, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(109, 156, 255, 0);
  }
}

@keyframes avatarMotionBlur {
  0% {
    filter: blur(0px);
    transform: scale(1);
  }
  50% {
    filter: blur(4px);
    transform: scale(1.05);
  }
  100% {
    filter: blur(0px);
    transform: scale(1);
  }
}

.light-mode .camera-container {
  border: 2px solid rgba(150, 180, 220, 0.6);
  background: rgba(220, 235, 250, 0.8);
}

.light-mode .camera-view {
  background: linear-gradient(45deg, #e6ecf5, #d5deeb);
}

.light-mode .camera-status {
  color: #4a6fba;
  background: rgba(255, 255, 255, 0.7);
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar,
:deep(textarea::-webkit-scrollbar) {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track,
:deep(textarea::-webkit-scrollbar-track) {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb,
:deep(textarea::-webkit-scrollbar-thumb) {
  background: rgba(109, 156, 255, 0.5);
  border-radius: 4px;
  transition: background 0.3s;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover,
:deep(textarea::-webkit-scrollbar-thumb:hover) {
  background: rgba(109, 156, 255, 0.8);
}

/* Base dialog shared styles */
:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

/* Dialog Theme Control Styles */
.dialog-content-wrapper {
  padding: 10px 0;
  text-align: center;
}

.light-mode-dialog {
  color: #1f2937;
}

.light-mode-dialog .dialog-title {
  color: #111827;
}

.light-mode-dialog .dialog-desc {
  color: #4b5563;
}

.light-mode-dialog .btn-cancel,
.light-mode-dialog .btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.light-mode-dialog .btn-cancel:hover,
.light-mode-dialog .btn-secondary:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.dark-mode-dialog {
  color: #f9fafb;
}

.dark-mode-dialog .dialog-title {
  color: #f9fafb;
}

.dark-mode-dialog .dialog-desc {
  color: #d1d5db;
}

.dark-mode-dialog .btn-cancel,
.dark-mode-dialog .btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: #f9fafb;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.dark-mode-dialog .btn-cancel:hover,
.dark-mode-dialog .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.warning-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulseWarning 1.5s infinite;
}

@keyframes pulseWarning {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(245, 158, 11, 0);
  }
}

.warning-icon .icon {
  font-size: 24px;
  color: #fff;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px;
}

.dialog-desc {
  font-size: 13px;
  margin: 0 0 20px;
}

.btn-custom {
  height: 38px;
  padding: 0 18px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 13px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border: none;
  color: #fff;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
}

.completion-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: bounceIn 0.6s ease-out;
}

@keyframes bounceIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.check-icon {
  font-size: 32px;
  color: #fff;
}

.light-mode .camera-inactive .icon {
  color: #ff3b3b;
}

.light-mode .pulse {
  background: #608bd6;
  animation: lightPulse 1.5s infinite;
}

@keyframes lightPulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(59, 108, 225, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(59, 108, 225, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(59, 108, 225, 0);
  }
}

.light-mode {
  --bg-primary: #f0f5fb;
  --bg-secondary: #e3ebf5;
  --bg-header: rgba(240, 245, 251, 0.95);
  --bg-avatar: rgba(255, 255, 255, 0.7);
  --bg-dialogue: rgba(245, 250, 255, 0.85);
  --bg-bubble-ai: rgba(240, 245, 251, 0.9);
  --bg-bubble-user: rgba(235, 242, 250, 0.9);
  --bg-prompt: rgba(230, 240, 250, 0.9);
  --bg-input: #ffffff;
  --text-primary: #2a3b56;
  --text-secondary: #5c6c8a;
  --text-accent: #4a6fba;
  --border-color: rgba(180, 200, 230, 0.5);
  --shadow-color: rgba(150, 180, 220, 0.2);
}

.interview-container {
  background: var(--bg-outer, linear-gradient(135deg, #0f172a 0%, #1e293b 100%));
  color: var(--text-primary, #f0f7ff);
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
}

.interview-container.light-mode {
  --bg-outer: linear-gradient(135deg, #d9e4f3 0%, #e8f0fb 100%);
}

.interview-header {
  background: var(--bg-header, rgba(8, 16, 30, 0.85));
}

.logo {
  background: linear-gradient(to right, #6d9cff, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 8px rgba(91, 124, 250, 0.3);
}

.progress-bar {
  background: rgba(255, 255, 255, 0.07);
}

/* Interview uncompleted progress bar to white */
.progress-bar :deep(.el-progress-bar__outer) {
  background-color: #ffffff !important;
}

.progress-bar :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, #3b6ce1, #6d9cff) !important;
  border-radius: 4px;
}

.time-remaining {
  color: #d1e0ff;
}

.time-used {
  color: #9ab4ff;
}

.avatar-section {
  background: rgba(10, 20, 40, 0.7);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(59, 108, 225, 0.2);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.dialogue-section {
  background: rgba(10, 20, 40, 0.7);
  border: 1px solid rgba(59, 108, 225, 0.2);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.dialogue-wrapper {
  background: linear-gradient(135deg, rgba(10, 18, 34, 0.8), rgba(15, 25, 48, 0.9));
}

.bubble {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
  color: #f0f7ff;
}

.bubble:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}

.ai-message .bubble {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(59, 108, 225, 0.25);
}

.user-message .bubble {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(30, 41, 59, 0.9));
  border: 1px solid rgba(91, 124, 250, 0.25);
  width: fit-content;
  min-width: 0;
  max-width: min(90%, 640px);
}

.content {
  color: #f0f7ff;
}

/* Scrollable Text Area Tweaks */
.text-input {
  flex: 1;
}

.text-input :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(109, 156, 255, 0.28);
  border-radius: 12px;
  color: #f0f7ff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
  transition: all 0.25s ease;
  padding: 8px 12px;
  line-height: 1.5;
}

.text-input :deep(.el-textarea__inner:focus) {
  border-color: rgba(109, 156, 255, 0.65);
  box-shadow: 0 0 0 1px rgba(109, 156, 255, 0.35),
  0 4px 14px rgba(59, 108, 225, 0.2);
}

.text-send-button {
  height: 40px;
  min-width: 76px;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 12px;
  justify-content: center;
  gap: 0;
}

.light-mode .text-input :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(180, 200, 230, 0.45);
  color: #2a3b56;
}

.light-mode .text-input :deep(.el-textarea__inner:focus) {
  border-color: rgba(96, 139, 214, 0.8);
  box-shadow: 0 0 0 1px rgba(96, 139, 214, 0.28),
  0 4px 14px rgba(96, 139, 214, 0.2);
}

.prompt {
  background: linear-gradient(90deg, rgba(35, 65, 130, 0.35), rgba(59, 108, 225, 0.45));
  border-left: 4px solid #6d9cff;
  color: #f0f7ff;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
}

.prompt .icon {
  color: #6d9cff;
}

.record-button {
  background: linear-gradient(135deg, #3b6ce1, #6d9cff);
  box-shadow: 0 0 15px rgba(109, 156, 255, 0.4);
  border-color: rgba(109, 156, 255, 0.6);
  transition: none !important;
  transform: none !important;
}

.record-button:hover {
  box-shadow: 0 0 20px rgba(109, 156, 255, 0.4) !important;
}

.record-button.recording {
  background: linear-gradient(135deg, #e05c5c, #d32f2f);
  box-shadow: 0 0 15px rgba(225, 92, 92, 0.6);
  border-color: rgba(209, 47, 47, 0.7);
}

.recording-info {
  color: #e05c5c;
  background: rgba(255, 109, 109, 0.15);
  border-color: rgba(255, 109, 109, 0.3);
}

.recording-info .pulse {
  background: #ff6d6d;
  box-shadow: 0 0 8px rgba(255, 109, 109, 0.8);
}

.action-button {
  background: rgba(30, 50, 90, 0.6);
  border-color: rgba(109, 156, 255, 0.4);
  color: #e6f0ff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-button:hover {
  background: rgba(40, 70, 120, 0.7);
}

.end-button {
  background: linear-gradient(135deg, #6d9cff, #3b6ce1);
  border-color: rgba(109, 156, 255, 0.6);
  box-shadow: 0 0 15px rgba(109, 156, 255, 0.4);
}

.audio-message {
  background: rgba(30, 50, 90, 0.5);
  border-color: rgba(59, 108, 225, 0.25);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.wave-bar {
  background: linear-gradient(to top, #6d9cff, #3b6ce1);
  height: var(--bar-height);
}

.wave-bar.playing {
  animation: waveBar 1.5s infinite ease-in-out;
}

@keyframes waveBar {
  0%,
  100% {
    height: calc(var(--bar-height) * 1);
    opacity: 0.7;
  }
  50% {
    height: calc(var(--bar-height) * 2.5);
    opacity: 1;
  }
}

.wave-bar:nth-child(1) {
  --bar-height: 9px;
  animation-delay: 0s;
}

.wave-bar:nth-child(2) {
  --bar-height: 13px;
  animation-delay: 0.2s;
}

.wave-bar:nth-child(3) {
  --bar-height: 7px;
  animation-delay: 0.4s;
}

.wave-bar:nth-child(4) {
  --bar-height: 11px;
  animation-delay: 0.6s;
}

.wave-bar:nth-child(5) {
  --bar-height: 15px;
  animation-delay: 0.8s;
}

.wave-bar:nth-child(6) {
  --bar-height: 8px;
  animation-delay: 1s;
}

.wave-bar:nth-child(7) {
  --bar-height: 12px;
  animation-delay: 1.2s;
}

.wave-bar:nth-child(8) {
  --bar-height: 6px;
  animation-delay: 1.4s;
}

.wave-bar:nth-child(9) {
  --bar-height: 10px;
  animation-delay: 0.1s;
}

.wave-bar:nth-child(10) {
  --bar-height: 14px;
  animation-delay: 0.3s;
}

.wave-bar:nth-child(11) {
  --bar-height: 8px;
  animation-delay: 0.5s;
}

.wave-bar:nth-child(12) {
  --bar-height: 12px;
  animation-delay: 0.7s;
}

.wave-bar:nth-child(13) {
  --bar-height: 9px;
  animation-delay: 0.9s;
}

.wave-bar:nth-child(14) {
  --bar-height: 13px;
  animation-delay: 1.1s;
}

.wave-bar:nth-child(15) {
  --bar-height: 7px;
  animation-delay: 1.3s;
}

.wave-bar:nth-child(16) {
  --bar-height: 11px;
  animation-delay: 1.5s;
}

.audio-duration {
  color: #9ab4ff;
}

.theme-toggle-button {
  background: var(--btn-bg);
  color: var(--btn-icon);
  border-color: var(--btn-border);
  --btn-bg: rgba(255, 255, 255, 0.1);
  --btn-border: rgba(255, 255, 255, 0.3);
  --btn-icon: white;
}

.light-mode .theme-toggle-button {
  background: rgba(210, 225, 245, 0.5);
  border-color: rgba(180, 200, 230, 0.4);
  color: #4a6fba;
}

.theme-toggle-button:hover {
  background: var(--btn-bg-hover, rgba(255, 255, 255, 0.2));
}

.light-mode .theme-toggle-button:hover {
  --btn-bg-hover: rgba(59, 108, 225, 0.15);
}

.light-mode .theme-toggle-button .icon {
  color: #3b6ce1;
}

.assistant-button {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.assistant-button:hover {
  background: rgba(59, 108, 225, 0.3);
  transform: translateY(-2px);
}

.assistant-button:hover .tooltip {
  opacity: 1;
}

.light-mode .assistant-button {
  background: rgba(59, 108, 225, 0.1);
  border-color: rgba(59, 108, 225, 0.3);
  color: #3b6ce1;
}

.behavior-analysis {
  background: rgba(10, 20, 40, 0.6);
  border: 1px solid rgba(91, 124, 250, 0.3);
}

.metric-label {
  color: #b8d0ff;
}

.metric-item :deep(.el-progress-bar) {
  flex: 1;
}

.feedback-tag {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.light-mode .behavior-analysis {
  background: rgba(220, 235, 250, 0.7);
  border-color: rgba(180, 200, 230, 0.4);
}

.light-mode .metric-label {
  color: #4a6fba;
}

:deep(.el-button) {
  background: rgba(30, 50, 90, 0.6);
  border: 1px solid rgba(109, 156, 255, 0.4);
  color: #d1e0ff;
  font-weight: 500;
  transition: all 0.3s;
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 8px;
}

:deep(.el-button:hover) {
  background: rgba(40, 70, 120, 0.7);
  border-color: #6d9cff;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #6d9cff, #3b6ce1);
  border: 1px solid rgba(109, 156, 255, 0.7);
  box-shadow: 0 2px 8px rgba(59, 108, 255, 0.4);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #3b6ce1, #6d9cff);
  box-shadow: 0 4px 12px rgba(59, 108, 255, 0.6);
}

:deep(.el-message) {
  background: linear-gradient(135deg, rgba(20, 30, 50, 0.95), rgba(15, 25, 45, 0.98));
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(59, 108, 225, 0.35);
}

:deep(.el-message__content) {
  color: #e6f0ff !important;
  font-size: 14px;
  font-weight: 500;
}

.light-mode .interview-container {
  background: rgba(245, 250, 255, 0.95);
  border-color: rgba(190, 210, 240, 0.4);
}

.light-mode .interview-header {
  background: var(--bg-header);
  border-bottom-color: rgba(180, 200, 230, 0.3);
}

.light-mode .logo {
  color: #3a60b0;
}

.light-mode .time-remaining,
.light-mode .time-used {
  color: #4a6fba;
}

.light-mode .avatar-section,
.light-mode .dialogue-section {
  background: var(--bg-dialogue);
  border-color: rgba(190, 210, 240, 0.5);
  box-shadow: 0 8px 20px rgba(150, 180, 220, 0.15);
}

.light-mode .dialogue-wrapper {
  background: linear-gradient(135deg, rgba(240, 248, 255, 0.85), rgba(230, 240, 250, 0.9));
}

.light-mode .ai-message .bubble {
  background: var(--bg-bubble-ai);
  border-color: rgba(180, 200, 230, 0.35);
  color: var(--text-primary);
}

.light-mode .user-message .bubble {
  background: var(--bg-bubble-user);
  border-color: rgba(190, 210, 240, 0.4);
  color: var(--text-primary);
}

.light-mode .prompt {
  background: linear-gradient(90deg, rgba(210, 230, 250, 0.35), rgba(200, 225, 245, 0.45));
  border-left-color: #6d9cff;
  color: var(--text-primary);
}

.light-mode .record-button {
  background: linear-gradient(135deg, #7ea8e6, #608bd6);
}

.light-mode .record-button.recording {
  background: linear-gradient(135deg, #e67e7e, #d66060);
}

.light-mode .action-button {
  background: rgba(210, 225, 245, 0.7);
  color: var(--text-primary);
}

.light-mode .end-button {
  background: linear-gradient(135deg, #7ea8e6, #608bd6);
}

.light-mode .audio-message {
  background: rgba(210, 225, 245, 0.55);
  border-color: rgba(180, 200, 230, 0.35);
}

.light-mode .wave-bar {
  background: linear-gradient(to top, #3b6ce1, #6d9cff);
}

.light-mode .name-tag,
.light-mode .ai-status,
.light-mode .user-status,
.light-mode .content,
.light-mode .prompt span {
  color: var(--text-primary, #333) !important;
}

.light-mode .note-character-count {
  color: #666;
}

@media screen and (max-width: 767.98px) {
  .interview-container {
    height: auto;
    min-height: 100vh;
  }

  .interview-header {
    flex-direction: column;
  }

  .timer {
    width: 100%;
    margin-top: 5px;
    align-items: center;
  }

  .content-wrapper {
    flex-direction: column;
  }

  .avatar-section {
    width: 100%;
    min-width: unset;
    overflow-y: visible;
  }

  .dialogue-section {
    width: 100%;
    max-width: 100%;
  }

  .record-container {
    flex-direction: column;
    gap: 8px;
  }

  .recording-info {
    justify-content: center;
  }
}

@media screen and (min-width: 768px) and (max-width: 991.98px) {
  .avatar-section {
    width: 30%;
    min-width: 180px;
  }

  .dialogue-section {
    width: 70%;
  }
}

/* ==================== processing 卡片样式 ==================== */
.processing-message .bubble {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(59, 108, 225, 0.25);
  padding: 14px 16px 16px;
}

.light-mode .processing-message .bubble {
  background: var(--bg-bubble-ai);
  border-color: rgba(180, 200, 230, 0.35);
}

.processing-card {
  width: 100%;
  min-width: 260px;
  max-width: 400px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.spinner-icon {
  font-size: 18px;
  color: #6d9cff;
}

.spinner-icon.spinning {
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: #f0f7ff;
}

.light-mode .header-title {
  color: #1f2937;
}

.step-count {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
}

.light-mode .step-count {
  color: rgba(0, 0, 0, 0.4);
}

.card-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 14px 0;
  line-height: 1.5;
}

.light-mode .card-desc {
  color: rgba(0, 0, 0, 0.55);
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.4s ease;
}

.light-mode .step-item {
  background: rgba(0, 0, 0, 0.03);
  border-color: rgba(0, 0, 0, 0.06);
}

.step-item.active {
  border-color: rgba(109, 156, 255, 0.4);
  background: rgba(109, 156, 255, 0.08);
}

.light-mode .step-item.active {
  background: rgba(109, 156, 255, 0.1);
  border-color: rgba(109, 156, 255, 0.3);
}

.step-item.completed {
  border-color: rgba(103, 194, 58, 0.3);
  background: rgba(103, 194, 58, 0.08);
}

.light-mode .step-item.completed {
  background: rgba(103, 194, 58, 0.08);
  border-color: rgba(103, 194, 58, 0.25);
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
  transition: all 0.4s ease;
}

.light-mode .step-number {
  background: rgba(0, 0, 0, 0.06);
  color: rgba(0, 0, 0, 0.3);
  border-color: rgba(0, 0, 0, 0.08);
}

.step-item.active .step-number {
  background: #6d9cff;
  color: #fff;
  border-color: #6d9cff;
  box-shadow: 0 0 12px rgba(109, 156, 255, 0.3);
}

.light-mode .step-item.active .step-number {
  background: #608bd6;
  border-color: #608bd6;
}

.step-item.completed .step-number {
  background: #67c23a;
  color: #fff;
  border-color: #67c23a;
  box-shadow: 0 0 12px rgba(103, 194, 58, 0.25);
}

.step-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.light-mode .step-title {
  color: rgba(0, 0, 0, 0.7);
}

.step-item.active .step-title {
  color: #f0f7ff;
}

.light-mode .step-item.active .step-title {
  color: #1f2937;
}

.step-item.completed .step-title {
  color: rgba(255, 255, 255, 0.8);
}

.light-mode .step-item.completed .step-title {
  color: rgba(0, 0, 0, 0.75);
}

.step-status {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.3);
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
}

.light-mode .step-status {
  color: rgba(0, 0, 0, 0.3);
  background: rgba(0, 0, 0, 0.03);
}

.step-item.active .step-status {
  color: #6d9cff;
  background: rgba(109, 156, 255, 0.12);
}

.light-mode .step-item.active .step-status {
  color: #608bd6;
  background: rgba(96, 139, 214, 0.12);
}

.step-item.completed .step-status {
  color: #67c23a;
  background: rgba(103, 194, 58, 0.12);
}

.progress-area {
  margin-top: 2px;
}

.progress-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.progress-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.light-mode .progress-label {
  color: rgba(0, 0, 0, 0.4);
}

.progress-value {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.light-mode .progress-value {
  color: rgba(0, 0, 0, 0.6);
}

.progress-track {
  width: 100%;
  height: 5px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  overflow: hidden;
}

.light-mode .progress-track {
  background: rgba(0, 0, 0, 0.06);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6d9cff, #3b6ce1);
  border-radius: 4px;
  transition: width 0.2s ease;
}

.light-mode .progress-fill {
  background: linear-gradient(90deg, #608bd6, #3b6ce1);
}
</style>
