<template>
  <div class="vh-sidebar-mask" @click.self="closeSidebar">
    <div class="vh-sidebar-panel">
      <button class="vh-sidebar-close" @click="closeSidebar" title="关闭">×</button>
      <div class="vh-sidebar-content">
        <div v-if="enableVirtualHuman" class="vh-avatar-area">
          <div ref="videoContainer" class="vh-avatar-video-el"></div>
          <img v-if="!playerReady" class="vh-avatar-img" src="/images/brand/brand-01.svg" alt="虚拟人形象" />
          <div v-if="connectionError" class="vh-error-tip">{{ connectionError }}</div>
          <div v-if="showPlayPrompt" class="vh-play-prompt" @click="resumePlayer">
            <div class="vh-play-icon">▶</div>
            <span>点击恢复播放</span>
            <span class="vh-play-hint">或按空格键</span>
          </div>
        </div>
        <div v-else class="vh-chat-area">
          <div class="vh-chat-header">
            <div class="vh-chat-avatar">AI</div>
            <div>
              <div class="vh-chat-title">面试答疑助手</div>
              <div class="vh-chat-subtitle">{{ chatLoading ? '正在整理答案...' : '随时为你解答面试问题' }}</div>
            </div>
          </div>
          <div class="vh-knowledge-status">
            {{ knowledgeStatus || '回答将优先参考系统知识库与面试知识图谱' }}
          </div>
          <div ref="chatListRef" class="vh-chat-list">
            <div
              v-for="message in chatMessages"
              :key="message.id"
              :class="['vh-chat-message', `is-${message.role}`]"
            >
              <div
                v-if="message.role === 'assistant'"
                class="vh-chat-bubble vh-chat-markdown"
                v-html="renderMarkdown(message.content)"
              ></div>
              <div v-else class="vh-chat-bubble">{{ message.content }}</div>
            </div>
            <div v-if="chatLoading" class="vh-chat-message is-assistant">
              <div class="vh-chat-bubble vh-typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
          <div v-if="chatError" class="vh-chat-error">{{ chatError }}</div>
        </div>
        <div class="vh-input-bar">
          <input v-model="inputText" @keyup.enter="sendText" :disabled="chatLoading" placeholder="输入你的问题..." class="vh-input" />
          <!-- <button @mousedown="startRecording" @mouseup="stopRecording" @mouseleave="stopRecording"
            :class="['vh-mic-btn', { recording }]" title="语音输入">
            <span class="vh-mic-icon">
              <svg v-if="!recording" width="24" height="24" fill="none" viewBox="0 0 24 24">
                <path d="M12 15a3 3 0 0 0 3-3V7a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3Zm5-3a1 1 0 1 1 2 0 5 5 0 0 1-10 0 1 1 0 1 1 2 0 3 3 0 0 0 6 0Z" fill="currentColor" />
              </svg>
              <span v-if="recording" class="vh-mic-wave">
                <span v-for="i in 5" :key="i" class="vh-mic-bar"></span>
              </span>
            </span>
          </button> -->
          <button @click="sendText" class="vh-send-btn" :disabled="chatLoading" title="发送">
            <svg width="22" height="22" fill="none" viewBox="0 0 24 24"><path d="M22 2 11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="m22 2-7 20-4-9-9-4 20-7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, onMounted, onUnmounted } from 'vue'
import { showVirtualHumanSidebar } from '@/store/virtualHumanSidebar'
import { API_BASE_URL, getApiUrl } from '@/config/api'
import MarkdownIt from 'markdown-it'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import CryptoJS from 'crypto-js'

declare const __QWEN_MODEL__: string

const inputText = ref('')
const enableVirtualHuman = false
const chatListRef = ref<HTMLElement | null>(null)
const chatLoading = ref(false)
const chatError = ref('')
const knowledgeStatus = ref('')
const QWEN_MODEL = __QWEN_MODEL__
const markdown = new MarkdownIt({
  breaks: true,
  html: false,
  linkify: true,
})
type ChatRole = 'user' | 'assistant'
type ChatMessage = {
  id: string
  role: ChatRole
  content: string
}
type KeywordGraphResult = {
  keywords?: string[]
  matched_nodes?: Array<Record<string, unknown>>
  relationships?: Array<Record<string, unknown>>
  context?: string
}
const chatMessages = ref<ChatMessage[]>([
  {
    id: getRequestId(),
    role: 'assistant',
    content: '你好，我是你的面试答疑助手。随时为你解答面试问题。',
  },
])
const mathTokenPrefix = 'VH_MATH_TOKEN_'
const mathTokenPattern = new RegExp(`${mathTokenPrefix}(\\d+)`, 'g')
const cjkPattern = /[\u3400-\u9fff]/
const longMathPattern = /[{}⟨⟩<>]|\\[a-zA-Z]+|,.*,/ 

