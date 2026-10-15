<template>
  <div class="vhc-root dark:bg-gray-900 dark:text-white" @click="handlePageClick" @keydown="handleKeyPress"
    tabindex="0">
    <div class="vhc-header">
      <div class="vhc-avatar-video">
        <div ref="videoContainer" class="vhc-avatar-video-el"></div>
        <img v-if="!rtcPlayer" class="vhc-avatar" src="/images/brand/brand-01.svg" alt="虚拟人形象" />
        <!-- 播放提示覆盖层 -->
        <div v-if="showPlayPrompt" class="vhc-play-prompt" @click="resumePlayer">
          <div class="vhc-play-icon">▶</div>
          <span>点击恢复播放</span>
          <span class="vhc-play-hint">或按空格键</span>
        </div>
      </div>
      <span class="vhc-title">虚拟人实时语音对话</span>
    </div>
    <div class="vhc-chat-window" ref="chatWindow">
      <div v-for="msg in messages" :key="msg.id" :class="['vhc-bubble', msg.role]">
        <div v-if="msg.role === 'bot'" class="vhc-avatar-bot">
          <img src="/images/brand/brand-01.svg" alt="虚拟人" />
        </div>
        <div class="vhc-bubble-content">
          <span v-if="msg.type === 'text'">{{ msg.content }}</span>
          <span v-if="msg.type === 'audio'">
            <button @click="playAudio(msg.audioUrl)" class="vhc-audio-btn">
              <span :class="['vhc-audio-wave', { playing: playingId === msg.id }]">
                <span v-for="i in 5" :key="i" class="vhc-audio-bar"></span>
              </span>
              <span class="vhc-audio-label">播放语音</span>
            </button>
          </span>
        </div>
      </div>
    </div>
    <div class="vhc-input-bar">
      <input v-model="inputText" @keyup.enter="sendText" placeholder="说点什么..." class="vhc-input" />
      <button @mousedown="startRecording" @mouseup="stopRecording" @mouseleave="stopRecording"
        :class="['vhc-mic-btn', { recording }]">
        <span class="vhc-mic-icon">
          <svg v-if="!recording" width="28" height="28" fill="none" viewBox="0 0 24 24">
            <path
              d="M12 15a3 3 0 0 0 3-3V7a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3Zm5-3a1 1 0 1 1 2 0 5 5 0 0 1-10 0 1 1 0 1 1 2 0 3 3 0 0 0 6 0Z"
              fill="currentColor" />
          </svg>
          <span v-if="recording" class="vhc-mic-wave">
            <span v-for="i in 5" :key="i" class="vhc-mic-bar"></span>
          </span>
        </span>
      </button>
      <button @click="sendText" class="vhc-send-btn">发送</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import CryptoJS from 'crypto-js'

interface Message {
  id: string
  role: 'user' | 'bot'
  type: 'text' | 'audio'
  content?: string
  audioUrl?: string
}

const messages = reactive<Message[]>([])
const inputText = ref('')
const recording = ref(false)
const playingId = ref<string | null>(null)
const chatWindow = ref<HTMLElement | null>(null)
const videoContainer = ref<HTMLElement | null>(null)
let ws: WebSocket | null = null
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
const videoUrl = ref<string | null>(null)
let pingTimer: NodeJS.Timeout | null = null
let rtcPlayer: any = null
const isPlayerBlocked = ref(false) // 新增：播放器是否被阻止
const showPlayPrompt = ref(false) // 新增：是否显示播放提示

