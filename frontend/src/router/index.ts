import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/voter/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../pages/auth/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../pages/auth/Register.vue')
    },
    {
      path: '/payment/:type?',
      name: 'payment',
      component: () => import('../pages/voter/Payment.vue'),
      props: true
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../pages/voter/Dashboard.vue'),
      // meta: { requiresAuth: true }
    },
    {
      path: '/elections',
      name: 'elections',
      component: () => import('../pages/elections/ElectionList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/elections/:id',
      name: 'election-detail',
      component: () => import('../pages/elections/ElectionDetail.vue'),
      // meta: { requiresAuth: true },
      // props: true
    },
    {
      path: '/elections/:id/vote',
      name: 'vote',
      component: () => import('../pages/elections/VotingInterface.vue'),
      // meta: { requiresAuth: true },
      // props: true
    },
    {
      path: '/elections/:id/results',
      name: 'election-results',
      component: () => import('../pages/elections/ElectionResults.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../pages/admin/AdminDashboard.vue'),
      // meta: { requiresAuth: true, requiresEC: true }
    },
    // {
    //   path: '/admin/elections/create',
    //   name: 'create-election',
    //   component: () => import('../pages/admin/CreateElection.vue'),
    //   // meta: { requiresAuth: true, requiresEC: true }
    // },
    {
      path: '/admin/elections/:id/candidates',
      name: 'manage-candidates',
      component: () => import('../pages/admin/ManageCandidates.vue'),
      // meta: { requiresAuth: true, requiresEC: true },
      // props: true
    },
    {
      path: '/admin/members',
      name: 'member-management',
      component: () => import('../pages/admin/MemberManagement.vue'),
      // meta: { requiresAuth: true, requiresEC: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../pages/voter/Profile.vue'),
      // meta: { requiresAuth: true }
    },
    {
      path: '/help',
      name: 'help',
      component: () => import('../pages/voter/Help.vue')
    }
  ]
})

// router.beforeEach((to, from, next) => {
//   const authStore = useAuthStore()
  
//   if (to.meta.requiresAuth && !authStore.isAuthenticated) {
//     next('/login')
//     return
//   }
  
//   if (to.meta.requiresEC && !authStore.isECMember) {
//     next('/dashboard')
//     return
//   }
  
//   // Check payment status for authenticated routes
//   if (to.meta.requiresAuth && authStore.isAuthenticated && !authStore.user?.can_vote) {
//     if (to.name !== 'payment') {
//       next('/payment/dues')
//       return
//     }
//   }
  
//   next()
// })

export default router