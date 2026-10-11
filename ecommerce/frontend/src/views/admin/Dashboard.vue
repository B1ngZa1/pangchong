<template>
  <DsAsyncState
    :state="requestState"
    empty-title="暂无运营数据"
    empty-description="完成首笔订单后，这里会展示经营趋势。"
    error-title="仪表盘加载失败"
    :error-description="requestError"
    @retry="fetchDashboard"
  >
    <div class="space-y-8">
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div v-for="card in statCards" :key="card.label" class="min-w-0 rounded-xl border border-dark-800 bg-dark-900 p-4 sm:p-5">
          <div class="mb-3 flex items-center justify-between gap-3">
            <span class="text-sm text-dark-500">{{ card.label }}</span>
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg sm:h-10 sm:w-10" :class="card.bgClass">
              <i :class="card.icon" class="text-lg" aria-hidden="true"></i>
            </div>
          </div>
          <p class="break-words text-xl font-bold sm:text-2xl">{{ card.value }}</p>
          <p v-if="card.sub" class="mt-1 text-xs text-dark-500">{{ card.sub }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section class="rounded-xl border border-dark-800 bg-dark-900 p-6">
          <h2 class="mb-4 font-bold">近 7 天订单趋势</h2>
          <div class="space-y-3">
            <div v-for="day in data.daily_stats" :key="day.date" class="flex items-center gap-3">
              <span class="w-10 text-xs text-dark-500">{{ day.date }}</span>
              <div class="relative h-5 flex-1 overflow-hidden rounded-full bg-dark-800">
                <div class="h-full rounded-full bg-primary-500/30" :style="{ width: getBarWidth(day.orders, maxDailyOrders) }" aria-hidden="true"></div>
                <span class="absolute inset-y-0 left-2 flex items-center whitespace-nowrap text-[10px] font-medium text-primary-500">{{ day.orders }} 单</span>
              </div>
              <span class="w-20 text-right text-xs text-dark-400">¥{{ Number(day.revenue || 0).toLocaleString() }}</span>
            </div>
            <p v-if="!data.daily_stats.length" class="py-6 text-center text-sm text-dark-500">暂无趋势数据</p>
          </div>
        </section>

        <section class="rounded-xl border border-dark-800 bg-dark-900 p-6">
          <h2 class="mb-4 font-bold">订单状态分布</h2>
          <div class="space-y-3">
            <div v-for="item in statusList" :key="item.key" class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-3">
                <span class="h-3 w-3 rounded-full" :class="item.dotClass" aria-hidden="true"></span>
                <span class="text-sm text-dark-300">{{ item.label }}</span>
              </div>
              <div class="flex items-center gap-3">
                <div class="h-3 w-16 overflow-hidden rounded-full bg-dark-800 sm:w-32">
                  <div class="h-full rounded-full" :class="item.barClass" :style="{ width: getBarWidth(data.order_status_counts[item.key], totalOrders) }"></div>
                </div>
                <span class="w-10 text-right text-sm font-medium">{{ data.order_status_counts[item.key] || 0 }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <section class="overflow-hidden rounded-xl border border-dark-800 bg-dark-900 p-6">
        <div class="mb-4 flex items-center justify-between gap-3">
          <h2 class="font-bold">热销商品 TOP 5</h2>
          <span class="text-xs text-dark-500">按销量排序</span>
        </div>
        <DsDataTable label="热销商品列表">
          <table>
            <thead>
              <tr>
                <th>排名</th>
                <th>商品</th>
                <th class="text-right">售价</th>
                <th class="text-right">销量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(product, index) in data.hot_products" :key="product.id">
                <td>
                  <span class="flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold" :class="index < 3 ? 'bg-primary-500 text-dark-950' : 'bg-dark-800 text-dark-400'">
                    {{ index + 1 }}
                  </span>
                </td>
                <td>
                  <div class="flex items-center gap-3">
                    <div class="h-10 w-10 flex-shrink-0 overflow-hidden rounded-lg bg-dark-800">
                      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="h-full w-full object-cover" />
                    </div>
                    <span class="max-w-xs truncate">{{ product.name }}</span>
                  </div>
                </td>
                <td class="text-right font-medium">¥{{ Number(product.price || 0).toLocaleString() }}</td>
                <td class="text-right">{{ product.sold_count }}</td>
              </tr>
              <tr v-if="!data.hot_products.length">
                <td colspan="4" class="py-8 text-center text-dark-500">暂无热销商品</td>
              </tr>
            </tbody>
          </table>
        </DsDataTable>
      </section>
    </div>
  </DsAsyncState>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '@/api'
import { DsAsyncState, DsDataTable } from '@/design-system'

const emptyDashboard = () => ({
  total_users: 0,
  today_users: 0,
  total_products: 0,
  total_orders: 0,
  today_orders: 0,
  pending_shipment: 0,
  pending_payment: 0,
  total_revenue: 0,
  today_revenue: 0,
  month_revenue: 0,
  daily_stats: [],
  order_status_counts: {},
  hot_products: [],
})
const data = ref(emptyDashboard())
const requestState = ref('loading')
const requestError = ref('请检查网络连接后重试。')

const totalOrders = computed(() => Object.values(data.value.order_status_counts).reduce((sum, value) => sum + (Number(value) || 0), 0))
const maxDailyOrders = computed(() => Math.max(1, ...data.value.daily_stats.map(day => Number(day.orders) || 0)))

const statCards = computed(() => [
  { label: '今日销售额', value: `¥${Number(data.value.today_revenue).toLocaleString()}`, sub: `本月 ¥${Number(data.value.month_revenue).toLocaleString()}`, icon: 'fas fa-yen-sign text-green-400', bgClass: 'bg-green-500/10' },
  { label: '今日订单', value: data.value.today_orders, sub: `累计 ${data.value.total_orders}`, icon: 'fas fa-shopping-bag text-blue-400', bgClass: 'bg-blue-500/10' },
  { label: '待发货', value: data.value.pending_shipment, sub: `待付款 ${data.value.pending_payment}`, icon: 'fas fa-truck text-yellow-400', bgClass: 'bg-yellow-500/10' },
  { label: '总用户', value: data.value.total_users, sub: `今日新增 ${data.value.today_users}`, icon: 'fas fa-users text-purple-400', bgClass: 'bg-purple-500/10' },
])

const statusList = [
  { key: 'pending', label: '待付款', dotClass: 'bg-yellow-500', barClass: 'bg-yellow-500' },
  { key: 'paid', label: '待发货', dotClass: 'bg-blue-500', barClass: 'bg-blue-500' },
  { key: 'shipped', label: '已发货', dotClass: 'bg-indigo-500', barClass: 'bg-indigo-500' },
  { key: 'completed', label: '已完成', dotClass: 'bg-green-500', barClass: 'bg-green-500' },
  { key: 'cancelled', label: '已取消', dotClass: 'bg-dark-500', barClass: 'bg-dark-500' },
]

function getBarWidth(value, max) {
  if (!Number.isFinite(Number(max)) || Number(max) <= 0) return '0%'
  return `${Math.min(100, Math.max(0, ((Number(value) || 0) / Number(max)) * 100))}%`
}

async function fetchDashboard() {
  requestState.value = 'loading'
  try {
    data.value = { ...emptyDashboard(), ...(await adminApi.getDashboard() || {}) }
    requestState.value = 'success'
  } catch (error) {
    requestState.value = 'error'
    requestError.value = error?.displayMessage || error?.message || '仪表盘服务暂不可用，请稍后重试。'
    console.warn('Failed to load admin dashboard', error)
  }
}

onMounted(fetchDashboard)
</script>
