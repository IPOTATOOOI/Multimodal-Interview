<template>
  <div class="resume-preview-container">
    <div class="preview-header">
      <div class="header-left">
        <el-button @click="handleBack" text>
          <Icon icon="lucide:arrow-left" class="w-4 h-4 mr-1" />
          返回编辑
        </el-button>
        <div class="header-title">
          <Icon icon="lucide:eye" class="w-5 h-5 text-indigo-600 mr-2" />
          <span>简历预览</span>
        </div>
      </div>
    </div>

    <div class="preview-content">
      <div class="preview-wrapper">
        <div ref="resumePreviewRef" class="resume-paper">
          <div v-html="resumeHTML" />
        </div>
      </div>
    </div>

    <div class="preview-footer">
      <div class="footer-info">
        <Icon icon="lucide:info" class="w-4 h-4 text-zinc-400 mr-1" />
        <span>预览模式下可查看最终效果</span>
      </div>
      <div class="footer-actions">
        <el-button
          v-if="props.isManualMode"
          type="warning"
          @click="handleAIRefine"
          :loading="isRefining"
        >
          <Icon icon="lucide:sparkles" class="w-4 h-4 mr-1" />
          {{ isRefining ? '生成建议中...' : '简历内容润色' }}
        </el-button>
        <el-button type="primary" @click="showExportDialog = true">
          <Icon icon="lucide:download" class="w-4 h-4 mr-1" />
          导出简历
        </el-button>
      </div>
    </div>

    <el-dialog v-model="showExportDialog" title="导出简历" width="500px">
      <div class="export-options">
        <div
          v-for="option in exportOptions"
          :key="option.id"
          :class="['export-option', { active: selectedExportFormat === option.id }]"
          @click="selectedExportFormat = option.id"
        >
          <div class="option-icon" :style="{ background: option.color }">
            <Icon :icon="option.icon" class="w-6 h-6 text-white" />
          </div>
          <div class="option-content">
            <h4>{{ option.name }}</h4>
            <p>{{ option.description }}</p>
          </div>
          <Icon
            v-if="selectedExportFormat === option.id"
            icon="lucide:check-circle"
            class="w-5 h-5 text-green-500"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" :loading="isExporting" @click="handleExport">
          立即导出
        </el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="showPolishDrawer" title="简历内容润色" size="460px" append-to-body>
      <div class="polish-panel">
        <div class="polish-actions">
          <el-button type="primary" :loading="isRefining" @click="handleAIRefine">
            <Icon icon="lucide:refresh-cw" class="w-4 h-4 mr-1" />
            重新生成建议
          </el-button>
          <el-button :disabled="!acceptedPolishCount" @click="applyPolishSuggestions">
            <Icon icon="lucide:check" class="w-4 h-4 mr-1" />
            应用已选建议
          </el-button>
        </div>

        <div class="polish-tip">
          当前会调用大模型生成润色建议；应用前可逐条确认和编辑，避免事实被误改。
        </div>

        <el-empty
          v-if="!polishSuggestions.length"
          description="暂无可润色的内容，填写经历描述后可生成建议"
        />

        <div v-else class="polish-list">
          <div v-for="suggestion in polishSuggestions" :key="suggestion.id" class="polish-item">
            <div class="polish-head">
              <el-checkbox v-model="suggestion.accepted" />
              <div class="polish-title">
                <div>{{ suggestion.label }}</div>
                <span>{{ suggestion.reason }}</span>
              </div>
            </div>

            <div class="polish-text">
              <label>原文</label>
              <div class="original-text">{{ suggestion.original }}</div>
            </div>

            <div class="polish-text">
              <label>润色后</label>
              <el-input
                v-model="suggestion.replacement"
                type="textarea"
                :rows="4"
                resize="none"
                :disabled="!suggestion.accepted"
              />
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { ElMessage } from 'element-plus'
import html2pdf from 'html2pdf.js'

