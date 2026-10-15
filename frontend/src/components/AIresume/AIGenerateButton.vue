<template>
  <div
    class="w-full flex flex-col items-center gap-6 p-8 bg-white dark:bg-zinc-800 rounded-2xl border-2 border-zinc-100 dark:border-zinc-700 transition-all duration-300"
  >
    <el-button
      :type="isGenerating ? 'info' : 'primary'"
      :loading="isGenerating"
      :disabled="!canGenerate"
      class="w-full max-w-[400px] !h-14 !text-base !font-semibold !rounded-xl !border-none !shadow-md transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:!bg-zinc-200 dark:disabled:!bg-zinc-700 disabled:!text-zinc-400 disabled:transform-none disabled:!shadow-none"
      :class="[
        isGenerating
          ? '!bg-zinc-100 !text-zinc-500 dark:!bg-zinc-700 dark:!text-zinc-400'
          : '!bg-gradient-to-r !from-indigo-600 !to-violet-600 hover:!from-indigo-700 hover:!to-violet-700 !text-white shadow-indigo-200 dark:shadow-none',
      ]"
      @click="handleGenerate"
    >
      <template v-if="!isGenerating">
        <div class="flex items-center justify-center gap-2">
          <Icon icon="lucide:wand-2" class="w-5 h-5" />
          <span>{{ buttonText }}</span>
        </div>
      </template>
      <template v-else>
        <span class="flex items-center gap-2 animate-pulse">{{ generatingText }}</span>
      </template>
    </el-button>

    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform opacity-0 -translate-y-2"
      leave-active-class="transition duration-200 ease-in"
      leave-to-class="transform opacity-0 -translate-y-2"
    >
      <div v-if="isGenerating" class="w-full max-w-[500px] mt-2">
        <div class="flex justify-between items-center mb-2.5">
          <div class="text-sm font-medium text-zinc-500 dark:text-zinc-400">{{ currentStep }}</div>
          <div class="text-sm font-bold text-indigo-600 dark:text-indigo-400">
            {{ Math.round(progress) }}%
          </div>
        </div>
        <div class="w-full h-2 bg-zinc-100 dark:bg-zinc-700 rounded-full overflow-hidden mb-4">
          <div
            class="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full transition-all duration-300 ease-out"
            :style="{ width: progress + '%' }"
          />
        </div>
        <div class="flex flex-wrap gap-2 justify-center">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition-all duration-300"
            :class="[
              index === currentStepIndex
                ? 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 font-semibold ring-1 ring-indigo-100 dark:ring-indigo-900'
                : index < currentStepIndex
                  ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 font-medium'
                  : 'bg-zinc-50 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-500',
            ]"
          >
            <Icon
              :icon="index < currentStepIndex ? 'lucide:circle-check' : step.icon"
              class="w-3.5 h-3.5"
            />
            <span>{{ step.text }}</span>
          </div>
        </div>
      </div>
    </transition>

    <transition
      enter-active-class="transition duration-500 ease-out"
      enter-from-class="transform opacity-0 scale-95"
      leave-active-class="transition duration-300 ease-in"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isCompleted && !isGenerating"
        class="flex items-start gap-4 p-5 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20 border border-emerald-100 dark:border-emerald-900/30 rounded-xl w-full"
      >
        <div class="flex-shrink-0 mt-0.5">
          <Icon icon="lucide:circle-check" class="w-6 h-6 text-emerald-500 dark:text-emerald-400" />
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-bold text-emerald-800 dark:text-emerald-300 mb-1">
            简历生成完成！
          </h4>
          <p class="text-xs text-emerald-700/80 dark:text-emerald-400/80 line-height-relaxed">
            AI 已根据您提供的信息完成智绘优化，您可在下方视图中实时预览、精细化编辑及切换主题模板。
          </p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  isGenerating: { type: Boolean, default: false },
  progress: { type: Number, default: 0 },
  canGenerate: { type: Boolean, default: true },
  isCompleted: { type: Boolean, default: false },
})

const emit = defineEmits(['generate'])

const steps = [
  { icon: 'lucide:file-text', text: '分析个人信息' },
  { icon: 'lucide:target', text: '匹配岗位JD' },
  { icon: 'lucide:sparkles', text: 'AI智能优化' },
  { icon: 'lucide:layout', text: '生成简历模板' },
]

const currentStepIndex = ref(0)
const currentStep = ref(steps[0].text)

const generatingTexts = [
  '正在分析您的个人信息...',
  '正在匹配目标岗位要求...',
  'AI 正在智能优化简历内容...',
  '正在生成专业简历模板...',
]

const buttonText = computed(() => {
  return props.canGenerate ? 'AI 一键生成专业简历' : '请先完善录入信息及目标JD'
})

const generatingText = computed(() => {
  return generatingTexts[currentStepIndex.value] || 'AI 正在精雕细琢...'
})

watch(
  () => props.progress,
  (newProgress) => {
    const stepIndex = Math.min(Math.floor((newProgress / 100) * steps.length), steps.length - 1)
    currentStepIndex.value = stepIndex
    currentStep.value = steps[stepIndex].text
  },
)

const handleGenerate = () => {
  if (props.canGenerate && !props.isGenerating) {
    emit('generate')
  }
}
</script>
