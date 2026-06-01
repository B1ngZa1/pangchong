<template>
  <div class="card p-6">
    <h2 class="text-xl font-bold mb-6">个人信息</h2>

    <div v-if="loading" class="text-dark-400">加载中...</div>
    <form v-else @submit.prevent="handleUpdate" class="space-y-6">
      <div>
        <label class="block text-sm text-dark-400 mb-2">用户名</label>
        <input :value="userStore.user?.username" class="input" disabled />
      </div>
      <div>
        <label class="block text-sm text-dark-400 mb-2">邮箱</label>
        <input :value="userStore.user?.email" class="input" disabled />
      </div>
      <div>
        <label class="block text-sm text-dark-400 mb-2">昵称</label>
        <input v-model="form.nickname" class="input" />
      </div>
      <div>
        <label class="block text-sm text-dark-400 mb-2">手机号</label>
        <input v-model="form.phone" class="input" />
      </div>

      <p v-if="message" :class="success ? 'text-green-500' : 'text-red-500'">{{ message }}</p>

      <button type="submit" class="btn-primary" :disabled="saving">
        {{ saving ? '保存中...' : '保存修改' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import api from '@/api'

const userStore = useUserStore()
const form = ref({ nickname: '', phone: '' })
const loading = ref(true)
const saving = ref(false)
const message = ref('')
const success = ref(false)

onMounted(async () => {
  if (!userStore.user) {
    try {
      await userStore.fetchProfile()
    } catch (e) {
      console.warn('fetchProfile failed:', e)
    }
  }
  if (userStore.user) {
    form.value.nickname = userStore.user.nickname || ''
    form.value.phone = userStore.user.phone || ''
  }
  loading.value = false
})

const handleUpdate = async () => {
  saving.value = true
  message.value = ''
  try {
    const data = await api.put('/auth/me', form.value)
    userStore.user = data
    success.value = true
    message.value = '保存成功'
  } catch (e) {
    success.value = false
    message.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>