// 讯飞虚拟人接口参数
const APPID = import.meta.env.VITE_AVATAR_APP_ID || ''
const APIKey = import.meta.env.VITE_AVATAR_API_KEY || ''
const APISecret = import.meta.env.VITE_AVATAR_API_SECRET || ''
const SERVICE_ID = import.meta.env.VITE_AVATAR_SERVICE_ID || ''
const AVATAR_ID = import.meta.env.VITE_AVATAR_ID || ''
// 生成握手鉴权参数（严格按讯飞WebSocket HMAC-SHA256）
function getHandShakeUrl() {
  if (!APPID || !APIKey || !APISecret || !SERVICE_ID || !AVATAR_ID) {
    throw new Error('虚拟人服务未配置，请检查 VITE_AVATAR_* 环境变量')
  }
  const apiKey = APIKey
  const apiSecret = APISecret
  const appId = APPID
  const wsUrl = 'wss://avatar.cn-huadong-1.xf-yun.com/v1/interact'

  // 1. 构造时间
  const date = new Date().toUTCString()
  const host = 'avatar.cn-huadong-1.xf-yun.com'
  const requestLine = 'GET /v1/interact HTTP/1.1'
  // 2. 构造签名字符串
  const signatureOrigin = `host: ${host}\ndate: ${date}\n${requestLine}`
  // 3. HMAC-SHA256
  const hash = CryptoJS.HmacSHA256(signatureOrigin, apiSecret)
  const signature = CryptoJS.enc.Base64.stringify(hash)
  // 4. 构造authorization
  const authorizationOrigin = `hmac username=\"${apiKey}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"${signature}\"`
  const authorization = btoa(authorizationOrigin)
  // 5. 拼接URL
  const url = `${wsUrl}?authorization=${encodeURIComponent(authorization)}&host=${encodeURIComponent(host)}&date=${encodeURIComponent(date)}`
  return url
}

// 生成唯一request_id
declare function cryptoRandomUUID(): string // 兼容性声明
function getRequestId() {
  if (window.crypto && (window.crypto as any).randomUUID) {
    return (window.crypto as any).randomUUID()
  }
  return Date.now() + '-' + Math.random().toString(36).slice(2)
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatWindow.value) {
      chatWindow.value.scrollTop = chatWindow.value.scrollHeight
    }
  })
}

