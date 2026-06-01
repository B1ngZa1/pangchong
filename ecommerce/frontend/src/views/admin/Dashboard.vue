<template>
  <div>
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-500"></div>
    </div>

    <div v-else>
      <!-- 核心指标卡片 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div v-for="card in statCards" :key="card.label"
          class="bg-dark-900 rounded-xl border border-dark-800 p-5">
          <div class="flex items-center justify-between mb-3">
            <span class="text-dark-500 text-sm">{{ card.label }}</span>
            <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="card.bgClass">
              <i :class="card.icon" class="text-lg"></i>
            </div>
          </div>
          <p class="text-2xl font-bold">{{ card.value }}</p>
          <p v-if="card.sub" class="text-dark-500 text-xs mt-1">{{ card.sub }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- 近7天趋势 -->
        <div class="bg-dark-900 rounded-xl border border-dark-800 p-6">
          <h3 class="font-bold mb-4">近7天订单趋势</h3>
          <div class="space-y-3">
            <div v-for="day in data.daily_stats" :key="day.date" class="flex items-center gap-3">
              <span class="text-dark-500 text-xs w-10">{{ day.date }}</span>
              <div class="flex-1 bg-dark-800 rounded-full h-5 overflow-hidden">
                <div class="h-full bg-primary-500/30 rounded-full flex items-center px-2"
                  :style="{ width: getBarWidth(day.orders, maxDailyOrders) }">
                  <span class="text-[10px] text-primary-500 font-medium whitespace-nowrap">{{ day.orders }}单</span>
                </div>
              </div>
              <span class="text-dark-400 text-xs w-20 text-right">¥{{ day.revenue.toLocaleString() }}</span>
            </div>
          </div>
        </div>

        <!-- 订单状态分布 -->
        <div class="bg-dark-900 rounded-xl border border-dark-800 p-6">
          <h3 class="font-bold mb-4">订单状态分布</h3>
          <div class="space-y-3">
            <div v-for="item in statusList" :key="item.key" class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="w-3 h-3 rounded-full" :class="item.dotClass"></span>
                <span class="text-sm text-dark-300">{{ item.label }}</span>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-32 bg-dark-800 rounded-full h-3 overflow-hidden">
                  <div class="h-full rounded-full" :class="item.barClass"
                    :style="{ width: getBarWidth(data.order_status_counts[item.key], totalOrders) }"></div>
                </div>
                <span class="text-sm font-medium w-10 text-right">{{ data.order_status_counts[item.key] || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 热销商品 -->
      <div class="bg-dark-900 rounded-xl border border-dark-800 p-6">
        <h3 class="font-bold mb-4">热销商品 TOP 5</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-dark-500 border-b border-dark-800">
                <th class="text-left py-3 px-2">排名</th>
                <th class="text-left py-3 px-2">商品</th>
                <th class="text-right py-3 px-2">售价</th>
                <th class="text-right py-3 px-2">销量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, idx) in data.hot_products" :key="p.id"
                class="border-b border-dark-800 last:border-0">
                <td class="py-3 px-2">
                  <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                    :class="idx < 3 ? 'bg-primary-500 text-dark-950' : 'bg-dark-800 text-dark-400'">
                    {{ idx + 1 }}
                  </span>
                </td>
                <td class="py-3 px-2">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 bg-dark-800 rounded-lg flex-shrink-0 overflow-hidden">
                      <img v-if="p.image_url" :src="p.image_url" class="w-full h-full object-cover" />
                    </div>
                    <span class="truncate max-w-xs">{{ p.name }}</span>
                  </div>
                </td>
                <td class="py-3 px-2 text-right font-medium">¥{{ p.price.toLocaleString() }}</td>
                <td class="py-3 px-2 text-right">{{ p.sold_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'

const data = ref({
  total_users: 0, today_users: 0, total_products: 0,
  total_orders: 0, today_orders: 0, pending_shipment: 0, pending_payment: 0,
  total_revenue: 0, today_revenue: 0, month_revenue: 0,
  daily_stats: [], order_status_counts: {}, hot_products: [],
})
const loading = ref(true)

const totalOrders = computed(() => {
  const c = data.value.order_status_counts
  return (c.pending || 0) + (c.paid || 0) + (c.shipped || 0) + (c.completed || 0) + (c.cancelled || 0)
})

const maxDailyOrders = computed(() => {
  return Math.max(1, ...data.value.daily_stats.map(d => d.orders))
})

const statCards = computed(() => [
  { label: '今日销售额', value: '¥' + data.value.today_revenue.toLocaleString(), sub: '本月 ¥' + data.value.month_revenue.toLocaleString(), icon: 'fas fa-yen-sign text-green-400', bgClass: 'bg-green-500/10' },
  { label: '今日订单', value: data.value.today_orders, sub: '总计 ' + data.value.total_orders, icon: 'fas fa-shopping-bag text-blue-400', bgClass: 'bg-blue-500/10' },
  { label: '待发货', value: data.value.pending_shipment, sub: '待付款 ' + data.value.pending_payment, icon: 'fas fa-truck text-yellow-400', bgClass: 'bg-yellow-500/10' },
  { label: '总用户', value: data.value.total_users, sub: '今日新增 ' + data.value.today_users, icon: 'fas fa-users text-purple-400', bgClass: 'bg-purple-500/10' },
])

const statusList = [
  { key: 'pending', label: '待付款', dotClass: 'bg-yellow-500', barClass: 'bg-yellow-500' },
  { key: 'paid', label: '待发货', dotClass: 'bg-blue-500', barClass: 'bg-blue-500' },
  { key: 'shipped', label: '已发货', dotClass: 'bg-indigo-500', barClass: 'bg-indigo-500' },
  { key: 'completed', label: '已完成', dotClass: 'bg-green-500', barClass: 'bg-green-500' },
  { key: 'cancelled', label: '已取消', dotClass: 'bg-dark-500', barClass: 'bg-dark-500' },
]

function getBarWidth(value, max) {
  return Math.max(2, ((value || 0) / max) * 100) + '%'
}

onMounted(async () => {
  try {
    data.value = await adminApi.getDashboard()
  } catch (e) {
    console.error('加载仪表盘失败:', e)
  } finally {
    loading.value = false
  }
})
</script>
