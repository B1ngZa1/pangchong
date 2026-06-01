<template>
  <div class="min-h-screen bg-dark-950 flex items-center justify-center py-12 px-4">
    <div class="card w-full max-w-md p-8">
      <h1 class="text-2xl font-bold text-center mb-8">注册</h1>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <div>
          <label class="block text-sm text-dark-400 mb-2">用户名</label>
          <input v-model="form.username" type="text" class="input" placeholder="3-50个字符" required />
        </div>
        <div>
          <label class="block text-sm text-dark-400 mb-2">邮箱</label>
          <input v-model="form.email" type="email" class="input" placeholder="your@email.com" required />
        </div>
        <div>
          <label class="block text-sm text-dark-400 mb-2">密码</label>
          <input v-model="form.password" type="password" class="input" placeholder="至少8位，包含大写字母和数字" required />
          <p v-if="passwordErrors.length" class="mt-1 space-y-0.5">
            <span v-for="(msg, i) in passwordErrors" :key="i" class="block text-red-400 text-xs">{{ msg }}</span>
          </p>
        </div>
        <div>
          <label class="block text-sm text-dark-400 mb-2">确认密码</label>
          <input v-model="form.confirmPassword" type="password" class="input" placeholder="再次输入密码" required />
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="text-center text-dark-400 mt-6">
        已有账号？<router-link to="/login" class="text-primary-500 hover:underline">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useCartStore } from '@/store/cart'

const router = useRouter()
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
  error.value = ''

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
      username: form.value.username,
      email: form.value.email,
      password: form.value.password
    })
    await cartStore.mergeCart()
    router.push('/')
  } catch (e) {
    error.value = e.displayMessage || e.response?.data?.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