const shouldUseDisplayMath = (formula: string) => {
  const normalized = formula.trim()
  return normalized.length > 32 || longMathPattern.test(normalized)
}

const normalizeMathText = (content: string) =>
  content
    // Fix model output like "D$是数据元素的有限集$" to "$D$是数据元素的有限集".
    .replace(
      /(^|[^A-Za-z0-9_$\\])([A-Za-z][A-Za-z0-9_{}^\\]*)\$([^$\n]*[\u3400-\u9fff][^$\n]*)\$/g,
      (_match, prefix: string, formula: string, text: string) => `${prefix}$${formula}$${text}`,
    )
    // Fix model output like "是D$ 上 关系 的有限集" to "是$D$ 上 关系 的有限集".
    .replace(
      /(^|[\s，。；、：:是为和及与])([A-Za-z][A-Za-z0-9_{}^\\]*)\$(?=\s*[\u3400-\u9fff])/g,
      (_match, prefix: string, formula: string) => `${prefix}$${formula}$`,
    )
    // Fix model output like "$ A=(D,R) ，其中 $" to "$A=(D,R)$，其中".
    .replace(/\$([^$\n，。；、：:]+?)\s*([，。；、：:][^$\n]*?)\$/g, (_match, formula: string, text: string) => {
      return `$${formula.trim()}$${text}`
    })
    // Fix right-only delimiters commonly produced as "R $ 是 $ D $".
    .replace(/(^|[\s，。；、：:（(])([A-Za-z][A-Za-z0-9_{}^\\]*)\s+\$/g, (_match, prefix: string, formula: string) => {
      return `${prefix}$${formula}$`
    })
    // Remove harmless spaces just inside inline dollar delimiters.
    .replace(/\$\s*([^$\n]+?)\s*\$/g, (_match, formula: string) => `$${formula.trim()}$`)

const renderKatex = (formula: string, displayMode: boolean) => {
  const normalized = formula.trim()
  if (!normalized || cjkPattern.test(normalized)) {
    return formula
  }

  return katex.renderToString(normalized, {
    displayMode,
    throwOnError: false,
    strict: false,
  })
}

const protectMath = (content: string) => {
  const mathHtml: string[] = []
  const stash = (formula: string, displayMode = false) => {
    const token = `${mathTokenPrefix}${mathHtml.length}`
    mathHtml.push(renderKatex(formula, displayMode || shouldUseDisplayMath(formula)))
    return token
  }

  const text = normalizeMathText(content || '')
    .replace(/\$\$([\s\S]+?)\$\$/g, (_match, formula: string) => stash(formula, true))
    .replace(/\\\[([\s\S]+?)\\\]/g, (_match, formula: string) => stash(formula, true))
    .replace(/\\\(([\s\S]+?)\\\)/g, (_match, formula: string) => stash(formula))
    .replace(/\$([^$\n]+?)\$/g, (_match, formula: string) => stash(formula))

  return { text, mathHtml }
}

const renderMarkdown = (content: string) => {
  const { text, mathHtml } = protectMath(content)
  return markdown.render(text).replace(mathTokenPattern, (_match, index: string) => mathHtml[Number(index)] || '')
}
const recording = ref(false)
const videoContainer = ref<HTMLElement | null>(null)
let ws: WebSocket | null = null
let mediaRecorder: MediaRecorder | null = null
let micStream: MediaStream | null = null
let audioChunks: Blob[] = []
void audioChunks
let rtcPlayer: any = null
const isPlayerBlocked = ref(false)
const showPlayPrompt = ref(false)
const playerReady = ref(false)
const connectionError = ref('')
let seq = 0
let firstPacket = true
let currentRequestId = ''
let hasSentEndPacket = false
let endNextPacket = false
let avatarReady = false
let heartbeatInterval: ReturnType<typeof setInterval> | null = null
let shouldReconnect = true

const APPID = import.meta.env.VITE_AVATAR_APP_ID || ''
const APIKey = import.meta.env.VITE_AVATAR_API_KEY || ''
const APISecret = import.meta.env.VITE_AVATAR_API_SECRET || ''
const SERVICE_ID = import.meta.env.VITE_AVATAR_SERVICE_ID || ''
const AVATAR_ID = import.meta.env.VITE_AVATAR_ID || ''
function getHandShakeUrl() {
  if (!APPID || !APIKey || !APISecret || !SERVICE_ID || !AVATAR_ID) {
    throw new Error('虚拟人服务未配置，请检查 VITE_AVATAR_* 环境变量')
  }
  const apiKey = APIKey
  const apiSecret = APISecret
  const appId = APPID
  void appId
  const wsUrl = 'wss://avatar.cn-huadong-1.xf-yun.com/v1/interact'
  const date = new Date().toUTCString()
  const host = 'avatar.cn-huadong-1.xf-yun.com'
  const requestLine = 'GET /v1/interact HTTP/1.1'
  const signatureOrigin = `host: ${host}\ndate: ${date}\n${requestLine}`
  const hash = CryptoJS.HmacSHA256(signatureOrigin, apiSecret)
  const signature = CryptoJS.enc.Base64.stringify(hash)
  const authorizationOrigin = `hmac username=\"${apiKey}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"${signature}\"`
  const authorization = btoa(authorizationOrigin)
  const url = `${wsUrl}?authorization=${encodeURIComponent(authorization)}&host=${encodeURIComponent(host)}&date=${encodeURIComponent(date)}`
  return url
}
function getRequestId() {
  if (window.crypto && (window.crypto as any).randomUUID) {
    return (window.crypto as any).randomUUID()
  }
  return Date.now() + '-' + Math.random().toString(36).slice(2)
}
const closeSidebar = () => {
  shouldReconnect = false
  showVirtualHumanSidebar.value = false
  if (ws) ws.close()
  if (rtcPlayer) rtcPlayer.destroy()
  playerReady.value = false
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
}
const initRTCPlayer = async (streamConfig: any) => {
  const { RTCPlayer } = await import('@/../src/rtcplayer.esm.js')
  if (rtcPlayer) rtcPlayer.destroy()
  rtcPlayer = new RTCPlayer()
  rtcPlayer.on('play', () => { isPlayerBlocked.value = false; showPlayPrompt.value = false })
    .on('playing', () => { isPlayerBlocked.value = false; showPlayPrompt.value = false })
    .on('error', (e: any) => {
      if (e && (e.message?.includes('NotAllowedError') || e.name === 'NotAllowedError')) {
        isPlayerBlocked.value = true; showPlayPrompt.value = true
      }
    })
    .on('not-allowed', () => { isPlayerBlocked.value = true; showPlayPrompt.value = true })
  rtcPlayer.onCustomSignParam = (_params: any) => ({ ...streamConfig })
  rtcPlayer.playerType = 12
  rtcPlayer.stream = streamConfig
  rtcPlayer.videoSize = { width: 720, height: 1280 }
  rtcPlayer.videoMode = 'stretch'
  if (rtcPlayer.setCropArea) {
    rtcPlayer.setCropArea({ x: 0, y: 0, width: 720, height: 960 })
  }
  if (videoContainer.value) {
    videoContainer.value.style.width = '100%'
    videoContainer.value.style.height = '100%'
    videoContainer.value.style.borderRadius = '18px'
    videoContainer.value.style.overflow = 'hidden'
    videoContainer.value.style.border = 'none'
    videoContainer.value.style.background = '#fff'
    videoContainer.value.style.objectFit = 'contain'
    rtcPlayer.container = videoContainer.value
    setTimeout(() => {
      try { rtcPlayer.play(); playerReady.value = true } catch (error) { isPlayerBlocked.value = true; showPlayPrompt.value = true }
    }, 1000)
  }
}

// ws关闭时自动重连，保证录音按钮可用
const connectWS = () => {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return
  }
  connectionError.value = ''
  ws = new WebSocket(getHandShakeUrl())
  ws.binaryType = 'arraybuffer'
  ws.onopen = () => {
    const handshake = {
      header: { app_id: APPID, request_id: getRequestId(), scene_id: SERVICE_ID, ctrl: 'start' },
      parameter: {
        avatar: {
          stream: { protocol: 'xrtc', fps: 25, bitrate: 5000, alpha: 1 },
          avatar_id: AVATAR_ID,
          width: 720,
          height: 1280
        },
        tts: { vcn: 'x4_lingxiaoying_assist', speed: 50, pitch: 50, volume: 50 },
        subtitle: { subtitle: 0, font_color: '#FF0000', font_size: 10, position_x: 0, position_y: 0, font_name: 'mainTitle', width: 100, height: 100 }
      },
      payload: {}
    }
    ws!.send(JSON.stringify(handshake))
    // 启动心跳
    heartbeatInterval = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          header: { app_id: APPID, request_id: getRequestId(), ctrl: 'ping' }
        }))
      }
    }, 5000)
  }
  ws.onmessage = async (e) => {
    if (e.data instanceof ArrayBuffer) return
    let data = null
    try { data = JSON.parse(e.data) } catch { return }

    if (typeof data?.header?.code === 'number' && data.header.code !== 0) {
      console.error('[VirtualHuman] 服务端错误:', data.header.code, data.header.message || '', data)

      const code = data.header.code
      const msg = data.header.message || '未知错误'
      if (code === 11203) {
        connectionError.value = `虚拟人授权失败（${code}）：${msg}`
        shouldReconnect = false
        if (ws && ws.readyState === WebSocket.OPEN) ws.close()
      } else if (code === 11200) {
        connectionError.value = `虚拟人能力未授权（${code}）：${msg}`
        shouldReconnect = false
        if (ws && ws.readyState === WebSocket.OPEN) ws.close()
      } else if (code === 10107) {
        connectionError.value = `虚拟人参数或场景配置错误（${code}）：${msg}`
      }
      return
    }

    if (data?.header?.code === 0 && data?.payload?.avatar?.event_type === 'stream_info') {
      const info = data.payload.avatar
      const ext = info.stream_extend || {}
      const streamUrl = info.stream_url || ''
      const m = streamUrl.match(/^xrtcs?:\/\/([^\/]+)\/(.+)$/)
      if (!m) return
      const host = m[1], sid = m[2]
      const streamConfig = {
        sid,
        server: `https://${host}`,
        auth: ext.user_sign ? `Bearer ${ext.user_sign}` : '',
        appid: ext.appid || APPID,
        roomId: sid,
        userId: ext.userId || getRequestId(),
        timeStr: ext.timeStr || ''
      }
      initRTCPlayer(streamConfig)
      avatarReady = true
      return
    }
    // 监听 ASR 最终结果，自动发 text_interact
    if (
      data?.header?.ctrl === 'audio_interact' &&
      data?.header?.status === 2
    ) {
      console.log('收到ASR最终结果:', data)
      const asrText = data?.payload?.asr?.text
      console.log('ASR文本内容:', asrText)

      if (asrText && asrText.trim() !== "") {
        const recognized = asrText.trim()
        console.log('ASR识别结果有效:', recognized)

        // Use text_driver instead of text_interact, matching the original demo.
        const textDriver = {
          header: {
            app_id: APPID,
            request_id: getRequestId(),
            ctrl: 'text_driver'
          },
          parameter: {
            tts: {
              vcn: 'x4_lingxiaoying_assist',
              speed: 50,
              pitch: 50
            },
            avatar_dispatch: {
              interactive_mode: 0
            }
          },
          payload: {
            text: { content: recognized }
          }
        }
        console.log('发送text_driver:', textDriver)
        if (ws) ws.send(JSON.stringify(textDriver))
      } else {
        console.log('ASR result is empty, skip sending.')
      }
    }
    // 处理NLP错误响应
    if (data?.payload?.nlp?.error_code) {
      console.error('NLP错误:', data.payload.nlp.error_message)
      console.error('错误详情:', data.payload.nlp)
    }
  }
  ws.onclose = () => {
    ws = null
    if (rtcPlayer) rtcPlayer.destroy(); playerReady.value = false
    avatarReady = false
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
    if (shouldReconnect) {
      setTimeout(() => connectWS(), 1000) // 1秒后自动重连
    }
  }
  ws.onerror = () => {
    ws = null
    if (rtcPlayer) rtcPlayer.destroy(); playerReady.value = false
    avatarReady = false
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
    if (shouldReconnect) {
      setTimeout(() => connectWS(), 1000)
    }
  }
}

