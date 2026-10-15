<template>
  <aside
    :class="[
      'fixed mt-16 flex flex-col lg:mt-0 top-0 px-5 left-0 bg-white dark:bg-gray-900 dark:border-gray-800 text-gray-900 h-screen transition-all duration-300 ease-in-out z-99999 border-r border-gray-200',
      {
        'lg:w-[220px]': isExpanded || isMobileOpen || isHovered,
        'lg:w-[90px]': !isExpanded && !isHovered,
        'translate-x-0 w-[220px]': isMobileOpen,
        '-translate-x-full': !isMobileOpen,
        'lg:translate-x-0': true,
      },
    ]"
    @mouseenter="!isExpanded && (isHovered = true)"
    @mouseleave="isHovered = false"
  >
    <div :class="['py-8 flex', !isExpanded && !isHovered ? 'lg:justify-center' : 'justify-start']">
      <router-link to="/">
        <div class="flex items-center space-x-2">
          <img
            v-if="isExpanded || isHovered || isMobileOpen"
            class="dark:hidden"
            :src="appStore.appLogo"
            alt="Logo"
            width="60"
            height="60"
          />
          <img
            v-if="isExpanded || isHovered || isMobileOpen"
            class="hidden dark:block"
            :src="appStore.appLogo"
            alt="Logo"
            width="60"
            height="60"
          />
          <img
            v-if="isExpanded || isHovered || isMobileOpen"
            class="dark:hidden"
            :src="appStore.appIcon"
            :alt="appStore.appName"
            width="100"
            height="100"
          />
          <img
            v-if="isExpanded || isHovered || isMobileOpen"
            class="hidden dark:block"
            :src="appStore.appIcon"
            :alt="appStore.appName"
            width="100"
            height="100"
          />
          <img v-else :src="appStore.appLogo" alt="Logo" width="60" height="60" />
        </div>
      </router-link>
    </div>
    <div class="flex flex-col overflow-y-auto duration-300 ease-linear no-scrollbar">
      <nav class="mb-6">
        <div class="flex flex-col gap-4">
          <div v-for="(menuGroup, groupIndex) in menuGroups" :key="groupIndex">
            <h2
              :class="[
                'mb-4 text-xs uppercase flex leading-[20px] text-gray-400',
                !isExpanded && !isHovered ? 'lg:justify-center' : 'justify-start',
              ]"
            >
              <template v-if="isExpanded || isHovered || isMobileOpen">
                {{ menuGroup.title }}
              </template>
              <HorizontalDots v-else />
            </h2>
            <ul class="flex flex-col gap-4">
              <li v-for="(item, index) in menuGroup.items" :key="item.name">
                <button
                  v-if="item.subItems"
                  @click="toggleSubmenu(groupIndex, index)"
                  :class="[
                    'flex items-center py-2.5 px-3.5 rounded-lg text-sm font-medium transition-colors duration-200 group w-full',
                    {
                      'bg-brand-50 text-brand-500 dark:bg-gray-800': isSubmenuOpen(
                        groupIndex,
                        index,
                      ),
                      'text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800':
                        !isSubmenuOpen(groupIndex, index),
                    },
                    !isExpanded && !isHovered ? 'lg:justify-center' : 'lg:justify-start',
                  ]"
                >
                  <span
                    :class="[
                      'flex items-center justify-center w-8 h-8',
                      {
                        'text-brand-500': isSubmenuOpen(groupIndex, index),
                        'text-gray-500 dark:text-gray-400': !isSubmenuOpen(groupIndex, index),
                      },
                    ]"
                  >
                    <component :is="item.icon" class="w-6 h-6" />
                  </span>
                  <span
                    v-if="isExpanded || isHovered || isMobileOpen"
                    class="ml-3 flex-1 text-left"
                    >{{ item.name }}</span
                  >
                  <ChevronDownIcon
                    v-if="isExpanded || isHovered || isMobileOpen"
                    :class="[
                      'ml-auto w-5 h-5 transition-transform duration-200',
                      {
                        'rotate-180 text-brand-500': isSubmenuOpen(groupIndex, index),
                      },
                    ]"
                  />
                </button>
                <button
                  v-else-if="item.path"
                  @click="handleMenuItemClick(item)"
                  :class="[
                    'flex items-center py-2.5 px-3.5 rounded-lg text-sm font-medium transition-colors duration-200 group w-full',
                    {
                      'bg-brand-50 text-brand-500 dark:bg-gray-800': isActive(item.path),
                      'text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800':
                        !isActive(item.path),
                    },
                  ]"
                >
                  <span
                    :class="[
                      'flex items-center justify-center w-8 h-8',
                      {
                        'text-brand-500': isActive(item.path),
                        'text-gray-500 dark:text-gray-400': !isActive(item.path),
                      },
                    ]"
                  >
                    <component :is="item.icon" class="w-6 h-6" />
                  </span>
                  <span
                    v-if="isExpanded || isHovered || isMobileOpen"
                    class="ml-3 flex-1 text-left"
                    >{{ item.name }}</span
                  >
                </button>
                <transition
                  @enter="startTransition"
                  @after-enter="endTransition"
                  @before-leave="startTransition"
                  @after-leave="endTransition"
                >
                  <div
                    v-show="
                      isSubmenuOpen(groupIndex, index) && (isExpanded || isHovered || isMobileOpen)
                    "
                  >
                    <ul class="mt-2 space-y-1 ml-9">
                      <li v-for="subItem in item.subItems" :key="subItem.name">
                        <router-link
                          v-if="subItem.path"
                          :to="subItem.path.startsWith('http') ? '' : subItem.path"
                          @click="subItem.path.startsWith('http') ? subItem.onClick() : null"
                          :class="[
                            'flex items-center py-2 px-3 rounded-lg text-sm font-medium transition-colors duration-200',
                            {
                              'bg-brand-50 text-brand-500 dark:bg-gray-800': isActive(subItem.path),
                              'text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800':
                                !isActive(subItem.path),
                            },
                          ]"
                        >
                          <span
                            v-if="subItem.icon"
                            class="flex items-center justify-center w-5 h-5 mr-2"
                          >
                            <component :is="subItem.icon" class="w-4 h-4" />
                          </span>
                          {{ subItem.name }}
                          <span class="flex items-center gap-1 ml-auto">
                            <span
                              v-if="subItem.new"
                              :class="[
                                'text-xs px-1.5 py-0.5 rounded',
                                {
                                  'bg-brand-100 text-brand-800': isActive(subItem.path),
                                  'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300':
                                    !isActive(subItem.path),
                                },
                              ]"
                            >
                              new
                            </span>
                            <span
                              v-if="subItem.pro"
                              :class="[
                                'text-xs px-1.5 py-0.5 rounded',
                                {
                                  'bg-brand-100 text-brand-800': isActive(subItem.path),
                                  'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300':
                                    !isActive(subItem.path),
                                },
                              ]"
                            >
                              pro
                            </span>
                          </span>
                        </router-link>
                      </li>
                    </ul>
                  </div>
                </transition>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <SidebarWidget v-if="isExpanded || isHovered || isMobileOpen" />
    </div>

    <!-- 退出登录按钮 -->
    <div class="mt-auto py-4">
      <button
        @click="handleSignOut"
        :class="[
          'flex items-center py-2.5 px-3.5 rounded-lg text-sm font-medium transition-colors duration-200 group w-full',
          'text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800',
          !isExpanded && !isHovered ? 'lg:justify-center' : 'lg:justify-start',
        ]"
      >
        <span class="flex items-center justify-center w-8 h-8 text-gray-500 dark:text-gray-400">
          <LogoutIcon class="w-5 h-5" />
        </span>
        <span v-if="isExpanded || isHovered || isMobileOpen" class="ml-3 flex-1 text-left">
          退出登录
        </span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/store/app'
