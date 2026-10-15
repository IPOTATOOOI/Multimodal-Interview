<template>
  <div class="w-full">
    <div class="flex items-center gap-4 mb-6">
      <el-button @click="handleCancel" text>
        <Icon icon="lucide:arrow-left" class="w-4 h-4 mr-1" />
        返回
      </el-button>
      <div>
        <h3 class="text-xl font-bold text-zinc-800 dark:text-zinc-100">解析已有简历</h3>
        <p class="text-sm text-zinc-400 dark:text-zinc-500">
          保留 Word 原版式，只替换确认后的文字内容
        </p>
      </div>
    </div>

    <el-card
      v-if="!uploadedFile"
      class="border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 w-full mb-6"
      shadow="never"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <Icon icon="lucide:upload-cloud" class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <span class="font-semibold text-zinc-800 dark:text-zinc-100">选择 Word 简历</span>
        </div>
      </template>

      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-remove="handleRemove"
        accept=".docx"
        :limit="1"
        class="upload-zone w-full"
      >
        <div class="py-16 px-6 text-center">
          <div
            class="mx-auto w-16 h-16 mb-4 rounded-full bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center"
          >
            <Icon icon="lucide:file-up" class="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          </div>
          <p class="text-base font-semibold text-zinc-800 dark:text-zinc-100 mb-2">
            拖拽 .docx 简历文件到此处，或
            <span class="text-indigo-600 dark:text-indigo-400">点击上传</span>
          </p>
          <p class="text-xs text-zinc-400 dark:text-zinc-500">
            当前原样预览和回写仅支持 .docx，文件大小不超过 10MB
          </p>
        </div>
      </el-upload>
    </el-card>

    <div v-else class="resume-workspace">
      <section class="preview-panel">
        <ResumeDocxEditor
          :docx-file="previewFile"
          :initial-title="previewTitle"
          :pdf-error="pdfPreviewError"
          :pdf-loading="isPreviewLoading"
          :pdf-url="pdfPreviewUrl"
          :show-back="false"
        />
      </section>

      <aside class="control-panel">
        <el-card shadow="never" class="mb-4">
          <template #header>
            <div class="flex items-center justify-between gap-3">
              <div class="min-w-0">
                <div class="font-semibold text-zinc-800 truncate">{{ uploadedFile.name }}</div>
                <div class="text-xs text-zinc-400 mt-1">{{ formatFileSize(uploadedFile.size) }}</div>
              </div>
              <el-button @click="resetUpload">
                <Icon icon="lucide:rotate-ccw" class="w-4 h-4 mr-1.5" />
                重新上传
              </el-button>
            </div>
          </template>

          <div class="action-grid">
            <el-button type="primary" :loading="isParsing" @click="parseResume">
              <Icon icon="lucide:sparkles" class="w-4 h-4 mr-1.5" />
              {{ isParsing ? 'AI 解析中...' : 'AI 解析并生成建议' }}
            </el-button>
            <el-button :disabled="!acceptedPatchCount" :loading="isExporting" @click="exportPatchedDocx">
              <Icon icon="lucide:file-down" class="w-4 h-4 mr-1.5" />
              导出修改后的 Word
            </el-button>
          </div>
        </el-card>

        <el-card v-if="parsedData" shadow="never" class="mb-4">
          <template #header>
            <div class="flex items-center gap-2">
              <Icon icon="lucide:list-checks" class="w-5 h-5 text-indigo-600" />
              <span class="font-semibold text-zinc-800">AI 解析结果</span>
            </div>
          </template>

          <div class="summary-list">
            <div v-if="parsedData.basic_info?.name">
              <span>姓名</span>
              <strong>{{ parsedData.basic_info.name }}</strong>
            </div>
            <div v-if="parsedData.target_role">
              <span>目标岗位</span>
              <strong>{{ parsedData.target_role }}</strong>
            </div>
            <div v-if="parsedData.basic_info?.phone">
              <span>电话</span>
              <strong>{{ parsedData.basic_info.phone }}</strong>
            </div>
            <div v-if="parsedData.basic_info?.email">
              <span>邮箱</span>
              <strong>{{ parsedData.basic_info.email }}</strong>
            </div>
          </div>

          <div v-if="parsedData.highlights?.length" class="mt-4">
            <div class="section-label">亮点</div>
            <ul class="compact-list">
              <li v-for="(item, index) in parsedData.highlights" :key="index">{{ item }}</li>
            </ul>
          </div>
        </el-card>

        <el-card shadow="never">
          <template #header>
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2">
                <Icon icon="lucide:replace" class="w-5 h-5 text-indigo-600" />
                <span class="font-semibold text-zinc-800">文字替换建议</span>
              </div>
              <span class="text-xs text-zinc-400">{{ acceptedPatchCount }}/{{ patches.length }} 已选择</span>
            </div>
          </template>

          <el-empty v-if="!patches.length" description="AI 解析后会在这里生成可确认的文字替换建议" />

          <div v-else class="patch-list">
            <div v-for="patch in patches" :key="patch.localId" class="patch-item">
              <div class="patch-head">
                <el-checkbox v-model="patch.accepted" />
                <div class="patch-title">
                  <div>{{ patch.label || '文字优化' }}</div>
                  <span>{{ patch.reason || '保留原位置，仅替换文字内容' }}</span>
                </div>
              </div>

              <div class="patch-text">
                <label>原文</label>
                <div class="original-text">{{ patch.original }}</div>
              </div>

              <div class="patch-text">
                <label>替换为</label>
                <el-input
                  v-model="patch.replacement"
                  type="textarea"
                  :rows="2"
                  resize="none"
                  :disabled="!patch.accepted"
                />
              </div>
            </div>
          </div>
        </el-card>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Icon } from '@iconify/vue'