onMounted(() => {
  shouldReconnect = true
  connectionError.value = ''
  if (enableVirtualHuman) {
    connectWS()
  }
})
onUnmounted(() => {
  shouldReconnect = false
  if (ws) ws.close();
  if (rtcPlayer) rtcPlayer.destroy();
  playerReady.value = false
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
})
const scrollChatToBottom = async () => {
  await nextTick()
  if (chatListRef.value) {
    chatListRef.value.scrollTop = chatListRef.value.scrollHeight
  }
}

const getAuthHeader = (): Record<string, string> => {
  const token =
    localStorage.getItem('admin_access_token') || localStorage.getItem('access_token') || ''
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const requestKnowledgeGraph = async (question: string) => {
  const requestOptions: RequestInit = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
    body: JSON.stringify({ question, limit: 8, neighbor_limit: 80 }),
  }
  const endpoints = [
    getApiUrl('/graph-rag-keyword/query'),
    `${API_BASE_URL}/graph-rag-keyword/query`,
  ]

  let lastError: Error | null = null
  for (const endpoint of endpoints) {
    try {
      const response = await fetch(endpoint, requestOptions)
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(errorText || `GraphRAG request failed: ${response.status}`)
      }
      return response.json()
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('GraphRAG request failed')
    }
  }
  throw lastError || new Error('GraphRAG request failed')
}

