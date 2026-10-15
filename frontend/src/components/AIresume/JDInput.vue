<template>
  <div
    class="w-full bg-white dark:bg-zinc-800 rounded-2xl p-6 border border-zinc-100 dark:border-zinc-700/70 mb-6 transition-all duration-300"
  >
    <div class="flex items-start gap-4 mb-5">
      <div
        class="w-12 h-12 bg-indigo-50 dark:bg-indigo-950/50 rounded-xl flex items-center justify-center flex-shrink-0"
      >
        <Icon icon="lucide:target" class="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
      </div>
      <div>
        <h3 class="text-base font-semibold text-zinc-800 dark:text-zinc-100 mb-0.5">
          目标岗位描述 / Job Description
        </h3>
        <p class="text-xs text-zinc-400 dark:text-zinc-500 leading-normal">
          贴入您心仪职位的招聘需求（JD），AI 将对简历展开高契合度精准定向优化。
        </p>
      </div>
    </div>
    <div class="relative">
      <el-input
        v-model="localValue"
        type="textarea"
        :rows="5"
        class="custom-textarea"
        placeholder="请在此粘贴目标岗位的具体要求，例如：&#10;职位：前端开发工程师&#10;职责：负责核心业务线的 Vue3 组件库研发与体验升级&#10;要求：精通 CSS3/JS，具备良好的工程化思维与前端性能优化经验..."
        @input="handleInput"
      />
      <div
        class="flex justify-between items-center mt-3 text-xs text-zinc-400 dark:text-zinc-500 px-1"
      >
        <div class="flex items-center gap-1.5 text-zinc-500 dark:text-zinc-400">
          <Icon icon="lucide:lightbulb" class="w-4 h-4 text-amber-500" />
          <span>描述越详尽，简历画像与该岗位的匹配度及斩获面试率越高</span>
        </div>
        <div class="font-medium tabular-nums">{{ charCount }} 字</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const localValue = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const charCount = computed(() => localValue.value.length)
const handleInput = (value) => {
  localValue.value = value
}
</script>

<style scoped>
:deep(.el-textarea__inner) {
  border: 1px solid #f4f4f5;
  border-radius: 12px;
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
  background-color: #fafafa;
  box-shadow: none !important;
  transition: all 0.25s ease;
}

.dark :deep(.el-textarea__inner) {
  background-color: #18181b;
  border-color: #27272a;
  color: #f4f4f5;
}
:deep(.el-textarea__inner:focus) {
  border-color: #4f46e5;
  background-color: #ffffff;
}
.dark :deep(.el-textarea__inner:focus) {
  border-color: #6366f1;
  background-color: #18181b;
}
</style>

<style scoped>
.dark .custom-textarea >>> .el-textarea__inner {
  background-color: #18181b;
  border-color: #27272a;
  color: #f4f4f5;
}
</style>
