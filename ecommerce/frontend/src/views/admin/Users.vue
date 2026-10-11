<template>
  <div class="space-y-4">
    <DsAlert
      v-if="feedback"
      :tone="feedback.tone"
      :title="feedback.title"
      :description="feedback.description"
      dismissible
      @dismiss="feedback = null"
    />

    <section class="rounded-xl border border-dark-800 bg-dark-900 p-4">
      <form class="grid gap-3 md:grid-cols-[minmax(0,1fr)_12rem_auto] md:items-end" @submit.prevent="searchUsers">
        <DsField
          v-model="filters.keyword"
          label="搜索用户"
          placeholder="用户名 / 邮箱 / 手机号"
          autocomplete="off"
        />
        <DsField
          v-model="filters.is_active"
          as="select"
          label="状态"
          placeholder="全部状态"
          :options="statusOptions"
          @change="searchUsers"
        />
        <DsButton variant="secondary" type="submit" :loading="requestState === 'loading'">
          搜索
        </DsButton>
      </form>
    </section>

    <section class="overflow-hidden rounded-xl border border-dark-800 bg-dark-900">
      <DsAsyncState
        :state="requestState"
        empty-title="暂无用户数据"
        empty-description="调整筛选条件后可以重新搜索。"
        error-title="用户列表加载失败"
        :error-description="requestError"
        @retry="fetchUsers"
      >
        <DsDataTable v-if="requestState === 'success'" label="后台用户列表">
          <table>
            <thead>
              <tr>
                <th>用户</th>
                <th>邮箱</th>
                <th>手机号</th>
                <th class="text-center">角色</th>
                <th class="text-center">状态</th>
                <th>注册时间</th>
                <th class="text-center">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>
                  <p class="font-medium">{{ user.nickname || user.username }}</p>
                  <p class="text-xs text-dark-500">@{{ user.username }}</p>
                </td>
                <td class="text-xs text-dark-400">{{ user.email }}</td>
                <td class="text-xs text-dark-400">{{ user.phone || '-' }}</td>
                <td class="text-center">
                  <span v-if="user.is_admin" class="rounded-full bg-purple-500/20 px-2 py-0.5 text-[10px] font-medium text-purple-400">管理员</span>
                  <span v-else class="rounded-full bg-dark-700 px-2 py-0.5 text-[10px] text-dark-400">普通用户</span>
                </td>
                <td class="text-center">
                  <span
                    class="rounded-full px-2.5 py-1 text-xs font-medium"
                    :class="user.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'"
                  >
                    {{ user.is_active ? '正常' : '已禁用' }}
                  </span>
                </td>
                <td class="text-xs text-dark-500">{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="flex items-center justify-center gap-2">
                    <DsButton variant="ghost" size="sm" type="button" @click="viewDetail(user)">详情</DsButton>
                    <DsButton
                      v-if="!user.is_admin"
                      :variant="user.is_active ? 'danger' : 'secondary'"
                      size="sm"
                      type="button"
                      @click="requestToggle(user)"
                    >
                      {{ user.is_active ? '禁用' : '启用' }}
                    </DsButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </DsDataTable>
      </DsAsyncState>

      <div v-if="requestState === 'success'" class="flex flex-wrap items-center justify-between gap-3 border-t border-dark-800 px-4 py-3">
        <span class="text-xs text-dark-500">共 {{ total }} 条</span>
        <DsPagination
          v-if="totalPages > 1"
          v-model:page="currentPage"
          :total-pages="totalPages"
          aria-label="用户列表分页"
          @change="fetchUsers"
        />
      </div>
    </section>

    <DsDialog
      v-model:open="showDetail"
      title="用户详情"
      :description="detail ? `${detail.nickname || detail.username} 的账户信息` : ''"
      size="md"
    >
      <div v-if="detail" class="space-y-4">
        <div class="flex items-center gap-4">
          <div class="flex h-14 w-14 items-center justify-center rounded-full bg-dark-800 text-xl">
            {{ (detail.nickname || detail.username || '?')[0].toUpperCase() }}
          </div>
          <div>
            <p class="text-lg font-bold">{{ detail.nickname || detail.username }}</p>
            <p class="text-sm text-dark-500">@{{ detail.username }}</p>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 break-words">
          <div class="rounded-lg bg-dark-800 p-3">
            <p class="mb-1 text-xs text-dark-500">邮箱</p>
            <p class="text-sm">{{ detail.email }}</p>
          </div>
          <div class="rounded-lg bg-dark-800 p-3">
            <p class="mb-1 text-xs text-dark-500">手机</p>
            <p class="text-sm">{{ detail.phone || '-' }}</p>
          </div>
          <div class="rounded-lg bg-dark-800 p-3">
            <p class="mb-1 text-xs text-dark-500">订单数</p>
            <p class="text-sm font-bold">{{ detail.order_count }}</p>
          </div>
          <div class="rounded-lg bg-dark-800 p-3">
            <p class="mb-1 text-xs text-dark-500">总消费</p>
            <p class="text-sm font-bold text-primary-500">¥{{ Number(detail.total_spent).toLocaleString() }}</p>
          </div>
        </div>

        <div v-if="detail.addresses?.length">
          <p class="mb-2 text-xs text-dark-500">收货地址（{{ detail.addresses.length }}）</p>
          <div class="space-y-2">
            <div v-for="address in detail.addresses" :key="address.id" class="rounded-lg bg-dark-800 p-3 text-xs">
              <div class="mb-1 flex flex-wrap items-center gap-2">
                <span class="text-sm font-medium">{{ address.recipient_name }}</span>
                <span class="text-dark-500">{{ address.phone }}</span>
                <span v-if="address.is_default" class="rounded bg-primary-500/20 px-1.5 py-0.5 text-[10px] text-primary-500">默认</span>
              </div>
              <p class="text-dark-400">{{ address.province }}{{ address.city }}{{ address.district }}{{ address.address }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-lg bg-dark-800 p-3">
          <p class="mb-1 text-xs text-dark-500">注册时间</p>
          <p class="text-sm">{{ formatDate(detail.created_at) }}</p>
        </div>
      </div>
    </DsDialog>

    <DsDialog
      v-model:open="confirmOpen"
      title="确认修改用户状态"
      :description="pendingUser ? `确定要${pendingUser.is_active ? '禁用' : '启用'}用户 ${pendingUser.username} 吗？` : ''"
      size="sm"
    >
      <template #footer>
        <DsButton variant="ghost" type="button" @click="confirmOpen = false">取消</DsButton>
        <DsButton :variant="pendingUser?.is_active ? 'danger' : 'primary'" type="button" :loading="statusUpdating" @click="toggleStatus">
          确认
        </DsButton>
      </template>
    </DsDialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '@/api'
import { DsAlert, DsAsyncState, DsButton, DsDataTable, DsDialog, DsField, DsPagination } from '@/design-system'

const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const filters = ref({ keyword: '', is_active: '' })
const requestState = ref('loading')
const requestError = ref('请检查网络连接后重试。')
const feedback = ref(null)
const showDetail = ref(false)
const detail = ref(null)
const confirmOpen = ref(false)
const pendingUser = ref(null)
const statusUpdating = ref(false)
let listRequestId = 0
let detailRequestId = 0

const statusOptions = [
  { value: 'true', label: '正常' },
  { value: 'false', label: '已禁用' },
]

const totalPages = computed(() => Math.ceil(total.value / pageSize))
const formatDate = value => value ? new Date(value).toLocaleString('zh-CN') : '-'

function errorMessage(error, fallback) {
  return error?.displayMessage || error?.message || fallback
}

async function fetchUsers() {
  const requestId = ++listRequestId
  requestState.value = 'loading'
  requestError.value = '正在重新加载用户列表。'
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.is_active !== '') params.is_active = filters.value.is_active
    const response = await adminApi.getUsers(params)
    if (requestId !== listRequestId) return
    users.value = response.items || []
    total.value = response.total || 0
    requestState.value = users.value.length ? 'success' : 'empty'
  } catch (error) {
    if (requestId !== listRequestId) return
    requestState.value = 'error'
    requestError.value = errorMessage(error, '用户服务暂不可用，请稍后重试。')
    console.warn('Failed to load admin users', error)
  }
}

