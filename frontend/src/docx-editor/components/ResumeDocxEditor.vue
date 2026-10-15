<template>
  <div class="resume-docx-preview">
    <div class="preview-toolbar">
      <div class="preview-title">{{ props.initialTitle || 'Word 简历预览' }}</div>
      <el-button v-if="showBack" text @click="emit('cancel')">返回</el-button>
    </div>

    <div v-loading="previewLoading" class="preview-scroll">
      <div v-if="props.pdfLoading" class="preview-message">正在生成 PDF 预览...</div>
      <div v-else-if="props.pdfUrl" class="pdf-preview-frame-wrap">
        <iframe class="pdf-preview-frame" :src="props.pdfUrl" title="Word PDF 预览"></iframe>
      </div>
      <div v-else-if="props.pdfError" class="preview-warning">
        {{ props.pdfError }}，已切换为文本预览
      </div>
      <div v-if="!props.docxFile && !previewLoading && !props.pdfUrl && !props.pdfLoading" class="preview-message">未选择 Word 文件</div>
      <div v-else-if="previewError" class="preview-error">{{ previewError }}</div>
      <div v-else-if="previewLoading && !props.pdfUrl && !props.pdfLoading" class="preview-message">正在渲染 Word 预览...</div>
      <template v-if="!props.pdfUrl && !props.pdfLoading">
        <div ref="styleRef" class="preview-styles"></div>
        <div ref="previewRef" class="preview-root"></div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { renderAsync } from 'docx-preview'
import { buildPlainResumeText, extractDocxTextNodes } from '@/utils/docxTextPatch'

const props = withDefaults(
  defineProps<{
    docxFile?: Blob | File | null
    initialTitle?: string
    pdfError?: string
    pdfLoading?: boolean
    pdfUrl?: string
    showBack?: boolean
  }>(),
  {
    docxFile: null,
    initialTitle: '',
    pdfError: '',
    pdfLoading: false,
    pdfUrl: '',
    showBack: true,
  },
)

const emit = defineEmits(['cancel'])

const previewRef = ref<HTMLElement | null>(null)
const styleRef = ref<HTMLElement | null>(null)
const previewLoading = ref(false)
const previewError = ref('')

async function renderDocxPreview() {
  if (props.pdfUrl || props.pdfLoading) return
  if (!previewRef.value) return
  previewRef.value.innerHTML = ''
  if (styleRef.value) styleRef.value.innerHTML = ''
  previewError.value = ''

  if (!props.docxFile) return
  if ('name' in props.docxFile && props.docxFile.name && !/\.docx$/i.test(props.docxFile.name)) {
    previewError.value = '当前预览仅支持 .docx 文件，.doc 老格式请先另存为 .docx'
    return
  }

  previewLoading.value = true
  try {
    const arrayBuffer = await props.docxFile.arrayBuffer()
    await renderAsync(arrayBuffer, previewRef.value, styleRef.value || undefined, {
      breakPages: true,
      className: 'docx',
      experimental: true,
      ignoreLastRenderedPageBreak: false,
      ignoreFonts: false,
      inWrapper: true,
      renderEndnotes: true,
      renderFooters: true,
      renderHeaders: true,
      renderFootnotes: true,
      useBase64URL: true,
    })
    await waitForPaint()
    if (!previewRef.value.querySelector('.docx-wrapper, section.docx')) {
      previewError.value = 'Word 预览没有生成有效页面，但仍可以继续 AI 解析和导出'
      await renderTextFallback()
    } else if (getRenderedTextLength() < 30) {
      await renderTextFallback()
    }
  } catch (error) {
    console.error('docx preview failed:', error)
    await renderTextFallback()
  } finally {
    previewLoading.value = false
  }
}

onMounted(async () => {
  await nextTick()
  renderDocxPreview()
})

watch(
  () => props.docxFile,
  async () => {
    await nextTick()
    renderDocxPreview()
  },
)

watch(
  () => [props.pdfUrl, props.pdfLoading],
  async () => {
    await nextTick()
    renderDocxPreview()
  },
)

onBeforeUnmount(() => {
  if (previewRef.value) previewRef.value.innerHTML = ''
  if (styleRef.value) styleRef.value.innerHTML = ''
})

function waitForPaint() {
  return new Promise((resolve) => requestAnimationFrame(() => resolve(undefined)))
}

