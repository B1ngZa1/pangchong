<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <DsAsyncState
        v-if="loadState !== 'success'"
        :state="loadState"
        loading-label="正在加载订单详情"
        empty-title="订单不存在"
        empty-description="订单可能已被删除，或当前账号没有访问权限。"
        error-title="订单详情加载失败"
        :error-description="loadError"
        @retry="fetchOrder"
      >
        <template #action>
          <DsButton v-if="loadState === 'error'" size="sm" :loading="loadState === 'loading'" @click="fetchOrder">重新加载订单</DsButton>
          <DsButton variant="secondary" size="sm" type="button" @click="router.push('/orders')">返回订单列表</DsButton>
        </template>
      </DsAsyncState>

      <div v-else-if="order">
        <div class="flex flex-wrap items-start justify-between gap-4 mb-8">
          <div class="min-w-0">
            <h1 class="text-3xl font-bold">订单详情</h1>
            <p class="text-dark-400 text-sm mt-2 break-all">订单号：{{ order.order_no }}</p>
          </div>
          <router-link to="/orders" class="text-primary-500 hover:underline text-sm">
            <i class="fas fa-arrow-left mr-1"></i>返回订单列表
          </router-link>
        </div>

        <DsAlert
          v-if="feedback"
          class="mb-6"
          :title="feedback.title"
          :description="feedback.description"
          :tone="feedback.tone"
          :role="feedback.tone === 'danger' ? 'alert' : 'status'"
          dismissible
          @dismiss="feedback = null"
        />

        <!-- 订单状态 -->
        <div class="bg-dark-900 rounded-2xl border border-dark-800 p-6 mb-6">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div>
              <span class="text-xs px-3 py-1 rounded-full font-medium" :class="statusClass(order.status)">
                {{ statusText(order.status) }}
              </span>
              <p class="text-dark-500 text-sm mt-2">{{ formatDate(order.created_at) }}</p>
            </div>
            <div v-if="order.status === 'pending'" class="flex flex-wrap items-center gap-3">
              <p class="text-yellow-400 text-sm font-medium w-full">完成支付后开始备货</p>
              <DsButton :loading="paying" :disabled="cancelling" type="button" @click="startPayment">去支付</DsButton>
              <DsButton v-if="isSandboxPaymentPath" variant="secondary" :loading="paying" type="button" @click="sandboxMockPay">沙箱模拟支付</DsButton>
            </div>
            <div v-if="order.status === 'pending'" class="mt-2">
              <DsButton variant="ghost" size="sm" :loading="cancelling" :disabled="paying" type="button" @click="cancelOrder">取消订单</DsButton>
            </div>
            <DsButton v-if="order.status === 'shipped'" :loading="completing" @click="completeDialogOpen = true">确认收货</DsButton>
          </div>

          <!-- 物流信息 -->
          <div v-if="order.tracking_number" class="mt-4 p-3 bg-dark-800 rounded-lg">
            <p class="text-xs text-dark-400">
              <i class="fas fa-truck mr-1"></i>
              {{ order.shipping_company }} · {{ order.tracking_number }}
            </p>
          </div>
        </div>

        <!-- 订单进度 -->
        <div class="bg-dark-900 rounded-2xl border border-dark-800 p-6 mb-6">
          <DsOrderTimeline :events="timelineEvents" :current-label="timelineCurrentLabel" />
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
                <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name" class="w-full h-full object-cover" @error="handleImageError" />
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
                <OrderDiySnapshot v-if="hasCustomSnapshotDisplay(item)" :item="item" />
                <div v-else-if="displaySpecs(item).length" class="mt-1 flex flex-wrap gap-1">
                  <span v-for="spec in displaySpecs(item)" :key="spec.label"
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
              <span>{{ order.status === 'pending' ? '应付金额' : '订单金额' }}</span>
              <span class="text-primary-500">¥{{ Number(order.final_amount).toLocaleString() }}</span>
            </div>
          </div>
        </div>

        <DsDialog v-model:open="cancelDialogOpen" title="确认取消订单？" description="取消后当前订单将停止处理，此操作不可撤销。">
          <p class="text-sm text-dark-300">如果商品已经进入装机或发货阶段，请先联系客户服务。</p>
          <template #footer>
            <DsButton variant="ghost" type="button" @click="cancelDialogOpen = false">暂不取消</DsButton>
            <DsButton variant="danger" :loading="cancelling" type="button" @click="confirmCancelOrder">确认取消</DsButton>
          </template>
        </DsDialog>
        <DsDialog v-model:open="completeDialogOpen" title="确认已收到商品？" description="请检查商品数量、外观和配件，确认无误后完成收货。">
          <template #footer>
            <DsButton variant="ghost" :disabled="completing" @click="completeDialogOpen = false">暂未收到</DsButton>
            <DsButton :loading="completing" @click="confirmCompleteOrder">确认收货</DsButton>
          </template>
        </DsDialog>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { orderApi, paymentApi } from '@/api'
import { redirectToPayment } from '@/utils/payment'
import OrderDiySnapshot from '@/components/OrderDiySnapshot.vue'
import { formatCustomSpecs, formatSpecs, hasCustomSnapshotDisplay, isCustomOrderItem } from '@/utils/orderSpecs'
import { DsAlert, DsAsyncState, DsButton, DsDialog, DsOrderTimeline } from '@/design-system'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const fallbackImage = '/assets/pangchong-product-fallback.png'

function handleImageError(event) {
  const image = event.target
  if (image instanceof HTMLImageElement && !image.src.endsWith(fallbackImage)) {
    image.src = fallbackImage
  }
}

