import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const HASH_SCROLL_TIMEOUT = 1200
const HASH_SCROLL_INTERVAL = 16
const HASH_SCROLL_OFFSET = 92

function getHashTarget(hash) {
  if (!hash) return null

  let id = hash.slice(1)
  try {
    id = decodeURIComponent(id)
  } catch {
    // Keep the raw hash id if it is not URI encoded cleanly.
  }

  return document.getElementById(id)
}

export function resolveHashScroll(hash, timeout = HASH_SCROLL_TIMEOUT) {
  if (!hash) return null

  const currentTarget = getHashTarget(hash)
  if (currentTarget) {
    return { el: currentTarget, top: HASH_SCROLL_OFFSET, behavior: 'smooth' }
  }

  return new Promise((resolve) => {
    const startedAt = Date.now()

    const findTarget = () => {
      const target = getHashTarget(hash)
      if (target) {
        resolve({ el: target, top: HASH_SCROLL_OFFSET, behavior: 'smooth' })
        return
      }

      if (Date.now() - startedAt >= timeout) {
        resolve({ top: 0 })
        return
      }

      window.setTimeout(findTarget, HASH_SCROLL_INTERVAL)
    }

    window.setTimeout(findTarget, 0)
  })
}

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/views/Products.vue'),
    meta: { title: '全部商品' }
  },
  {
    path: '/products/:slug',
    name: 'ProductDetail',
    component: () => import('@/views/ProductDetail.vue'),
    meta: { title: '商品详情' }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/views/Cart.vue'),
    meta: { title: '购物车' }
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('@/views/Checkout.vue'),
    meta: { title: '确认订单' }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/views/Orders.vue'),
    meta: { title: '我的订单', requiresAuth: true }
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('@/views/OrderDetail.vue'),
    meta: { title: '订单详情', requiresAuth: true }
  },
  {
    path: '/sandbox/orders/:id',
    name: 'SandboxOrderDetail',
    component: () => import('@/views/OrderDetail.vue'),
    meta: { title: '沙箱订单支付', requiresAuth: true, sandboxPayment: true }
  },
  {
    path: '/user',
    name: 'User',
    component: () => import('@/views/User.vue'),
    meta: { title: '个人中心', requiresAuth: true },
    redirect: '/user/profile',
    children: [
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/user/Profile.vue'),
        meta: { title: '个人信息' }
      },
      {
        path: 'addresses',
        name: 'UserAddresses',
        component: () => import('@/views/user/Addresses.vue'),
        meta: { title: '收货地址' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', guest: true }
  },
  {
    path: '/diy',
    name: 'DIY',
    component: () => import('@/views/DIY.vue'),
    meta: { title: 'DIY装机' }
  },
  {
    path: '/customize',
    redirect: to => ({ name: 'DIY', query: to.query, hash: to.hash }),
    meta: { title: 'DIY装机' }
  },
  {
    path: '/store',
    name: 'Store',
    component: () => import('@/views/Store.vue'),
    meta: { title: '武汉线下门店' }
  },
  {
    path: '/services',
    name: 'Services',
    component: () => import('@/views/Services.vue'),
    meta: { title: '服务协议中心' }
  },
  // 管理后台
  {
    path: '/admin',
    component: () => import('@/views/admin/Layout.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '数据概览' }
      },
      {
        path: 'orders',
        name: 'AdminOrders',
        component: () => import('@/views/admin/Orders.vue'),
        meta: { title: '订单管理' }
      },
      {
        path: 'products',
        name: 'AdminProducts',
        component: () => import('@/views/admin/Products.vue'),
        meta: { title: '商品管理' }
      },
      {
        path: 'assets',
        name: 'AdminAssets',
        component: () => import('@/views/admin/Assets.vue'),
        meta: { title: '素材库' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户管理' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return resolveHashScroll(to.hash)
    }
    return { top: 0 }
  }
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '胖虫科技'} - 胖虫科技`
  // Public catalog and DIY routes can render while the cookie session is
  // restored. Protected, guest, cart, and checkout routes still wait so their
  // access and cart identity decisions use the restored session.
  const userStore = useUserStore()
  const session = userStore.hydrateSession()
  const needsSession = to.meta.requiresAuth || to.meta.requiresAdmin || to.meta.guest
    || to.name === 'Cart' || to.name === 'Checkout'
  if (needsSession) await session

  // A returning admin still reaches the dashboard after background restore.
  // isReady() ensures the initial public navigation has committed first.
  if (to.name === 'Home') {
    if (userStore.isAdmin) {
      next({ name: 'AdminDashboard' })
      return
    }
    void session.then(async () => {
      await router.isReady()
      if (router.currentRoute.value.name !== 'Home' || !userStore.isLoggedIn) return
      try {
        if (!userStore.user) await userStore.fetchProfile()
        if (userStore.isAdmin) {
          await router.replace({ name: 'AdminDashboard' })
        }
      } catch { /* ignore */ }
    }).catch(() => { /* anonymous sessions keep the public home page */ })
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth || to.meta.requiresAdmin) {
    if (!userStore.isLoggedIn) {
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 确保用户资料已加载（解决竞态条件）
    if (!userStore.user) {
      try {
        await userStore.fetchProfile()
      } catch (e) {
        // 获取资料失败，token 可能已过期
        userStore.logout()
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }

    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && !userStore.isAdmin) {
      next({ name: 'Home' })
      return
    }
  }

  // 检查是否是游客页面（已登录用户不应访问登录/注册页）
  if (to.meta.guest) {
    if (userStore.isLoggedIn) {
      next({ name: 'Home' })
      return
    }
  }

  next()
})

export default router