const normalizeKeywordGraphContext = (graphData: KeywordGraphResult) => {
  const matchedNodes = Array.isArray(graphData?.matched_nodes) ? graphData.matched_nodes : []
  const relationships = Array.isArray(graphData?.relationships) ? graphData.relationships : []
  const context = typeof graphData?.context === 'string' ? graphData.context : ''
  return {
    context,
    sourceCount: matchedNodes.length,
    relationshipCount: relationships.length,
    keywords: Array.isArray(graphData?.keywords) ? graphData.keywords : [],
  }
}

const sendText = async () => {
  const text = inputText.value.trim()
  if (!text || chatLoading.value) return

  inputText.value = ''
  chatError.value = ''
  chatMessages.value.push({ id: getRequestId(), role: 'user', content: text })
  chatLoading.value = true
  await scrollChatToBottom()

  try {
    knowledgeStatus.value = '正在检索知识库...'
    let knowledgeContext = ''
    let knowledgeSourceCount = 0
    try {
      const graphData = await requestKnowledgeGraph(text)
      const keywordGraph = normalizeKeywordGraphContext(graphData)
      knowledgeSourceCount = keywordGraph.sourceCount
      knowledgeContext = keywordGraph.context
      knowledgeStatus.value = knowledgeSourceCount
        ? `已参考知识图谱中的 ${knowledgeSourceCount} 个关键词节点`
        : '知识库暂未检索到直接相关内容'
    } catch (error) {
      console.warn('[GraphRAG] retrieval failed, fallback to LLM only:', error)
      knowledgeStatus.value = '知识库暂不可用，已切换为通用答疑'
    }

    const history = chatMessages.value
      .filter((message) => message.role === 'user' || message.role === 'assistant')
      .slice(-12)
      .map((message) => ({
        role: message.role,
        content: message.content,
      }))

    const response = await fetch('/qwen/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: QWEN_MODEL,
        messages: [
          {
            role: 'system',
            content:
              '你是面试系统中的答疑助手，负责结合系统知识库和面试知识图谱回答用户问题。回答要清晰、可靠、偏向面试学习场景；如果知识库上下文不足，可以说明并给出通用建议。',
          },
          ...(knowledgeContext
            ? [
                {
                  role: 'system',
                  content: `以下是从系统知识图谱检索到的相关知识库内容，请优先依据这些内容回答：\n${knowledgeContext}`,
                },
              ]
            : []),
          ...history,
        ],
        temperature: 0.7,
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(errorText || `请求失败：${response.status}`)
    }

    const data = await response.json()
    const content = data?.choices?.[0]?.message?.content?.trim()
    if (!content) {
      throw new Error('千问没有返回有效内容')
    }

    const sourceNote = knowledgeSourceCount
      ? `\n\n---\n知识库参考：已结合 ${knowledgeSourceCount} 个关键词节点及其邻居关系。`
      : ''
    chatMessages.value.push({ id: getRequestId(), role: 'assistant', content: `${content}${sourceNote}` })
  } catch (error) {
    console.error('[QwenChat] request failed:', error)
    chatError.value = error instanceof Error ? error.message : '千问请求失败，请稍后再试'
    chatMessages.value.push({
      id: getRequestId(),
      role: 'assistant',
      content: '抱歉，刚才没有成功连上千问，请稍后再试。',
    })
  } finally {
    chatLoading.value = false
    await scrollChatToBottom()
  }
}