const order = ref(null)
const loadState = ref('loading')
const loadError = ref('请检查网络后重试。')
const paying = ref(false)
const cancelling = ref(false)
const cancelDialogOpen = ref(false)
const completeDialogOpen = ref(false)
const completing = ref(false)
let requestId = 0
const feedback = ref(null)
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
const isCustomItem = isCustomOrderItem
const displaySpecs = (item) => isCustomItem(item)
  ? formatCustomSpecs(item.product_specs)
  : formatSpecs(item.product_specs)

const timelineCurrentLabel = computed(() => order.value ? statusText(order.value.status) : '')
const timelineEvents = computed(() => {
  if (!order.value) return []
  const currentStatus = order.value.status
  const stages = [
    { id: 'created', label: '订单已提交', timestamp: order.value.created_at, description: '订单信息已确认，等待后续履约。' },
    { id: 'paid', label: '支付成功', timestamp: order.value.paid_at, description: '款项已到账，订单进入备货流程。' },
    { id: 'shipped', label: '商品已发货', timestamp: order.value.shipped_at, description: order.value.tracking_number ? `${order.value.shipping_company || '物流'} · ${order.value.tracking_number}` : '包裹出库后会在这里显示物流信息。' },
    { id: 'completed', label: '订单已完成', timestamp: order.value.completed_at, description: '感谢你的购买，欢迎再次探索胖虫硬件。' },
  ]
  const statusIndex = { pending: 0, paid: 1, shipped: 2, completed: 3 }
  if (currentStatus === 'cancelled') {
    return [
      { ...stages[0], state: 'complete' },
      ...(order.value.paid_at ? [{ ...stages[1], state: 'complete' }] : []),
      { id: 'cancelled', label: '订单已取消', timestamp: order.value.updated_at, description: '订单已停止处理，如有疑问请联系客服。', state: 'cancelled' },
    ]
  }
  if (currentStatus === 'refunded') {
    return [
      { ...stages[0], state: 'complete' },
      { ...stages[1], state: 'complete' },
      { id: 'refunded', label: '款项已退款', timestamp: order.value.updated_at, description: '退款状态已更新，请留意原支付账户。', state: 'refunded' },
    ]
  }
  const activeIndex = statusIndex[currentStatus] ?? 0
  return stages.map((stage, index) => ({
    ...stage,
    state: index < activeIndex ? 'complete' : index === activeIndex ? 'current' : 'upcoming',
  }))
})

function setFeedback(title, description, tone = 'danger') {
  feedback.value = { title, description, tone }
}

async function fetchOrder() {
  const activeRequest = ++requestId
  loadState.value = 'loading'
  loadError.value = '请检查网络后重试。'
  try {
    const data = await orderApi.getOrder(route.params.id)
    if (activeRequest !== requestId) return
    order.value = data
    loadState.value = order.value ? 'success' : 'empty'
  } catch (e) {
    if (activeRequest !== requestId) return
    order.value = null
    loadError.value = e.displayMessage || e.message || '请检查网络后重试。'
    loadState.value = e.response?.status === 404 ? 'empty' : 'error'
  }
}

function resolvePaymentMethod() {
  return ['alipay', 'wechat'].includes(order.value?.payment_method)
    ? order.value.payment_method
    : 'alipay'
}

async function startPayment() {
  if (!order.value || paying.value || cancelling.value) return
  feedback.value = null
  paying.value = true
  try {
    const payment = await paymentApi.createPayment(order.value.id, {
      payment_method: resolvePaymentMethod(),
    })
    redirectToPayment(payment)
  } catch (e) {
    setFeedback('创建支付失败', e.displayMessage || e.message || '请重试')
  } finally {
    paying.value = false
  }
}

async function sandboxMockPay() {
  if (!order.value || !isSandboxPaymentPath.value) return
  feedback.value = null
  paying.value = true
  try {
    await paymentApi.sandboxMockPay(order.value.id)
    await fetchOrder()
    if (loadState.value === 'success') setFeedback('支付状态已更新', '沙箱支付已完成，订单进入备货流程。', 'success')
  } catch (e) {
    setFeedback('沙箱支付失败', e.displayMessage || e.message || '请重试')
  } finally {
    paying.value = false
  }
}

async function cancelOrder() {
  if (!order.value) return
  feedback.value = null
  cancelDialogOpen.value = true
}

async function confirmCancelOrder() {
  if (!order.value || cancelling.value || paying.value) return
  cancelling.value = true
  try {
    await orderApi.cancelOrder(order.value.id, { reason: '用户主动取消' })
    cancelDialogOpen.value = false
    await fetchOrder()
    if (loadState.value === 'success') setFeedback('订单已取消', '当前订单已停止处理。', 'success')
  } catch (e) {
    cancelDialogOpen.value = false
    setFeedback('取消订单失败', e.displayMessage || e.message || '请重试')
  } finally {
    cancelling.value = false
  }
}

async function confirmCompleteOrder() {
  if (!order.value || completing.value) return
  completing.value = true
  try {
    order.value = await orderApi.completeOrder(order.value.id)
    completeDialogOpen.value = false
    setFeedback('收货已确认', '感谢你的购买，售后服务可在服务中心查看。', 'success')
  } catch (error) {
    completeDialogOpen.value = false
    setFeedback('确认收货失败', error.displayMessage || error.message || '请重试')
  } finally {
    completing.value = false
  }
}

watch(() => route.params.id, () => {
  feedback.value = null
  cancelDialogOpen.value = false
  completeDialogOpen.value = false
  if (userStore.isLoggedIn) fetchOrder()
})

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return
  }
  fetchOrder()
})
</script>
