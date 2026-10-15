import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import InterviewView from '@/views/InterviewView.vue'
import HistoryView from '@/views/HistoryView.vue'
import ResourcesView from '@/views/ResourcesView.vue'
import ResumeView from '@/views/ResumeView.vue'
import Signin from '@/views/Auth/Signin.vue'
import Signup from '@/views/Auth/Signup.vue'
import BlankPage from '@/views/BlankPage.vue'
import FourZeroFour from '@/views/Errors/FourZeroFour.vue'
import { useAuth } from '@/composables/useAuth'
import { KeepAlive } from 'vue'

import { useAppStore } from '@/store/app'

const routes: Array<RouteRecordRaw> = [
  // 全屏的BlankPage路由
  {
    path: '/',
    name: 'Welcome',
    component: BlankPage,
    meta: { title: '欢迎使用', requireUser: true },
  },
  {
    path: '/app',
    component: AdminLayout,
    children: [
      { path: '', redirect: '/app/interview' },
      {
        path: 'interview',
        name: 'Interview',
        component: InterviewView,
        meta: { title: '模拟面试', KeepAlive: true, requireUser: true },
      },
      {
        path: 'interview/result',
        name: 'InterviewResult',
        component: () => import('@/components/interview/InterviewResult.vue'),
        meta: { title: '模拟面试结果', requireUser: true },
      },
      {
        path: 'interview/written_test',
        name: 'WrittenTest',
        component: () => import('@/components/interview/WrittenTest.vue'),
        meta: { title: '笔试', requireUser: true },
      },
      {
        path: 'interview/weakness_training',
        name: 'WeaknessTraining',
        component: () => import('@/components/interview/WeaknessTraining.vue'),
        meta: { title: '薄弱点训练', requireUser: true },
      },
      {
        path: 'history',
        name: 'History',
        component: HistoryView,
        meta: { title: '历史评测', requireUser: true },
      },
      {
        path: 'resources',
        component: ResourcesView,
        redirect: '/app/resources/recommend',
        meta: { title: '学习资源', requireUser: true },
        children: [
          {
            path: 'recommend',
            component: () => import('@/components/resources/Recommend.vue'),
            meta: { title: '推荐', requireUser: true },
          },

          {
            path: 'quiz',
            name: 'QuizList',
            component: () => import('@/components/resources/QuizList.vue'),
            meta: { title: '题库练习', requireUser: true },
          },
          {
            path: 'question-practice',
            name: 'QuestionPractice',
            component: () => import('@/views/QuestionPracticeView.vue'),
            meta: { title: '题库练习', requireUser: true },
          },
          {
            path: 'news',
            name: 'FieldNews',
            component: () => import('@/components/resources/News.vue'),
            meta: { title: '行业资讯', requireUser: true },
          },
        ],
      },
      {
        path: 'common-practice',
        name: 'CommonPractice',
        component: () => import('@/views/CommonPractice.vue'),
        meta: { title: '通用训练', requireUser: true },
      },
      {
        path: 'common-practice/voice-test',
        component: () => import('@/components/common-practice/voicetest.vue'),
        meta: { title: '语音测速', requireUser: true },
      },
      {
        path: 'common-practice/tag-filter',
        component: () => import('@/components/common-practice/tag-filter.vue'),
        meta: { title: '口头禅过滤', requireUser: true },
      },
      {
        path: 'common-practice/pressure-test',
        component: () => import('@/components/common-practice/pressure-test.vue'),
        meta: { title: '压力测试', requireUser: true },
      },
      {
        path: 'common-practice/logic-decomposer',
        component: () => import('@/components/common-practice/logic-decomposer.vue'),
        meta: { title: '逻辑思维拆解', requireUser: true },
      },
      {
        path: 'resume',
        name: 'Resume',
        component: ResumeView,
        meta: { title: 'AI简历', requireUser: true },
      },
      {
        path: 'history/:history_id',
        name: 'HistoryDetail',
        component: () => import('@/views/HistoryDetailView.vue'),
        meta: { title: '历史详情', requireUser: true },
      },
    ],
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true },
    children: [
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/UserDashboard.vue'),
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/DataDashboard.vue'),
      },
      {
        path: 'dashboard/user/:userId',
        name: 'AdminDashboardUser',
        component: () => import('@/views/DataDashboardUser.vue'),
        meta: { title: '用户面试数据' },
      },
      {
        path: 'history/:history_id',
        name: 'AdminHistoryDetail',
        component: () => import('@/views/HistoryDetailView.vue'),
        meta: { title: '历史详情' },
      },
      {
        path: 'vector-database',
        name: 'VectorDatabase',
        redirect: '/admin/vector-database/upload',
        children: [
          {
            path: 'upload',
            name: 'AdminVectorDatabaseUpload',
            component: () => import('@/components/vector-database/vector-database-upload.vue'),
            meta: { title: '向量数据库上传' },
          },
        ],
      },
      // 修复：管理员的知识图谱路由使用不同的路径和名称
      {
        path: 'knowledge-graph',
        name: 'AdminKnowledgeGraph',
        redirect: '/admin/knowledge-graph/display',
        children: [
          {
            path: 'display',
            name: 'AdminKGDisplay',
            component: () => import('@/components/kg/kg-display.vue'),
            meta: { title: '知识图谱展示' },
          },
          {
            path: 'upload',
            name: 'AdminKGUpload',
            component: () => import('@/components/kg/kg-upload.vue'),
            meta: { title: '知识图谱上传' },
          },
        ],
      },
    ],
  },

  {
    path: '/signin',
    name: 'Signin',
    component: Signin,
    meta: {
      title: '登录',
      requiresGuest: true,
    },
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup,
    meta: {
      title: '注册',
      requiresGuest: true,
    },
  },
  {
    path: '/interview/dialoging',
    name: 'InterviewDialoging',
    component: () => import('@/components/interview/InterviewMain.vue'),
    meta: { requireUser: true },
  },
  {
    path: '/interview/result',
    name: 'InterviewResult',
    component: () => import('@/components/interview/InterviewResult.vue'),
    meta: { requireUser: true },
  },
  {
    path: '/prepare/:category/:job',
    name: 'PrepareDetail',
    component: () => import('@/components/prepare/prepareView.vue'),
    meta: { requireUser: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: FourZeroFour,
    meta: { title: '页面未找到' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 新增：根路径处理函数
const clearAuthAndRedirect = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('isAuthenticated')
  return '/signin'
}

// 路由守卫
router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuth()
  const userRole = localStorage.getItem('userRole')
  const isAdmin = userRole === 'admin'
  const isRegularUser = userRole === 'user' || (!isAdmin && isAuthenticated.value)

  // 设置页面标题
  const appStore = useAppStore()
  document.title = to.meta.title ? `${to.meta.title} -  ${appStore.appName}` : appStore.appName

  // 0. 处理根路径：已认证用户访问根路径时直接进入BlankPage，未认证用户重定向到登录
  if (to.path === '/') {
    if (isAuthenticated.value) {
      next()
    } else {
      next(clearAuthAndRedirect())
    }
    return
  }

  // 1. 处理404页面
  if (to.name === 'NotFound') {
    next()
    return
  }

  // 2. 处理认证状态
  if (!isAuthenticated.value) {
    // 未认证用户只能访问游客页面
    if (to.meta.requiresGuest) {
      next()
    } else {
      next({ name: 'Signin', query: { redirect: to.fullPath } })
    }
    return
  }

  // 3. 已认证用户处理逻辑
  if (isAuthenticated.value) {
    // 3.1 已认证用户尝试访问游客页面（登录/注册）
    if (to.meta.requiresGuest) {
      // 根据用户角色重定向到相应首页
      next(isAdmin ? { name: 'AdminDashboard' } : { name: 'Welcome' })
      return
    }

    // 3.2 管理员权限检查
    if (to.meta.requiresAdmin && !isAdmin) {
      next({ name: 'FourZeroFour' })
      return
    }

    // 3.3 普通用户权限检查 - 修复：允许管理员访问知识图谱相关路由
    if (to.meta.requireUser && isAdmin) {
      next({ name: 'AdminDashboard' }) // 管理员不能访问普通用户页面
      return
    }

    // 3.4 普通用户尝试访问管理员路由
    if (to.path.startsWith('/admin') && !isAdmin) {
      next({ name: 'FourZeroFour' })
      return
    }

    // 3.5 管理员尝试访问普通用户路由 - 修复：允许访问知识图谱路由
    if (!to.path.startsWith('/admin') && isAdmin && !to.meta.requiresAdmin) {
      // 允许管理员访问一些共享页面（如404），但重定向非管理员路由到管理员首页
      if (to.name !== 'NotFound') {
        next({ name: 'AdminDashboard' })
        return
      }
    }
  }

  // 其他情况放行
  next()
})

export default router
