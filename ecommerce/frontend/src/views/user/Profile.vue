<template>
  <div class="card p-6">
    <h2 class="text-xl font-bold mb-6">个人信息</h2>

    <DsAsyncState v-if="loading" state="loading" loading-label="正在加载个人信息" />
    <DsAsyncState v-else-if="loadError" state="error" error-title="个人信息加载失败" :error-description="loadError" @retry="loadProfile" />
    <form v-else @submit.prevent="handleUpdate" class="space-y-6">
      <DsField :model-value="userStore.user?.username || ''" label="用户名" disabled autocomplete="username" />
      <DsField :model-value="userStore.user?.email || ''" label="邮箱" disabled autocomplete="email" />
      <DsField v-model="form.nickname" label="昵称" maxlength="50" autocomplete="nickname" hint="选择一个你喜欢的称呼。" />
      <DsField v-model="form.phone" label="手机号" type="tel" maxlength="11" autocomplete="tel" hint="选填，用于订单联系。" />

      <DsAlert v-if="message" :title="success ? '保存成功' : '保存失败'" :description="message" :tone="success ? 'success' : 'danger'" :role="success ? 'status' : 'alert'" />

      <DsButton type="submit" :loading="saving">保存修改</DsButton>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { DsAlert, DsAsyncState, DsButton, DsField } from '@/design-system'
import { authErrorMessage } from '@/utils/authNavigation'

const userStore = useUserStore()
const form = ref({ nickname: '', phone: '' })
const loading = ref(true)
const saving = ref(false)
const message = ref('')
const success = ref(false)
const loadError = ref('')

async function loadProfile() {
  loading.value = true
  loadError.value = ''
  if (!userStore.user) {
    try {
      await userStore.fetchProfile()
    } catch (e) {
      loadError.value = authErrorMessage(e, '请检查网络后重试。')
    }
  }
  if (userStore.user) {
    form.value.nickname = userStore.user.nickname || ''
    form.value.phone = userStore.user.phone || ''
  }
  loading.value = false
}
onMounted(loadProfile)

const handleUpdate = async () => {
  if (saving.value) return
  if (form.value.phone.trim() && !/^1[3-9]\d{9}$/.test(form.value.phone.trim())) {
    success.value = false
    message.value = '请输入正确的 11 位手机号，或留空。'
    return
  }
  saving.value = true
  message.value = ''
  try {
    await userStore.updateProfile({ nickname: form.value.nickname.trim() || null, phone: form.value.phone.trim() || null })
    success.value = true
    message.value = '保存成功'
  } catch (e) {
    success.value = false
    message.value = authErrorMessage(e, '保存失败，请重试')
  } finally {
    saving.value = false
  }
}
</script>
