<template>
  <div class="card p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold">收货地址</h2>
      <button v-if="!showForm" @click="openCreate"
        class="px-4 py-2 bg-primary-500 text-dark-950 text-sm font-semibold rounded-lg hover:bg-primary-400 transition-colors">
        <i class="fas fa-plus mr-1"></i>添加地址
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500 mx-auto"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="addresses.length === 0 && !showForm" class="text-center py-12">
      <div class="text-5xl mb-4 opacity-30">📍</div>
      <p class="text-dark-400 mb-2">暂无收货地址</p>
      <p class="text-dark-600 text-sm mb-6">添加地址后即可快速下单</p>
      <button @click="openCreate"
        class="px-6 py-2.5 bg-primary-500 text-dark-950 font-semibold rounded-lg hover:bg-primary-400 transition-colors">
        添加第一个地址
      </button>
    </div>

    <!-- 地址列表 -->
    <div v-else-if="!showForm" class="space-y-3">
      <div v-for="addr in addresses" :key="addr.id"
        class="p-4 bg-dark-900 rounded-xl border transition-all"
        :class="addr.is_default ? 'border-primary-500/50' : 'border-dark-800'">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-medium text-sm">{{ addr.recipient_name }}</span>
              <span class="text-dark-500 text-xs">{{ addr.phone }}</span>
              <span v-if="addr.is_default"
                class="text-[10px] bg-primary-500/20 text-primary-500 px-2 py-0.5 rounded-full font-medium">默认</span>
            </div>
            <p class="text-dark-400 text-xs leading-relaxed">
              {{ addr.province }}{{ addr.city }}{{ addr.district }}{{ addr.address }}
            </p>
            <p v-if="addr.postal_code" class="text-dark-600 text-xs mt-0.5">邮编：{{ addr.postal_code }}</p>
          </div>
          <div class="flex items-center gap-3 ml-4">
            <button v-if="!addr.is_default" @click="setDefault(addr)"
              class="text-xs text-dark-500 hover:text-primary-500 transition-colors">设为默认</button>
            <button @click="openEdit(addr)"
              class="text-xs text-dark-500 hover:text-primary-500 transition-colors">编辑</button>
            <button @click="deleteAddr(addr)"
              class="text-xs text-dark-500 hover:text-red-400 transition-colors">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑表单 -->
    <div v-if="showForm" class="mt-2">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold">{{ editingId ? '编辑地址' : '添加新地址' }}</h3>
        <button @click="closeForm" class="text-dark-500 hover:text-white text-sm">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <AddressForm v-model="form" :errors="formErrors" ref="addressFormRef" />

      <div class="flex gap-3 mt-2">
        <button @click="handleSubmit" :disabled="saving"
          class="px-6 py-2.5 bg-primary-500 text-dark-950 text-sm font-semibold rounded-lg hover:bg-primary-400 transition-colors disabled:opacity-50">
          {{ saving ? '保存中...' : (editingId ? '更新地址' : '保存地址') }}
        </button>
        <button @click="closeForm"
          class="px-6 py-2.5 bg-dark-800 text-dark-300 text-sm rounded-lg hover:bg-dark-700 transition-colors">
          取消
        </button>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="bg-dark-900 rounded-2xl border border-dark-700 p-6 w-[90vw] max-w-sm shadow-2xl">
          <h3 class="text-lg font-bold mb-2">确认删除</h3>
          <p class="text-dark-400 text-sm mb-6">确定要删除此收货地址吗？</p>
          <div class="flex gap-3 justify-end">
            <button @click="showDeleteModal = false"
              class="px-5 py-2 rounded-lg text-sm bg-dark-800 text-dark-300 hover:bg-dark-700">取消</button>
            <button @click="confirmDelete"
              class="px-5 py-2 rounded-lg text-sm bg-red-500 text-white hover:bg-red-600">删除</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import AddressForm from '@/components/AddressForm.vue'

const userStore = useUserStore()

const addresses = ref([])
const loading = ref(true)
const showForm = ref(false)
const saving = ref(false)
const editingId = ref(null)
const showDeleteModal = ref(false)
const deletingAddr = ref(null)
const addressFormRef = ref(null)
const formErrors = ref({})

const defaultForm = {
  recipient_name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  address: '',
  postal_code: '',
  is_default: false,
}

const form = ref({ ...defaultForm })

async function fetchAddresses() {
  loading.value = true
  try {
    await userStore.fetchAddresses()
    addresses.value = userStore.addresses || []
  } catch (e) {
    console.error('加载地址失败:', e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { ...defaultForm }
  formErrors.value = {}
  showForm.value = true
}

function openEdit(addr) {
  editingId.value = addr.id
  form.value = {
    recipient_name: addr.recipient_name,
    phone: addr.phone,
    province: addr.province,
    city: addr.city,
    district: addr.district || '',
    address: addr.address,
    postal_code: addr.postal_code || '',
    is_default: addr.is_default,
  }
  formErrors.value = {}
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingId.value = null
  formErrors.value = {}
}

async function handleSubmit() {
  // 前端验证
  if (addressFormRef.value) {
    const errs = addressFormRef.value.validate()
    if (Object.keys(errs).length > 0) {
      formErrors.value = errs
      return
    }
  }

  saving.value = true
  formErrors.value = {}
  try {
    if (editingId.value) {
      await userStore.updateAddress(editingId.value, form.value)
    } else {
      await userStore.createAddress(form.value)
    }
    closeForm()
    addresses.value = userStore.addresses || []
  } catch (e) {
    const detail = e.response?.data?.detail
    if (typeof detail === 'string') {
      alert(detail)
    } else if (Array.isArray(detail)) {
      // Pydantic validation errors
      const fieldErrors = {}
      detail.forEach(err => {
        const field = err.loc?.[err.loc.length - 1]
        if (field) fieldErrors[field] = err.msg
      })
      formErrors.value = fieldErrors
    } else {
      alert('操作失败，请重试')
    }
  } finally {
    saving.value = false
  }
}

async function setDefault(addr) {
  try {
    await userStore.updateAddress(addr.id, { is_default: true })
    addresses.value = userStore.addresses || []
  } catch (e) {
    alert('设置失败')
  }
}

function deleteAddr(addr) {
  deletingAddr.value = addr
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!deletingAddr.value) return
  try {
    await userStore.deleteAddress(deletingAddr.value.id)
    addresses.value = userStore.addresses || []
  } catch (e) {
    alert('删除失败')
  } finally {
    showDeleteModal.value = false
    deletingAddr.value = null
  }
}

onMounted(fetchAddresses)
</script>