// 初始化RTCPlayer
const initRTCPlayer = async (streamConfig: any) => {
  try {
    // 从本地文件导入RTCPlayer
    const { RTCPlayer } = await import('../rtcplayer.esm.js')

    if (rtcPlayer) {
      rtcPlayer.destroy()
    }

    rtcPlayer = new RTCPlayer()

    // 注册事件
    rtcPlayer.on("play", () => {
      console.log("RTCPlayer play事件")
      isPlayerBlocked.value = false
      showPlayPrompt.value = false
    })
      .on("playing", () => {
        console.log("RTCPlayer playing事件")
        isPlayerBlocked.value = false
        showPlayPrompt.value = false
      })
      .on("waiting", () => {
        console.log("RTCPlayer waiting事件")
      })
      .on("pause", () => {
        console.log("RTCPlayer pause事件")
      })
      .on("ended", () => {
        console.log("RTCPlayer ended事件")
      })
      .on("error", (e: any) => {
        console.log("RTCPlayer error:", e)
        // 如果是自动播放被阻止的错误，显示提示
        if (e && (e.message?.includes('NotAllowedError') || e.name === 'NotAllowedError')) {
          console.log("检测到自动播放被阻止")
          isPlayerBlocked.value = true
          showPlayPrompt.value = true
        }
      })
      .on("not-allowed", () => {
        console.log("触发浏览器限制播放策略，播放前必须要先与浏览器产生交互")
        isPlayerBlocked.value = true
        showPlayPrompt.value = true
        // 不要在这里自动调用resume，等待用户交互
      })

    // 必须注册 onCustomSignParam 回调，兼容部分SDK强制调用
    rtcPlayer.onCustomSignParam = (params: any) => {
      return {
        sid: streamConfig.sid,
        server: streamConfig.server,
        auth: streamConfig.auth,
        appid: streamConfig.appid,
        timeStr: streamConfig.timeStr,
        userId: streamConfig.userId,
        roomId: streamConfig.roomId
      }
    }

    // 解析streamConfig，确保所有字段正确
    const sid = streamConfig.sid || ''
    // server: xrtcs://xrtc-cn-east-2.xf-yun.com/xxx  => https://xrtc-cn-east-2.xf-yun.com
    let server = streamConfig.server || ''
    if (server.startsWith('xrtcs://')) server = server.replace('xrtcs://', 'https://')
    if (server.startsWith('xrtc://')) server = server.replace('xrtc://', 'http://')
    if (server.endsWith('/')) server = server.slice(0, -1)
    // roomId: 路径最后一段
    const roomId = streamConfig.roomId || sid
    // auth: user_sign
    const auth = streamConfig.auth || ''
    // appid
    const appid = streamConfig.appid || ''
    // timeStr
    const timeStr = streamConfig.timeStr || ''
    // userId: 若无则生成唯一字符串
    const userId = streamConfig.userId || (Date.now() + '-' + Math.random().toString(36).slice(2))

    rtcPlayer.playerType = 12
    rtcPlayer.stream = {
      sid,
      server,
      auth,
      appid,
      timeStr,
      userId,
      roomId
    }

    rtcPlayer.videoSize = {
      width: 720,
      height: 1280,
    }

    // 设置视频显示模式，让虚拟人显示上半身
    rtcPlayer.videoMode = 'stretch' // 拉伸模式，填充整个容器

    // 尝试设置视频裁剪区域，显示上半身
    if (rtcPlayer.setCropArea) {
      rtcPlayer.setCropArea({
        x: 0,
        y: 0,
        width: 720,
        height: 960 // 只显示上半部分，约75%的高度
      })
    }

    if (videoContainer.value) {
      // 调整容器尺寸为更大的显示区域，使用更宽的宽高比显示上半身
      videoContainer.value.style.width = '450px'
      videoContainer.value.style.height = '600px'
      videoContainer.value.style.borderRadius = '16px'
      videoContainer.value.style.overflow = 'hidden'
      videoContainer.value.style.border = '2px solid #e0e7ef'
      videoContainer.value.style.background = '#fff'
      videoContainer.value.style.objectFit = 'cover' // 确保视频填充整个容器

      rtcPlayer.container = videoContainer.value

      // 延迟播放，给用户交互的机会
      setTimeout(() => {
        try {
          rtcPlayer.play()
          console.log('RTCPlayer初始化完成，开始播放')
        } catch (error) {
          console.log('播放被阻止，等待用户交互:', error)
          isPlayerBlocked.value = true
          showPlayPrompt.value = true
        }
      }, 1000) // 延迟1秒播放
    }
  } catch (error) {
    console.error('RTCPlayer初始化失败:', error)
    // 如果RTCPlayer不可用，回退到iframe方式
    const streamUrl = `xrtcs://${streamConfig.server.replace('https://', '')}/${streamConfig.sid}?auth=${streamConfig.auth.replace('Bearer ', '')}&appid=${streamConfig.appid}&userId=${streamConfig.userId}&roomId=${streamConfig.roomId}&timeStr=${streamConfig.timeStr}`
    const playerUrl = `https://ossrs.net/players/rtc_player.html?url=${encodeURIComponent(streamUrl)}&playerType=12&schema=https&api=https://ossrs.net&eip=ossrs.net&autoplay=true&muted=true`
    videoUrl.value = playerUrl
    console.log('回退到iframe播放器:', playerUrl)
  }
}

