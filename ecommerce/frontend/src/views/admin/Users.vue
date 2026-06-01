<template>
  <div>
    <!-- 筛选栏 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 p-4 mb-4 flex flex-wrap gap-3">
      <input v-model="filters.keyword" placeholder="搜索用户名/邮箱/手机号" @keyup.enter="fetchUsers"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-4 py-2 text-sm focus:border-primary-500 outline-none w-64" />
      <select v-model="filters.is_active" @change="fetchUsers"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-3 py-2 text-sm focus:border-primary-500 outline-none">
        <option value="">全部状态</option>
        <option value="true">正常</option>
        <option value="false">已禁用</option>
      </select>
      <button @click="fetchUsers" class="px-4 py-2 bg-dark-800 text-dark-300 text-sm rounded-lg hover:bg-dark-700">
        <i class="fas fa-search mr-1"></i>搜索
      </button>
    </div>

    <!-- 用户表格 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 overflow-hidden">
      <div v-if="loading" class="flex justify-center py-16">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
      </div>

      <div v-else-if="users.length === 0" class="text-center py-16 text-dark-500">
        暂无用户数据
      </div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr class="text-dark-500 border-b border-dark-800 bg-dark-950/50">
            <th class="text-left py-3 px-4">用户</th>
            <th class="text-left py-3 px-4">邮箱</th>
            <th class="text-left py-3 px-4">手机号</th>
            <th class="text-center py-3 px-4">角色</th>
            <th class="text-center py-3 px-4">状态</th>
            <th class="text-left py-3 px-4">注册时间</th>
            <th class="text-center py-3 px-4">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id"
            class="border-b border-dark-800 last:border-0 hover:bg-dark-800/50 transition-colors">
            <td class="py-3 px-4">
              <div>
                <p class="font-medium">{{ u.nickname || u.username }}</p>
                <p class="text-dark-500 text-xs">@{{ u.username }}</p>
              </div>
            </td>
            <td class="py-3 px-4 text-dark-400 text-xs">{{ u.email }}</td>
            <td class="py-3 px-4 text-dark-400 text-xs">{{ u.phone || '-' }}</td>
            <td class="py-3 px-4 text-center">
              <span v-if="u.is_admin" class="text-[10px] bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full font-medium">管理员</span>
              <span v-else class="text-[10px] bg-dark-700 text-dark-400 px-2 py-0.5 rounded-full">普通用户</span>
            </td>
            <td class="py-3 px-4 text-center">
              <span class="text-xs px-2.5 py-1 rounded-full font-medium"
                :class="u.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'">
                {{ u.is_active ? '正常' : '已禁用' }}
              </span>
            </td>
            <td class="py-3 px-4 text-dark-500 text-xs">{{ formatDate(u.created_at) }}</td>
            <td class="py-3 px-4 text-center">
              <div class="flex items-center justify-center gap-2">
                <button @click="viewDetail(u)" class="text-primary-500 hover:underline text-xs">详情</button>
                <button v-if="!u.is_admin" @click="toggleStatus(u)"
                  class="text-xs hover:underline"
                  :class="u.is_active ? 'text-red-400' : 'text-green-400'">
                  {{ u.is_active ? '禁用' : '启用' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-dark-800">
        <span class="text-dark-500 text-xs">共 {{ total }} 条</span>
        <div class="flex gap-1">
          <button v-for="p in visiblePages" :key="p"
            @click="currentPage = p; fetchUsers()"
            class="w-8 h-8 rounded text-xs font-medium transition-colors"
            :class="currentPage === p ? 'bg-primary-500 text-dark-950' : 'bg-dark-800 text-dark-400 hover:text-white'">
            {{ p }}
          </button>
        </div>
      </div>
    </div>

    <!-- 用户详情弹窗 -->
    <Teleport to="body">
      <div v-if="showDetail" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="bg-dark-900 rounded-2xl border border-dark-700 w-[90vw] max-w-lg max-h-[85vh] shadow-2xl flex flex-col">
          <div class="flex items-center justify-between p-6 border-b border-dark-800">
            <h3 class="text-lg font-bold">用户详情</h3>
            <button @click="showDetail = false" class="text-dark-500 hover:text-white"><i class="fas fa-times"></i></button>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-4" v-if="detail">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-dark-800 rounded-full flex items-center justify-center text-xl">
                {{ (detail.nickname || detail.username || '?')[0].toUpperCase() }}
              </div>
              <div>
                <p class="font-bold text-lg">{{ detail.nickname || detail.username }}</p>
                <p class="text-dark-500 text-sm">@{{ detail.username }}</p>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="p-3 bg-dark-800 rounded-lg">
                <p class="text-dark-500 text-xs mb-1">邮箱</p>
                <p class="text-sm">{{ detail.email }}</p>
              </div>
              <div class="p-3 bg-dark-800 rounded-lg">
                <p class="text-dark-500 text-xs mb-1">手机</p>
                <p class="text-sm">{{ detail.phone || '-' }}</p>
              </div>
              <div class="p-3 bg-dark-800 rounded-lg">
                <p class="text-dark-500 text-xs mb-1">订单数</p>
                <p class="text-sm font-bold">{{ detail.order_count }}</p>
              </div>
              <div class="p-3 bg-dark-800 rounded-lg">
                <p class="text-dark-500 text-xs mb-1">总消费</p>
                <p class="text-sm font-bold text-primary-500">¥{{ Number(detail.total_spent).toLocaleString() }}</p>
              </div>
            </div>

            <div v-if="detail.addresses?.length > 0">
              <p class="text-dark-500 text-xs mb-2">收货地址 ({{ detail.addresses.length }})</p>
              <div class="space-y-2">
                <div v-for="addr in detail.addresses" :key="addr.id"
                  class="p-3 bg-dark-800 rounded-lg text-xs">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-medium text-sm">{{ addr.recipient_name }}</span>
                    <span class="text-dark-500">{{ addr.phone }}</span>
                    <span v-if="addr.is_default" class="text-[10px] bg-primary-500/20 text-primary-500 px-1.5 py-0.5 rounded">默认</span>
                  </div>
                  <p class="text-dark-400">{{ addr.province }}{{ addr.city }}{{ addr.district }}{{ addr.address }}</p>
                </div>
              </div>
            </div>

            <div class="p-3 bg-dark-800 rounded-lg">
              <p class="text-dark-500 text-xs mb-1">注册时间</p>
              <p class="text-sm">{{ formatDate(detail.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'

const users = ref([])
const loading = ref(true)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const filters = ref({ keyword: '', is_active: '' })

const totalPages = computed(() => Math.ceil(total.value / pageSize))
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const showDetail = ref(false)
const detail = ref(null)

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''

async function fetchUsers() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.is_active !== '') params.is_active = filters.value.is_active
    const data = await adminApi.getUsers(params)
    users.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('获取用户失败:', e)
  } finally {
    loading.value = false
  }
}

async function viewDetail(u) {
  try {
    detail.value = await adminApi.getUserDetail(u.id)
    showDetail.value = true
  } catch (e) {
    alert('获取详情失败')
  }
}

async function toggleStatus(u) {
  const action = u.is_active ? '禁用' : '启用'
  if (!confirm(`确定要${action}用户「${u.username}」吗？`)) return
  try {
    await adminApi.updateUserStatus(u.id, !u.is_active)
    u.is_active = !u.is_active
  } catch (e) {
    alert('操作失败：' + (e.message || '请重试'))
  }
}

onMounted(fetchUsers)
</script>
