<template>
  <el-button @click="goToPractice" type="primary" class="mb-4"> 返回通用训练列表 </el-button>
  <el-container class="h-screen dark:bg-gray-900 dark:text-gray-200">
    <!-- 左侧模板库 -->
    <el-aside
      width="280px"
      class="border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
    >
      <div class="p-4">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold dark:text-gray-400">逻辑模板库</h2>
          <el-button type="primary" size="small" @click="openTemplateDialog">添加模板</el-button>
        </div>

        <el-input
          v-model="templateSearch"
          placeholder="搜索模板..."
          class="mb-4 search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-scrollbar height="calc(100vh - 180px)">
          <el-card
            v-for="(template, index) in filteredTemplates"
            :key="index"
            shadow="hover"
            class="mb-3 cursor-pointer transition-transform hover:scale-[1.08]"
            :class="{
              'border-2 border-blue-500': selectedTemplateIndex === index,
            }"
            @click="selectTemplate(index)"
          >
            <div class="flex items-start">
              <div>
                <h3 class="dark:text-gray-400 font-bold text-lg">{{ template.name }}</h3>
                <p class="text-gray-500 dark:text-gray-400 text-sm mt-1">{{ template.desc }}</p>
                <el-tag size="small" class="mt-2">{{ template.scenario }}</el-tag>
              </div>
            </div>
          </el-card>
        </el-scrollbar>
      </div>
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-main class="bg-white dark:bg-gray-900">
      <div class="max-w-5xl mx-auto">
        <!-- 顶部操作栏 -->
        <div class="flex justify-end items-center mb-6">
          <div class="flex space-x-2">
            <el-button @click="clearContent" plain>清空内容</el-button>
            <el-button @click="copyResult" type="primary" :disabled="!currentTheme">
              <el-icon><CopyDocument /></el-icon> 复制结果
            </el-button>
          </div>
        </div>

        <!-- 主题输入区 -->
        <el-card shadow="never" class="mb-6">
          <template #header>
            <div class="flex items-center">
              <el-icon class="mr-2"><Edit class="dark:text-gray-400" /></el-icon>
              <span class="font-bold dark:text-gray-400">拆解主题</span>
            </div>
          </template>

          <el-input
            v-model="currentTheme"
            @input="saveToLocal"
            placeholder="输入需要拆解的主题（如：一个项目方案、一个争议问题）"
            size="large"
          >
            <template #prefix>
              <el-icon><Lightning /></el-icon>
            </template>
          </el-input>
        </el-card>

        <!-- 框架编辑区 -->
        <el-card shadow="never" v-if="currentTemplate">
          <template #header>
            <div class="flex items-center">
              <el-icon class="mr-2"><SetUp class="dark:text-gray-400" /></el-icon>
              <span class="font-bold dark:text-gray-400">{{ currentTemplate.name }} 框架</span>
              <el-tag type="info" class="ml-2">{{ currentTemplate.scenario }}</el-tag>
            </div>
          </template>

          <div class="space-y-6">
            <el-card
              v-for="(item, i) in currentTemplate.structure"
              :key="i"
              shadow="hover"
              class="transition-all hover:shadow-lg"
            >
              <div class="flex items-start">
                <div
                  class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center mr-4"
                >
                  <span class="font-bold text-blue-600 dark:text-blue-300">{{ i + 1 }}</span>
                </div>
                <div class="flex-1">
                  <div class="flex justify-between items-start">
                    <h3 class="font-bold text-lg dark:text-gray-400">{{ item.label }}</h3>
                    <el-tooltip effect="dark" :content="item.desc" placement="top">
                      <el-icon class="text-gray-400 cursor-pointer dark:text-white"
                        ><InfoFilled
                      /></el-icon>
                    </el-tooltip>
                  </div>
                  <p class="text-gray-500 dark:text-gray-400 text-sm mt-1">{{ item.desc }}</p>

                  <el-input
                    v-model="currentContent[i]"
                    @input="saveToLocal"
                    type="textarea"
                    :autosize="{ minRows: 2, maxRows: 6 }"
                    :placeholder="`请输入...（如：${item.placeholder}）`"
                    class="mt-3"
                  />
                </div>
              </div>
            </el-card>
          </div>
        </el-card>
      </div>
    </el-main>

    <!-- 添加模板对话框 -->
    <el-dialog
      class="transparent-dialog"
      v-model="templateDialogVisible"
      title="添加新模板"
      width="600px"
    >
      <el-form :model="newTemplate" label-width="100px " class="dark:dark:bg-gray-800">
        <el-form-item label="模板名称">
          <el-input v-model="newTemplate.name" placeholder="例如：SWOT分析" />
        </el-form-item>
        <el-form-item label="模板描述">
          <el-input v-model="newTemplate.desc" placeholder="例如：从四个维度拆解问题" />
        </el-form-item>
        <el-form-item label="适用场景">
          <el-input v-model="newTemplate.scenario" placeholder="例如：项目决策/竞争分析" />
        </el-form-item>

        <el-divider>结构定义</el-divider>

        <div
          v-for="(item, index) in newTemplate.structure"
          :key="index"
          class="mb-4 p-4 border rounded"
        >
          <div class="flex justify-between items-center mb-3">
            <span class="font-bold">步骤 {{ index + 1 }}</span>
            <el-button type="danger" size="small" @click="removeStructureItem(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>

          <el-form-item label="标题">
            <el-input v-model="item.label" placeholder="例如：优势（S）" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="item.desc" placeholder="例如：内部有利因素" />
          </el-form-item>
          <el-form-item label="占位符">
            <el-input v-model="item.placeholder" placeholder="例如：自身/项目的核心竞争力" />
          </el-form-item>
        </div>

        <el-button type="primary" plain @click="addStructureItem">
          <el-icon><Plus /></el-icon> 添加步骤
        </el-button>
      </el-form>

      <template #footer>
        <el-button @click="templateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNewTemplate">保存模板</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script>