// 连接WebSocket
const connectWS = () => {
  console.log('开始连接WebSocket...')
  ws = new WebSocket(getHandShakeUrl())
  ws.binaryType = 'arraybuffer'
  ws.onopen = () => {
    console.log('WebSocket连接成功')
    // 发送握手包（start帧，header.ctrl: 'start'）
    const handshake = {
      header: {
        app_id: APPID,
        request_id: getRequestId(),
        scene_id: SERVICE_ID,
        ctrl: 'start',
      },
      parameter: {
        avatar: {
          stream: {
            protocol: 'xrtc', // 讯飞自研协议，支持透明背景
            fps: 25,
            bitrate: 5000,
            alpha: 1, // 0关闭透明背景，1开启
          },
          avatar_id: AVATAR_ID,
          width: 720,
          height: 1280,
          scale: 1.0, // 虚拟人缩放大小，0.8表示80%大小，让虚拟人显示更多身体部分
          move_v: 0, // 向上移动200像素，让虚拟人显示更多上半身
          audio_format: 1, // 1=16k, 2=24k
        },
        tts: {
          vcn: 'x4_lingxiaoying_assist', // 必填，发音人参数，需与你账号下授权的发音人一致
          speed: 50,
          pitch: 50,
          volume: 50,
        },
        subtitle: {
          subtitle: 0, // 0关闭，1开启
          font_color: "#FF0000",
          font_size: 10,
          position_x: 0,
          position_y: 0,
          font_name: "mainTitle",
          width: 100,
          height: 100
        }
      },
      payload: {},
    }
    console.log('发送握手包:', handshake)
    ws!.send(JSON.stringify(handshake))

    // 启动ping心跳，每5秒发送一次
    pingTimer = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        const pingPayload = {
          header: {
            app_id: APPID,
            request_id: getRequestId(),
            ctrl: 'ping'
          }
        }
        ws.send(JSON.stringify(pingPayload))
      }
    }, 5000)
  }
  ws.onmessage = async (e) => {
    console.log('收到WebSocket消息:', e.data)

    // 1. 判断是否为二进制音频流
    if (e.data instanceof ArrayBuffer) {
      console.log('收到音频流数据', e.data)
      // 音频流
      const audioBlob = new Blob([e.data], { type: 'audio/wav' })
      const url = URL.createObjectURL(audioBlob)
      messages.push({ id: Date.now() + Math.random() + '', role: 'bot', type: 'audio', audioUrl: url })
      scrollToBottom()
      return
    }
    // 2. 尝试解析为JSON
    let data = null
    try {
      data = JSON.parse(e.data)
      console.log('解析的JSON数据:', data)
    } catch (err) {
      console.log('消息不是JSON格式:', e.data)
      messages.push({
        id: Date.now() + Math.random() + '',
        role: 'bot',
        type: 'text',
        content: '[调试] 非JSON消息: ' + String(e.data)
      })
      return
    }
    // 2.1 新增：处理大模型NLP回复
    if (data?.payload?.nlp) {
      // 如果是自动TTS驱动的回声，不再自动TTS驱动
      if (data?.payload?.from === 'auto-tts') {
        return
      }
      const nlp = data.payload.nlp
      // 优先ttsAnswer.text，其次answer.text
      const botText = nlp.ttsAnswer?.text || nlp.answer?.text
      if (botText) {
        messages.push({
          id: Date.now() + Math.random() + '',
          role: 'bot',
          type: 'text',
          content: botText
        })
        scrollToBottom()
        // 只对status===0的nlp回复自动TTS驱动，且只自动一次
        if (nlp.ttsAnswer?.text && nlp.ttsAnswer.text.trim() && nlp.status === 0) {
          const ttsText = nlp.ttsAnswer.text.trim()
          const ttsPayload = {
            header: {
              app_id: APPID,
              request_id: getRequestId(),
              service_id: SERVICE_ID,
              ctrl: 'text_interact',
            },
            parameter: {
              tts: {
                vcn: 'x4_lingxiaoying_assist',
                speed: 50,
                pitch: 50,
                audio: {
                  sample_rate: 16000
                }
              },
              air: {
                air: 1,
                add_nonsemantic: 1
              },
              nlp: {
                nlp: false // 只做TTS驱动，不再走大模型，避免死循环
              }
            },
            payload: {
              text: {
                content: ttsText
              },
              from: 'auto-tts' // 标记来源，防止回声死循环
            },
          }
          console.log('自动TTS驱动虚拟人说话:', ttsPayload)
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(ttsPayload))
          } else {
            console.warn('WebSocket未连接，无法自动TTS驱动')
          }
        }
        return
      }
    }
    // 3. 过滤心跳包
    if (data?.payload?.avatar?.event_type === 'pong') {
      console.log('收到心跳pong包，忽略')
      return
    }
    // 4. 检查 driver_status
    if (data?.payload?.avatar?.event_type === 'driver_status') {
      console.log('收到driver_status:', data?.payload?.avatar)
      messages.push({
        id: Date.now() + Math.random() + '',
        role: 'bot',
        type: 'text',
        content: '[调试] driver_status: ' + JSON.stringify(data?.payload?.avatar)
      })
      return
    }
    if (typeof data?.header?.code === 'number' && data.header.code !== 0) {
      console.error('[VirtualHuman] 服务端错误:', data.header.code, data.header.message || '', data)
    }

    // 5. 检查握手响应
    if (data?.header?.code === 0 && data?.payload?.avatar?.event_type === 'stream_info') {
      const info = data.payload.avatar;
      const ext = info.stream_extend || {};
      const streamUrl = info.stream_url || '';
      const m = streamUrl.match(/^xrtcs?:\/\/([^\/]+)\/(.+)$/);
      if (!m) return;
      const host = m[1], sid = m[2];
      const streamConfig = {
        sid,
        server: `https://${host}`,
        auth: ext.user_sign ? `Bearer ${ext.user_sign}` : '',
        appid: ext.appid || APPID,
        roomId: sid,
        userId: ext.userId || getRequestId(),
        timeStr: ext.timeStr || ''
      };
      console.log('解析到完整 streamConfig:', streamConfig);
      initRTCPlayer(streamConfig);
      return
    }
    // 6. 检查NLP错误响应
    if (data?.payload?.nlp?.error_code) {
      const errorMsg = data.payload.nlp.error_message || ''
      console.log('NLP错误:', errorMsg)
      let helpText = ''
      if (errorMsg.includes('tdp.url')) {
        helpText = '请在讯飞交互平台配置大模型对话URL。'
      } else if (errorMsg.includes('tdp.botId')) {
        helpText = '请在讯飞交互平台配置大模型对话Bot ID。'
      } else {
        helpText = '请在讯飞交互平台检查大模型对话配置。'
      }
      messages.push({
        id: Date.now() + Math.random() + '',
        role: 'bot',
        type: 'text',
        content: `配置错误: ${errorMsg}\n\n${helpText}\n\n配置步骤：\n1. 登录讯飞交互平台\n2. 找到接口服务ID: ${SERVICE_ID}\n3. 在\"大模型对话\"中启用星火大模型\n4. 配置对话场景和回复规则`
      })
      return
    }
    // 7. 检查文本响应
    if (data?.payload?.text) {
      console.log('收到文本响应:', data.payload.text)
      messages.push({ id: Date.now() + Math.random() + '', role: 'bot', type: 'text', content: data.payload.text })
      scrollToBottom()
      return
    }
    // 8. 检查音频URL
    if (data?.payload?.audio_url) {
      console.log('收到音频URL:', data.payload.audio_url)
      messages.push({ id: Date.now() + Math.random() + '', role: 'bot', type: 'audio', audioUrl: data.payload.audio_url })
      scrollToBottom()
      return
    }
    // 9. 检查结果响应
    if (data?.payload?.result) {
      console.log('收到结果响应:', data.payload.result)
      messages.push({ id: Date.now() + Math.random() + '', role: 'bot', type: 'text', content: data.payload.result })
      scrollToBottom()
      return
    }
    // 10. 兼容其他可能的响应格式
    if (data?.payload?.stream_url) {
      console.log('收到stream_url:', data.payload.stream_url)
      videoUrl.value = data.payload.stream_url
    }
    // 11. 兜底显示所有payload
    console.log('未识别的payload:', data)
    messages.push({
      id: Date.now() + Math.random() + '',
      role: 'bot',
      type: 'text',
      content: '[调试] 未识别payload: ' + JSON.stringify(data)
    })
    scrollToBottom()
  }
  ws.onclose = () => {
    console.log('WebSocket连接关闭')
    if (pingTimer) {
      clearInterval(pingTimer)
      pingTimer = null
    }
  }
  ws.onerror = (error) => {
    console.log('WebSocket连接错误:', error)
    if (pingTimer) {
      clearInterval(pingTimer)
      pingTimer = null
    }
  }
}

