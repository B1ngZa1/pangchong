<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-500"></div>
      </div>

      <div v-else-if="!order" class="text-center py-20">
        <div class="text-7xl mb-6 opacity-30">❓</div>
        <p class="text-dark-400 text-xl mb-2">订单不存在</p>
        <router-link to="/orders" class="text-primary-500 hover:underline text-sm">返回订单列表</router-link>
      </div>

      <div v-else>
        <div class="flex items-center justify-between mb-8">
          <div>
            <h1 class="text-3xl font-bold">订单详情</h1>
            <p class="text-dark-500 text-sm mt-1">订单号：{{ order.order_no }}</p>
          </div>
          <router-link to="/orders" class="text-primary-500 hover:underline text-sm">
            <i class="fas fa-arrow-left mr-1"></i>返回订单列表
          </router-link>
        </div>

        <!-- 订单状态 -->
        <div class="bg-dark-900 rounded-2xl border border-dark-800 p-6 mb-6">
          <div class="flex items-center justify-between">
            <div>
              <span class="text-xs px-3 py-1 rounded-full font-medium" :class="statusClass(order.status)">
                {{ statusText(order.status) }}
              </span>
              <p class="text-dark-500 text-sm mt-2">{{ formatDate(order.created_at) }}</p>
            </div>
            <div v-if="order.status === 'pending'" class="flex items-center gap-3">
              <p class="text-yellow-400 text-sm font-medium">请在30分钟内完成支付</p>
              <button @click="startPayment" :disabled="paying"
                class="px-5 py-2 rounded-lg text-sm bg-primary-500 text-dark-950 font-semibold hover:bg-primary-400 disabled:opacity-50">
                {{ paying ? '支付创建中...' : '去支付' }}
              </button>
              <button v-if="isSandboxPaymentPath" @click="sandboxMockPay" :disabled="paying"
                class="px-5 py-2 rounded-lg text-sm bg-dark-800 text-dark-300 hover:bg-dark-700 disabled:opacity-50">
                沙箱模拟支付
              </button>
            </div>
            <div v-if="order.status === 'pending'" class="mt-2">
              <button @click="cancelOrder" :disabled="cancelling"
                class="text-xs text-dark-500 hover:text-red-400 transition-colors disabled:opacity-50">
                {{ cancelling ? '取消中...' : '取消订单' }}
              </button>
            </div>
          </div>

          <!-- 物流信息 -->
          <div v-if="order.tracking_number" class="mt-4 p-3 bg-dark-800 rounded-lg">
            <p class="text-xs text-dark-400">
              <i class="fas fa-truck mr-1"></i>
              {{ order.shipping_company }} · {{ order.tracking_number }}
            </p>
          </div>
        </div>

        <!-- 收货信息 -->
        <div class="bg-dark-900 rounded-2xl border border-dark-800 p-6 mb-6">
          <h2 class="text-lg font-bold mb-3">收货信息</h2>
          <p class="text-sm font-medium">{{ order.recipient_name }} {{ order.recipient_phone }}</p>
          <p class="text-dark-400 text-sm mt-1">{{ order.shipping_address }}</p>
          <p v-if="order.remark" class="text-dark-500 text-xs mt-2">备注：{{ order.remark }}</p>
        </div>

        <!-- 商品列表 -->
        <div class="bg-dark-900 rounded-2xl border border-dark-800 p-6 mb-6">
          <h2 class="text-lg font-bold mb-4">商品与定制清单</h2>
          <div class="space-y-3">
            <div v-for="item in order.items" :key="item.id"
              class="flex items-center gap-4 py-3 border-b border-dark-800 last:border-0">
              <div class="w-16 h-16 bg-dark-800 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0">
                <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name" class="w-full h-full object-cover" />
                <span v-else-if="isCustomItem(item)" class="text-xs font-bold text-primary-500">DIY</span>
                <span v-else class="text-2xl opacity-40">📦</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 min-w-0">
                  <p class="font-medium text-sm truncate">{{ item.product_name }}</p>
                  <span v-if="isCustomItem(item)"
                    class="flex-shrink-0 rounded-full border border-primary-500/40 bg-primary-500/10 px-2 py-0.5 text-[10px] font-medium leading-none text-primary-500">
                    定制
                  </span>
                </div>
                <p class="text-dark-500 text-xs mt-0.5">x{{ item.quantity }} · ¥{{ Number(item.price).toLocaleString() }}</p>
                <div v-if="formatSpecs(item.product_specs).length" class="mt-1 flex flex-wrap gap-1">
                  <span v-for="spec in formatSpecs(item.product_specs)" :key="spec.label"
                    class="text-[10px] text-dark-400 bg-dark-800 px-1.5 py-0.5 rounded">
                    {{ spec.label }}: {{ spec.value }}
                  </span>
                </div>
              </div>
              <span class="font-bold text-sm">¥{{ Number(item.subtotal).toLocaleString() }}</span>
            </div>
          </div>
        </div>

        <!-- 金额汇总 -->
        <div class="bg-dark-900 rounded-2xl border border-dark-800 p-6">
          <h2 class="text-lg font-bold mb-4">订单金额</h2>
          <div class="space-y-2.5 text-sm">
            <div class="flex justify-between text-dark-300">
              <span>商品金额</span>
              <span>¥{{ Number(order.total_amount).toLocaleString() }}</span>
            </div>
            <div class="flex justify-between text-dark-300">
              <span>运费</span>
              <span>{{ Number(order.shipping_fee) > 0 ? '¥' + Number(order.shipping_fee).toLocaleString() : '包邮' }}</span>
            </div>
            <div v-if="Number(order.discount_amount) > 0" class="flex justify-between text-primary-500">
              <span>优惠减免</span>
              <span>-¥{{ Number(order.discount_amount).toLocaleString() }}</span>
            </div>
            <hr class="border-dark-700 my-3">
            <div class="flex justify-between text-xl font-bold">
              <span>实付金额</span>
              <span class="text-primary-500">¥{{ Number(order.final_amount).toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { orderApi, paymentApi } from '@/api'
import { redirectToPayment } from '@/utils/payment'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const order = ref(null)
const loading = ref(true)
const paying = ref(false)
const cancelling = ref(false)
const isSandboxPaymentPath = computed(() => route.meta.sandboxPayment === true)

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
const isCustomItem = (item) => item?.item_type === 'custom'
const formatSpecs = (specs) => {
  if (!specs || typeof specs !== 'object') return []
  return Object.entries(specs).map(([label, value]) => ({
    label,
    value: Array.isArray(value)
      ? value.join(', ')
      : value && typeof value === 'object'
        ? JSON.stringify(value)
        : String(value),
  }))
}

async function fetchOrder() {
  loading.value = true
  try {
    order.value = await orderApi.getOrder(route.params.id)
  } catch (e) {
    console.error('获取订单详情失败:', e)
    order.value = null
  } finally {
    loading.value = false
  }
}

function resolvePaymentMethod() {
  return ['alipay', 'wechat'].includes(order.value?.payment_method)
    ? order.value.payment_method
    : 'alipay'
}

async function startPayment() {
  if (!order.value) return
  paying.value = true
  try {
    const payment = await paymentApi.createPayment(order.value.id, {
      payment_method: resolvePaymentMethod(),
    })
    redirectToPayment(payment)
  } catch (e) {
    alert('创建支付失败：' + (e.displayMessage || e.message || '请重试'))
  } finally {
    paying.value = false
  }
}

async function sandboxMockPay() {
  if (!order.value || !isSandboxPaymentPath.value) return
  paying.value = true
  try {
    await paymentApi.sandboxMockPay(order.value.id)
    await fetchOrder()
  } catch (e) {
    alert('沙箱支付失败：' + (e.displayMessage || e.message || '请重试'))
  } finally {
    paying.value = false
  }
}

async function cancelOrder() {
  if (!order.value) return
  if (!confirm('确定要取消此订单吗？')) return
  cancelling.value = true
  try {
    await orderApi.cancelOrder(order.value.id, { reason: '用户主动取消' })
    await fetchOrder()
  } catch (e) {
    alert('取消失败：' + (e.message || '请重试'))
  } finally {
    cancelling.value = false
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return
  }
  fetchOrder()
})
</script>
