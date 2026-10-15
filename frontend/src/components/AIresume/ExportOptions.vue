<template>
  <div
    class="w-full p-6 bg-white dark:bg-zinc-800 rounded-2xl border border-zinc-100 dark:border-zinc-700/70 transition-all duration-300"
  >
    <div class="flex items-center gap-3 mb-5">
      <Icon icon="lucide:download" class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
      <h3 class="text-base font-semibold text-zinc-800 dark:text-zinc-100">高保真多端导出</h3>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
      <div
        v-for="option in exportOptions"
        :key="option.id"
        class="group relative p-5 border-2 rounded-xl cursor-pointer transition-all duration-300 bg-zinc-50/50 dark:bg-zinc-900/30 flex gap-4 hover:border-indigo-300 dark:hover:border-indigo-800"
        :class="[
          selectedFormat === option.id
            ? 'border-indigo-600 bg-indigo-50/10 dark:bg-indigo-950/10'
            : 'border-zinc-100 dark:border-zinc-700/50',
        ]"
        @click="selectFormat(option.id)"
      >
        <div
          class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
          :class="[option.bgClass]"
        >
          <Icon :icon="option.icon" class="w-6 h-6 text-white" />
        </div>
        <div>
          <h4 class="text-sm font-bold text-zinc-800 dark:text-zinc-100 mb-0.5">
            {{ option.name }}
          </h4>
          <p class="text-xs text-zinc-400 dark:text-zinc-500 leading-normal">
            {{ option.description }}
          </p>
        </div>
        <div
          v-if="selectedFormat === option.id"
          class="absolute top-4 right-4 text-indigo-600 dark:text-indigo-400"
        >
          <Icon icon="lucide:check-circle" class="w-4 h-4" />
        </div>
      </div>
    </div>

    <div class="flex justify-center">
      <el-button
        type="primary"
        size="large"
        :loading="isExporting"
        :disabled="!selectedFormat"
        class="w-full max-w-[320px] !h-12 !font-semibold !rounded-xl !border-none shadow-md"
        :class="[
          '!bg-gradient-to-r !from-indigo-600 !to-violet-600 hover:!from-indigo-700 hover:!to-violet-700 !text-white shadow-indigo-100 dark:shadow-none',
        ]"
        @click="handleExport"
      >
        <template v-if="!isExporting">
          <div class="flex items-center justify-center gap-2">
            <Icon icon="lucide:download" class="w-4 h-4" />
            <span>打包导出为 {{ selectedFormatName }}</span>
          </div>
        </template>
        <template v-else>正在进行排版转换...</template>
      </el-button>
    </div>

    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform opacity-0 -translate-y-2"
      leave-active-class="transition duration-200 ease-in"
      leave-to-class="transform opacity-0 -translate-y-2"
    >
      <div
        v-if="exportSuccess"
        class="flex items-center gap-3 p-4 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/30 rounded-xl mt-4"
      >
        <Icon icon="lucide:circle-check" class="w-5 h-5 text-emerald-500" />
        <div>
          <h4 class="text-xs font-bold text-emerald-800 dark:text-emerald-400">打包成功</h4>
          <p class="text-[11px] text-emerald-700 dark:text-emerald-500/80">
            已触发本地静默安全下载，请注意浏览器弹窗。
          </p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import html2pdf from 'html2pdf.js'

const props = defineProps({
  resumeElement: { type: Object, default: null },
  fileName: { type: String, default: '简历' },
})

const emit = defineEmits(['export'])

const selectedFormat = ref('pdf')
const isExporting = ref(false)
const exportSuccess = ref(false)

const exportOptions = [
  {
    id: 'pdf',
    name: '标准 A4 PDF 格式',
    description: '跨平台不格式错乱，完美解析，适配网络投递、网申系统。',
    icon: 'lucide:file-text',
    bgClass: 'bg-gradient-to-br from-rose-500 to-red-600',
  },
  {
    id: 'word',
    name: '可编辑 Word 格式',
    description: '全文本流原生排版，支持离线二次精准调整和细化。',
    icon: 'lucide:file-code',
    bgClass: 'bg-gradient-to-br from-blue-500 to-indigo-600',
  },
]

const selectedFormatName = computed(() => {
  const option = exportOptions.find((opt) => opt.id === selectedFormat.value)
  return option ? option.name.split(' ')[1] : ''
})

const selectFormat = (formatId) => {
  selectedFormat.value = formatId
}

const handleExport = async () => {
  if (!props.resumeElement || !selectedFormat.value) return

  isExporting.value = true
  exportSuccess.value = false

  try {
    await new Promise((resolve) => setTimeout(resolve, 1200))
    if (selectedFormat.value === 'pdf') {
      await exportToPDF()
    } else if (selectedFormat.value === 'word') {
      await exportToWord()
    }
    exportSuccess.value = true
    emit('export', selectedFormat.value)
    setTimeout(() => {
      exportSuccess.value = false
    }, 4000)
  } catch (error) {
    console.error('导出崩溃:', error)
    alert('导出发生阻碍，请检查浏览器配置后重试')
  } finally {
    isExporting.value = false
  }
}

const exportToPDF = async () => {
  const opt = {
    margin: [12, 12, 12, 12],
    filename: `${props.fileName}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2.5, useCORS: true, letterRendering: true },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
  }
  await html2pdf().set(opt).from(props.resumeElement).save()
}

const exportToWord = async () => {
  const htmlContent = props.resumeElement.outerHTML
  const fullHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>${props.fileName}</title>
      <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 30px; line-height: 1.6; }
        h1 { font-size: 24px; color: #18181b; font-weight: bold; margin-bottom: 6px; text-align: center; }
        p { font-size: 13px; color: #4b5563; }
        h2 { font-size: 15px; color: #4f46e5; border-bottom: 2px solid #e0e7ff; padding-bottom: 6px; margin-top: 24px; font-weight: bold; }
      </style>
    </head>
    <body>${htmlContent}</body>
    </html>
  `
  const blob = new Blob(['\ufeff', fullHtml], { type: 'application/msword' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.fileName}.doc`
  link.click()
  URL.revokeObjectURL(url)
}
</script>