onMounted(() => {
  // 添加全局错误处理，捕获RTCPlayer的Promise错误
  const originalErrorHandler = window.onerror
  window.onerror = (message, source, lineno, colno, error) => {
    if (message && typeof message === 'string' && message.includes('NotAllowedError')) {
      console.log('捕获到自动播放被阻止错误，显示播放提示')
      isPlayerBlocked.value = true
      showPlayPrompt.value = true
      return true // 阻止错误继续传播
    }
    // 调用原始错误处理器
    if (originalErrorHandler) {
      return originalErrorHandler(message, source, lineno, colno, error)
    }
    return false
  }

  // 添加Promise错误处理
  const originalUnhandledRejectionHandler = window.onunhandledrejection
  window.onunhandledrejection = function (event: PromiseRejectionEvent) {
    if (event.reason && event.reason.message && event.reason.message.includes('NotAllowedError')) {
      console.log('捕获到Promise自动播放被阻止错误，显示播放提示')
      isPlayerBlocked.value = true
      showPlayPrompt.value = true
      event.preventDefault() // 阻止错误继续传播
      return
    }
    // 调用原始处理器
    if (originalUnhandledRejectionHandler) {
      originalUnhandledRejectionHandler.call(window, event)
    }
  }

  connectWS()
})

onUnmounted(() => {
  // 清理全局错误处理器
  window.onerror = null
  window.onunhandledrejection = null

  if (pingTimer) {
    clearInterval(pingTimer)
    pingTimer = null
  }
  if (ws) {
    ws.close()
  }
  if (rtcPlayer) {
    rtcPlayer.destroy()
    rtcPlayer = null
  }
})



