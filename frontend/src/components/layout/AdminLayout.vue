<template>
  <div class="min-h-screen xl:flex">
    <app-sidebar />
    <Backdrop />
    <div
      class="flex-1 transition-all duration-300 ease-in-out"
      :class="[isExpanded || isHovered ? 'lg:ml-[220px]' : 'lg:ml-[90px]']"
    >
      <app-header />
      <VirtualHumanSidebar v-if="showVirtualHumanSidebar" />
      <div class="p-4 mx-auto max-w-(--breakpoint-2xl) md:p-6">
        <div class="min-h-screen">
          <router-view v-slot="{ Component }">
            <keep-alive>
              <component :is="Component" />
            </keep-alive>
          </router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import Backdrop from './Backdrop.vue'
import { useSidebar } from '@/composables/useSidebar'
import { showVirtualHumanSidebar } from '@/store/virtualHumanSidebar'
import VirtualHumanSidebar from '@/components/virtual-human/VirtualHumanSidebar.vue'

const { isExpanded, isHovered } = useSidebar()
const route = useRoute()
const currentPageTitle = ref('首页')
const parentTitle = ref('首页')

// 监听路由变化，动态更新标题
watch(
  () => route.meta.title,
  (title) => {
    currentPageTitle.value = title || '首页'

    // 增强父标题判断逻辑
    parentTitle.value = [
      '模拟面试',
      '历史评测',
      '学习资源',
      'AI简历',
      '推荐',
      '通用训练',
      '题库练习',
      '语音测速',
      '口头禅过滤',
      '压力测试',
      '逻辑思维拆解',
      '行业资讯',
    ].includes(title)
      ? 'AI面试助手'
      : '首页'
  },
  { immediate: true },
)
</script>