const sendTextToAvatar = () => {
  const text = inputText.value.trim()
  if (!text || !ws || ws.readyState !== WebSocket.OPEN) return

  // Use the original text_interact protocol for the virtual human mode.
  const payload = {
    header: {
      app_id: APPID,
      request_id: getRequestId(),
      ctrl: 'text_interact',
    },
    parameter: {
      tts: {
        vcn: 'x4_lingxiaoying_assist',
        speed: 50,
        pitch: 50
      },
      avatar_dispatch: {
        interactive_mode: 0
      },
      air: {
        air: 1,
        add_nonsemantic: 1
      },
      nlp: {
        nlp: true // 开启语义理解，走大模型，不传tdp
      }
    },
    payload: { text: { content: text } }
  }
  console.log('手动发送text_driver:', payload)
  ws.send(JSON.stringify(payload))
  inputText.value = ''
}
void sendTextToAvatar

const startRecording = async () => {
  if (recording.value || !ws || ws.readyState !== WebSocket.OPEN || !avatarReady) return
  // Release previous recording resources.
  if (mediaRecorder) {
    try { mediaRecorder.stop() } catch {}
    mediaRecorder = null
  }
  if (micStream) {
    try { micStream.getTracks().forEach(t => t.stop()) } catch {}
    micStream = null
  }
  micStream = await navigator.mediaDevices.getUserMedia({ audio: true })
  let mimeType = ''
  let encoding = 'raw'
  let sampleRate = 16000
  let channels = 1
  let bitDepth = 16
  if (MediaRecorder.isTypeSupported('audio/wav')) {
    mimeType = 'audio/wav'
    encoding = 'raw'
  } else if (MediaRecorder.isTypeSupported('audio/webm')) {
    mimeType = 'audio/webm'
    encoding = 'opus-wb'
  } else {
    alert('当前浏览器不支持语音输入')
    return
  }
  seq = 0
  firstPacket = true
  hasSentEndPacket = false
  endNextPacket = false
  // 生成本轮唯一 request_id
  if (window.crypto && (window.crypto as any).randomUUID) {
    currentRequestId = (window.crypto as any).randomUUID()
  } else {
    currentRequestId = Date.now() + '-' + Math.random().toString(36).slice(2)
  }
  mediaRecorder = new MediaRecorder(micStream, { mimeType })
  mediaRecorder.ondataavailable = async (e) => {
    if (hasSentEndPacket) return
    const arrayBuffer = await e.data.arrayBuffer()
    const audioB64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))
    // Keep the original virtual human audio packet protocol.
    const isEnd = endNextPacket
    const status = firstPacket ? 0 : (isEnd ? 2 : 1)
    // 即使是尾包，也要发送真实的音频数据，不能为空字符串
    const audioPayload = audioB64
    const frameSize = arrayBuffer.byteLength
    ws!.send(JSON.stringify({
      header: {
        app_id: APPID,
        request_id: currentRequestId,
        ctrl: 'audio_interact'
      },
      parameter: {
        avatar_dispatch: {
          full_duplex: 0
        },
        nlp: {
          nlp: true
        }
      },
      payload: {
        audio: {
          encoding,
          sample_rate: sampleRate,
          channels,
          bit_depth: bitDepth,
          status,
          seq: seq++,
          audio: audioPayload,
          frame_size: frameSize
        }
      }
    }))
    firstPacket = false
    if (isEnd) {
      hasSentEndPacket = true
      // Finalize recording and clean up resources.
      if (mediaRecorder) {
        mediaRecorder.ondataavailable = null
        mediaRecorder.stop()
      }
      if (micStream) {
        micStream.getTracks().forEach(t => t.stop())
        micStream = null
      }
      recording.value = false
      endNextPacket = false
    }
  }
  mediaRecorder.onstop = async () => {
    // 只做资源清理
    if (mediaRecorder) mediaRecorder = null
    if (micStream) {
      micStream.getTracks().forEach(t => t.stop())
      micStream = null
    }
  }
  mediaRecorder.start(200)
  recording.value = true
}
void startRecording