import { STABLE_DIFFUSION_URL } from '@/config/api'

import {
  GridIcon,
  HomeIcon,
  MessageSquareIcon,
  HistoryIcon,
  BookOpenIcon,
  FileTextIcon,
  LogoutIcon,
  ChevronDownIcon,
  HorizontalDots,
  CommonIcon,
  StaredIcon, // 新增图标导入
  ListIcon, // 新增图标导入
  TaskIcon,
  UserGroupIcon,
  LayoutDashboardIcon,
  VectorDatabaseIcon,
  PlusIcon,
  KG,
  KGDisplay,
  KGUpload,
} from '../../icons'
import SidebarWidget from './SidebarWidget.vue'
import { useSidebar } from '@/composables/useSidebar'
import { useAuth } from '@/composables/useAuth'

const { isAuthenticated, logout } = useAuth()
const isLogoutConfirmationVisible = ref(false)

const handleSignOut = async () => {
  try {
    logout()
    router.push('/signin')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}

const confirmLogout = () => {
  isLogoutConfirmationVisible.value = true
}

const cancelLogout = () => {
  isLogoutConfirmationVisible.value = false
}

const performLogout = async () => {
  await handleSignOut()
  isLogoutConfirmationVisible.value = false
}

const route = useRoute()
const router = useRouter()
const { isExpanded, isMobileOpen, isHovered, openSubmenu } = useSidebar()
const appStore = useAppStore()

const menuGroups = computed(() => {
  const isAdmin = localStorage.getItem('userRole') === 'admin' // 判断是否为管理员
  if (isAuthenticated.value) {
    if (isAdmin) {
      // 管理员菜单
      return [
        {
          title: '管理功能',
          items: [
            {
              icon: UserGroupIcon, // 需要导入这个图标
              name: '用户管理',
              path: '/admin/users',
            },
            {
              icon: LayoutDashboardIcon, // 需要导入这个图标
              name: '可视化大屏',
              path: '/admin/dashboard',
            },
            {
              icon: VectorDatabaseIcon, // 需要导入这个图标
              name: '向量数据库',
              path: STABLE_DIFFUSION_URL,
              onClick: () => window.open(STABLE_DIFFUSION_URL, '_blank'),
            },
            {
              icon: KG, // 需要导入这个图标
              name: '知识图谱',
              path: '/admin/kg',
              subItems: [
                {
                  name: '数据库展示',
                  path: '/admin/knowledge-graph/display',
                  icon: KGDisplay,
                },
                {
                  name: '数据上传',
                  path: '/admin/knowledge-graph/upload',
                  icon: KGUpload,
                },
              ],
            },
          ],
        },
      ]
    } else {
      // 普通用户菜单
      return [
        {
          title: 'AI面试助手',
          items: [
            {
              icon: MessageSquareIcon,
              name: '模拟面试',
              path: '/app/interview',
            },
            {
              icon: HistoryIcon,
              name: '历史评测',
              path: '/app/history',
            },
            {
              icon: BookOpenIcon,
              name: '资源中心',
              subItems: [
                { name: '推荐', path: '/app/resources/recommend', icon: StaredIcon },
                { name: '题库练习', path: '/app/resources/quiz', icon: ListIcon },
                { name: '行业资讯', path: '/app/resources/news', icon: TaskIcon },
              ],
            },
            {
              icon: CommonIcon,
              name: '通用训练',
              path: '/app/common-practice',
            },
            {
              icon: FileTextIcon,
              name: 'AI简历',
              path: '/app/resume',
            },
            //{
            //  icon: KGUpload, // 需要导入这个图标
            //  name: '知识库管理',
            //  path: '/app/knowledge-base-management',
            //},
          ],
        },
      ]
    }
  } else {
    // 未登录用户菜单
    return [
      {
        title: 'Others',
        items: [
          {
            icon: PlugInIcon,
            name: 'Authentication',
            subItems: [
              { name: 'Signin', path: '/signin', pro: false },
              { name: 'Signup', path: '/signup', pro: false },
            ],
          },
        ],
      },
    ]
  }
})

const isActive = (path) => route.path === path

const toggleSubmenu = (groupIndex, itemIndex) => {
  const key = `${groupIndex}-${itemIndex}`
  openSubmenu.value = openSubmenu.value === key ? null : key
}

const isAnySubmenuRouteActive = computed(() => {
  return menuGroups.value.some((group) =>
    group.items.some(
      (item) => item.subItems && item.subItems.some((subItem) => isActive(subItem.path)),
    ),
  )
})

const isSubmenuOpen = (groupIndex, itemIndex) => {
  const key = `${groupIndex}-${itemIndex}`
  return (
    openSubmenu.value === key ||
    (isAnySubmenuRouteActive.value &&
      menuGroups.value[groupIndex].items[itemIndex].subItems?.some((subItem) =>
        isActive(subItem.path),
      ))
  )
}

const startTransition = (el) => {
  el.style.height = 'auto'
  const height = el.scrollHeight
  el.style.height = '0px'
  el.offsetHeight // force reflow
  el.style.height = height + 'px'
}

const endTransition = (el) => {
  el.style.height = ''
}

// 新增：处理菜单项点击事件
const handleMenuItemClick = (item) => {
  if (item.onClick) {
    item.onClick()
  } else if (item.path.startsWith('http')) {
    window.open(item.path, '_blank')
  } else {
    router.push(item.path)
  }
}
</script>

<style scoped>
.icon-small {
  width: 80%;
  height: 80%;
  font-size: 80%;
}
</style>