function getRenderedTextLength() {
  return (previewRef.value?.innerText || '').replace(/\s+/g, '').length
}

async function renderTextFallback() {
  if (!props.docxFile || !previewRef.value) return

  try {
    const nodes = await extractDocxTextNodes(props.docxFile)
    const text = buildPlainResumeText(nodes)
    if (!text.trim()) {
      previewError.value = 'Word 预览失败，请确认文件是有效的 .docx 格式'
      return
    }

    previewError.value = ''
    previewRef.value.innerHTML = ''
    const wrapper = document.createElement('div')
    wrapper.className = 'fallback-wrapper'
    const page = document.createElement('section')
    page.className = 'fallback-page'

    text
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .forEach((line) => {
        const paragraph = document.createElement('p')
        paragraph.textContent = line
        if (isLikelyHeading(line)) paragraph.className = 'fallback-heading'
        page.appendChild(paragraph)
      })

    wrapper.appendChild(page)
    previewRef.value.appendChild(wrapper)
  } catch (fallbackError) {
    console.error('docx text fallback failed:', fallbackError)
    previewError.value = 'Word 预览失败，请确认文件是有效的 .docx 格式'
  }
}

function isLikelyHeading(text: string) {
  return (
    text.length <= 18 &&
    /^(个人信息|教育经历|校园经历|项目经历|实习经历|工作经历|专业技能|技能证书|荣誉奖项|自我评价|求职意向|证书|项目|技能)/.test(
      text,
    )
  )
}
</script>

<style scoped>
.resume-docx-preview {
  background: #f3f3f2;
  border: 1px solid #e5e7eb;
  min-height: 560px;
}

.preview-toolbar {
  align-items: center;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-sizing: border-box;
  display: flex;
  justify-content: space-between;
  min-height: 48px;
  padding: 8px 16px;
}

.preview-title {
  color: #1f2937;
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-scroll {
  box-sizing: border-box;
  min-height: 560px;
  overflow: visible;
  padding: 24px 16px;
  width: 100%;
}

.preview-root {
  min-height: 100%;
}

.preview-styles {
  display: none;
}

.preview-error {
  color: #b91c1c;
  font-size: 14px;
  margin: 32px auto;
  max-width: 640px;
  text-align: center;
}

.preview-message {
  color: #6b7280;
  font-size: 14px;
  margin: 32px auto;
  max-width: 640px;
  text-align: center;
}

.preview-warning {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  color: #9a3412;
  font-size: 13px;
  line-height: 1.6;
  margin: 0 auto 16px;
  max-width: 794px;
  padding: 10px 12px;
}

.pdf-preview-frame-wrap {
  align-items: flex-start;
  background: transparent;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  padding: 0;
  width: 100%;
}

.pdf-preview-frame {
  background: #ffffff;
  border: 0;
  display: block;
  height: min(1122px, calc(100vh - 180px));
  min-height: 760px;
  width: min(794px, 100%);
}

:deep(.docx-wrapper) {
  background: #d4d4d8;
  min-height: 100%;
  padding: 24px 0;
}

:deep(.docx-wrapper > section.docx) {
  flex: 0 0 auto;
  overflow: visible;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
  margin: 0 auto 24px;
}

:deep(.docx-wrapper > section.docx > article) {
  position: relative;
}

:deep(.docx-wrapper svg),
:deep(.docx-wrapper foreignObject) {
  overflow: visible;
}

:deep(.docx-wrapper img) {
  max-width: none;
}

:deep(.fallback-wrapper) {
  align-items: flex-start;
  background: #d4d4d8;
  display: flex;
  justify-content: center;
  min-height: 100%;
  padding: 24px 0;
}

:deep(.fallback-page) {
  background: #ffffff;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
  box-sizing: border-box;
  color: #111827;
  font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
  font-size: 12px;
  line-height: 1.75;
  min-height: 1122px;
  padding: 54px 60px;
  width: 794px;
}

:deep(.fallback-page p) {
  margin: 0 0 8px;
  white-space: pre-wrap;
}

:deep(.fallback-heading) {
  border-bottom: 1px solid #d4d4d8;
  font-size: 15px;
  font-weight: 700;
  margin-top: 18px;
  padding-bottom: 4px;
}
</style>