import mammoth from 'mammoth'
import ResumeDocxEditor from '@/docx-editor/components/ResumeDocxEditor.vue'
import { API_BASE_URL } from '@/config/api'
import {
  applyDocxTextPatches,
  buildAiCandidateNodes,
  downloadBlob,
  extractDocxTextNodes,
} from '@/utils/docxTextPatch'

const QWEN_MODEL = typeof __QWEN_MODEL__ !== 'undefined' ? __QWEN_MODEL__ : 'qwen-plus'

const emit = defineEmits(['cancel'])

const uploadedFile = ref(null)
const modifiedBlob = ref(null)
const pdfPreviewUrl = ref('')
const pdfPreviewError = ref('')
const isParsing = ref(false)
const isExporting = ref(false)
const isPreviewLoading = ref(false)
const parsedData = ref(null)
const patches = ref([])
const textNodes = ref([])

const previewFile = computed(() => modifiedBlob.value || uploadedFile.value)
const previewTitle = computed(() => {
  if (modifiedBlob.value && uploadedFile.value) return `已修改 - ${uploadedFile.value.name}`
  return uploadedFile.value?.name || 'Word 简历预览'
})
const acceptedPatchCount = computed(
  () => patches.value.filter((patch) => patch.accepted && patch.replacement?.trim()).length,
)

const handleFileChange = (file) => {
  const raw = file.raw
  if (!raw) return
  if (!/\.docx$/i.test(raw.name)) {
    ElMessage.warning('当前仅支持 .docx 文件，请先在 Word 中另存为 .docx')
    return
  }
  if (raw.size > 10 * 1024 * 1024) {
    ElMessage.warning('文件大小不能超过 10MB')
    return
  }

  uploadedFile.value = raw
  modifiedBlob.value = null
  clearPdfPreviewUrl()
  pdfPreviewError.value = ''
  parsedData.value = null
  patches.value = []
  textNodes.value = []
  refreshPdfPreview(raw, raw.name)
}

const handleRemove = () => resetUpload()

