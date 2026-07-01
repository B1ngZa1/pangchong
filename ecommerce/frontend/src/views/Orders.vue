<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">我的订单</h1>

      <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-500"></div>
      </div>

      <div v-else-if="orders.length === 0" class="text-center py-20">
        <div class="text-7xl mb-6 opacity-30">📦</div>
        <p class="text-dark-400 text-xl mb-2">暂无订单</p>
        <p class="text-dark-600 text-sm mb-8">快去挑选心仪的配件吧</p>
        <router-link to="/products" class="inline-block px-8 py-3 bg-primary-500 text-dark-950 font-semibold rounded-xl hover:bg-primary-400 transition-colors">
          去购物
        </router-link>
      </div>

      <div v-else class="space-y-4">
        <!-- 状态筛选 -->
        <div class="flex gap-2 mb-4 overflow-x-auto pb-2">
          <button v-for="s in statusFilters" :key="s.value"
            @click="currentStatus = s.value; fetchOrders()"
            class="px-4 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors"
            :class="currentStatus === s.value ? 'bg-primary-500 text-dark-950' : 'bg-dark-800 text-dark-400 hover:text-dark-200'">
            {{ s.label }}
          </button>
        </div>

        <router-link v-for="order in ordersWithPreview" :key="order.id" :to="`/orders/${order.id}`"
          class="block bg-dark-900 rounded-2xl border border-dark-800 p-6 hover:border-primary-500/30 transition-colors">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-4">
              <span class="text-dark-400 text-sm">订单号：{{ order.order_no }}</span>
              <span class="text-dark-600 text-sm">{{ formatDate(order.created_at) }}</span>
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
              <span class="text-dark-400">{{ order.items?.length || 0 }} 件商品</span>
              <span v-if="hasCustomItems(order)"
                class="inline-flex items-center rounded-full border border-primary-500/40 bg-primary-500/10 px-2 py-0.5 text-[10px] font-medium text-primary-500">
                含定制
              </span>
            </div>
            <span class="text-xl font-bold text-primary-500">¥{{ Number(order.final_amount).toLocaleString() }}</span>
          </div>
        </router-link>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
          <button v-for="p in totalPages" :key="p"
            @click="currentPage = p; fetchOrders()"
            class="w-9 h-9 rounded-lg text-sm font-medium transition-colors"
            :class="currentPage === p ? 'bg-primary-500 text-dark-950' : 'bg-dark-800 text-dark-400 hover:text-dark-200'">
            {{ p }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { orderApi } from '@/api'
import { buildOrderCustomPreview, isCustomOrderItem } from '@/utils/orderSpecs'

const router = useRouter()
const userStore = useUserStore()

const orders = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)
const currentStatus = ref('')

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
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (currentStatus.value) params.status = currentStatus.value
    const data = await orderApi.getOrders(params)
    orders.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('获取订单失败:', e)
    orders.value = []
  } finally {
    loading.value = false
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
