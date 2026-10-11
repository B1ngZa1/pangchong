<template>
  <nav class="app-navbar-shell relative sticky top-0 z-50" @mouseleave="activeMenu = null">
    <div class="app-navbar__inner mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <router-link to="/" class="app-navbar__brand flex items-center gap-3">
        <span class="inline-flex h-7 w-7 items-center justify-center rounded-md border border-primary-500/60 bg-primary-500/10">
          <span class="h-3 w-3 rounded-sm bg-primary-500" />
        </span>
        <span class="app-navbar__wordmark text-base font-semibold tracking-[0.16em] text-white">PANGCHONG</span>
      </router-link>

      <div class="hidden h-full items-center gap-7 md:flex">
        <div
          v-for="item in navItems"
          :key="item.name"
          class="flex h-full items-center"
          @mouseenter="activeMenu = item.children ? item.name : null"
          @focusin="activeMenu = item.children ? item.name : null"
        >
          <router-link
            :to="item.to"
            :data-qa="item.name === '商店' ? 'nav-shop-link' : null"
            :aria-current="isNavItemActive(item) ? 'page' : undefined"
            class="relative flex h-full items-center text-sm text-dark-300 transition-colors after:absolute after:bottom-0 after:left-0 after:h-px after:w-full after:origin-center after:scale-x-0 after:bg-primary-500 after:transition-transform after:duration-[var(--pc-motion-duration-normal)] hover:text-white hover:after:scale-x-100"
            active-class="text-primary-500"
          >
            {{ item.name }}
          </router-link>
        </div>
      </div>

      <div class="app-navbar__actions flex items-center gap-2 sm:gap-4" @mouseenter="activeMenu = null">
        <form class="navbar-search" @submit.prevent="handleSearch">
          <svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.5-5.5m2.5-5.5a8 8 0 11-16 0 8 8 0 0116 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索产品"
            aria-label="搜索产品"
            @keydown.enter.prevent="handleSearch"
          >
          <button type="submit" aria-label="提交搜索">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </button>
        </form>

        <DsIconButton
          ref="mobileSearchTrigger"
          label="搜索商品"
          class="mobile-search-trigger"
          aria-controls="mobile-search-panel"
          :aria-expanded="showSearch"
          @click="toggleSearch"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.5-5.5m2.5-5.5a8 8 0 11-16 0 8 8 0 0116 0z" />
          </svg>
        </DsIconButton>

        <DsContrastToggle />

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

        <DsMenu v-if="userStore.isLoggedIn" v-model:open="showUserMenu" label="用户菜单" class="app-navbar__user-menu">
          <template #trigger="{ triggerProps }">
            <button
              v-bind="triggerProps"
              class="flex items-center gap-2 rounded-md p-2 text-dark-300 transition-colors hover:bg-dark-800 hover:text-white"
              aria-label="用户菜单"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span class="hidden text-sm sm:inline">{{ userStore.user?.nickname || '用户' }}</span>
            </button>
          </template>

          <router-link to="/orders" role="menuitem" class="menu-item">我的订单</router-link>
          <router-link to="/user/profile" role="menuitem" class="menu-item">个人中心</router-link>
          <router-link v-if="userStore.isAdmin" to="/admin/dashboard" role="menuitem" class="menu-item text-primary-400">管理后台</router-link>
          <button type="button" role="menuitem" @click="handleLogout" class="menu-item w-full text-left text-red-400">退出登录</button>
        </DsMenu>

        <div v-else class="hidden items-center gap-2 sm:flex">
          <router-link to="/login" class="px-3 py-2 text-sm text-dark-300 transition-colors hover:text-white">登录</router-link>
          <router-link to="/register" class="rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-dark-950 transition-colors hover:bg-primary-600">注册</router-link>
        </div>

        <button
          ref="mobileMenuTrigger"
          @click="toggleMobileMenu"
          class="rounded-md p-2 text-dark-300 transition-colors hover:bg-dark-800 hover:text-white md:hidden"
          aria-label="移动端菜单"
          aria-controls="mobile-navigation"
          :aria-expanded="showMobileMenu"
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!showMobileMenu" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <transition name="nav-fog">
      <div
        v-if="activeNav?.children"
        data-qa="navbar-fog"
        class="app-navbar__fog pointer-events-none fixed inset-x-0 bottom-0 top-16 hidden md:block"
      />
    </transition>

    <transition name="mega">
      <div v-if="activeNav?.children" data-qa="navbar-mega" class="app-navbar__mega absolute left-0 right-0 top-full hidden overflow-hidden md:block">
        <div class="mx-auto grid max-w-7xl grid-cols-[1.08fr_1fr_1fr] gap-8 px-4 py-7 sm:px-6 lg:px-8">
          <div class="app-navbar__mega-primary rounded-lg p-5">
            <p class="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-dark-500">{{ activeNav.eyebrow }}</p>
            <div class="space-y-1">
              <router-link
                v-for="child in activeNav.children"
                :key="child.name"
                :to="child.to"
                :aria-current="isNavItemActive(child) ? 'page' : undefined"
                class="app-navbar__mega-link app-navbar__mega-link--featured block rounded-md px-3 py-2 text-2xl font-semibold leading-tight text-white transition-colors"
              >
                {{ child.name }}
              </router-link>
            </div>
          </div>

          <div v-for="group in activeNav.groups" :key="group.title" class="app-navbar__mega-group rounded-lg p-5">
            <p class="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-dark-500">{{ group.title }}</p>
            <div class="space-y-1">
              <router-link
                v-for="link in group.links"
                :key="link.name"
                  :to="link.to"
                  :aria-current="isNavItemActive(link) ? 'page' : undefined"
                  class="app-navbar__mega-link block rounded-md px-3 py-2 text-sm font-medium text-dark-300 transition-colors"
              >
                {{ link.name }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <transition name="slide-down">
      <div v-if="showSearch" id="mobile-search-panel" ref="mobileSearchPanel" class="border-t border-dark-800 bg-dark-900/95">
        <div class="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <DsSearchField
            v-model="searchQuery"
            label="搜索产品、型号或关键词"
            placeholder="输入产品、型号或关键词"
            @submit="handleSearch"
          />
        </div>
      </div>
    </transition>

    <transition name="slide-down">
      <div
        v-if="showMobileMenu"
        id="mobile-navigation"
        ref="mobileMenuPanel"
        class="border-t border-dark-800 bg-dark-900 md:hidden"
        role="region"
        aria-label="移动端导航"
      >
        <div class="space-y-3 px-4 py-4">
          <div v-for="item in navItems" :key="item.name">
            <router-link
              :to="item.to"
              :aria-current="isNavItemActive(item) ? 'page' : undefined"
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
                :aria-current="isNavItemActive(child) ? 'page' : undefined"
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
import { computed, nextTick, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore, useCartStore } from '@/store'
import { DsContrastToggle, DsIconButton, DsMenu, DsSearchField } from '@/design-system'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartStore = useCartStore()

const isNavItemActive = (item) => {
  if (!item?.to || item.activeMode === 'never') return false

  const target = router.resolve(item.to)
  const isSamePathOrDescendant = route.path === target.path || (target.path !== '/' && route.path.startsWith(`${target.path}/`))

  if (item.activeMode === 'path') return isSamePathOrDescendant
  if (item.activeMode === 'base') {
    return isSamePathOrDescendant && Object.keys(route.query).length === 0 && !route.hash
  }
  if (item.activeMode === 'query') {
    return route.path === target.path && Object.keys(route.query).length > 0
  }

  if (route.path !== target.path || route.hash !== target.hash) return false
  const targetQuery = target.query || {}
  const currentQuery = route.query || {}
  const targetKeys = Object.keys(targetQuery)
  const currentKeys = Object.keys(currentQuery)
  return targetKeys.length === currentKeys.length && targetKeys.every((key) => JSON.stringify(targetQuery[key]) === JSON.stringify(currentQuery[key]))
}

const showSearch = ref(false)
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const activeMenu = ref(null)
const searchQuery = ref('')
const mobileMenuTrigger = ref(null)
const mobileMenuPanel = ref(null)
const mobileSearchTrigger = ref(null)
const mobileSearchPanel = ref(null)

const navItems = [
  {
    name: '商店',
    to: '/products',
    activeMode: 'base',
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
          { name: '选购商品', to: '/products', activeMode: 'never' },
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
    activeMode: 'query',
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
    activeMode: 'path',
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
          { name: '配件目录', to: '/products' },
          { name: '兼容性咨询', to: '/services#tech-support' }
        ]
      },
      {
        title: '常用说明',
        links: [
          { name: '配送说明', to: '/services#delivery' },
          { name: '保修政策', to: '/services#warranty' },
          { name: '服务协议', to: '/services#user-agreement' }
        ]
      }
    ]
  },
  {
    name: '服务支持',
    to: '/services',
    activeMode: 'path',
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
          { name: '售后咨询', to: '/services#tech-support', activeMode: 'never' },
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

function mobileMenuFocusables() {
  return [...mobileMenuPanel.value?.querySelectorAll('a[href], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])') || []]
}

async function closeMobileMenu({ restoreFocus = true } = {}) {
  const shouldRestoreFocus = restoreFocus && mobileMenuPanel.value?.contains(document.activeElement)
  showMobileMenu.value = false
  if (shouldRestoreFocus) {
    await nextTick()
    mobileMenuTrigger.value?.focus()
  }
}

async function closeMobileSearch({ restoreFocus = true } = {}) {
  const shouldRestoreFocus = restoreFocus && mobileSearchPanel.value?.contains(document.activeElement)
  showSearch.value = false
  if (shouldRestoreFocus) {
    await nextTick()
    mobileSearchTrigger.value?.$el?.focus?.()
  }
}

async function handleDocumentKeydown(event) {
  if (event.key === 'Escape') {
    if (showMobileMenu.value) {
      event.preventDefault()
      closeMobileMenu()
      return
    }
    if (showSearch.value) {
      event.preventDefault()
      await closeMobileSearch()
      return
    }
    if (showUserMenu.value) {
      event.preventDefault()
      showUserMenu.value = false
    }
    return
  }

  if (event.key !== 'Tab' || !showMobileMenu.value) return
  const items = mobileMenuFocusables()
  if (!items.length) return
  const first = items[0]
  const last = items[items.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

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

watch(showMobileMenu, async (isOpen) => {
  if (!isOpen) return
  await nextTick()
  mobileMenuFocusables()[0]?.focus()
})

watch(showSearch, async (isOpen) => {
  if (!isOpen) return
  await nextTick()
  mobileSearchPanel.value?.querySelector('input, button, [tabindex]:not([tabindex="-1"])')?.focus()
})

onMounted(() => {
  document.addEventListener('keydown', handleDocumentKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleDocumentKeydown)
})
</script>

<style scoped>
.app-navbar-shell {
  border-bottom: 1px solid rgb(var(--pc-color-dark-50-rgb) / 0.1);
  background: rgb(var(--pc-color-dark-950-rgb) / 0.82);
  box-shadow: 0 1px 0 rgb(var(--pc-color-dark-50-rgb) / 0.04);
  backdrop-filter: blur(20px);
}

.app-navbar__fog {
  background: rgb(var(--pc-color-dark-950-rgb) / 0.42);
  backdrop-filter: blur(6px);
}

.app-navbar__mega {
  border-top: 1px solid rgb(var(--pc-color-dark-50-rgb) / 0.1);
  background: linear-gradient(180deg, rgb(var(--pc-color-dark-900-rgb) / 0.94), rgb(var(--pc-color-dark-950-rgb) / 0.9));
  box-shadow: 0 28px 80px rgb(var(--pc-color-dark-950-rgb) / 0.46);
  backdrop-filter: blur(20px);
}

.app-navbar__mega-primary {
  border: 1px solid rgb(var(--pc-color-dark-50-rgb) / 0.1);
  background: rgb(var(--pc-color-dark-50-rgb) / 0.035);
  box-shadow: inset 0 1px 0 rgb(var(--pc-color-dark-50-rgb) / 0.05);
  backdrop-filter: blur(12px);
}

.app-navbar__mega-group {
  border: 1px solid rgb(var(--pc-color-dark-50-rgb) / 0.07);
  background: rgb(var(--pc-color-dark-50-rgb) / 0.025);
}

.app-navbar__mega-link:hover,
.app-navbar__mega-link:focus-visible {
  background: rgb(var(--pc-color-dark-50-rgb) / 0.055);
  color: var(--pc-color-dark-50);
  backdrop-filter: blur(8px);
}

.app-navbar__mega-link--featured:hover,
.app-navbar__mega-link--featured:focus-visible {
  background: rgb(var(--pc-color-dark-50-rgb) / 0.06);
  color: var(--pc-color-brand-400);
}

.menu-item {
  @apply block px-4 py-2 text-sm text-dark-300 transition-colors hover:bg-dark-800 hover:text-white;
}

.navbar-search {
  display: none;
  width: 244px;
  height: 38px;
  align-items: center;
  gap: 8px;
  border: 1px solid rgb(var(--pc-color-dark-400-rgb) / 0.18);
  border-radius: var(--pc-radius-md);
  background: rgb(var(--pc-color-dark-900-rgb) / 0.48);
  padding: 0 11px;
  color: var(--pc-color-dark-400);
  box-shadow: inset 0 1px 0 rgb(var(--pc-color-dark-50-rgb) / 0.035);
}

.navbar-search:focus-within {
  border-color: rgb(var(--pc-color-brand-500-rgb) / 0.55);
  color: var(--pc-color-brand-500);
}

.navbar-search input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--pc-color-dark-50);
  font-size: var(--pc-font-size-sm);
}

.navbar-search input::placeholder {
  color: var(--pc-color-dark-500);
}

.navbar-search button {
  display: inline-flex;
  width: 28px;
  height: 28px;
  flex: 0 0 28px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: var(--pc-radius-sm);
  background: transparent;
  color: var(--pc-color-dark-400);
  transition: background-color var(--pc-motion-duration-fast) var(--pc-motion-ease-standard), color var(--pc-motion-duration-fast) var(--pc-motion-ease-standard);
}

.navbar-search button:hover,
.navbar-search button:focus-visible {
  background: rgb(var(--pc-color-brand-500-rgb) / 0.14);
  color: var(--pc-color-brand-500);
  outline: 0;
}

.navbar-search button svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

@media (max-width: 639px) {
  .app-navbar__inner { gap: var(--pc-space-2); padding-inline: var(--pc-space-3); }
  .app-navbar__brand { min-width: 0; flex: 1 1 auto; gap: var(--pc-space-2); }
  .app-navbar__wordmark { overflow: hidden; font-size: var(--pc-font-size-sm); letter-spacing: .1em; text-overflow: ellipsis; white-space: nowrap; }
  .app-navbar__actions { flex: 0 0 auto; gap: var(--pc-space-1); }
  .app-navbar__actions > * { flex: 0 0 auto; }
}

@media (min-width: 1024px) {
  .mobile-search-trigger {
    display: none;
  }
  .navbar-search {
    display: flex;
  }
}

.dropdown-enter-active,
.dropdown-leave-active,
.slide-down-enter-active,
.slide-down-leave-active {
  transition: opacity var(--pc-motion-duration-normal) var(--pc-motion-ease-standard), transform var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}

.dropdown-enter-from,
.dropdown-leave-to,
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.mega-enter-active,
.mega-leave-active {
  transition: opacity var(--pc-motion-duration-fast) var(--pc-motion-ease-standard), filter var(--pc-motion-duration-fast) var(--pc-motion-ease-standard);
}

.mega-enter-from,
.mega-leave-to {
  opacity: 0;
  filter: blur(10px);
}

.nav-fog-enter-active,
.nav-fog-leave-active {
  transition: opacity var(--pc-motion-duration-fast) var(--pc-motion-ease-standard), backdrop-filter var(--pc-motion-duration-fast) var(--pc-motion-ease-standard);
}

.nav-fog-enter-from,
.nav-fog-leave-to {
  opacity: 0;
  backdrop-filter: blur(0);
}
</style>
