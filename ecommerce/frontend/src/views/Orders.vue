<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <p class="text-xs uppercase tracking-[0.25em] text-primary-500 mb-3">我的装备进度</p>
      <h1 class="text-3xl font-bold mb-3">我的订单</h1>
      <p class="text-sm text-dark-400 mb-8">每一次升级的进度，都在这里。</p>

      <div class="mb-4 flex gap-2 overflow-x-auto pb-2" role="group" aria-label="订单状态筛选">
        <button v-for="s in statusFilters" :key="s.value"
          @click="currentStatus = s.value; currentPage = 1; fetchOrders()"
          class="shrink-0 rounded-full px-4 py-1.5 text-xs font-medium whitespace-nowrap transition-colors"
          :class="currentStatus === s.value ? 'bg-primary-500 text-dark-950' : 'bg-dark-800 text-dark-400 hover:text-dark-200'"
          :aria-pressed="currentStatus === s.value">
          {{ s.label }}
        </button>
      </div>

      <DsAsyncState
        :state="requestState"
        loading-label="正在加载订单"
        :empty-title="currentStatus ? '暂无' + statusText(currentStatus) + '订单' : '暂无订单'"
        :empty-description="currentStatus ? '试试其他状态，或查看全部订单。' : '去挑选心仪的配件，完成第一笔配置。'"
        error-title="订单加载失败"
        :error-description="requestError"
        retry-label="重试加载订单"
        @retry="fetchOrders"
      >
        <template #action>
          <DsButton v-if="requestState === 'empty' && currentStatus" variant="secondary" size="sm" type="button" @click="currentStatus = ''; currentPage = 1; fetchOrders()">查看全部订单</DsButton>
          <DsButton v-else-if="requestState === 'empty'" variant="primary" size="sm" type="button" @click="router.push('/products')">
            去购物
          </DsButton>
          <DsButton v-else-if="requestState === 'error'" variant="secondary" size="sm" type="button" @click="fetchOrders">
            重试加载订单
          </DsButton>
        </template>

        <div class="space-y-4">

        <router-link v-for="order in ordersWithPreview" :key="order.id" :to="`/orders/${order.id}`"
          class="block bg-dark-900 rounded-2xl border border-dark-800 p-6 hover:border-primary-500/30 transition-colors">
          <div class="flex flex-wrap items-start justify-between gap-3 mb-4">
            <div class="min-w-0 flex flex-col gap-1">
              <span class="text-dark-300 text-sm break-all">订单号：{{ order.order_no }}</span>
              <span class="text-dark-400 text-xs">{{ formatDate(order.created_at) }}</span>
            </div>
            <span class="text-xs px-3 py-1 rounded-full font-medium" :class="statusClass(order.status)">
              {{ statusText(order.status) }}
            </span>
          </div>

          <!-- 商品预览 -->
          <div class="flex items-center gap-3 mb-4">
            <div v-for="(item, idx) in (order.items || []).slice(0, 3)" :key="idx"
              class="relative w-12 h-12 bg-dark-800 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0">
              <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name" class="w-full h-full object-cover" />
              <span v-else-if="isCustomItem(item)" class="text-[11px] font-bold text-primary-500">DIY</span>
              <span v-else class="text-lg opacity-40">📦</span>
              <span v-if="isCustomItem(item)"
                class="absolute left-1 top-1 rounded bg-primary-500 px-1 py-0.5 text-[9px] font-semibold leading-none text-dark-950">
                定制
              </span>
            </div>
            <span v-if="(order.items || []).length > 3" class="text-dark-500 text-xs">
              +{{ order.items.length - 3 }} 件
            </span>
          </div>

          <div v-if="order.customPreview" class="mb-4 border-t border-dark-800 pt-3">
            <div class="flex flex-wrap items-center gap-2 text-xs">
              <span class="rounded border border-primary-500/30 bg-primary-500/10 px-2 py-0.5 font-medium text-primary-500">
                {{ order.customPreview.title }}
              </span>
              <span class="min-w-0 max-w-full truncate text-dark-300 sm:max-w-[420px]">
                {{ order.customPreview.summary }}
              </span>
              <span v-for="badge in order.customPreview.badges" :key="badge.key"
                class="rounded border border-white/5 bg-dark-800 px-2 py-0.5 text-[10px] text-dark-400">
                {{ badge.label }}：{{ badge.value }}
              </span>
            </div>
          </div>

          <div class="flex items-center justify-between pt-3 border-t border-dark-800">
            <div class="flex items-center gap-2 text-sm">
              <span class="text-dark-400">{{ (order.items || []).reduce((count, item) => count + Number(item.quantity || 0), 0) }} 件商品</span>
              <span v-if="hasCustomItems(order)"
                class="inline-flex items-center rounded-full border border-primary-500/40 bg-primary-500/10 px-2 py-0.5 text-[10px] font-medium text-primary-500">
                含定制
              </span>
            </div>
            <span class="text-xl font-bold text-primary-500">¥{{ Number(order.final_amount).toLocaleString() }}</span>
          </div>
        </router-link>

        <!-- 分页 -->
        <DsPagination
          v-if="totalPages > 1"
          v-model:page="currentPage"
          class="mt-6"
          :total-pages="totalPages"
          :disabled="loading"
          @change="fetchOrders"
        />
        </div>
      </DsAsyncState>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { orderApi } from '@/api'
