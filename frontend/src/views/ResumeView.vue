<template>
  <div class="w-full max-w-[1400px] mx-auto px-4 py-0">
    <div v-if="currentStep === 'entry'" class="entry-step">
      <EntryMethodSelector v-model="entryMethod" />

      <div class="entry-actions">
        <el-button type="primary" size="large" :disabled="!entryMethod" @click="handleEntrySelect">
          <Icon icon="lucide:arrow-right" class="w-4 h-4 mr-1" />
          下一步
        </el-button>
      </div>
    </div>

    <div v-if="currentStep === 'input'" class="input-step">
      <BlankForm
        v-if="entryMethod === 'manual'"
        v-model="formData"
        @submit="handleFormSubmit"
        @cancel="handleCancel"
      />

      <UploadResume
        v-if="entryMethod === 'upload'"
        @submit="handleFormSubmit"
        @cancel="handleCancel"
      />
    </div>

    <div v-if="currentStep === 'preview'" class="preview-step">
      <ResumePreview
        :resume-data="formData"
        :is-manual-mode="entryMethod === 'manual'"
        :is-upload-mode="entryMethod === 'upload'"
        :entry-method="entryMethod"
        @back="handleBack"
        @updateResume="handleResumeUpdate"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import EntryMethodSelector from '@/components/AIresume/EntryMethodSelector.vue'
import BlankForm from '@/components/AIresume/BlankForm.vue'

import UploadResume from '@/components/AIresume/UploadResume.vue'
import ResumePreview from '@/components/AIresume/ResumePreview.vue'

const steps = ['entry', 'input', 'preview']
const currentStep = ref('entry')
const entryMethod = ref('')

const formData = ref({
  basic_info: {
    name: '',
    phone: '',
    email: '',
  },
  education: [],
  work_experience: [],
  project_experience: [],
  skills: [],
  job_intention: {
    job_title: '',
    location1: '',
  },
})

const handleEntrySelect = () => {
  if (entryMethod.value) {
    currentStep.value = 'input'
  }
}

const handleFormSubmit = (data) => {
  formData.value = data
  currentStep.value = 'preview'
}

const handleCancel = () => {
  currentStep.value = 'entry'
  entryMethod.value = ''
}

const handleBack = () => {
  currentStep.value = 'input'
}

const handleResumeUpdate = (updatedData) => {
  formData.value = updatedData
}
</script>

<style scoped>
.entry-step,
.input-step,
.preview-step {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.entry-actions {
  display: flex;
  justify-content: center;
  padding: 24px;
  border-radius: 12px;
}
</style>