function searchUsers() {
  currentPage.value = 1
  return fetchUsers()
}

async function viewDetail(user) {
  const requestId = ++detailRequestId
  try {
    const response = await adminApi.getUserDetail(user.id)
    if (requestId !== detailRequestId) return
    detail.value = response
    showDetail.value = true
  } catch (error) {
    if (requestId !== detailRequestId) return
    feedback.value = { tone: 'danger', title: '用户详情加载失败', description: errorMessage(error, '请稍后重试。') }
  }
}

function requestToggle(user) {
  pendingUser.value = user
  confirmOpen.value = true
}

async function toggleStatus() {
  if (!pendingUser.value || statusUpdating.value) return
  statusUpdating.value = true
  const user = pendingUser.value
  try {
    await adminApi.updateUserStatus(user.id, !user.is_active)
    user.is_active = !user.is_active
    feedback.value = { tone: 'success', title: '用户状态已更新', description: `${user.username} 当前为${user.is_active ? '正常' : '已禁用'}状态。` }
    confirmOpen.value = false
    if (filters.value.is_active !== '') await searchUsers()
  } catch (error) {
    feedback.value = { tone: 'danger', title: '用户状态更新失败', description: errorMessage(error, '请稍后重试。') }
  } finally {
    statusUpdating.value = false
  }
}

onMounted(fetchUsers)
</script>
