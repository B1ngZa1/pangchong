<template>
  <div class="min-h-screen bg-dark-950 flex">
    <!-- 侧边栏 -->
    <aside class="hidden lg:flex w-64 bg-dark-900 border-r border-dark-800 flex-col flex-shrink-0">
      <!-- Logo -->
      <div class="h-16 flex items-center gap-2 px-6 border-b border-dark-800">
        <span class="text-2xl">🐛</span>
        <span class="text-lg font-bold text-white">胖虫管理后台</span>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors"
          :class="isActive(item.path) ? 'bg-primary-500/10 text-primary-500' : 'text-dark-400 hover:text-white hover:bg-dark-800'"
        >
          <i :class="item.icon" class="w-5 text-center"></i>
          <span>{{ item.name }}</span>
          <span v-if="item.badge" class="ml-auto text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded-full">{{ item.badge }}</span>
        </router-link>
      </nav>

      <!-- 底部 -->
      <div class="p-4 border-t border-dark-800">
        <button @click="handleLogout" class="flex items-center gap-2 text-dark-500 hover:text-red-400 text-sm transition-colors w-full">
          <i class="fas fa-sign-out-alt text-xs"></i>
          <span>退出登录</span>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- 顶部栏 -->
      <header class="min-h-16 bg-dark-900 border-b border-dark-800 flex items-center justify-between gap-4 px-4 lg:px-6 py-3 flex-shrink-0">
        <h1 class="text-lg font-semibold">{{ currentPageTitle }}</h1>
        <div class="flex items-center gap-4">
          <span class="text-sm text-dark-400">{{ userStore.user?.nickname || userStore.user?.username || '管理员' }}</span>
          <button @click="handleLogout" class="text-dark-500 hover:text-red-400 text-sm transition-colors">
            <i class="fas fa-sign-out-alt mr-1"></i>退出
          </button>
        </div>
      </header>

      <nav class="lg:hidden flex gap-2 overflow-x-auto border-b border-dark-800 bg-dark-900 px-4 py-2" aria-label="后台导航">
        <router-link
          v-for="item in menuItems"
          :key="`mobile-${item.path}`"
          :to="item.path"
          class="flex min-h-11 flex-shrink-0 items-center gap-2 rounded-lg px-3 text-xs font-semibold"
          :class="isActive(item.path) ? 'bg-primary-500/10 text-primary-500' : 'text-dark-400 hover:bg-dark-800 hover:text-white'"
        >
          <i :class="item.icon" aria-hidden="true"></i>
          <span>{{ item.name }}</span>
        </router-link>
      </nav>

      <!-- 页面内容 -->
      <main class="flex-1 min-w-0 overflow-y-auto p-4 lg:p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const menuItems = [
  { name: '数据概览', path: '/admin/dashboard', icon: 'fas fa-chart-pie' },
  { name: '订单管理', path: '/admin/orders', icon: 'fas fa-shopping-bag' },
  { name: '商品管理', path: '/admin/products', icon: 'fas fa-box' },
  { name: '素材库', path: '/admin/assets', icon: 'fas fa-images' },
  { name: '用户管理', path: '/admin/users', icon: 'fas fa-users' },
]

const currentPageTitle = computed(() => {
  const item = menuItems.find(m => route.path.startsWith(m.path))
  return item?.name || '管理后台'
})

function isActive(path) {
  return route.path.startsWith(path)
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>