const stopRecording = () => {
  if (mediaRecorder && recording.value) {
    endNextPacket = true // 下一帧为尾包
  }
}
void stopRecording
const resumePlayer = () => {
  if (rtcPlayer && isPlayerBlocked.value) {
    try { rtcPlayer.resume(); isPlayerBlocked.value = false; showPlayPrompt.value = false } catch { try { rtcPlayer.play(); isPlayerBlocked.value = false; showPlayPrompt.value = false } catch {} }
  }
}
</script>

<style scoped>
.vh-sidebar-mask {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: rgba(30, 41, 59, 0.15);
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
}
.vh-sidebar-panel {
  width: 500px;
  max-width: 100vw;
  height: 100vh;
  background: #fff;
  box-shadow: -2px 0 24px rgba(70,95,255,0.12);
  border-top-left-radius: 18px;
  border-bottom-left-radius: 18px;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0;
  animation: slideInRight 0.25s cubic-bezier(.4,1.3,.6,1) 1;
}
@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
.vh-sidebar-close {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 10;
  font-size: 2rem;
  background: rgba(255,255,255,0.85);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  color: #465fff;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(70,95,255,0.08);
  transition: background 0.2s;
}
.vh-sidebar-close:hover {
  background: #e0e7ef;
}
.vh-sidebar-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  padding: 0;
  position: relative;
}
.vh-avatar-area {
  flex: 1 1 auto;
  width: 100%;
  height: 100%;
  min-height: 0;
  max-height: none;
  margin-top: 0;
  padding: 0;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
}
.vh-avatar-video-el, .vh-avatar-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  margin: 0;
  background: transparent;
  border: none;
  box-shadow: none;
}
.vh-avatar-img {
  border-radius: 18px;
  background: #fff;
}
.vh-play-prompt {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 18px 28px;
  box-shadow: 0 4px 24px rgba(70,95,255,0.12);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}
