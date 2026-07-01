<template>
  <div>
    <!-- 筛选栏 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 p-4 mb-4 flex flex-wrap gap-3">
      <input v-model="filters.keyword" placeholder="搜索订单号/收货人/手机号" @keyup.enter="fetchOrders"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-4 py-2 text-sm focus:border-primary-500 outline-none w-64" />
      <select v-model="filters.status" @change="fetchOrders"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-3 py-2 text-sm focus:border-primary-500 outline-none">
        <option value="">全部状态</option>
        <option value="pending">待付款</option>
        <option value="paid">待发货</option>
        <option value="shipped">已发货</option>
        <option value="completed">已完成</option>
        <option value="cancelled">已取消</option>
      </select>
      <button @click="fetchOrders" class="px-4 py-2 bg-primary-500 text-dark-950 text-sm font-semibold rounded-lg hover:bg-primary-400">
        <i class="fas fa-search mr-1"></i>搜索
      </button>
    </div>

    <!-- 订单表格 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 overflow-hidden">
      <div v-if="loading" class="flex justify-center py-16">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
      </div>

      <div v-else-if="orders.length === 0" class="text-center py-16 text-dark-500">
        暂无订单数据
      </div>

      <table v-else class="w-full text-sm">
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

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-dark-800">
        <span class="text-dark-500 text-xs">共 {{ total }} 条</span>
        <div class="flex gap-1">
          <button v-for="p in visiblePages" :key="p"
            @click="currentPage = p; fetchOrders()"
            class="w-8 h-8 rounded text-xs font-medium transition-colors"
            :class="currentPage === p ? 'bg-primary-500 text-dark-950' : 'bg-dark-800 text-dark-400 hover:text-white'">
            {{ p }}
          </button>
        </div>
      </div>
    </div>

    <!-- 订单详情弹窗 -->
    <Teleport to="body">
      <div v-if="showDetail" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="bg-dark-900 rounded-2xl border border-dark-700 w-[90vw] max-w-2xl max-h-[85vh] shadow-2xl flex flex-col">
          <div class="flex items-center justify-between p-6 border-b border-dark-800">
            <h3 class="text-lg font-bold">订单详情</h3>
            <button @click="showDetail = false" class="text-dark-500 hover:text-white"><i class="fas fa-times"></i></button>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-4" v-if="detail">
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
                    <img v-if="item.product_image" :src="item.product_image" class="w-full h-full object-cover" />
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
        </div>
      </div>
    </Teleport>

    <!-- 发货弹窗 -->
    <Teleport to="body">
      <div v-if="showShipDialog" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="bg-dark-900 rounded-2xl border border-dark-700 p-6 w-[90vw] max-w-md shadow-2xl">
          <h3 class="text-lg font-bold mb-4">订单发货</h3>
          <p class="text-dark-400 text-sm mb-4">订单号：{{ shipOrder?.order_no }}</p>
          <div class="space-y-3 mb-4">
            <div>
              <label class="text-sm text-dark-400 block mb-1">物流公司</label>
              <select v-model="shipForm.shipping_company"
                class="w-full bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-3 py-2 text-sm focus:border-primary-500 outline-none">
                <option value="">选择物流公司</option>
                <option value="顺丰速运">顺丰速运</option>
                <option value="中通快递">中通快递</option>
                <option value="圆通速递">圆通速递</option>
                <option value="韵达快递">韵达快递</option>
                <option value="申通快递">申通快递</option>
                <option value="京东物流">京东物流</option>
                <option value="邮政EMS">邮政EMS</option>
              </select>
            </div>
            <div>
              <label class="text-sm text-dark-400 block mb-1">物流单号</label>
              <input v-model="shipForm.tracking_number" placeholder="请输入物流单号"
                class="w-full bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-3 py-2 text-sm focus:border-primary-500 outline-none" />
            </div>
          </div>
          <div class="flex gap-3 justify-end">
            <button @click="showShipDialog = false" class="px-5 py-2 rounded-lg text-sm bg-dark-800 text-dark-300 hover:bg-dark-700">取消</button>
            <button @click="confirmShip" :disabled="shipping"
              class="px-5 py-2 rounded-lg text-sm bg-primary-500 text-dark-950 font-semibold hover:bg-primary-400 disabled:opacity-50">
              {{ shipping ? '发货中...' : '确认发货' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import OrderDiySnapshot from '@/components/OrderDiySnapshot.vue'
import {
  buildOrderCustomPreview,
  formatCustomSpecs,
  formatSpecs,
  hasCustomSnapshotDisplay,
  isCustomOrderItem,
} from '@/utils/orderSpecs'

const orders = ref([])
const loading = ref(true)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const filters = ref({ keyword: '', status: '' })

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

// 发货弹窗
const showShipDialog = ref(false)
const shipOrder = ref(null)
const shipForm = ref({ shipping_company: '', tracking_number: '' })
const shipping = ref(false)

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
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.status) params.status = filters.value.status
    const data = await adminApi.getOrders(params)
    orders.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('获取订单失败:', e)
  } finally {
    loading.value = false
  }
}

async function viewDetail(order) {
  try {
    detail.value = await adminApi.getOrderDetail(order.id)
    showDetail.value = true
  } catch (e) {
    alert('获取详情失败')
  }
}

function openShipDialog(order) {
  shipOrder.value = order
  shipForm.value = { shipping_company: '', tracking_number: '' }
  showShipDialog.value = true
}

async function confirmShip() {
  if (!shipForm.value.shipping_company || !shipForm.value.tracking_number) {
    alert('请填写物流公司和物流单号')
    return
  }
  shipping.value = true
  try {
    await adminApi.shipOrder(shipOrder.value.id, shipForm.value)
    showShipDialog.value = false
    fetchOrders()
  } catch (e) {
    alert('发货失败：' + (e.message || '请重试'))
  } finally {
    shipping.value = false
  }
}

onMounted(fetchOrders)
</script>