// 发送文本
const sendText = () => {
  const text = inputText.value.trim()
  if (!text) return

  console.log('发送文本:', text)
  console.log('WebSocket状态:', ws?.readyState)

  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.log('WebSocket未连接，尝试重连...')
    alert('虚拟人服务未连接，正在重连...')
    connectWS()
    return
  }

  messages.push({ id: Date.now() + Math.random() + '', role: 'user', type: 'text', content: text })

  // 发送文本驱动协议（header.ctrl: 'text_interact'）
  const payload = {
    header: {
      app_id: APPID,
      request_id: getRequestId(),
      service_id: SERVICE_ID,
      ctrl: 'text_interact',
    },
    parameter: {
      tts: {
        vcn: 'x4_lingxiaoying_assist',
        speed: 50,
        pitch: 50,
        audio: {
          sample_rate: 16000
        }
      },
      air: {
        air: 1,
        add_nonsemantic: 1
      },
      nlp: {
        nlp: true // 开启语义理解，走大模型，不传tdp
      }
    },
    payload: {
      text: {
        content: text
      }
    },
  }

  console.log('发送payload:', payload)
  ws.send(JSON.stringify(payload))
  inputText.value = ''
  scrollToBottom()
}

// 录音相关
const startRecording = async () => {
  if (recording.value) return
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    alert('虚拟人服务未连接，正在重连...')
    connectWS()
    return
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
  audioChunks = []
  mediaRecorder.ondataavailable = (e) => {
    audioChunks.push(e.data)
  }
  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
    // 发送音频驱动协议（header.ctrl: 'audio_driver'）
    const arrayBuffer = await audioBlob.arrayBuffer()
    const audioData = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))
    const payload = {
      header: {
        app_id: APPID,
        request_id: getRequestId(),
        service_id: SERVICE_ID,
        ctrl: 'audio_driver',
      },
      parameter: {
        nlp: {
          nlp: true // 开启语义理解，走大模型，不传tdp
        }
      },
      payload: {
        audio: {
          status: 2, // 2表示结束
          audio: audioData
        }
      },
    }
    ws!.send(JSON.stringify(payload))
    messages.push({ id: Date.now() + Math.random() + '', role: 'user', type: 'audio', audioUrl: URL.createObjectURL(audioBlob) })
    scrollToBottom()
  }
  mediaRecorder.start()
  recording.value = true
}
const stopRecording = () => {
  if (mediaRecorder && recording.value) {
    mediaRecorder.stop()
    recording.value = false
  }
}