const props = defineProps({
  resumeData: {
    type: Object,
    default: () => ({}),
  },
  isManualMode: {
    type: Boolean,
    default: false,
  },
  isUploadMode: {
    type: Boolean,
    default: false,
  },
  entryMethod: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['back', 'updateResume'])

const resumeHTML = ref('')
const resumePreviewRef = ref(null)
const isRefining = ref(false)
const showExportDialog = ref(false)
const showPolishDrawer = ref(false)
const selectedExportFormat = ref('pdf')
const isExporting = ref(false)
const polishSuggestions = ref([])
const QWEN_MODEL = typeof __QWEN_MODEL__ !== 'undefined' ? __QWEN_MODEL__ : 'qwen-plus'

const cloneResumeData = (data) => JSON.parse(JSON.stringify(data || {}))
const localResumeData = ref(cloneResumeData(props.resumeData))
const acceptedPolishCount = computed(
  () =>
    polishSuggestions.value.filter(
      (suggestion) => suggestion.accepted && suggestion.replacement?.trim(),
    ).length,
)

const exportOptions = [
  {
    id: 'pdf',
    name: 'PDF 格式',
    description: '通用格式，排版稳定，适合在线投递',
    icon: 'lucide:file-text',
    color: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
  },
  {
    id: 'word',
    name: 'Word 格式',
    description: '可编辑格式，方便后续微调',
    icon: 'lucide:file-code',
    color: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
  },
]

const sectionIcons = {
  profile:
    '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"></circle><path d="M5 21c1.5-4 12.5-4 14 0"></path></svg>',
  target:
    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"></circle><circle cx="12" cy="12" r="4"></circle><path d="M12 3v3M12 18v3M3 12h3M18 12h3"></path></svg>',
  education:
    '<svg viewBox="0 0 24 24"><path d="M22 10 12 5 2 10l10 5 10-5Z"></path><path d="M6 12v5c3 2 9 2 12 0v-5"></path></svg>',
  work:
    '<svg viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="13" rx="2"></rect><path d="M8 7V5c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><path d="M3 13h18"></path></svg>',
  project:
    '<svg viewBox="0 0 24 24"><path d="M4 7h6l2 2h8v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7Z"></path><path d="M8 14h8"></path></svg>',
  skills:
    '<svg viewBox="0 0 24 24"><path d="m14.7 6.3 3 3"></path><path d="m8.5 18.5 9.9-9.9a2.1 2.1 0 0 0-3-3l-9.9 9.9L4 20l4.5-1.5Z"></path></svg>',
  certificate:
    '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="5"></circle><path d="m8.5 12.5-1.5 8 5-3 5 3-1.5-8"></path></svg>',
  activity:
    '<svg viewBox="0 0 24 24"><path d="M8 6h13"></path><path d="M8 12h13"></path><path d="M8 18h13"></path><path d="M3 6h.01"></path><path d="M3 12h.01"></path><path d="M3 18h.01"></path></svg>',
}

const sectionTitle = (title, icon) => `
  <h2 class="section-title">
    <span class="section-icon">${sectionIcons[icon] || ''}</span>
    <span>${title}</span>
  </h2>
`

const detailItem = (label, value) =>
  value ? `<span class="detail-item"><span class="detail-label">${label}：</span>${value}</span>` : ''

const joinDetailItems = (items) => items.filter(Boolean).join('<span class="detail-separator">|</span>')

const dateRange = (item, periodKey) => {
  if (item?.[periodKey]) return item[periodKey]
  if (item?.start_date || item?.end_date) return `${item.start_date || ''}${item.end_date ? ` - ${item.end_date}` : ''}`
  return ''
}

const generateResumeHTML = () => {
  const data = localResumeData.value
  const photoHtml = data.basic_info?.photo
    ? `<img class="resume-photo" src="${data.basic_info.photo}" alt="个人照片" />`
    : ''

  // 拼接联系方式
  const contactItems = []
  if (data.basic_info?.phone) contactItems.push(detailItem('手机', data.basic_info.phone))
  if (data.basic_info?.email) contactItems.push(detailItem('邮箱', data.basic_info.email))
  const contactHtml =
    contactItems.length > 0 ? contactItems.join('<span class="contact-separator">|</span>') : ''
  const intentItems = []
  if (data.job_intention?.job_title) intentItems.push(detailItem('目标岗位', data.job_intention.job_title))
  if (data.job_intention?.location1) intentItems.push(detailItem('期望城市', data.job_intention.location1))
  const intentHtml =
    intentItems.length > 0 ? intentItems.join('<span class="contact-separator">|</span>') : ''

  return `
    <div class="resume-document">
      ${photoHtml}
      <div class="resume-header ${photoHtml ? 'has-photo' : ''}">
        <h1 class="resume-name">
          <span class="name-icon">${sectionIcons.profile}</span>
          <span>${data.basic_info?.name || '您的姓名'}</span>
        </h1>
        <div class="resume-contact">
          ${contactHtml}
        </div>
        ${
          intentHtml
            ? `
        <div class="resume-contact resume-intention">
          ${intentHtml}
        </div>
        `
            : ''
        }
      </div>

      ${
        data.education?.length
          ? `
        <div class="resume-section">
          ${sectionTitle('教育背景', 'education')}
          ${data.education
            .map(
              (edu) => `
            <div class="section-item">
              <div class="item-header">
                <strong class="item-title">${edu.school || ''}</strong>
                <span class="item-date">${dateRange(edu, 'study_period')}</span>
              </div>
              <div class="item-subtitle">
                ${joinDetailItems([
                  detailItem('专业', edu.major),
                  detailItem('学历', edu.degree),
                ])}
              </div>
              ${edu.description ? `<div class="item-content">${edu.description}</div>` : ''}
            </div>
          `,
            )
            .join('')}
        </div>
      `
          : ''
      }

      ${
        data.work_experience?.length
          ? `
        <div class="resume-section">
          ${sectionTitle('工作经历', 'work')}
          ${data.work_experience
            .map(
              (work) => `
            <div class="section-item">
              <div class="item-header">
                <strong class="item-title">${work.company_name || ''}</strong>
                <span class="item-date">${dateRange(work, 'work_period')}</span>
              </div>
              <div class="item-subtitle">
                ${joinDetailItems([
                  detailItem('职位', work.position),
                  detailItem('城市', work.city),
                ])}
              </div>
              ${work.description ? `<div class="item-content">${work.description}</div>` : ''}
            </div>
          `,
            )
            .join('')}
        </div>
      `
          : ''
      }

      ${
        data.project_experience?.length
          ? `
        <div class="resume-section">
          ${sectionTitle('项目经验', 'project')}
          ${data.project_experience
            .map(
              (project) => `
            <div class="section-item">
              <div class="item-header">
                <strong class="item-title">${project.name || ''}</strong>
                <span class="item-date">${dateRange(project, 'project_period')}</span>
              </div>
              ${
                project.role
                  ? `<div class="item-subtitle">${detailItem('担任角色', project.role)}</div>`
                  : ''
              }
              ${project.description ? `<div class="item-content">${project.description}</div>` : ''}
            </div>
          `,
            )
            .join('')}
        </div>
      `
          : ''
      }

      ${
        data.skills?.length
          ? `
        <div class="resume-section">
          ${sectionTitle('专业技能', 'skills')}
          <ul class="skill-tags">
            ${data.skills
              .map(
                (skill) => `
                  <li>
                    <span>${skill.content || ''}</span>
                    ${
                      skill.level
                        ? `<span class="inline-detail">${detailItem('熟练度', skill.level)}</span>`
                        : ''
                    }
                  </li>
                `,
              )
              .join('')}
          </ul>
        </div>
      `
          : ''
      }

      ${
        data.campus_experience_text || data.competition_experience_text
          ? `
        <div class="resume-section">
          ${sectionTitle('其他经历', 'activity')}
          ${
            data.campus_experience_text
              ? `
            <div class="section-item">
              <div class="item-header">
                <strong class="item-title">校园经历</strong>
              </div>
              <div class="item-content">${data.campus_experience_text}</div>
            </div>
          `
              : ''
          }
          ${
            data.competition_experience_text
              ? `
            <div class="section-item">
              <div class="item-header">
                <strong class="item-title">竞赛经历</strong>
              </div>
              <div class="item-content">${data.competition_experience_text}</div>
            </div>
          `
              : ''
          }
        </div>
      `
          : ''
      }

      ${
        data.certificates?.length
          ? `
        <div class="resume-section">
          ${sectionTitle('荣誉证书', 'certificate')}
          <ul class="skills-list">
            ${data.certificates
              .map(
                (cert) =>
                  `<li>
                    <span>${cert.name || ''}</span>
                    <span class="inline-detail">
                      ${joinDetailItems([
                        detailItem('获得时间', cert.obtain_time),
                        detailItem('颁发机构', cert.issuer),
                      ])}
                    </span>
                  </li>`,
              )
              .join('')}
          </ul>
        </div>
      `
          : ''
      }
    </div>

    <style>
      /* 简历内部专用极简专业样式 */
      .resume-document {
        font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
        color: #222; /* 使用深灰替代纯黑，阅读更舒适 */
        line-height: 1.5;
        padding: 40px;
        background-color: #fff;
        text-align: left;
        position: relative;
      }

      .resume-header {
        text-align: center;
        margin-bottom: 24px;
      }

      .resume-header.has-photo {
        min-height: 116px;
        padding-right: 116px;
      }

      .resume-photo {
        position: absolute;
        top: 40px;
        right: 40px;
        width: 88px;
        height: 112px;
        object-fit: cover;
        border: 1px solid #d4d4d8;
        border-radius: 4px;
        background: #fff;
      }

      .resume-name {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        font-size: 26px;
        font-weight: bold;
        color: #111;
        margin: 0 0 10px 0;
        letter-spacing: 2px;
      }

      .name-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        color: #2563eb;
        letter-spacing: 0;
      }

      .name-icon svg {
        width: 22px;
        height: 22px;
        stroke: currentColor;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
        fill: none;
      }

      .resume-contact {
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 13px;
        color: #555;
      }

      .resume-intention {
        margin-top: 6px;
      }

      .contact-separator {
        margin: 0 12px;
        color: #ccc;
      }

      .detail-item {
        display: inline;
      }

      .detail-label {
        color: #8a8a8a;
        font-size: 12px;
        font-weight: 500;
      }

      .detail-separator {
        color: #d4d4d8;
        margin: 0 10px;
      }

      .inline-detail {
        color: #555;
        margin-left: 10px;
      }

      .resume-section {
        margin-bottom: 24px;
      }

      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: bold;
        color: #222;
        margin: 0 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #333; /* 经典的黑色实线下划线 */
      }

      .section-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        color: #2563eb;
        flex: 0 0 auto;
      }

      .section-icon svg {
        width: 18px;
        height: 18px;
        stroke: currentColor;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
        fill: none;
      }

      .section-content {
        font-size: 14px;
        color: #333;
      }

      .section-item {
        margin-bottom: 16px;
      }

      .section-item:last-child {
        margin-bottom: 0;
      }

      .item-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 4px;
      }

      .item-title {
        font-size: 15px;
        font-weight: bold;
        color: #222;
      }

      .item-date {
        font-size: 13px;
        color: #666;
        font-family: Arial, sans-serif;
      }

      .item-subtitle {
        font-size: 14px;
        font-weight: bold;
        color: #444;
        margin-bottom: 6px;
      }

      .item-content {
        font-size: 13px;
        color: #444;
        line-height: 1.6;
        white-space: pre-line;
        text-align: justify;
      }

      .skills-list {
        list-style-type: disc;
        padding-left: 20px;
        margin: 0;
        font-size: 13px;
        color: #444;
        line-height: 1.8;
      }
      
      .skills-list li {
        margin-bottom: 4px;
      }

      .skill-tags {
        list-style: none;
        margin: 0;
        padding: 0;
      }

      .skill-tags {
        display: grid;
        gap: 8px;
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .skill-tags li {
        background: #fafafa;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        color: #1f2937;
        font-size: 13px;
        line-height: 1.6;
        padding: 8px 10px;
      }

        align-items: center;
        display: flex;
        justify-content: space-between;
        gap: 8px;
      }

      .skill-tags .inline-detail {
        border-radius: 999px;
        color: #555;
        margin-left: 0;
        white-space: nowrap;
      }
    </style>
  `
}

onMounted(() => {
  resumeHTML.value = generateResumeHTML()
})

watch(
  () => props.resumeData,
  (newData) => {
    localResumeData.value = cloneResumeData(newData)
    resumeHTML.value = generateResumeHTML()
  },
  { deep: true },
)

const handleBack = () => {
  emit('back')
}

const createPolishSuggestion = ({ label, path, original, replacement, reason }) => {
  if (!original || !replacement || original.trim() === replacement.trim()) return null

  return {
    id: `${path.join('.')}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    label,
    path,
    original,
    replacement,
    reason,
    accepted: true,
  }
}

const splitTextLines = (text) => {
  if (!text) return []
  if (text.includes('\n')) return text.split('\n')

  const matched = text.match(/[^。；;]+[。；;]?/g)
  return matched?.length > 1 ? matched : [text]
}

const ensureEndingPunctuation = (text) => {
  const trimmed = text.trim()
  if (!trimmed) return ''
  return /[。；;，,、.!?？]$/.test(trimmed) ? trimmed : `${trimmed}。`
}

const polishLongText = (text) => {
  const lines = splitTextLines(String(text || '').replace(/\r/g, '').trim())
    .map((line) => ensureEndingPunctuation(line.replace(/\s+/g, ' ')))
    .filter(Boolean)

  return lines.join('\n')
}

const buildPolishSuggestions = (data) => {
  const suggestions = []

  data.education?.forEach((edu, index) => {
    suggestions.push(
      createPolishSuggestion({
        label: `教育经历 #${index + 1}`,
        path: ['education', index, 'description'],
        original: edu.description,
        replacement: polishLongText(edu.description),
        reason: '统一描述标点和换行，让教育成果更易阅读',
      }),
    )
  })

  data.work_experience?.forEach((work, index) => {
    suggestions.push(
      createPolishSuggestion({
        label: `工作经历 #${index + 1}`,
        path: ['work_experience', index, 'description'],
        original: work.description,
        replacement: polishLongText(work.description),
        reason: '将职责内容整理为更清晰的分行表达',
      }),
    )
  })

  data.project_experience?.forEach((project, index) => {
    suggestions.push(
      createPolishSuggestion({
        label: `项目经验 #${index + 1}`,
        path: ['project_experience', index, 'description'],
        original: project.description,
        replacement: polishLongText(project.description),
        reason: '统一项目描述结构，突出贡献与结果',
      }),
    )
  })

  return suggestions.filter(Boolean)
}

