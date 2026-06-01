<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">个人中心</h1>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- 侧边栏 -->
        <div class="space-y-2">
          <router-link to="/user/profile" class="block px-4 py-3 rounded-lg hover:bg-dark-800 transition-colors"
            :class="{ 'bg-dark-800 text-primary-500': $route.path === '/user/profile' }">个人信息</router-link>
          <router-link to="/user/addresses" class="block px-4 py-3 rounded-lg hover:bg-dark-800 transition-colors"
            :class="{ 'bg-dark-800 text-primary-500': $route.path === '/user/addresses' }">收货地址</router-link>
          <router-link to="/orders" class="block px-4 py-3 rounded-lg hover:bg-dark-800 transition-colors">我的订单</router-link>
          <button @click="handleLogout" class="block w-full text-left px-4 py-3 rounded-lg hover:bg-dark-800 text-red-400 transition-colors">退出登录</button>
        </div>

        <!-- 内容区 -->
        <div class="md:col-span-3">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>
