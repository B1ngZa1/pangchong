<template>
  <div class="min-h-screen bg-dark-950">
    <!-- 导航栏 -->
    <AppNavbar />

    <!-- 主内容 -->
    <main>
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
  transition: opacity 0.2s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