export default {
  name: 'LogicDecomposer',
  methods: {
    goToPractice() {
      this.$router.push({ name: 'CommonPractice' })
    },
  },
}
</script>

<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  Search,
  ArrowLeft,
  CopyDocument,
  Edit,
  Lightning,
  SetUp,
  InfoFilled,
  Delete,
  Plus,
} from '@element-plus/icons-vue'

// 模板数据
const templates = ref([
  {
    name: 'SWOT分析',
    desc: '从优势、劣势、机会、威胁四个维度拆解',
    scenario: '项目决策/竞争分析',
    structure: [
      { label: '优势（S）', desc: '内部有利因素', placeholder: '自身/项目的核心竞争力' },
      { label: '劣势（W）', desc: '内部不利因素', placeholder: '需要改进的短板' },
      { label: '机会（O）', desc: '外部有利条件', placeholder: '可利用的市场/政策机会' },
      { label: '威胁（T）', desc: '外部不利因素', placeholder: '潜在的风险/竞争对手' },
    ],
  },
  {
    name: '5W1H',
    desc: '从原因、对象、时间、地点、人员、方法拆解',
    scenario: '问题分析/方案规划',
    structure: [
      { label: 'Why（为什么）', desc: '目的/原因', placeholder: '做这件事的核心目标' },
      { label: 'What（是什么）', desc: '对象/内容', placeholder: '具体要做什么' },
      { label: 'When（何时）', desc: '时间/节点', placeholder: '关键时间点/周期' },
      { label: 'Where（何地）', desc: '地点/场景', placeholder: '实施的场景/环境' },
      { label: 'Who（谁）', desc: '人员/责任', placeholder: '参与方及职责' },
      { label: 'How（如何）', desc: '方法/步骤', placeholder: '具体实施的步骤' },
    ],
  },
  {
    name: '金字塔原理',
    desc: '结论先行，论据分层支撑',
    scenario: '汇报/观点表达',
    structure: [
      { label: '核心结论', desc: '最顶层的观点', placeholder: '一句话总结你的核心观点' },
      { label: '论据1', desc: '支撑结论的第一个理由', placeholder: '用数据/案例说明' },
      { label: '论据2', desc: '支撑结论的第二个理由', placeholder: '用数据/案例说明' },
      { label: '论据3', desc: '支撑结论的第三个理由', placeholder: '用数据/案例说明' },
      { label: '总结', desc: '重申结论并升华', placeholder: '结合论据总结核心价值' },
    ],
  },
  {
    name: '鱼骨图分析',
    desc: '从人、机、料、法、环、测六个维度分析',
    scenario: '问题根源分析',
    structure: [
      { label: '人员因素', desc: '与人员相关的原因', placeholder: '人员技能、态度等问题' },
      { label: '机器设备', desc: '设备相关的原因', placeholder: '设备故障、老化等问题' },
      { label: '材料因素', desc: '原材料相关的原因', placeholder: '材料质量、供应等问题' },
      { label: '方法因素', desc: '流程方法相关的原因', placeholder: '方法不当、流程缺陷' },
      { label: '环境因素', desc: '环境相关的原因', placeholder: '工作环境、外部环境' },
      { label: '测量因素', desc: '测量相关的原因', placeholder: '测量工具、方法问题' },
    ],
  },
])

// 响应式数据
const selectedTemplateIndex = ref(0)
const currentTheme = ref('')
const currentContent = ref([])
const templateSearch = ref('')
const templateDialogVisible = ref(false)
const newTemplate = ref({
  name: '',
  desc: '',
  scenario: '',
  structure: [{ label: '', desc: '', placeholder: '' }],
})

