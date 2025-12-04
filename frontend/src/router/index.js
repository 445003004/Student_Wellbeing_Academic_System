import { createRouter, createWebHistory } from 'vue-router'
// 1. 引入组件
// 登录页通常直接引入，保证加载速度
import Login from '../views/LoginView.vue'

const routes = [
  // --- A. 默认路由 ---
  {
    path: '/',
    redirect: '/login' // 访问根路径时，自动跳到登录页
  },

  // --- B. 登录页 ---
  {
    path: '/login',
    name: 'Login',
    component: Login,
    // 登录页不需要权限
    meta: { requiresAuth: false }
  },

  // --- C. 课程主管仪表盘 (Course Director) ---
  {
    path: '/academic/dashboard',
    name: 'AcademicDashboard',
    // 路由懒加载 (Lazy Loading): 只有访问时才加载这个文件，提高首屏速度
    component: () => import('../views/AcademicDashboard.vue'),
    // ★ 关键配置: 需要登录 + 角色必须是 course_director
    meta: {
      requiresAuth: true,
      role: 'course_director'
    }
  },

  // --- D. 福利官仪表盘 (Wellbeing Officer) ---
  {
    path: '/wellbeing/dashboard',
    name: 'WellbeingDashboard',
    component: () => import('../views/WellbeingDashboard.vue'),
    // ★ 关键配置: 需要登录 + 角色必须是 wellbeing_officer
    meta: {
      requiresAuth: true,
      role: 'wellbeing_officer'
    }
  },

  // --- E. 捕获所有未定义路由 (404) ---
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

// 2. 创建 Router 实例
const router = createRouter({
  // 使用 HTML5 History 模式 (没有 # 号)
  history: createWebHistory(),
  routes
})

// 3. 全局前置守卫 (Global Navigation Guard)
// 就像机场安检，每次页面跳转前都会执行这里的代码
router.beforeEach((to, from, next) => {
  // 从 LocalStorage 获取 Token 和 角色
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('role')

  // 情况 1: 页面需要登录权限 (requiresAuth: true)
  if (to.meta.requiresAuth) {

    // 如果没有 Token，踢回登录页
    if (!token) {
      next('/login')
    }
    // 如果有 Token，但角色不匹配 (例如: 福利官想看主管的页面)
    else if (to.meta.role && to.meta.role !== userRole) {
      alert('⚠️ Access Denied: You do not have permission to view this page.')
      // 踢回登录页，或者踢回该用户对应的 Dashboard
      next('/login')
    }
    // 验证通过，放行
    else {
      next()
    }
  }

  // 情况 2: 如果用户已经登录了，还想去访问登录页 '/login'
  else if (to.path === '/login' && token) {
    // 自动把他们转到对应的 Dashboard，提升体验
    if (userRole === 'course_director') {
      next('/academic/dashboard')
    } else if (userRole === 'wellbeing_officer') {
      next('/wellbeing/dashboard')
    } else {
      next()
    }
  }

  // 情况 3: 不需要权限的页面 (如 404)，直接放行
  else {
    next()
  }
})

export default router