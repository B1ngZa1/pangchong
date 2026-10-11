<template>
  <div class="min-h-screen bg-dark-950">
    <a class="skip-link" href="#main-content">跳转到主要内容</a>
    <!-- 导航栏 -->
    <AppNavbar />

    <!-- 主内容 -->
    <main id="main-content" tabindex="-1">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 页脚 -->
    <AppFooter />

    <!-- Toast 通知 -->
    <Toast />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/store'
import AppNavbar from '@/components/AppNavbar.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'

const cartStore = useCartStore()

onMounted(() => {
  cartStore.fetchCart()
})
</script>

<style>
/* 页面过渡动画 */
.page-enter-active,
.page-leave-active {
  transition: opacity var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}

.skip-link {
  position: fixed;
  z-index: 1200;
  top: var(--pc-space-3);
  left: var(--pc-space-3);
  padding: var(--pc-space-3) var(--pc-space-4);
  border-radius: var(--pc-radius-md);
  background: var(--pc-color-semantic-action-primary);
  color: var(--pc-color-semantic-text-inverse);
  font-size: var(--pc-font-size-sm);
  font-weight: var(--pc-font-weight-bold);
  transform: translateY(-160%);
  transition: transform var(--pc-motion-duration-fast) var(--pc-motion-ease-standard);
}

.skip-link:focus-visible {
  outline: 2px solid var(--pc-color-semantic-border-focus);
  outline-offset: 3px;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  .skip-link,
  .page-enter-active,
  .page-leave-active { transition: none; }
}
</style>