// 播放音频
const playAudio = (url?: string) => {
  if (!url) return
  const audio = new Audio(url)
  playingId.value = url
  audio.onended = () => { playingId.value = null }
  audio.play()
}

// 新增：用户交互恢复播放
const resumePlayer = () => {
  if (rtcPlayer && isPlayerBlocked.value) {
    try {
      rtcPlayer.resume()
      console.log('用户交互后恢复播放')
      isPlayerBlocked.value = false
      showPlayPrompt.value = false
    } catch (error) {
      console.error('恢复播放失败:', error)
      // 如果resume失败，尝试重新播放
      try {
        rtcPlayer.play()
        console.log('重新播放成功')
        isPlayerBlocked.value = false
        showPlayPrompt.value = false
      } catch (playError) {
        console.error('重新播放也失败:', playError)
      }
    }
  }
}

// 新增：处理页面点击事件
const handlePageClick = () => {
  if (isPlayerBlocked.value) {
    resumePlayer()
  }
}

// 新增：处理键盘事件
const handleKeyPress = (event: KeyboardEvent) => {
  if (isPlayerBlocked.value && (event.key === 'Enter' || event.key === ' ')) {
    resumePlayer()
  }
}
</script>

<style scoped>
.vhc-root {
  max-width: 800px;
  margin: 20px auto;
  background: var(--color-gray-50, #f9fafb);
  border-radius: 18px;
  box-shadow: 0 4px 32px rgba(0, 0, 0, 0.08);
  padding: 0 0 16px 0;
  min-height: 90vh;
  display: flex;
  flex-direction: column;
}

.vhc-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px 24px 0 24px;
  text-align: center;
}

.vhc-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #e0e7ef;
}

.vhc-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-brand-700, #2a31d8);
}

.vhc-chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-height: 300px;
  /* 限制聊天窗口高度，给虚拟人更多空间 */
}

.vhc-bubble {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  margin-bottom: 2px;
}

.vhc-bubble.user {
  flex-direction: row-reverse;
}

.vhc-bubble .vhc-bubble-content {
  max-width: 70%;
  background: #fff;
  border-radius: 16px;
  padding: 12px 18px;
  font-size: 1rem;
  color: #222;
  box-shadow: 0 2px 8px rgba(70, 95, 255, 0.04);
  position: relative;
  word-break: break-all;
}

.vhc-bubble.user .vhc-bubble-content {
  background: #465fff;
  color: #fff;
}

.vhc-avatar-bot img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1.5px solid #e0e7ef;
}

.vhc-avatar-video {
  width: 450px;
  height: 600px;
  border-radius: 16px;
  overflow: hidden;
  background: #fff;
  border: 2px solid #e0e7ef;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  /* Added for positioning the prompt */
  margin: 0 auto 20px auto;
  /* 居中显示并添加底部间距 */
}

.vhc-avatar-video-el {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  border: none;
  overflow: hidden;
  object-fit: cover;
  object-position: center top;
  /* 确保显示上半部分 */
}

.vhc-play-prompt {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  z-index: 10;
  cursor: pointer;
  border-radius: 16px;
  transition: background-color 0.2s;
  text-align: center;
  padding: 20px;
}

.vhc-play-prompt:hover {
  background-color: rgba(0, 0, 0, 0.8);
}

