<template>
  <div>
    <DsAlert
      v-if="feedback"
      class="mb-4"
      :title="feedback.title"
      :description="feedback.description"
      :tone="feedback.tone"
      :role="feedback.tone === 'danger' ? 'alert' : 'status'"
      dismissible
      @dismiss="feedback = null"
    />

    <!-- 筛选栏 -->
    <form class="bg-dark-900 rounded-xl border border-dark-800 p-4 mb-4 grid gap-3 sm:grid-cols-[minmax(0,1fr)_12rem_auto] items-end" @submit.prevent="searchOrders">
      <DsField v-model="filters.keyword" label="搜索订单" placeholder="订单号 / 收货人 / 手机号" autocomplete="off" />
      <DsField v-model="filters.status" as="select" label="订单状态" placeholder="全部状态" :options="statusOptions" @change="searchOrders" />
      <DsButton :loading="loading" type="submit"><i class="fas fa-search mr-1" aria-hidden="true"></i>搜索</DsButton>
    </form>

    <!-- 订单表格 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 overflow-hidden">
      <DsAsyncState
        :state="requestState"
        loading-label="正在加载订单列表"
        empty-title="暂无订单数据"
        empty-description="调整搜索条件，或等待新的订单进入系统。"
        error-title="订单列表加载失败"
        :error-description="requestError"
        @retry="fetchOrders"
      >
        <DsDataTable v-if="requestState === 'success'" label="后台订单列表">
        <table>
        <thead>
          <tr class="text-dark-500 border-b border-dark-800 bg-dark-950/50">
            <th class="text-left py-3 px-4">订单号</th>
            <th class="text-left py-3 px-4">收货人</th>
            <th class="text-right py-3 px-4">金额</th>
            <th class="text-center py-3 px-4">商品数</th>
            <th class="text-center py-3 px-4">状态</th>
            <th class="text-left py-3 px-4">下单时间</th>
            <th class="text-center py-3 px-4">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in ordersWithPreview" :key="order.id"
            class="border-b border-dark-800 last:border-0 hover:bg-dark-800/50 transition-colors">
            <td class="py-3 px-4">
              <span class="font-mono text-xs">{{ order.order_no }}</span>
              <div v-if="order.customPreview" class="mt-1 max-w-[260px]">
                <p class="truncate text-[11px] text-dark-300">
                  <span class="font-medium text-primary-500">{{ order.customPreview.title }}</span>
                  <span class="text-dark-600"> · </span>{{ order.customPreview.summary }}
                </p>
                <div v-if="order.customPreview.badges.length" class="mt-1 flex flex-wrap gap-1">
                  <span v-for="badge in order.customPreview.badges.slice(0, 3)" :key="badge.key"
                    class="rounded border border-white/5 bg-dark-800 px-1.5 py-0.5 text-[10px] text-dark-500">
                    {{ badge.label }}：{{ badge.value }}
                  </span>
                </div>
              </div>
            </td>
            <td class="py-3 px-4">
              <p class="font-medium">{{ order.recipient_name }}</p>
              <p class="text-dark-500 text-xs">{{ order.recipient_phone }}</p>
            </td>
            <td class="py-3 px-4 text-right font-bold">¥{{ Number(order.final_amount).toLocaleString() }}</td>
            <td class="py-3 px-4 text-center">
              <div class="inline-flex items-center gap-1.5">
                <span>{{ order.item_count }}</span>
                <span v-if="hasCustomItems(order)"
                  class="rounded-full border border-primary-500/40 bg-primary-500/10 px-2 py-0.5 text-[10px] font-medium leading-none text-primary-500">
                  定制
                </span>
              </div>
            </td>
            <td class="py-3 px-4 text-center">
              <span class="text-xs px-2.5 py-1 rounded-full font-medium" :class="statusClass(order.status)">
                {{ order.status_display }}
              </span>
            </td>
            <td class="py-3 px-4 text-dark-500 text-xs">{{ formatDate(order.created_at) }}</td>
            <td class="py-3 px-4 text-center">
              <div class="flex items-center justify-center gap-2">
                <button @click="viewDetail(order)" class="text-primary-500 hover:underline text-xs">详情</button>
                <button v-if="order.status === 'paid'" @click="openShipDialog(order)"
                  class="text-blue-400 hover:underline text-xs">发货</button>
              </div>
            </td>
          </tr>
        </tbody>
        </table>
        </DsDataTable>
      </DsAsyncState>

      <!-- 分页 -->
      <div v-if="requestState === 'success' && totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-dark-800">
        <span class="text-dark-500 text-xs">共 {{ total }} 条</span>
        <DsPagination v-model:page="currentPage" :total-pages="totalPages" :disabled="loading" @change="fetchOrders" />
      </div>
    </div>

    <!-- 订单详情弹窗 -->
    <DsDialog v-model:open="showDetail" title="订单详情" :description="detail?.order_no ? `订单号：${detail.order_no}` : '正在读取订单信息'" size="lg">
          <DsAsyncState
            :state="detailLoading ? 'loading' : detail ? 'success' : 'error'"
            loading-label="正在加载订单详情"
            error-title="订单详情加载失败"
            :error-description="detailError"
            @retry="retryDetail"
          >
          <div v-if="detail" class="space-y-4">
            <!-- 状态 -->
            <div class="flex items-center gap-3">
              <span class="text-xs px-3 py-1 rounded-full font-medium" :class="statusClass(detail.status)">
                {{ detail.status_display }}
              </span>
              <span class="text-dark-500 text-xs">{{ formatDate(detail.created_at) }}</span>
            </div>

            <!-- 收货信息 -->
            <div class="p-4 bg-dark-800 rounded-lg">
              <p class="text-xs text-dark-500 mb-1">收货信息</p>
              <p class="text-sm font-medium">{{ detail.recipient_name }} {{ detail.recipient_phone }}</p>
              <p class="text-dark-400 text-xs mt-1">{{ detail.shipping_address }}</p>
            </div>

            <!-- 商品 -->
            <div>
              <p class="text-xs text-dark-500 mb-2">商品与定制清单</p>
              <div class="space-y-2">
                <div v-for="item in detail.items" :key="item.id"
                  class="flex items-center gap-3 p-3 bg-dark-800 rounded-lg">
                  <div class="w-10 h-10 bg-dark-700 rounded flex-shrink-0 overflow-hidden flex items-center justify-center">
                    <img v-if="item.product_image" :src="item.product_image" class="w-full h-full object-cover" @error="handleImageError" />
                    <span v-else-if="isCustomItem(item)" class="text-[10px] font-bold text-primary-500">DIY</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 min-w-0">
                      <p class="text-sm truncate">{{ item.product_name }}</p>
                      <span v-if="isCustomItem(item)"
                        class="flex-shrink-0 rounded-full border border-primary-500/40 bg-primary-500/10 px-2 py-0.5 text-[10px] font-medium leading-none text-primary-500">
                        定制
                      </span>
                    </div>
                    <p class="text-dark-500 text-xs">x{{ item.quantity }} · ¥{{ Number(item.price).toLocaleString() }}</p>
                    <OrderDiySnapshot v-if="hasCustomSnapshotDisplay(item)" :item="item" />
                    <div v-else-if="displaySpecs(item).length" class="mt-1 flex flex-wrap gap-1">
                      <span v-for="spec in displaySpecs(item)" :key="spec.label"
                        class="text-[10px] text-dark-400 bg-dark-700 px-1.5 py-0.5 rounded">
                        {{ spec.label }}: {{ spec.value }}
                      </span>
                    </div>
                  </div>
                  <span class="text-sm font-medium">¥{{ Number(item.subtotal).toLocaleString() }}</span>
                </div>
              </div>
            </div>

            <!-- 金额 -->
            <div class="p-4 bg-dark-800 rounded-lg space-y-1.5 text-sm">
              <div class="flex justify-between text-dark-400"><span>商品金额</span><span>¥{{ Number(detail.total_amount).toLocaleString() }}</span></div>
              <div class="flex justify-between text-dark-400"><span>运费</span><span>{{ Number(detail.shipping_fee) > 0 ? '¥'+Number(detail.shipping_fee).toLocaleString() : '包邮' }}</span></div>
              <div v-if="Number(detail.discount_amount) > 0" class="flex justify-between text-primary-500"><span>优惠</span><span>-¥{{ Number(detail.discount_amount).toLocaleString() }}</span></div>
              <div class="flex justify-between font-bold pt-1 border-t border-dark-700"><span>实付</span><span class="text-primary-500">¥{{ Number(detail.final_amount).toLocaleString() }}</span></div>
            </div>

            <!-- 买家信息 -->
            <div v-if="detail.user" class="p-4 bg-dark-800 rounded-lg">
              <p class="text-xs text-dark-500 mb-1">买家信息</p>
              <p class="text-sm">{{ detail.user.nickname || detail.user.username }} · {{ detail.user.email }}</p>
            </div>

            <!-- 物流 -->
            <div v-if="detail.tracking_number" class="p-4 bg-dark-800 rounded-lg">
              <p class="text-xs text-dark-500 mb-1">物流信息</p>
              <p class="text-sm">{{ detail.shipping_company }} · {{ detail.tracking_number }}</p>
            </div>
          </div>
          </DsAsyncState>
    </DsDialog>

    <!-- 发货弹窗 -->
    <DsDialog v-model:open="showShipDialog" title="订单发货" :description="`订单号：${shipOrder?.order_no || ''}`" size="sm">
          <DsAlert v-if="shipError" class="mb-4" title="无法提交发货" :description="shipError" tone="danger" role="alert" />
          <div class="space-y-3 mb-4">
            <DsField
              v-model="shipForm.shipping_company"
              as="select"
              label="物流公司"
              placeholder="选择物流公司"
              :options="shippingCompanies"
              :error="shipError && !shipForm.shipping_company ? '请选择物流公司' : undefined"
              required
            />
            <DsField
              v-model="shipForm.tracking_number"
              label="物流单号"
              placeholder="请输入物流单号"
              :error="shipError && !shipForm.tracking_number ? '请输入物流单号' : undefined"
              required
            />
          </div>
          <template #footer>
            <DsButton variant="ghost" type="button" @click="showShipDialog = false">取消</DsButton>
            <DsButton :loading="shipping" type="button" @click="confirmShip">确认发货</DsButton>
          </template>
    </DsDialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import OrderDiySnapshot from '@/components/OrderDiySnapshot.vue'
