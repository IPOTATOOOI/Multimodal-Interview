<template>
  <div class="kg-main p-6 bg-gray-50 dark:bg-gray-900 min-h-screen min-w-[800px]">
      <!-- 主标题区域 -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-orange-500 dark:text-orange-400 mb-4 flex items-center justify-center">
          <i class="fas fa-project-diagram mr-4 text-5xl"></i>
          知识图谱
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          探索、构建和管理您的知识网络，通过可视化图谱发现数据间的深层关联
        </p>
      </div>

      <!-- 功能卡片区域 -->
      <div class="max-w-6xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- 数据库展示卡片 -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 border border-orange-100 dark:border-orange-900">
            <div class="p-8">
              <div class="flex items-center mb-6">
                <div class="w-16 h-16 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center mr-4">
                  <i class="fas fa-eye text-2xl text-orange-500 dark:text-orange-400"></i>
                </div>
                <div>
                  <h3 class="text-2xl font-bold text-gray-800 dark:text-white">数据库展示</h3>
                  <p class="text-gray-600 dark:text-gray-300">可视化知识图谱</p>
                </div>
              </div>
              <p class="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
                通过交互式图谱界面，探索节点和关系，发现知识间的连接模式。支持筛选、搜索和删除操作。
              </p>
              <div class="space-y-3 mb-6">
                <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <i class="fas fa-check-circle text-green-500 mr-2"></i>
                  交互式节点和关系展示
                </div>
                <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <i class="fas fa-check-circle text-green-500 mr-2"></i>
                  支持筛选和搜索功能
                </div>
                <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <i class="fas fa-check-circle text-green-500 mr-2"></i>
                  节点删除和管理功能
                </div>
              </div>
              <router-link
                to="/kg/display"
                class="inline-flex items-center px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg"
              >
                <i class="fas fa-arrow-right mr-2"></i>
                进入图谱展示
              </router-link>
            </div>
          </div>

          <!-- 数据上传卡片 -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 border border-orange-100 dark:border-orange-900">
            <div class="p-8">
              <div class="flex items-center mb-6">
                <div class="w-16 h-16 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center mr-4">
                  <i class="fas fa-upload text-2xl text-orange-500 dark:text-orange-400"></i>
                </div>
                <div>
                  <h3 class="text-2xl font-bold text-gray-800 dark:text-white">数据上传</h3>
                  <p class="text-gray-600 dark:text-gray-300">导入图数据文件</p>
                </div>
              </div>
              <p class="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
                上传各种格式的文件，自动提取实体和关系，构建您的专属知识图谱。支持多种文件格式。
              </p>
              <div class="space-y-3 mb-6">
                <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <i class="fas fa-check-circle text-green-500 mr-2"></i>
                  支持 TXT、CSV、XLSX、DOCX 格式
                </div>
                <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <i class="fas fa-check-circle text-green-500 mr-2"></i>
                  自动实体识别和关系抽取
                </div>
                <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <i class="fas fa-check-circle text-green-500 mr-2"></i>
                  权限控制和数据归属管理
                </div>
              </div>
              <router-link
                to="/kg/upload"
                class="inline-flex items-center px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg"
              >
                <i class="fas fa-arrow-right mr-2"></i>
                开始上传数据
              </router-link>
            </div>
          </div>
        </div>

        <!-- 使用说明区域 -->
        <div class="mt-12 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-orange-100 dark:border-orange-900">
          <h3 class="text-2xl font-bold text-gray-800 dark:text-white mb-6 flex items-center">
            <i class="fas fa-lightbulb text-yellow-500 mr-3"></i>
            使用说明
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-3">数据上传流程</h4>
              <ol class="space-y-2 text-gray-600 dark:text-gray-400">
                <li class="flex items-start">
                  <span class="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">1</span>
                  选择要上传的文件（支持多种格式）
                </li>
                <li class="flex items-start">
                  <span class="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">2</span>
                  输入主题名称，描述数据内容
                </li>
                <li class="flex items-start">
                  <span class="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">3</span>
                  系统自动处理并导入图谱数据库
                </li>
              </ol>
            </div>
            <div>
              <h4 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-3">图谱操作指南</h4>
              <ol class="space-y-2 text-gray-600 dark:text-gray-400">
                <li class="flex items-start">
                  <span class="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">1</span>
                  点击节点查看详细信息
                </li>
                <li class="flex items-start">
                  <span class="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">2</span>
                  使用工具栏进行筛选和搜索
                </li>
                <li class="flex items-start">
                  <span class="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">3</span>
                  选中节点后可进行删除操作
                </li>
              </ol>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
// 这是一个纯展示组件，不需要额外的逻辑
</script>

<style scoped>
/* 自定义动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.kg-main {
  animation: fadeInUp 0.6s ease-out;
}

/* 卡片悬停效果 */
.hover\:scale-105:hover {
  transform: scale(1.05);
}

/* 过渡动画 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}
</style>
