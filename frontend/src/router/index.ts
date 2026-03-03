import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Auth
    {
      path: '/login',
      component: AuthLayout,
      children: [{
        path: '',
        name: 'Login',
        component: () => import('@/views/auth/Login.vue')
      }]
    },

    // Main App
    {
      path: '/',
      component: MainLayout,
      redirect: '/my-courses',
      children: [
        // Dashboard
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/Index.vue'),
          meta: { title: '仪表盘' }
        },

        // ── 会话/课堂核心流程 ──────────────────────
        {
          path: 'my-courses',
          name: 'MyCourses',
          component: () => import('@/views/session/SessionHome.vue'),
          meta: { title: '我的课堂' }
        },
        {
          path: 'session/:sessionId/assess',
          name: 'Assessment',
          component: () => import('@/views/session/Assessment.vue'),
          meta: { title: '入学评测' }
        },
        {
          path: 'session/:sessionId/report',
          name: 'ProficiencyReport',
          component: () => import('@/views/session/SessionSyllabus.vue'),
          meta: { title: '学习大纲' }
        },
        {
          path: 'session/:sessionId/syllabus',
          name: 'SessionSyllabus',
          component: () => import('@/views/session/SessionSyllabus.vue'),
          meta: { title: '学习大纲' }
        },
        {
          path: 'session/:sessionId/classroom/:itemId',
          name: 'Classroom',
          component: () => import('@/views/session/Classroom.vue'),
          meta: { title: '上课' }
        },
        {
          path: 'session/:sessionId/exam/:examType',
          name: 'Exam',
          component: () => import('@/views/session/Exam.vue'),
          meta: { title: '考试' }
        },

        // ── 独立工具页面（快速使用）──────────────────
        {
          path: 'learn',
          name: 'QuickLearn',
          component: () => import('@/views/learning/QuickLearn.vue'),
          meta: { title: '快速学习' }
        },
        {
          path: 'syllabus',
          name: 'Syllabus',
          component: () => import('@/views/learning/Syllabus.vue'),
          meta: { title: '学习大纲' }
        },
        {
          path: 'practice',
          name: 'Practice',
          component: () => import('@/views/learning/Practice.vue'),
          meta: { title: '练习题' }
        },

        // 404
        {
          path: '/:pathMatch(.*)*',
          name: 'NotFound',
          component: () => import('@/views/error/404.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to) => {
  if (to.meta?.title) document.title = `${to.meta.title} — AI School`
  return true
})

export default router