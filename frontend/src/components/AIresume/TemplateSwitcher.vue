<template>
  <div
    class="w-full p-6 bg-white dark:bg-zinc-800 rounded-2xl border border-zinc-100 dark:border-zinc-700/70 mb-6 transition-all duration-300"
  >
    <div class="flex items-center gap-3 mb-5">
      <Icon icon="lucide:layout-template" class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
      <h3 class="text-base font-semibold text-zinc-800 dark:text-zinc-100">选择简历显示模板</h3>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
      <div
        v-for="template in templates"
        :key="template.id"
        class="group relative cursor-pointer border-2 rounded-xl overflow-hidden transition-all duration-300 bg-zinc-50 dark:bg-zinc-900/40"
        :class="[
          modelValue === template.id
            ? 'border-indigo-600 shadow-md shadow-indigo-50/50 dark:shadow-none'
            : 'border-transparent hover:border-zinc-200 dark:hover:border-zinc-700',
        ]"
        @click="selectTemplate(template.id)"
      >
        <div
          class="h-24 flex items-center justify-center relative transition-transform duration-300 group-hover:scale-105"
          :class="[template.previewClass]"
        >
          <div
            class="w-10 h-10 bg-white/20 backdrop-blur-md rounded-lg flex items-center justify-center"
          >
            <Icon :icon="template.icon" class="w-5 h-5 text-white" />
          </div>
        </div>
        <div
          class="p-3.5 bg-white dark:bg-zinc-800 border-t border-zinc-100 dark:border-zinc-700/50"
        >
          <h4 class="text-xs font-bold text-zinc-800 dark:text-zinc-100 mb-0.5">
            {{ template.name }}
          </h4>
          <p class="text-[11px] text-zinc-400 dark:text-zinc-500 line-clamp-1 leading-normal">
            {{ template.description }}
          </p>
        </div>
        <div
          v-if="modelValue === template.id"
          class="absolute top-2 right-2 w-5 h-5 bg-white rounded-full flex items-center justify-center shadow-sm"
        >
          <Icon icon="lucide:check-circle" class="w-4 h-4 text-indigo-600" />
        </div>
      </div>
    </div>

    <div
      class="flex items-center gap-2 px-4 py-3 bg-zinc-50 dark:bg-zinc-900/60 rounded-xl text-xs text-zinc-500 dark:text-zinc-400"
    >
      <Icon icon="lucide:info" class="w-4 h-4 text-indigo-500 flex-shrink-0" />
      <span>点击各类型样式模版可对下方渲染视图进行实时热替换，完美适配多元投递场景。</span>
    </div>
  </div>
</template>

<script setup>
import { Icon } from '@iconify/vue'

defineProps({
  modelValue: { type: String, default: 'modern' },
})

const emit = defineEmits(['update:modelValue'])

const templates = [
  {
    id: 'modern',
    name: '极客现代风',
    description: '色彩跃动，重点信息突出，适合互联网产研团队。',
    icon: 'lucide:zap',
    previewClass: 'bg-gradient-to-br from-indigo-600 to-violet-600',
  },
  {
    id: 'professional',
    name: '精英沉稳型',
    description: '标准严谨排版，严丝合缝，更受外企、传统名企青睐。',
    icon: 'lucide:briefcase',
    previewClass: 'bg-gradient-to-br from-slate-700 to-slate-800',
  },
  {
    id: 'creative',
    name: '多维视觉系',
    description: '极具个性的艺术留白，完美彰显独立创意色彩。',
    icon: 'lucide:palette',
    previewClass: 'bg-gradient-to-br from-violet-500 to-rose-400',
  },
  {
    id: 'minimalist',
    name: '极简北欧风',
    description: '剔除多余点缀，极高信息留白比，回归质朴内容。',
    icon: 'lucide:minus',
    previewClass: 'bg-gradient-to-br from-zinc-400 to-zinc-500',
  },
]

const selectTemplate = (templateId) => {
  emit('update:modelValue', templateId)
}
</script>