.vh-play-icon {
  font-size: 2rem;
  color: #465fff;
  margin-bottom: 8px;
}
.vh-play-hint {
  color: #888;
  font-size: 0.95em;
  margin-top: 4px;
}
.vh-error-tip {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 12px;
  z-index: 12;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(220, 38, 38, 0.92);
  color: #fff;
  font-size: 12px;
  line-height: 1.4;
}
.vh-chat-area {
  flex: 1 1 auto;
  width: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #f7f9fc;
  padding: 22px 18px 96px;
}
.vh-chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 44px 18px 2px;
}
.vh-chat-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #465fff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0;
}
.vh-chat-title {
  color: #111827;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.3;
}
.vh-chat-subtitle {
  color: #667085;
  font-size: 12px;
  line-height: 1.5;
}
.vh-knowledge-status {
  align-self: flex-start;
  margin: -4px 0 12px 2px;
  padding: 5px 10px;
  border-radius: 999px;
  background: #eef4ff;
  color: #465fff;
  border: 1px solid #d8e2ff;
  font-size: 12px;
  line-height: 1.4;
}
.vh-chat-list {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  padding: 6px 2px 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.vh-chat-message {
  display: flex;
  min-width: 0;
}
.vh-chat-message.is-user {
  justify-content: flex-end;
}
.vh-chat-message.is-assistant {
  justify-content: flex-start;
}
.vh-chat-bubble {
  max-width: 82%;
  min-width: 0;
  border-radius: 16px;
  padding: 11px 14px;
  font-size: 14px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  box-shadow: 0 6px 18px rgba(17, 24, 39, 0.06);
}
.vh-chat-message.is-user .vh-chat-bubble {
  color: #fff;
  background: #465fff;
  border-bottom-right-radius: 6px;
}
.vh-chat-message.is-assistant .vh-chat-bubble {
  color: #1f2937;
  background: #fff;
  border-bottom-left-radius: 6px;
}
.vh-chat-markdown {
  white-space: normal;
}
.vh-chat-markdown :deep(*) {
  margin-top: 0;
}
.vh-chat-markdown :deep(*:last-child) {
  margin-bottom: 0;
}
.vh-chat-markdown :deep(h1),
.vh-chat-markdown :deep(h2),
.vh-chat-markdown :deep(h3),
.vh-chat-markdown :deep(h4) {
  color: #111827;
  font-weight: 700;
  line-height: 1.35;
  margin-bottom: 8px;
}
.vh-chat-markdown :deep(h1) {
  font-size: 18px;
}
.vh-chat-markdown :deep(h2) {
  font-size: 17px;
}
.vh-chat-markdown :deep(h3),
.vh-chat-markdown :deep(h4) {
  font-size: 15px;
}
.vh-chat-markdown :deep(p) {
  margin-bottom: 8px;
}
.vh-chat-markdown :deep(ul),
.vh-chat-markdown :deep(ol) {
  margin: 6px 0 8px 18px;
  padding: 0;
}
.vh-chat-markdown :deep(li) {
  margin: 3px 0;
}
.vh-chat-markdown :deep(hr) {
  height: 1px;
  border: 0;
  background: #e5e7eb;
  margin: 10px 0;
}
.vh-chat-markdown :deep(code) {
  border-radius: 5px;
  background: #f3f4f6;
  color: #111827;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 0.92em;
  padding: 1px 5px;
}
.vh-chat-markdown :deep(pre) {
  overflow-x: auto;
  border-radius: 8px;
  background: #111827;
  color: #f9fafb;
  margin: 8px 0;
  padding: 10px 12px;
}
.vh-chat-markdown :deep(pre code) {
  display: block;
  background: transparent;
  color: inherit;
  padding: 0;
}
.vh-chat-markdown :deep(a) {
  color: #465fff;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.vh-chat-markdown :deep(blockquote) {
  border-left: 3px solid #c7d2fe;
  color: #4b5563;
  margin: 8px 0;
  padding: 2px 0 2px 10px;
}
.vh-chat-markdown :deep(.katex) {
  font-size: 1em;
  line-height: 1.4;
}
.vh-chat-markdown :deep(.katex-display) {
  display: block;
  overflow-x: auto;
  overflow-y: hidden;
  width: 100%;
  max-width: 100%;
  margin: 6px 0;
  padding: 4px 0 8px;
}
.vh-chat-markdown :deep(.katex-display > .katex) {
  display: inline-block;
  min-width: max-content;
  text-align: left;
}
.vh-chat-error {
  margin: 8px 4px 0;
  padding: 9px 11px;
  border-radius: 10px;
  background: #fef2f2;
  color: #b42318;
  font-size: 12px;
  line-height: 1.4;
}
.vh-typing {
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 54px;
}
.vh-typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #98a2b3;
  animation: typingPulse 1s infinite ease-in-out;
}
.vh-typing span:nth-child(2) {
  animation-delay: 0.15s;
}
.vh-typing span:nth-child(3) {
  animation-delay: 0.3s;
}
@keyframes typingPulse {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.45; }
  40% { transform: translateY(-4px); opacity: 1; }
}
.vh-input-bar {
  width: 100%;
  max-width: 380px;
  margin: 0 auto 24px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  z-index: 20;
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  background: rgba(255,255,255,0.97);
  border-radius: 28px;
  box-shadow: 0 4px 24px rgba(70,95,255,0.10);
  padding: 8px 18px;
}
.vh-input {
  flex: 1 1 auto;
  border: none;
  outline: none;
  background: transparent;
  font-size: 1rem;
  padding: 8px 12px;
  border-radius: 18px;
  color: #222;
}
.vh-input::placeholder {
  color: #aaa;
}
.vh-mic-btn, .vh-send-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f3f6fd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #465fff;
  font-size: 1.1rem;
  box-shadow: 0 2px 8px rgba(70,95,255,0.08);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.vh-mic-btn.recording {
  background: #ffe0e0;
  color: #e53935;
}
.vh-mic-btn:hover, .vh-send-btn:hover {
  background: #e0e7ef;
}
.vh-send-btn:disabled,
.vh-input:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}
.vh-mic-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}
.vh-mic-wave {
  display: flex;
  gap: 2px;
}
.vh-mic-bar {
  width: 3px;
  height: 14px;
  background: #e53935;
  border-radius: 2px;
  animation: mic-wave 1s infinite linear alternate;
}
@keyframes mic-wave {
  0% { height: 7px; }
  100% { height: 14px; }
}
</style>
