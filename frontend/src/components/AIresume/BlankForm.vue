<template>
  <div class="blank-form-container">
    <div class="form-header">
      <div class="header-left">
        <el-button @click="handleCancel" text>
          <Icon icon="lucide:arrow-left" class="w-4 h-4 mr-1" />
          返回
        </el-button>
        <div>
          <h3 class="text-xl font-bold text-zinc-800 dark:text-zinc-100">空白填写模式</h3>
          <p class="text-sm text-zinc-400 dark:text-zinc-500">
            从零开始构建您的专业简历，请填写以下信息
          </p>
        </div>
      </div>
    </div>

    <div class="form-sections">
      <el-form :model="formData" label-position="top">
        <el-card class="mb-6" shadow="never">
          <template #header>
            <div class="flex items-center gap-2">
              <Icon icon="lucide:user" class="w-5 h-5 text-indigo-600" />
              <span class="font-semibold">基本信息</span>
            </div>
          </template>

          <div class="photo-upload-row">
            <div>
              <div class="photo-upload-title">个人照片</div>
              <div class="photo-upload-tip">支持 JPG、PNG，建议使用证件照或清晰头像</div>
            </div>
            <div class="photo-upload-control">
              <el-upload
                :auto-upload="false"
                :show-file-list="false"
                accept="image/png,image/jpeg,image/jpg,image/webp"
                class="photo-uploader"
                @change="handlePhotoChange"
              >
                <div v-if="formData.basic_info.photo" class="photo-preview">
                  <img :src="formData.basic_info.photo" alt="个人照片预览" />
                </div>
                <div v-else class="photo-placeholder">
                  <Icon icon="lucide:image-plus" class="w-6 h-6" />
                  <span>上传照片</span>
                </div>
              </el-upload>
              <el-button
                v-if="formData.basic_info.photo"
                size="small"
                text
                type="danger"
                @click="removePhoto"
              >
                移除
              </el-button>
            </div>
          </div>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="姓名" required>
                <el-input v-model="formData.basic_info.name" placeholder="请输入您的姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="性别">
                <el-select
                  v-model="formData.basic_info.gender"
                  placeholder="请选择性别"
                  style="width: 100%"
                >
                  <el-option label="男" value="男" />
                  <el-option label="女" value="女" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="手机号码" required>
                <el-input v-model="formData.basic_info.phone" placeholder="请输入手机号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱地址" required>
                <el-input v-model="formData.basic_info.email" placeholder="请输入邮箱" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="求职意向">
                <el-input
                  v-model="formData.job_intention.job_title"
                  placeholder="例如：前端工程师"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="期望城市">
                <el-input v-model="formData.job_intention.location1" placeholder="例如：北京" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="个人简介">
            <el-input
              v-model="formData.basic_info.summary"
              type="textarea"
              :rows="3"
              placeholder="请简要介绍自己（可选）"
            />
          </el-form-item>
        </el-card>

        <el-card class="mb-6" shadow="never">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center gap-2">
                <Icon icon="lucide:graduation-cap" class="w-5 h-5 text-indigo-600" />
                <span class="font-semibold">教育经历</span>
              </div>
              <el-button type="primary" size="small" @click="addEducation">
                <Icon icon="lucide:plus" class="w-4 h-4 mr-1" />
                添加教育经历
              </el-button>
            </div>
          </template>

          <div v-for="(edu, index) in formData.education" :key="index" class="education-item">
            <div class="item-header">
              <span>教育经历 #{{ index + 1 }}</span>
              <el-button
                v-if="formData.education.length > 1"
                type="danger"
                size="small"
                text
                @click="removeEducation(index)"
              >
                <Icon icon="lucide:trash-2" class="w-4 h-4" />
              </el-button>
            </div>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="学校名称" required>
                  <el-input v-model="edu.school" placeholder="请输入学校名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="学历">
                  <el-select v-model="edu.degree" placeholder="请选择学历" style="width: 100%">
                    <el-option label="高中" value="高中" />
                    <el-option label="大专" value="大专" />
                    <el-option label="本科" value="本科" />
                    <el-option label="硕士" value="硕士" />
                    <el-option label="博士" value="博士" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="专业">
                  <el-input v-model="edu.major" placeholder="请输入专业" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="学习时间">
                  <el-date-picker
                    v-model="edu.study_period"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    style="width: 100%"
                    value-format="YYYY-MM"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="主修课程/荣誉">
              <el-input
                v-model="edu.description"
                type="textarea"
                :rows="2"
                placeholder="请输入主修课程、获奖情况等（可选）"
              />
            </el-form-item>

            <el-divider v-if="index < formData.education.length - 1" />
          </div>
        </el-card>

        <el-card class="mb-6" shadow="never">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center gap-2">
                <Icon icon="lucide:briefcase" class="w-5 h-5 text-indigo-600" />
                <span class="font-semibold">工作经历</span>
              </div>
              <el-button type="primary" size="small" @click="addWorkExperience">
                <Icon icon="lucide:plus" class="w-4 h-4 mr-1" />
                添加工作经历
              </el-button>
            </div>
          </template>

          <div v-for="(work, index) in formData.work_experience" :key="index" class="work-item">
            <div class="item-header">
              <span>工作经历 #{{ index + 1 }}</span>
              <el-button
                v-if="formData.work_experience.length > 1"
                type="danger"
                size="small"
                text
                @click="removeWorkExperience(index)"
              >
                <Icon icon="lucide:trash-2" class="w-4 h-4" />
              </el-button>
            </div>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公司名称" required>
                  <el-input v-model="work.company_name" placeholder="请输入公司名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="职位">
                  <el-input v-model="work.position" placeholder="请输入职位名称" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="工作时间">
                  <el-date-picker
                    v-model="work.work_period"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    style="width: 100%"
                    value-format="YYYY-MM"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="工作地点">
                  <el-input v-model="work.city" placeholder="请输入工作城市" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="工作描述" required>
              <el-input
                v-model="work.description"
                type="textarea"
                :rows="4"
                placeholder="请详细描述您的工作职责、主要成果、使用的技能等"
              />
            </el-form-item>

            <el-divider v-if="index < formData.work_experience.length - 1" />
          </div>
        </el-card>

        <el-card class="mb-6" shadow="never">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center gap-2">
                <Icon icon="lucide:folder" class="w-5 h-5 text-indigo-600" />
                <span class="font-semibold">项目经验</span>
              </div>
              <el-button type="primary" size="small" @click="addProjectExperience">
                <Icon icon="lucide:plus" class="w-4 h-4 mr-1" />
                添加项目经验
              </el-button>
            </div>
          </template>

          <div
            v-for="(project, index) in formData.project_experience"
            :key="index"
            class="project-item"
          >
            <div class="item-header">
              <span>项目经验 #{{ index + 1 }}</span>
              <el-button
                v-if="formData.project_experience.length > 1"
                type="danger"
                size="small"
                text
                @click="removeProjectExperience(index)"
              >
                <Icon icon="lucide:trash-2" class="w-4 h-4" />
              </el-button>
            </div>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="项目名称" required>
                  <el-input v-model="project.name" placeholder="请输入项目名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="担任角色">
                  <el-input v-model="project.role" placeholder="例如：项目负责人、核心开发" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="项目时间">
                  <el-date-picker
                    v-model="project.project_period"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    style="width: 100%"
                    value-format="YYYY-MM"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="项目描述" required>
              <el-input
                v-model="project.description"
                type="textarea"
                :rows="4"
                placeholder="请详细描述项目背景、您的贡献、使用的技术、取得的成果等"
              />
            </el-form-item>

            <el-divider v-if="index < formData.project_experience.length - 1" />
          </div>
        </el-card>

        <el-card class="mb-6" shadow="never">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center gap-2">
                <Icon icon="lucide:wrench" class="w-5 h-5 text-indigo-600" />
                <span class="font-semibold">专业技能</span>
              </div>
              <el-button type="primary" size="small" @click="addSkill">
                <Icon icon="lucide:plus" class="w-4 h-4 mr-1" />
                添加技能
              </el-button>
            </div>
          </template>

          <div v-for="(skill, index) in formData.skills" :key="index" class="skill-item">
            <el-row :gutter="20">
              <el-col :span="16">
                <el-form-item label="技能名称">
                  <el-input
                    v-model="skill.content"
                    placeholder="例如：Vue.js、Python、数据分析等"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="熟练度">
                  <el-select v-model="skill.level" placeholder="请选择" style="width: 100%">
                    <el-option label="精通" value="精通" />
                    <el-option label="熟练" value="熟练" />
                    <el-option label="掌握" value="掌握" />
                    <el-option label="了解" value="了解" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="2">
                <el-button
                  v-if="formData.skills.length > 1"
                  type="danger"
                  size="small"
                  text
                  @click="removeSkill(index)"
                >
                  <Icon icon="lucide:trash-2" class="w-4 h-4" />
                </el-button>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <el-card class="mb-6" shadow="never">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center gap-2">
                <Icon icon="lucide:trophy" class="w-5 h-5 text-indigo-600" />
                <span class="font-semibold">荣誉证书</span>
              </div>
              <el-button type="primary" size="small" @click="addCertificate">
                <Icon icon="lucide:plus" class="w-4 h-4 mr-1" />
                添加证书
              </el-button>
            </div>
          </template>

          <div v-for="(cert, index) in formData.certificates" :key="index" class="cert-item">
            <el-row :gutter="20">
              <el-col :span="10">
                <el-form-item label="证书名称">
                  <el-input v-model="cert.name" placeholder="请输入证书名称" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="获得时间">
                  <el-date-picker
                    v-model="cert.obtain_time"
                    type="month"
                    placeholder="选择日期"
                    style="width: 100%"
                    value-format="YYYY-MM"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="颁发机构">
                  <el-input v-model="cert.issuer" placeholder="颁发机构" />
                </el-form-item>
              </el-col>
              <el-col :span="2">
                <el-button
                  v-if="formData.certificates.length > 1"
                  type="danger"
                  size="small"
                  text
                  @click="removeCertificate(index)"
                >
                  <Icon icon="lucide:trash-2" class="w-4 h-4" />
                </el-button>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <el-card class="mb-6" shadow="never">
          <template #header>
            <div class="flex items-center gap-2">
              <Icon icon="lucide:message-square" class="w-5 h-5 text-indigo-600" />
              <span class="font-semibold">其他经历</span>
            </div>
          </template>

          <el-form-item label="校园经历">
            <el-input
              v-model="formData.campus_experience_text"
              type="textarea"
              :rows="3"
              placeholder="请描述您的校园活动、社团经历、志愿者经历等（可选）"
            />
          </el-form-item>

          <el-form-item label="竞赛经历">
            <el-input
              v-model="formData.competition_experience_text"
              type="textarea"
              :rows="3"
              placeholder="请描述您参加的竞赛及获奖情况（可选）"
            />
          </el-form-item>
        </el-card>
      </el-form>
    </div>

    <div class="form-actions">
      <el-button size="large" @click="loadHistory">
        <Icon icon="lucide:history" class="w-4 h-4 mr-1" />
        载入上次填写
      </el-button>
      <el-button size="large" @click="saveHistory">
        <Icon icon="lucide:save" class="w-4 h-4 mr-1" />
        保存本次填写
      </el-button>
      <el-button size="large" @click="handleCancel">取消</el-button>
      <el-button type="primary" size="large" @click="handleSubmit">
        <Icon icon="lucide:arrow-right" class="w-4 h-4 mr-1" />
        生成简历
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
import { ElMessage } from 'element-plus'
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({}),
  },
})
const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])
const STORAGE_KEY = 'resume_blank_form_data'
const HISTORY_KEY = 'resume_blank_form_history'
const formData = ref({
  basic_info: {
    name: '',
    gender: '',
    phone: '',
    email: '',
    summary: '',
    photo: '',
  },
  job_intention: {
    job_title: '',
    location1: '',
  },
  education: [
    {
      school: '',
      degree: '',
      major: '',
      study_period: '',
      description: '',
    },
  ],
  work_experience: [
    {
      company_name: '',
      position: '',
      work_period: '',
      city: '',
      description: '',
    },
  ],
  project_experience: [
    {
      name: '',
      role: '',
      project_period: '',
      description: '',
    },
  ],
  skills: [
    {
      content: '',
      level: '',
    },
  ],
  certificates: [
    {
      name: '',
      obtain_time: '',
      issuer: '',
    },
  ],
  campus_experience_text: '',
  competition_experience_text: '',
})
const saveToStorage = () => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(formData.value))
  } catch (e) {
    console.error('保存数据失败:', e)
  }
}
const loadFromStorage = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const savedData = JSON.parse(saved)
      Object.assign(formData.value, savedData)
    }
  } catch (e) {
    console.error('加载数据失败:', e)
  }
}
const clearStorage = () => {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (e) {
    console.error('清除数据失败:', e)
  }
}

