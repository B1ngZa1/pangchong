<template>
  <nav class="sticky top-0 z-50 border-b border-dark-800 bg-dark-950/92 backdrop-blur-xl" @mouseleave="activeMenu = null">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <router-link to="/" class="flex items-center gap-3">
        <span class="inline-flex h-7 w-7 items-center justify-center rounded-md border border-primary-500/60 bg-primary-500/10">
          <span class="h-3 w-3 rounded-sm bg-primary-500" />
        </span>
        <span class="text-base font-semibold tracking-[0.16em] text-white">PANGCHONG</span>
      </router-link>

      <div class="hidden h-full items-center gap-7 md:flex">
        <div
          v-for="item in navItems"
          :key="item.name"
          class="flex h-full items-center"
          @mouseenter="activeMenu = item.children ? item.name : null"
        >
          <router-link
            :to="item.to"
            class="text-sm text-dark-300 transition-colors hover:text-white"
            active-class="text-primary-500"
          >
            {{ item.name }}
          </router-link>
        </div>
      </div>

      <div class="flex items-center gap-2 sm:gap-4" @mouseenter="activeMenu = null">
        <button
          @click="toggleSearch"
          class="rounded-md p-2 text-dark-300 transition-colors hover:bg-dark-800 hover:text-white"
          aria-label="搜索商品"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.5-5.5m2.5-5.5a8 8 0 11-16 0 8 8 0 0116 0z" />
          </svg>
        </button>

        <router-link
          to="/cart"
          class="relative rounded-md p-2 text-dark-300 transition-colors hover:bg-dark-800 hover:text-white"
          aria-label="购物车"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          <span
            v-if="cartStore.totalItems > 0"
            class="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-primary-500 px-1 text-[11px] font-semibold text-dark-950"
          >
            {{ cartStore.totalItems > 99 ? '99+' : cartStore.totalItems }}
          </span>
        </router-link>

        <div v-if="userStore.isLoggedIn" class="relative">
          <button
            @click="showUserMenu = !showUserMenu"
            class="flex items-center gap-2 rounded-md p-2 text-dark-300 transition-colors hover:bg-dark-800 hover:text-white"
            aria-label="用户菜单"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span class="hidden text-sm sm:inline">{{ userStore.user?.nickname || '用户' }}</span>
          </button>

          <transition name="dropdown">
            <div
              v-if="showUserMenu"
              class="absolute right-0 mt-2 w-44 overflow-hidden rounded-lg border border-dark-700 bg-dark-900 shadow-xl"
            >
              <router-link to="/orders" class="menu-item" @click="showUserMenu = false">我的订单</router-link>
              <router-link to="/user/profile" class="menu-item" @click="showUserMenu = false">个人中心</router-link>
              <router-link v-if="userStore.isAdmin" to="/admin/dashboard" class="menu-item text-primary-400" @click="showUserMenu = false">管理后台</router-link>
              <button @click="handleLogout" class="menu-item w-full text-left text-red-400">退出登录</button>
            </div>
          </transition>
        </div>

        <div v-else class="hidden items-center gap-2 sm:flex">
          <router-link to="/login" class="px-3 py-2 text-sm text-dark-300 transition-colors hover:text-white">登录</router-link>
          <router-link to="/register" class="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-dark-950 transition-colors hover:bg-primary-600">注册</router-link>
        </div>

        <button
          @click="toggleMobileMenu"
          class="rounded-md p-2 text-dark-300 transition-colors hover:bg-dark-800 hover:text-white md:hidden"
          aria-label="移动端菜单"
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!showMobileMenu" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <transition name="mega">
      <div v-if="activeNav?.children" class="hidden border-t border-dark-800 bg-dark-950/96 shadow-2xl shadow-black/25 backdrop-blur-xl md:block">
        <div class="mx-auto grid max-w-7xl grid-cols-[1.1fr_1fr_1fr] gap-12 px-4 py-10 sm:px-6 lg:px-8">
          <div>
            <p class="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-dark-500">{{ activeNav.eyebrow }}</p>
            <div class="space-y-3">
              <router-link
                v-for="child in activeNav.children"
                :key="child.name"
                :to="child.to"
                class="block text-3xl font-semibold leading-tight text-white transition-colors hover:text-primary-400"
              >
                {{ child.name }}
              </router-link>
            </div>
          </div>

          <div v-for="group in activeNav.groups" :key="group.title">
            <p class="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-dark-500">{{ group.title }}</p>
            <div class="space-y-3">
              <router-link
                v-for="link in group.links"
                :key="link.name"
                :to="link.to"
                class="block text-sm font-medium text-dark-300 transition-colors hover:text-white"
              >
                {{ link.name }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <transition name="slide-down">
      <div v-if="showSearch" class="border-t border-dark-800 bg-dark-900/95">
        <div class="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索产品、型号或关键词"
              class="input pr-10"
              @keyup.enter="handleSearch"
            >
            <button
              @click="handleSearch"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-dark-400 transition-colors hover:text-white"
              aria-label="提交搜索"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.5-5.5m2.5-5.5a8 8 0 11-16 0 8 8 0 0116 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="slide-down">
      <div v-if="showMobileMenu" class="border-t border-dark-800 bg-dark-900 md:hidden">
        <div class="space-y-3 px-4 py-4">
          <div v-for="item in navItems" :key="item.name">
            <router-link
              :to="item.to"
              class="block rounded-md px-3 py-2 text-sm font-medium text-dark-200 transition-colors hover:bg-dark-800 hover:text-white"
              active-class="bg-dark-800 text-primary-500"
              @click="showMobileMenu = false"
            >
              {{ item.name }}
            </router-link>
            <div v-if="item.children" class="mt-1 grid grid-cols-2 gap-1 pl-3">
              <router-link
                v-for="child in item.children"
                :key="child.name"
                :to="child.to"
                class="rounded-md px-3 py-2 text-xs text-dark-400 hover:bg-dark-800 hover:text-white"
                @click="showMobileMenu = false"
              >
                {{ child.name }}
              </router-link>
            </div>
          </div>
          <router-link v-if="!userStore.isLoggedIn" to="/login" class="block rounded-md px-3 py-2 text-sm text-dark-300 transition-colors hover:bg-dark-800 hover:text-white" @click="showMobileMenu = false">登录</router-link>
          <router-link v-if="!userStore.isLoggedIn" to="/register" class="block rounded-md bg-primary-500 px-3 py-2 text-sm font-medium text-dark-950" @click="showMobileMenu = false">注册</router-link>
        </div>
      </div>
    </transition>
  </nav>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore, useCartStore } from '@/store'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartStore = useCartStore()