const resetUpload = () => {
  uploadedFile.value = null
  modifiedBlob.value = null
  clearPdfPreviewUrl()
  pdfPreviewError.value = ''
  parsedData.value = null
  patches.value = []
  textNodes.value = []
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const parseResume = async () => {
  if (!uploadedFile.value) return
  isParsing.value = true
  modifiedBlob.value = null

  try {
    const arrayBuffer = await uploadedFile.value.arrayBuffer()
    const rawTextResult = await mammoth.extractRawText({ arrayBuffer })
    textNodes.value = await extractDocxTextNodes(uploadedFile.value)

    const aiResult = await requestAiResumeAdvice(rawTextResult.value, textNodes.value)
    parsedData.value = normalizeParsedData(aiResult)
    patches.value = normalizePatches(aiResult?.patches || [], textNodes.value)

    if (!patches.value.length) {
      ElMessage.info('AI 已完成解析，但没有生成可安全回写的文字替换建议')
    } else {
      ElMessage.success(`AI 已生成 ${patches.value.length} 条文字替换建议`)
    }
  } catch (error) {
    console.error('AI resume parse failed:', error)
    ElMessage.error(error?.message || 'AI 解析失败，请稍后再试')
  } finally {
    isParsing.value = false
  }
}

const exportPatchedDocx = async () => {
  if (!uploadedFile.value || !acceptedPatchCount.value) return
  isExporting.value = true

  try {
    const blob = await applyDocxTextPatches(uploadedFile.value, patches.value)
    modifiedBlob.value = blob
    const fileName = uploadedFile.value.name.replace(/\.docx$/i, '-AI优化.docx')
    downloadBlob(blob, fileName)
    ElMessage.success('已导出修改后的 Word，原始排版会尽量保持不变')
  } catch (error) {
    console.error('docx export failed:', error)
    ElMessage.error('导出失败，请检查替换内容后重试')
  } finally {
    isExporting.value = false
  }
}

const handleCancel = () => emit('cancel')

onBeforeUnmount(() => {
  clearPdfPreviewUrl()
})

async function refreshPdfPreview(file, fileName) {
  if (!file) return
  isPreviewLoading.value = true
  pdfPreviewError.value = ''
  clearPdfPreviewUrl()

  try {
    const formData = new FormData()
    formData.append('file', file, fileName || 'resume.docx')
    const response = await fetch(`${API_BASE_URL}/api/resume/preview-pdf`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const message = await readApiError(response)
      throw new Error(message || `PDF 预览生成失败：${response.status}`)
    }

    const pdfBlob = await response.blob()
    pdfPreviewUrl.value = URL.createObjectURL(pdfBlob)
  } catch (error) {
    console.error('resume pdf preview failed:', error)
    pdfPreviewError.value = error?.message || 'PDF 预览生成失败'
  } finally {
    isPreviewLoading.value = false
  }
}

function clearPdfPreviewUrl() {
  if (!pdfPreviewUrl.value) return
  URL.revokeObjectURL(pdfPreviewUrl.value)
  pdfPreviewUrl.value = ''
}

async function readApiError(response) {
  const text = await response.text()
  if (!text) return ''
  try {
    const data = JSON.parse(text)
    return data?.detail || data?.message || text
  } catch {
    return text
  }
}

async function requestAiResumeAdvice(rawText, nodes) {
  const candidates = buildAiCandidateNodes(nodes)
  const body = {
    model: QWEN_MODEL,
    temperature: 0.2,
    messages: [
      {
        role: 'system',
        content:
          '你是专业中文简历优化助手。你必须只输出 JSON，不要输出 Markdown。你的任务是解析简历，并给出可安全回写到 docx 的文字替换建议。',
      },
      {
        role: 'user',
        content: buildAiPrompt(rawText, candidates),
      },
    ],
  }

  let response = await postQwenChat({
    ...body,
    response_format: { type: 'json_object' },
  })
  let failureMessage = ''

  if (!response.ok) {
    failureMessage = await response.text()
    if (shouldRetryWithoutJsonMode(response.status, failureMessage)) {
      response = await postQwenChat(body)
      failureMessage = ''
    }
  }

  if (!response.ok) {
    failureMessage = failureMessage || (await response.text())
    throw new Error(failureMessage || `AI 请求失败：${response.status}`)
  }

  const data = await response.json()
  const content = data?.choices?.[0]?.message?.content?.trim()
  if (!content) throw new Error('AI 没有返回有效内容')
  return parseJsonContent(content)
}

function postQwenChat(body) {
  return fetch('/qwen/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

function shouldRetryWithoutJsonMode(status, message) {
  return (
    status === 400 &&
    /response_format|json_object|unsupported|invalid|不支持|参数/i.test(String(message || ''))
  )
}

function buildAiPrompt(rawText, candidates) {
  return `
请解析并优化这份简历。

要求：
1. 输出 JSON，格式为：
{
  "basic_info": {"name": "", "phone": "", "email": ""},
  "target_role": "",
  "highlights": ["..."],
  "patches": [
    {
      "nodeId": "候选文字节点 id",
      "label": "改动标题",
      "original": "候选节点中的原文",
      "replacement": "优化后的文字",
      "reason": "为什么修改"
    }
  ]
}
2. patches 只能使用下面候选文字节点里的 nodeId。
3. replacement 必须适合放回原位置，尽量不要比 original 长太多，尤其是姓名、电话、标题、文本框内容。
4. 不要修改图片、布局、样式、标签类文字；只优化具体内容。
5. 如果无法安全修改，patches 返回空数组。

简历纯文本：
${String(rawText || '').slice(0, 12000)}

可回写的候选文字节点：
${JSON.stringify(candidates, null, 2)}
`
}

function parseJsonContent(content) {
  try {
    return JSON.parse(content)
  } catch {
    const match = content.match(/\{[\s\S]*\}/)
    if (match) return JSON.parse(match[0])
    throw new Error('AI 返回内容不是有效 JSON')
  }
}

function normalizeParsedData(result) {
  return {
    basic_info: result?.basic_info || {},
    target_role: result?.target_role || '',
    highlights: Array.isArray(result?.highlights) ? result.highlights.slice(0, 6) : [],
  }
}

function normalizePatches(rawPatches, nodes) {
  const nodeMap = new Map(nodes.map((node) => [node.id, node]))
  return rawPatches
    .map((patch, index) => {
      const node = nodeMap.get(patch.nodeId)
      if (!node || !patch.replacement) return null
      return {
        localId: `${patch.nodeId}-${index}`,
        nodeId: patch.nodeId,
        label: patch.label || '文字优化',
        original: node.text,
        replacement: String(patch.replacement),
        reason: patch.reason || '',
        accepted: true,
      }
    })
    .filter(Boolean)
}
</script>

<style scoped>
.resume-workspace {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1fr) 420px;
}

.preview-panel,
.control-panel {
  min-width: 0;
}

.control-panel {
  max-height: 78vh;
  overflow: auto;
  padding-right: 2px;
}

.action-grid {
  display: grid;
  gap: 10px;
}

.summary-list {
  display: grid;
  gap: 8px;
}

.summary-list > div {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.summary-list span,
.section-label {
  color: #71717a;
  font-size: 12px;
}

.summary-list strong {
  color: #27272a;
  font-size: 13px;
  font-weight: 600;
  text-align: right;
}

.compact-list {
  color: #3f3f46;
  font-size: 13px;
  line-height: 1.7;
  list-style: disc;
  margin: 6px 0 0 18px;
  padding: 0;
}

.patch-list {
  display: grid;
  gap: 12px;
}

.patch-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
}

.patch-head {
  align-items: flex-start;
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.patch-title {
  min-width: 0;
}

.patch-title div {
  color: #27272a;
  font-size: 13px;
  font-weight: 600;
}

.patch-title span {
  color: #71717a;
  display: block;
  font-size: 12px;
  line-height: 1.5;
  margin-top: 2px;
}

.patch-text {
  display: grid;
  gap: 4px;
  margin-top: 8px;
}

.patch-text label {
  color: #71717a;
  font-size: 12px;
}

.original-text {
  background: #f4f4f5;
  border-radius: 6px;
  color: #3f3f46;
  font-size: 12px;
  line-height: 1.6;
  max-height: 96px;
  overflow: auto;
  padding: 8px;
  white-space: pre-wrap;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
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

.w-full :deep(.el-upload) {
  display: block;
  width: 100%;
}

.w-full :deep(.el-upload-dragger) {
  background-color: #fafafa;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 0;
  transition: all 0.3s;
  width: 100%;
}

.w-full :deep(.el-upload-dragger:hover) {
  background-color: #f5f3ff;
  border-color: #4f46e5;
}

@media (max-width: 1180px) {
  .resume-workspace {
    grid-template-columns: 1fr;
  }

  .control-panel {
    max-height: none;
  }
}
</style>