async function requestAiPolishSuggestions(data) {
  const candidates = buildPolishCandidates(data)
  if (!candidates.length) return []

  const body = {
    model: QWEN_MODEL,
    temperature: 0.25,
    messages: [
      {
        role: 'system',
        content:
          '你是专业中文简历润色助手。你必须只输出 JSON，不要输出 Markdown。你的任务是基于候选字段给出可直接替换原字段的简历文字润色建议。',
      },
      {
        role: 'user',
        content: buildAiPolishPrompt(candidates),
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

  const result = await response.json()
  const content = result?.choices?.[0]?.message?.content?.trim()
  if (!content) throw new Error('AI 没有返回有效内容')

  return normalizeAiPolishSuggestions(parseJsonContent(content), candidates)
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

function parseJsonContent(content) {
  try {
    return JSON.parse(content)
  } catch {
    const match = content.match(/\{[\s\S]*\}/)
    if (match) return JSON.parse(match[0])
    throw new Error('AI 返回内容不是有效 JSON')
  }
}

function buildPolishCandidates(data) {
  const candidates = []
  const pushCandidate = ({ id, label, path, original }) => {
    const text = String(original || '').trim()
    if (text.length < 8) return
    candidates.push({ id, label, path, original: text })
  }

  data.education?.forEach((edu, index) => {
    pushCandidate({
      id: `education-${index}-description`,
      label: `教育经历 #${index + 1}`,
      path: ['education', index, 'description'],
      original: edu.description,
    })
  })

  data.work_experience?.forEach((work, index) => {
    pushCandidate({
      id: `work-${index}-description`,
      label: `工作经历 #${index + 1}`,
      path: ['work_experience', index, 'description'],
      original: work.description,
    })
  })

  data.project_experience?.forEach((project, index) => {
    pushCandidate({
      id: `project-${index}-description`,
      label: `项目经验 #${index + 1}`,
      path: ['project_experience', index, 'description'],
      original: project.description,
    })
  })

  return candidates
}

function buildAiPolishPrompt(candidates) {
  return `
请润色下面这些简历字段，输出 JSON。

输出格式：
{
  "suggestions": [
    {
      "id": "候选字段 id",
      "replacement": "润色后的内容",
      "reason": "简短说明为什么这样改"
    }
  ]
}

要求：
1. 只能改写候选字段里的具体内容，不要新增不存在的经历、公司、学校、奖项或数据。
2. 保留原文事实，不要夸大，不要虚构量化成果。
3. 语言要适合中文简历，精炼、专业、动词明确。
4. 可以把长段整理为多行，每行一个要点；不要使用 Markdown 符号。
5. replacement 必须能直接替换原字段。
6. 如果某字段已经足够好，可以不返回该字段建议。

候选字段：
${JSON.stringify(candidates.map(({ id, label, original }) => ({ id, label, original })), null, 2)}
`
}

function normalizeAiPolishSuggestions(result, candidates) {
  const candidateMap = new Map(candidates.map((candidate) => [candidate.id, candidate]))
  const rawSuggestions = Array.isArray(result?.suggestions) ? result.suggestions : []

  return rawSuggestions
    .map((item) => {
      const candidate = candidateMap.get(item?.id)
      if (!candidate || !item?.replacement) return null
      return createPolishSuggestion({
        label: candidate.label,
        path: candidate.path,
        original: candidate.original,
        replacement: String(item.replacement),
        reason: item.reason || '大模型根据简历表达进行了专业润色',
      })
    })
    .filter(Boolean)
}

const setValueByPath = (target, path, value) => {
  let cursor = target
  for (let index = 0; index < path.length - 1; index += 1) {
    cursor = cursor?.[path[index]]
    if (!cursor) return
  }
  cursor[path[path.length - 1]] = value
}

const handleAIRefine = async () => {
  isRefining.value = true
  try {
    polishSuggestions.value = await requestAiPolishSuggestions(localResumeData.value)
    showPolishDrawer.value = true

    if (!polishSuggestions.value.length) {
      ElMessage.info('大模型未生成可应用的润色建议')
    }
  } catch (error) {
    console.error('AI polish failed:', error)
    ElMessage.error(error?.message || '大模型润色失败，请稍后重试')
    showPolishDrawer.value = true
  } finally {
    isRefining.value = false
  }
}

const applyPolishSuggestions = () => {
  const nextData = cloneResumeData(localResumeData.value)
  polishSuggestions.value
    .filter((suggestion) => suggestion.accepted && suggestion.replacement?.trim())
    .forEach((suggestion) => {
      setValueByPath(nextData, suggestion.path, suggestion.replacement.trim())
    })

  localResumeData.value = nextData
  resumeHTML.value = generateResumeHTML()
  emit('updateResume', nextData)
  showPolishDrawer.value = false
  ElMessage.success(`已应用 ${acceptedPolishCount.value} 条润色建议`)
}

const handleExport = async () => {
  if (!selectedExportFormat.value) return

  isExporting.value = true

  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))

    if (selectedExportFormat.value === 'pdf') {
      await exportToPDF()
    } else if (selectedExportFormat.value === 'word') {
      await exportToWord()
    }

    showExportDialog.value = false
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请重试')
  } finally {
    isExporting.value = false
  }
}

const exportToPDF = async () => {
  const element = resumePreviewRef.value

  const originalOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'

  const opt = {
    margin: [5, 5, 5, 5],
    filename: `${localResumeData.value.basic_info?.name || '简历'}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      letterRendering: true,
      logging: false,
      backgroundColor: '#ffffff',
      scrollX: 0,
      scrollY: 0,
      windowWidth: element.offsetWidth,
      windowHeight: element.offsetHeight,
    },
    jsPDF: {
      unit: 'mm',
      format: 'a4',
      orientation: 'portrait',
    },
  }

  try {
    await html2pdf().set(opt).from(element).save()
  } finally {
    document.body.style.overflow = originalOverflow
  }
}

const exportToWord = async () => {
  // Word 导出模板同样使用新的极简样式
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>${localResumeData.value.basic_info?.name || '简历'}</title>
      <style>
        body { font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 20px; color: #222; }
        .resume-document { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; font-size: 26px; margin-bottom: 10px; color: #111; letter-spacing: 2px; }
        .resume-contact { text-align: center; font-size: 13px; color: #555; margin-bottom: 24px; }
        .contact-separator { margin: 0 12px; color: #ccc; }
        h2.section-title { font-size: 16px; font-weight: bold; color: #222; border-bottom: 1px solid #333; padding-bottom: 6px; margin-top: 24px; margin-bottom: 16px; }
        .item-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }
        .item-title { font-size: 15px; font-weight: bold; color: #222; }
        .item-date { font-size: 13px; color: #666; }
        .item-subtitle { font-size: 14px; font-weight: bold; color: #444; margin-bottom: 6px; }
        .item-content { font-size: 13px; line-height: 1.6; color: #444; text-align: justify; }
        ul { margin: 0; padding-left: 20px; font-size: 13px; line-height: 1.8; color: #444; }
      </style>
    </head>
    <body>${resumeHTML.value}</body>
    </html>
  `

  const blob = new Blob(['\ufeff', htmlContent], { type: 'application/msword' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${localResumeData.value.basic_info?.name || '简历'}.doc`
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.resume-preview-container {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  border-radius: 12px 12px 0 0;
}

.dark .preview-header {
  background: #27272a;
  border-color: #3f3f46;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.dark .header-title {
  color: #f9fafb;
}

.preview-content {
  overflow: visible;
  background: #f3f4f6;
}

.dark .preview-content {
  background: #18181b;
}

.editor-wrapper {
  background: white;
  padding: 20px;
}

.dark .editor-wrapper {
  background: #27272a;
}

.preview-wrapper {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  background: transparent;
}

.resume-paper {
  background: white;
  width: 800px;
  min-height: 1131px; /* 约等于A4比例 */
  padding: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 4px; /* 降低圆角让其更像A4纸 */
  overflow: visible;
}

.dark .resume-paper {
  /* 简历纸张即便在暗黑模式下也保持白色底和黑色字，保证导出的视觉一致性 */
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.preview-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e5e7eb;
  border-radius: 0 0 12px 12px;
}

.dark .preview-footer {
  background: #27272a;
  border-color: #3f3f46;
}

.footer-info {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #6b7280;
}

.dark .footer-info {
  color: #9ca3af;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

.polish-panel {
  display: grid;
  gap: 16px;
}

.polish-actions {
  display: flex;
  gap: 10px;
}

.polish-tip {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #71717a;
  font-size: 12px;
  line-height: 1.6;
  padding: 10px 12px;
}

.polish-list {
  display: grid;
  gap: 12px;
}

.polish-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
}

.polish-head {
  align-items: flex-start;
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.polish-title {
  min-width: 0;
}

.polish-title div {
  color: #27272a;
  font-size: 13px;
  font-weight: 600;
}

.polish-title span {
  color: #71717a;
  display: block;
  font-size: 12px;
  line-height: 1.5;
  margin-top: 2px;
}

.polish-text {
  display: grid;
  gap: 4px;
  margin-top: 8px;
}

.polish-text label {
  color: #71717a;
  font-size: 12px;
}

.original-text {
  background: #f4f4f5;
  border-radius: 6px;
  color: #3f3f46;
  font-size: 12px;
  line-height: 1.6;
  max-height: 120px;
  overflow: auto;
  padding: 8px;
  white-space: pre-wrap;
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.export-option {
  position: relative;
  padding: 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  gap: 16px;
  transition: all 0.3s ease;
}

.dark .export-option {
  border-color: #3f3f46;
}

.export-option:hover {
  border-color: #667eea;
  background: #f9fafb;
}

.dark .export-option:hover {
  background: #18181b;
}

.export-option.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
}

.option-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.option-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.dark .option-content h4 {
  color: #f9fafb;
}

.option-content p {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

.dark .option-content p {
  color: #9ca3af;
}

:deep(.ql-editor) {
  font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
}

:deep(.ql-toolbar) {
  border-radius: 8px 8px 0 0;
}

:deep(.ql-container) {
  border-radius: 0 0 8px 8px;
}
</style>
