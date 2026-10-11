<template>
  <div class="min-h-[75vh] bg-dark-950 flex items-center justify-center py-16 px-4">
    <div class="w-full max-w-md rounded-3xl border border-dark-800 bg-dark-900 p-6 sm:p-10 shadow-2xl">
      <p class="text-xs tracking-[0.25em] uppercase text-primary-500 mb-5">PANGCHONG · 开始装机计划</p>
      <h1 class="text-3xl font-bold mb-3">开启你的装备之旅</h1>
      <p class="text-sm text-dark-400 mb-8 leading-relaxed">创建账号，保存配置并同步订单进度。</p>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <DsField v-model="form.username" label="用户名" placeholder="3-50个字符" maxlength="50" autocomplete="username" required />
        <DsField v-model="form.email" label="邮箱" type="email" placeholder="name@example.com" autocomplete="email" required />
        <DsField v-model="form.password" label="密码" type="password" placeholder="至少8位，包含大写字母和数字" maxlength="100" autocomplete="new-password" :error="passwordErrors.join('；')" required />
        <DsField v-model="form.confirmPassword" label="确认密码" type="password" placeholder="再次输入密码" autocomplete="new-password" required />

        <DsAlert v-if="error" title="注册失败" :description="error" tone="danger" role="alert" />

        <DsButton type="submit" block :loading="loading">注册</DsButton>
      </form>

      <p class="text-center text-dark-400 mt-6">
        已有账号？<router-link :to="{ path: '/login', query: { redirect: redirectTarget } }" class="text-primary-500 hover:underline">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useCartStore } from '@/store/cart'
import { DsAlert, DsButton, DsField } from '@/design-system'
import { authErrorMessage, resolveAuthRedirect } from '@/utils/authNavigation'

const router = useRouter()
const route = useRoute()
const redirectTarget = computed(() => resolveAuthRedirect(route.query.redirect))
const userStore = useUserStore()
const cartStore = useCartStore()

const form = ref({ username: '', email: '', password: '', confirmPassword: '' })
const loading = ref(false)
const error = ref('')

const passwordErrors = computed(() => {
  const errs = []
  const pw = form.value.password
  if (!pw) return errs
  if (pw.length < 8) errs.push('密码长度不足8位')
  if (!/[A-Z]/.test(pw)) errs.push('需包含至少一个大写字母')
  if (!/\d/.test(pw)) errs.push('需包含至少一个数字')
  return errs
})

const handleRegister = async () => {
  if (loading.value) return
  error.value = ''

  if (form.value.username.trim().length < 3 || form.value.username.trim().length > 50) {
    error.value = '用户名需为 3–50 个字符'
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    error.value = '两次密码输入不一致'
    return
  }
  if (passwordErrors.value.length > 0) {
    error.value = '请修正密码格式'
    return
  }

  loading.value = true
  try {
    await userStore.register({
      username: form.value.username.trim(),
      email: form.value.email.trim(),
      password: form.value.password
    })
    await cartStore.mergeCart()
    await router.push(redirectTarget.value)
  } catch (e) {
    error.value = authErrorMessage(e, '注册失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>
