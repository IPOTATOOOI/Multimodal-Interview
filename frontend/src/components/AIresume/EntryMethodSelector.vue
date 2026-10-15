<template>
  <div class="w-full mb-8">
    <div class="text-center mb-8">
      <h3 class="text-xl font-bold text-zinc-800 dark:text-zinc-100 mb-2">选择简历录入方式</h3>
      <p class="text-sm text-zinc-400 dark:text-zinc-500">
        挑选您最舒适的录入模式，交由 AI 完成深度定制
      </p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 justify-center max-w-4xl mx-auto">
      <div
        v-for="method in entryMethods"
        :key="method.id"
        class="relative p-6 border-2 rounded-2xl cursor-pointer transition-all duration-300 bg-white dark:bg-zinc-800 flex flex-col items-start hover:-translate-y-1 hover:shadow-lg"
        :class="[
          selectedMethod === method.id
            ? 'border-indigo-600 bg-indigo-50/20 dark:bg-indigo-950/10 shadow-md shadow-indigo-100/50 dark:shadow-none'
            : 'border-zinc-100 dark:border-zinc-700/60 hover:border-indigo-300 dark:hover:border-indigo-800',
        ]"
        @click="selectMethod(method.id)"
      >
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center mb-4 shadow-sm"
          :class="[method.colorClass]"
        >
          <Icon :icon="method.icon" class="w-6 h-6 text-white" />
        </div>
        <div class="relative z-10 w-full">
          <h4 class="text-base font-semibold text-zinc-800 dark:text-zinc-100 mb-1.5">
            {{ method.title }}
          </h4>
          <p class="text-xs text-zinc-400 dark:text-zinc-500 leading-relaxed">
            {{ method.description }}
          </p>
        </div>
        <div
          v-if="selectedMethod === method.id"
          class="absolute top-4 right-4 w-5 h-5 bg-indigo-600 rounded-full flex items-center justify-center animate-fade-in"
        >
          <Icon icon="lucide:check" class="w-3.5 h-3.5 text-white" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  modelValue: { type: String, default: 'manual' },
})

const emit = defineEmits(['update:modelValue'])

const selectedMethod = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

onMounted(() => {
  localStorage.removeItem('resume_blank_form_data')
})

const entryMethods = [
  {
    id: 'manual',
    title: '空白填写',
    description: '结构化表单录入，由零开始构建完美的个人原生档案。',
    icon: 'lucide:file-edit',
    colorClass: 'bg-gradient-to-br from-indigo-500 to-violet-500',
  },
  {
    id: 'upload',
    title: '解析已有简历',
    description: '支持 Word 导入并完成全面润色。',
    icon: 'lucide:upload-cloud',
    colorClass: 'bg-gradient-to-br from-sky-500 to-indigo-500',
  },
]

const selectMethod = (methodId) => {
  selectedMethod.value = methodId
}
</script>