// 计算属性
const currentTemplate = computed(() => {
  return templates.value[selectedTemplateIndex.value]
})

const filteredTemplates = computed(() => {
  if (!templateSearch.value) return templates.value
  return templates.value.filter(
    (t) =>
      t.name.toLowerCase().includes(templateSearch.value.toLowerCase()) ||
      t.desc.toLowerCase().includes(templateSearch.value.toLowerCase()) ||
      t.scenario.toLowerCase().includes(templateSearch.value.toLowerCase()),
  )
})

// 生命周期钩子
onMounted(() => {
  const saved = localStorage.getItem('logicAnalyzer')
  if (saved) {
    const { theme, content, templateIndex } = JSON.parse(saved)
    currentTheme.value = theme
    currentContent.value = content
    selectedTemplateIndex.value = templateIndex
  } else {
    resetContent()
  }
})

// 方法
const selectTemplate = (index) => {
  selectedTemplateIndex.value = index
  resetContent()
  saveToLocal()
}

const resetContent = () => {
  currentContent.value = currentTemplate.value.structure.map(() => '')
}

const saveToLocal = () => {
  const data = {
    theme: currentTheme.value,
    content: currentContent.value,
    templateIndex: selectedTemplateIndex.value,
  }
  localStorage.setItem('logicAnalyzer', JSON.stringify(data))
}

const clearContent = () => {
  currentTheme.value = ''
  resetContent()
  saveToLocal()
  ElMessage.success('内容已清空')
}

// 修改后的复制功能 - 生成结构化数据
const copyResult = () => {
  if (!currentTheme.value) return

  // 创建结构化数据对象
  const structuredData = {
    theme: currentTheme.value,
    template: currentTemplate.value.name,
    createdAt: new Date().toISOString(),
    content: {},
  }

  // 添加每个部分的内容
  currentTemplate.value.structure.forEach((item, i) => {
    structuredData.content[item.label] = currentContent.value[i] || '（未填写）'
  })

  // 转换为格式化的JSON字符串
  const jsonData = JSON.stringify(structuredData, null, 2)

  // 复制到剪贴板
  navigator.clipboard.writeText(jsonData).then(() => {
    ElMessage.success('已复制结构化结果')
  })
}

const openTemplateDialog = () => {
  newTemplate.value = {
    name: '',
    desc: '',
    scenario: '',
    structure: [{ label: '', desc: '', placeholder: '' }],
  }
  templateDialogVisible.value = true
}

const addStructureItem = () => {
  newTemplate.value.structure.push({ label: '', desc: '', placeholder: '' })
}

const removeStructureItem = (index) => {
  if (newTemplate.value.structure.length > 1) {
    newTemplate.value.structure.splice(index, 1)
  } else {
    ElMessage.warning('至少需要保留一个结构项')
  }
}

const saveNewTemplate = () => {
  if (!newTemplate.value.name) {
    ElMessage.error('请输入模板名称')
    return
  }

  if (newTemplate.value.structure.some((item) => !item.label)) {
    ElMessage.error('请填写所有结构项的标题')
    return
  }

  templates.value.push({
    ...newTemplate.value,
    icon: 'https://img.icons8.com/color/96/000000/template.png',
  })

  templateDialogVisible.value = false
  ElMessage.success(`模板 "${newTemplate.value.name}" 已添加`)
  saveToLocal()
}
</script>

<style>
.el-aside,
.el-main {
  transition:
    background-color 0.3s,
    color 0.3s;
}

.dark .el-card {
  background-color: #1f2937;
  border-color: #374151;
}

.dark .el-input__inner {
  background-color: #1f2937;
  border-color: #4b5563;
  color: #e5e7eb;
}

.dark .el-textarea__inner {
  background-color: #1f2937;
  border-color: #4b5563;
  color: #e5e7eb;
}

.dark .el-tag {
  background-color: #374151;
  border-color: #4b5563;
  color: #d1d5db;
}

.dark .transparent-dialog {
  background-color: #1f2937;
}
.dark .el-dialog__title {
  color: #a8abb2;
}

.dark .el-button--primary {
  border: 0;
  background-color: #409eff;
  color: #e5e7eb;
}

.dark .el-dialog__footer .el-button {
  border: 0;
  background-color: #98a2b3;
  color: #313234;
}

.dark .el-dialog__footer .el-button--primary {
  border: 0;
  background-color: #409eff;
  color: #e5e7eb;
}
</style>

<style scoped>
::v-deep .el-input__wrapper {
  background-color: transparent !important;
}

.dark .el-divider :deep(.el-divider__text) {
  background-color: #98a2b3;
}
</style>