const showSearch = ref(false)
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const activeMenu = ref(null)
const searchQuery = ref('')

const navItems = [
  {
    name: '商店',
    to: '/products',
    eyebrow: '探索商店',
    children: [
      { name: '全部产品', to: '/products' },
      { name: '热门整机', to: '/products?tag=hot' },
      { name: '线下门店', to: '/store' }
    ],
    groups: [
      {
        title: '购买方式',
        links: [
          { name: '产品定制', to: '/customize' },
          { name: 'DIY 装机', to: '/diy' },
          { name: '购物车', to: '/cart' }
        ]
      },
      {
        title: '购买支持',
        links: [
          { name: '配送说明', to: '/services#delivery' },
          { name: '保修政策', to: '/services#warranty' },
          { name: '常见问题', to: '/services#faq' }
        ]
      }
    ]
  },
  {
    name: '电脑整机',
    to: '/products',
    eyebrow: '选择整机',
    children: [
      { name: '游戏本', to: '/products?category=gaming-laptop' },
      { name: '轻薄本', to: '/products?category=thin-laptop' },
      { name: '台式主机', to: '/products?category=desktop' },
      { name: '工作站', to: '/products?category=workstation' }
    ],
    groups: [
      {
        title: '推荐场景',
        links: [
          { name: '电竞游戏', to: '/products?scene=gaming' },
          { name: '设计渲染', to: '/products?scene=creator' },
          { name: '学习办公', to: '/products?scene=office' }
        ]
      },
      {
        title: '服务',
        links: [
          { name: '配置咨询', to: '/services#tech-support' },
          { name: '线下体验', to: '/store' },
          { name: '订单查询', to: '/orders' }
        ]
      }
    ]
  },
  {
    name: 'DIY 配件',
    to: '/diy',
    eyebrow: '探索 DIY 配件',
    children: [
      { name: 'CPU', to: '/diy?part=cpu' },
      { name: 'GPU 显卡', to: '/diy?part=gpu' },
      { name: '主板', to: '/diy?part=motherboard' },
      { name: '内存', to: '/diy?part=memory' },
      { name: 'SSD 硬盘', to: '/diy?part=ssd' },
      { name: '电源', to: '/diy?part=psu' },
      { name: '机箱', to: '/diy?part=case' },
      { name: '散热器', to: '/diy?part=cooling' }
    ],
    groups: [
      {
        title: '装机工具',
        links: [
          { name: '在线装机', to: '/diy' },
          { name: '产品定制', to: '/customize' },
          { name: '兼容性咨询', to: '/services#tech-support' }
        ]
      },
      {
        title: '常用说明',
        links: [
          { name: '配送说明', to: '/services#delivery' },
          { name: '保修政策', to: '/services#warranty' },
          { name: '服务协议', to: '/services' }
        ]
      }
    ]
  },
  {
    name: '服务支持',
    to: '/services',
    eyebrow: '获得支持',
    children: [
      { name: '技术支持', to: '/services#tech-support' },
      { name: '保修政策', to: '/services#warranty' },
      { name: '配送说明', to: '/services#delivery' },
      { name: '常见问题', to: '/services#faq' }
    ],
    groups: [
      {
        title: '协议',
        links: [
          { name: '隐私政策', to: '/services#privacy' },
          { name: '用户协议', to: '/services#user-agreement' },
          { name: 'Cookie 设置', to: '/services#cookie-settings' }
        ]
      },
      {
        title: '门店',
        links: [
          { name: '武汉线下门店', to: '/store' },
          { name: '售后咨询', to: '/services#tech-support' },
          { name: '订单中心', to: '/orders' }
        ]
      }
    ]
  }
]

const activeNav = computed(() => navItems.find((item) => item.name === activeMenu.value))

watch(() => route.fullPath, () => {
  showSearch.value = false
  showUserMenu.value = false
  showMobileMenu.value = false
  activeMenu.value = null
})

function handleSearch() {
  const keyword = searchQuery.value.trim()
  if (!keyword) return
  router.push({ path: '/products', query: { keyword } })
  showSearch.value = false
  searchQuery.value = ''
}

function toggleSearch() {
  showSearch.value = !showSearch.value
  showMobileMenu.value = false
  activeMenu.value = null
}

function toggleMobileMenu() {
  showMobileMenu.value = !showMobileMenu.value
  showSearch.value = false
  activeMenu.value = null
}

function handleLogout() {
  userStore.logout()
  showUserMenu.value = false
  router.push('/')
}

function handleOutsideClick(e) {
  if (!(e.target instanceof HTMLElement)) return
  if (!e.target.closest('.relative')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.menu-item {
  @apply block px-4 py-2 text-sm text-dark-300 transition-colors hover:bg-dark-800 hover:text-white;
}

.dropdown-enter-active,
.dropdown-leave-active,
.mega-enter-active,
.mega-leave-active,
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to,
.mega-enter-from,
.mega-leave-to,
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