import { DsAlert, DsAsyncState, DsButton, DsDataTable, DsDialog, DsField, DsPagination } from '@/design-system'
import {
  buildOrderCustomPreview,
  formatCustomSpecs,
  formatSpecs,
  hasCustomSnapshotDisplay,
  isCustomOrderItem,
} from '@/utils/orderSpecs'

const orders = ref([])
const loading = ref(true)
const requestState = ref('loading')
const requestError = ref('请检查网络后重试。')
const feedback = ref(null)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const filters = ref({ keyword: '', status: '' })
let listRequestId = 0
let detailRequestId = 0
const statusOptions = [
  { value: 'pending', label: '待付款' },
  { value: 'paid', label: '待发货' },
  { value: 'shipped', label: '已发货' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
]
const fallbackImage = '/assets/pangchong-product-fallback.png'

function handleImageError(event) {
  const image = event.target
  if (image instanceof HTMLImageElement && !image.src.endsWith(fallbackImage)) {
    image.src = fallbackImage
  }
}

const totalPages = computed(() => Math.ceil(total.value / pageSize))
const ordersWithPreview = computed(() => orders.value.map(order => ({
  ...order,
  customPreview: buildOrderCustomPreview(order),
})))
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// 详情弹窗
const showDetail = ref(false)
const detail = ref(null)
const detailTarget = ref(null)
const detailLoading = ref(false)
const detailError = ref('请重试。')

// 发货弹窗
const showShipDialog = ref(false)
const shipOrder = ref(null)
const shipForm = ref({ shipping_company: '', tracking_number: '' })
const shipping = ref(false)
const shipError = ref('')
const shippingCompanies = [
  { value: '顺丰速运', label: '顺丰速运' },
  { value: '中通快递', label: '中通快递' },
  { value: '圆通速递', label: '圆通速递' },
  { value: '韵达快递', label: '韵达快递' },
  { value: '申通快递', label: '申通快递' },
  { value: '京东物流', label: '京东物流' },
  { value: '邮政EMS', label: '邮政EMS' },
]

const statusClass = (s) => ({
  pending: 'bg-yellow-500/20 text-yellow-400',
  paid: 'bg-blue-500/20 text-blue-400',
  shipped: 'bg-indigo-500/20 text-indigo-400',
  completed: 'bg-green-500/20 text-green-400',
  cancelled: 'bg-dark-700 text-dark-400',
}[s] || 'bg-dark-700 text-dark-400')

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''
const isCustomItem = isCustomOrderItem
const hasCustomItems = (order) => (order.items || []).some(isCustomItem)
const displaySpecs = (item) => isCustomItem(item)
  ? formatCustomSpecs(item.product_specs)
  : formatSpecs(item.product_specs)

async function fetchOrders() {
  const requestId = ++listRequestId
  loading.value = true
  requestState.value = 'loading'
  requestError.value = '请检查网络后重试。'
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.status) params.status = filters.value.status
    const data = await adminApi.getOrders(params)
    if (requestId !== listRequestId) return
    orders.value = data.items || []
    total.value = data.total || 0
    requestState.value = orders.value.length ? 'success' : 'empty'
  } catch (e) {
    if (requestId !== listRequestId) return
    console.warn('后台订单服务不可用', e)
    requestError.value = e.displayMessage || e.message || '请检查网络后重试。'
    requestState.value = 'error'
  } finally {
    if (requestId === listRequestId) loading.value = false
  }
}