import { DsAsyncState, DsButton, DsPagination } from '@/design-system'
import { buildOrderCustomPreview, isCustomOrderItem } from '@/utils/orderSpecs'

const router = useRouter()
const userStore = useUserStore()

const orders = ref([])
const loading = ref(true)
const requestState = ref('loading')
const requestError = ref('')
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)
const currentStatus = ref('')
let requestId = 0

const totalPages = computed(() => Math.ceil(total.value / pageSize))
const ordersWithPreview = computed(() => orders.value.map(order => ({
  ...order,
  customPreview: buildOrderCustomPreview(order),
})))

const statusFilters = [
  { label: '全部', value: '' },
  { label: '待支付', value: 'pending' },
  { label: '已支付', value: 'paid' },
  { label: '已发货', value: 'shipped' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' },
  { label: '已退款', value: 'refunded' },
]

const statusText = (s) => ({ pending: '待支付', paid: '已支付', shipped: '已发货', completed: '已完成', cancelled: '已取消', refunded: '已退款' }[s] || s)
const statusClass = (s) => ({
  pending: 'bg-yellow-500/20 text-yellow-400',
  paid: 'bg-green-500/20 text-green-400',
  shipped: 'bg-blue-500/20 text-blue-400',
  completed: 'bg-primary-500/20 text-primary-500',
  cancelled: 'bg-dark-700 text-dark-400',
  refunded: 'bg-red-500/20 text-red-400',
}[s] || 'bg-dark-700 text-dark-400')

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''
const isCustomItem = isCustomOrderItem
const hasCustomItems = (order) => (order.items || []).some(isCustomItem)

async function fetchOrders() {
  const activeRequest = ++requestId
  loading.value = true
  requestState.value = 'loading'
  requestError.value = ''
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (currentStatus.value) params.status = currentStatus.value
    const data = await orderApi.getOrders(params)
    if (activeRequest !== requestId) return
    orders.value = data.items || []
    total.value = data.total || 0
    requestState.value = orders.value.length ? 'success' : 'empty'
  } catch (e) {
    if (activeRequest !== requestId) return
    orders.value = []
    total.value = 0
    requestError.value = '订单服务暂时不可用，请检查网络后重试。'
    requestState.value = 'error'
  } finally {
    if (activeRequest === requestId) loading.value = false
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push({ name: 'Login', query: { redirect: '/orders' } })
    return
  }
  fetchOrders()
})
</script>