const saveHistory = () => {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(formData.value))
    ElMessage.success('已保存本次填写内容')
  } catch (e) {
    console.error('保存历史失败:', e)
    ElMessage.error('保存失败，可能是照片或内容过大')
  }
}

const loadHistory = () => {
  try {
    const saved = localStorage.getItem(HISTORY_KEY)
    if (!saved) {
      ElMessage.warning('还没有保存过填写历史')
      return
    }

    const savedData = JSON.parse(saved)
    Object.assign(formData.value, savedData)
    saveToStorage()
    ElMessage.success('已载入上次填写内容')
  } catch (e) {
    console.error('载入历史失败:', e)
    ElMessage.error('载入失败，历史数据可能已损坏')
  }
}

watch(
  formData,
  (newVal) => {
    emit('update:modelValue', newVal)
    saveToStorage()
  },
  { deep: true },
)
onMounted(() => {
  if (Object.keys(props.modelValue).length === 0) {
    loadFromStorage()
  } else {
    Object.assign(formData.value, props.modelValue)
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
})
onUnmounted(() => {
  saveToStorage()
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
const handleBeforeUnload = (e) => {
  saveToStorage()
}

const handlePhotoChange = (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请上传 JPG、PNG 等图片文件')
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('照片大小不能超过 2MB')
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    formData.value.basic_info.photo = reader.result
  }
  reader.onerror = () => {
    ElMessage.error('照片读取失败，请重新选择')
  }
  reader.readAsDataURL(file)
}

const removePhoto = () => {
  formData.value.basic_info.photo = ''
}

const addEducation = () => {
  formData.value.education.push({
    school: '',
    degree: '',
    major: '',
    study_period: '',
    description: '',
  })
}

const removeEducation = (index) => {
  if (formData.value.education.length > 1) {
    formData.value.education.splice(index, 1)
  }
}

const addWorkExperience = () => {
  formData.value.work_experience.push({
    company_name: '',
    position: '',
    work_period: '',
    city: '',
    description: '',
  })
}

const removeWorkExperience = (index) => {
  if (formData.value.work_experience.length > 1) {
    formData.value.work_experience.splice(index, 1)
  }
}

const addProjectExperience = () => {
  formData.value.project_experience.push({
    name: '',
    role: '',
    project_period: '',
    description: '',
  })
}

const removeProjectExperience = (index) => {
  if (formData.value.project_experience.length > 1) {
    formData.value.project_experience.splice(index, 1)
  }
}

const addSkill = () => {
  formData.value.skills.push({
    content: '',
    level: '',
  })
}

const removeSkill = (index) => {
  if (formData.value.skills.length > 1) {
    formData.value.skills.splice(index, 1)
  }
}

const addCertificate = () => {
  formData.value.certificates.push({
    name: '',
    obtain_time: '',
    issuer: '',
  })
}

const removeCertificate = (index) => {
  if (formData.value.certificates.length > 1) {
    formData.value.certificates.splice(index, 1)
  }
}

const handleSubmit = () => {
  emit('submit', formData.value)
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.blank-form-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-sections {
  margin-bottom: 32px;
}

.photo-upload-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
  padding: 16px;
  border: 1px dashed #d4d4d8;
  border-radius: 10px;
  background: #fafafa;
}

.dark .photo-upload-row {
  background: #18181b;
  border-color: #3f3f46;
}

.photo-upload-title {
  color: #27272a;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.dark .photo-upload-title {
  color: #f4f4f5;
}

.photo-upload-tip {
  color: #71717a;
  font-size: 12px;
}

.photo-upload-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.photo-uploader :deep(.el-upload) {
  display: block;
}

.photo-preview,
.photo-placeholder {
  width: 82px;
  height: 104px;
  border-radius: 8px;
  overflow: hidden;
}

.photo-preview {
  border: 1px solid #e5e7eb;
  background: #fff;
}

.photo-preview img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px dashed #a1a1aa;
  color: #71717a;
  font-size: 12px;
  transition:
    border-color 0.2s,
    color 0.2s,
    background 0.2s;
}

.photo-placeholder:hover {
  background: #eef2ff;
  border-color: #4f46e5;
  color: #4f46e5;
}

.education-item,
.work-item,
.project-item,
.skill-item,
.cert-item {
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
}

.dark .font-semibold {
  color: #f1f5f9;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  color: #6b7280;
}

.dark .item-header {
  color: #9ca3af;
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  border-radius: 12px;
}

.dark .form-actions {
  background: #18181b;
}

.blank-form-container >>> .el-card {
  background: #ffffff;
  border-color: #e5e7eb;
}

.dark .blank-form-container >>> .el-card {
  background: #27272a;
  border-color: #3f3f46;
}

.blank-form-container >>> .el-card__header {
  padding: 10px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.dark .blank-form-container >>> .el-card__header {
  background: #27272a;
  border-color: #3f3f46;
}

.blank-form-container >>> .el-card__body {
  background: #ffffff;
  padding: 12px 16px;
}

.dark .blank-form-container >>> .el-card__body {
  background: #27272a;
}

.blank-form-container >>> .el-form-item__label {
  font-weight: 500;
  color: #374151;
}

.dark .blank-form-container >>> .el-form-item__label {
  color: #d1d5db;
}

.blank-form-container >>> .el-input__wrapper {
  background: #ffffff;
  border-color: #d1d5db;
}

.dark .blank-form-container >>> .el-input__wrapper {
  background: #3f3f46;
  border-color: #52525b;
}

.blank-form-container >>> .el-input__inner {
  color: #1f2937;
}

.dark .blank-form-container >>> .el-input__inner {
  color: #fafafa;
}

.blank-form-container >>> .el-select__wrapper {
  background: #ffffff;
  border-color: #d1d5db;
}

.dark .blank-form-container >>> .el-select__wrapper {
  background: #3f3f46;
  border-color: #52525b;
}

.blank-form-container >>> .el-select__placeholder {
  color: #9ca3af;
}

.dark .blank-form-container >>> .el-select__placeholder {
  color: #71717a;
}

.blank-form-container >>> .el-textarea__inner {
  background: #ffffff;
  border-color: #d1d5db;
  color: #1f2937;
}

.dark .blank-form-container >>> .el-textarea__inner {
  background: #3f3f46;
  border-color: #52525b;
  color: #fafafa;
}

.blank-form-container >>> .el-date-picker {
  background: #ffffff;
  border-color: #d1d5db;
}

.dark .blank-form-container >>> .el-date-picker {
  background: #3f3f46;
  border-color: #52525b;
}

.blank-form-container >>> .el-divider {
  background-color: #e5e7eb;
}

.dark .blank-form-container >>> .el-divider {
  background-color: #3f3f46;
}

.blank-form-container >>> .el-button {
  color: #374151;
  border-color: #d1d5db;
}

.dark .blank-form-container >>> .el-button {
  background: #3f3f46;
  border-color: #52525b;
  color: #f1f5f9;
}

.blank-form-container >>> .el-button--primary {
  background: #4f46e5;
  border-color: #4f46e5;
  color: #ffffff;
}

.dark .blank-form-container >>> .el-button--primary {
  background: #3b82f6;
  border-color: #3b82f6;
}

.blank-form-container >>> .el-button--danger {
  color: #dc2626;
}

.dark .blank-form-container >>> .el-button--danger {
  color: #f87171;
}

.blank-form-container >>> .el-option {
  color: #1f2937;
}

.dark .blank-form-container >>> .el-option {
  color: #fafafa;
}

.blank-form-container >>> .el-picker-panel {
  background: #ffffff;
  border-color: #e5e7eb;
}

.dark .blank-form-container >>> .el-picker-panel {
  background: #27272a;
  border-color: #3f3f46;
}

.blank-form-container >>> .el-picker-panel__content {
  color: #1f2937;
}

.dark .blank-form-container >>> .el-picker-panel__content {
  color: #fafafa;
}

.blank-form-container >>> .el-date-table {
  color: #1f2937;
}

.dark .blank-form-container >>> .el-date-table {
  color: #fafafa;
}

.blank-form-container >>> .el-date-table th {
  color: #6b7280;
}

.dark .blank-form-container >>> .el-date-table th {
  color: #9ca3af;
}

.blank-form-container >>> .el-calendar-day {
  color: #1f2937;
}

.dark .blank-form-container >>> .el-calendar-day {
  color: #fafafa;
}
</style>