function searchOrders() {
  currentPage.value = 1
  return fetchOrders()
}

async function viewDetail(order) {
  const requestId = ++detailRequestId
  detailTarget.value = order
  showDetail.value = true
  detail.value = null
  detailLoading.value = true
  detailError.value = '请重试。'
  try {
    const response = await adminApi.getOrderDetail(order.id)
    if (requestId === detailRequestId) detail.value = response
  } catch (e) {
    if (requestId !== detailRequestId) return
    detailError.value = e.displayMessage || e.message || '请检查网络后重试。'
  } finally {
    if (requestId === detailRequestId) detailLoading.value = false
  }
}

function retryDetail() {
  if (detailTarget.value) return viewDetail(detailTarget.value)
  showDetail.value = false
}

function openShipDialog(order) {
  shipOrder.value = order
  shipForm.value = { shipping_company: '', tracking_number: '' }
  shipError.value = ''
  showShipDialog.value = true
}

async function confirmShip() {
  if (shipping.value || !shipOrder.value) return
  const shipment = {
    shipping_company: shipForm.value.shipping_company.trim(),
    tracking_number: shipForm.value.tracking_number.trim(),
  }
  if (!shipment.shipping_company || !shipment.tracking_number) {
    shipError.value = '请填写物流公司和物流单号。'
    return
  }
  shipError.value = ''
  shipping.value = true
  try {
    await adminApi.shipOrder(shipOrder.value.id, shipment)
    showShipDialog.value = false
    await fetchOrders()
    feedback.value = { title: '发货信息已保存', description: '订单状态已更新为已发货。', tone: 'success' }
  } catch (e) {
    shipError.value = e.displayMessage || e.message || '请重试。'
  } finally {
    shipping.value = false
  }
}

onMounted(fetchOrders)
</script>
