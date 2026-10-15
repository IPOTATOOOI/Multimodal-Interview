<template>
  <div class="flex flex-col h-full">
    <!-- 根分类导航栏 -->
    <div
      class="root-category-bar flex justify-center gap-8 px-6 pt-4 pb-2 dark:bg-gray-900 border-b border-gray-100 dark:border-gray-800 relative"
    >
      <!-- 滑动指示器 -->
      <div
        class="root-category-indicator"
        :style="{
          width: indicatorWidth + 'px',
          left: indicatorLeft + 'px',
        }"
      ></div>

      <div
        v-for="tab in tabs"
        :key="tab.id"
        class="root-category-item"
        :class="{ active: currentTab === tab.id }"
        @click="switchTab(tab.id)"
        ref="tabItems"
      >
        <div class="flex items-center">
          <Icon :icon="tab.icon" class="text-lg mr-2" />
          <span>{{ tab.title }}</span>
        </div>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="p-[30px] minh-[300px]">
      <Transition name="fade" mode="out-in">
        <component :is="currentComponent" />
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, nextTick } from 'vue'
import VideoRecommendations from '@/components/resources/recommend/VideoRecommendations.vue'
import BlogRecommendations from '@/components/resources/recommend/BlogRecommendations.vue'
import { Icon } from '@iconify/vue'

const tabs = [
  {
    id: 'videos',
    title: '视频推荐',
    icon: 'lucide:video',
    component: VideoRecommendations,
  },
  {
    id: 'blogs',
    title: '博客推荐',
    icon: 'lucide:book',
    component: BlogRecommendations,
  },
]

const currentTab = ref('videos')
const currentComponent = shallowRef(VideoRecommendations)
const tabItems = ref([])
const indicatorWidth = ref(0)
const indicatorLeft = ref(0)

function updateIndicatorPosition() {
  const activeIndex = tabs.findIndex((tab) => tab.id === currentTab.value)
  if (activeIndex !== -1 && tabItems.value[activeIndex]) {
    const rect = tabItems.value[activeIndex].getBoundingClientRect()
    const barRect = tabItems.value[0].parentElement.getBoundingClientRect()
    indicatorWidth.value = rect.width
    indicatorLeft.value = rect.left - barRect.left
  }
}

function switchTab(tabId) {
  currentTab.value = tabId
  const selectedTab = tabs.find((tab) => tab.id === tabId)
  currentComponent.value = selectedTab.component
  nextTick(() => {
    updateIndicatorPosition()
  })
}

onMounted(() => {
  nextTick(() => {
    updateIndicatorPosition()
  })
})
</script>

<style scoped>
.root-category-bar {
  font-size: 18px;
  font-weight: 500;
  position: relative;
}

.root-category-indicator {
  position: absolute;
  height: 6px;
  bottom: 4px;
  z-index: 1;
  background: linear-gradient(135deg, #3641f5 0%, #5a65ff 100%);
  border-radius: 8px;
  transition: all 0.3s ease-out;
}

.root-category-item {
  padding: 8px 18px 4px 18px;
  cursor: pointer;
  color: #475467;
  transition: all 0.3s;
  position: relative;
  transform-origin: bottom center;
}

.root-category-item.active {
  color: #3641f5;
  transform: scale(1.15);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