.vhc-play-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.vhc-play-hint {
  font-size: 0.6rem;
  opacity: 0.8;
  margin-top: 2px;
}

.vhc-input-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px 0 24px;
}

.vhc-input {
  flex: 1;
  border: 1px solid #e0e7ef;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 1rem;
  outline: none;
  background: #fff;
  transition: border 0.2s;
}

.vhc-input:focus {
  border-color: #465fff;
}

.vhc-mic-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #e0e7ef;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border 0.2s, box-shadow 0.2s;
  position: relative;
}

.vhc-mic-btn.recording {
  border-color: #f04438;
  box-shadow: 0 0 0 4px #f0443822;
}

.vhc-mic-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.vhc-mic-wave {
  display: flex;
  gap: 2px;
  margin-left: 2px;
}

.vhc-mic-bar {
  width: 3px;
  height: 16px;
  background: #f04438;
  border-radius: 2px;
  animation: mic-wave 1s infinite linear alternate;
}

.vhc-mic-bar:nth-child(2) {
  animation-delay: 0.1s;
}

.vhc-mic-bar:nth-child(3) {
  animation-delay: 0.2s;
}

.vhc-mic-bar:nth-child(4) {
  animation-delay: 0.3s;
}

.vhc-mic-bar:nth-child(5) {
  animation-delay: 0.4s;
}

@keyframes mic-wave {
  0% {
    height: 8px;
  }

  100% {
    height: 22px;
  }
}

.vhc-send-btn {
  background: linear-gradient(90deg, #465fff, #2a31d8);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0 18px;
  height: 44px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.vhc-send-btn:hover {
  background: linear-gradient(90deg, #2a31d8, #465fff);
}

.vhc-audio-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.vhc-audio-wave {
  display: flex;
  gap: 2px;
  align-items: flex-end;
}

.vhc-audio-bar {
  width: 3px;
  height: 10px;
  background: #465fff;
  border-radius: 2px;
  transition: height 0.2s;
}

.vhc-audio-wave.playing .vhc-audio-bar {
  animation: audio-wave 0.8s infinite linear alternate;
}

.vhc-audio-bar:nth-child(2) {
  animation-delay: 0.1s;
}

.vhc-audio-bar:nth-child(3) {
  animation-delay: 0.2s;
}

.vhc-audio-bar:nth-child(4) {
  animation-delay: 0.3s;
}

.vhc-audio-bar:nth-child(5) {
  animation-delay: 0.4s;
}

@keyframes audio-wave {
  0% {
    height: 8px;
  }

  100% {
    height: 22px;
  }
}

.vhc-audio-label {
  font-size: 0.95rem;
  color: #465fff;
}

.dark .vhc-root {
  background: #181c24;
}

.dark .vhc-header {
  border-bottom: 1px solid #232a3a;
}

.dark .vhc-chat-window {
  background: #181c24;
}

.dark .vhc-bubble .vhc-bubble-content {
  background: #232a3a;
  color: #fff;
}

.dark .vhc-bubble.user .vhc-bubble-content {
  background: #465fff;
  color: #fff;
}

.dark .vhc-input-bar {
  background: #181c24;
}

.dark .vhc-input {
  background: #232a3a;
  color: #fff;
  border-color: #232a3a;
}

.dark .vhc-mic-btn {
  background: #232a3a;
  border-color: #232a3a;
}

.dark .vhc-send-btn {
  background: linear-gradient(90deg, #465fff, #2a31d8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .vhc-root {
    max-width: 95vw;
    margin: 10px auto;
  }

  .vhc-avatar-video {
    width: 350px;
    height: 450px;
  }

  .vhc-chat-window {
    max-height: 250px;
  }
}

@media (max-width: 480px) {
  .vhc-avatar-video {
    width: 300px;
    height: 400px;
  }

  .vhc-chat-window {
    max-height: 200px;
  }

  .vhc-title {
    font-size: 1.2rem;
  }
}
</style>
