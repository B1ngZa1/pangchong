<template>
  <div class="min-h-screen bg-black">
    <div class="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      <!-- 页面标题 -->
      <div class="mb-8">
        <p class="text-xs uppercase tracking-[0.25em] text-primary-500 mb-3">准备下一次升级</p>
        <h1 class="text-2xl font-bold text-white">购物车
          <span class="text-dark-500 text-base font-normal ml-2">({{ cart.totalItems }})</span>
        </h1>
        <p class="mt-3 text-sm text-dark-400">心仪的硬件，距离你的桌面更近一步。</p>
      </div>

      <DsAsyncState v-if="cart.loading && cart.isEmpty" state="loading" loading-label="正在加载购物车" />
      <DsAsyncState v-else-if="cart.loadError && cart.isEmpty" state="error" error-title="购物车暂时无法加载" :error-description="cart.loadError" @retry="cart.fetchCart" />
      <!-- 空购物车 -->
      <div v-else-if="cart.isEmpty" class="flex flex-col items-center justify-center py-24">
        <div class="w-32 h-32 rounded-full bg-dark-900 flex items-center justify-center mb-8">
          <svg class="w-16 h-16 text-dark-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <p class="text-dark-400 text-xl mb-2">购物车还是空的</p>
        <p class="text-dark-400 text-sm mb-8">去发现心仪的配件吧</p>
        <router-link to="/products"
          class="inline-flex items-center gap-2 px-8 py-3.5 bg-primary-500 text-dark-950 font-bold rounded-full hover:bg-primary-400 transition-transform hover:scale-[1.01] active:scale-[0.98]">
          <i class="fas fa-arrow-right"></i>去逛逛
        </router-link>
      </div>

      <!-- 购物车主体 -->
      <div v-else class="flex flex-col lg:flex-row gap-8">
        <!-- 左侧：商品清单 -->
        <div class="flex-1 min-w-0">
          <DsAlert v-if="cart.loadError" class="mb-4" title="购物车尚未同步" :description="cart.loadError" tone="warning">
            <template #action><DsButton variant="secondary" size="sm" :loading="cart.loading" @click="cart.fetchCart">重新同步</DsButton></template>
          </DsAlert>
          <!-- 全选工具栏 -->
          <div class="flex items-center justify-between mb-4">
            <DsCheckbox
              :model-value="cart.allSelected"
              label="全选"
              :mixed="hasSelected && !cart.allSelected"
              @update:model-value="cart.toggleSelectAll()"
            />
            <DsButton
              v-if="hasSelected"
              variant="ghost"
              size="sm"
              type="button"
              @click="confirmRemoveSelected"
            >
              <i class="fas fa-trash-alt" aria-hidden="true"></i>删除所选
            </DsButton>
          </div>

          <!-- 商品列表 -->
          <div class="space-y-0">
            <DsCartLineItem
              v-for="item in cart.items"
              :key="item.id"
              :item="item"
              :selected="item.selected"
              :disabled="item.stock <= 0"
              :fallback-image="fallbackImage"
              @toggle="cart.toggleSelect(item.id)"
              @remove="confirmRemove(item)"
              @decrement="updateQuantity(item, -1)"
              @increment="updateQuantity(item, 1)"
            >
              <template #details>
                <OrderDiySnapshot v-if="hasCustomSnapshotDisplay(item)" :item="item" />
              </template>
            </DsCartLineItem>
          </div>

          <!-- 底部操作栏 -->
          <div class="flex items-center justify-between mt-6 pt-6 border-t border-dark-800">
            <router-link to="/products"
              class="flex items-center gap-2 text-dark-400 hover:text-primary-500 text-sm transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              继续购物
            </router-link>
            <span class="text-dark-500 text-xs">已选 {{ cart.selectedCount }} 件</span>
          </div>
        </div>

        <!-- 右侧：订单摘要 – 雷蛇精确尺寸 -->
        <div class="w-full lg:w-[400px] flex-shrink-0">
          <div class="sticky top-24">
            <!-- 主卡片 -->
            <div class="bg-dark-900 rounded-2xl border border-dark-800 shadow-sm overflow-hidden">

              <!-- 价格区域 -->
              <div class="px-6 pt-6 pb-0">
                <p class="text-white text-[32px] font-bold leading-none">
                  ¥{{ cart.totalAmount.toLocaleString() }}
                </p>
                <p v-if="cart.discountAmount > 0" class="text-primary-500 text-sm mt-2">
                  <i class="fas fa-tag mr-1"></i>已优惠 ¥{{ cart.discountAmount.toLocaleString() }}
                </p>
              </div>

              <!-- ADD TO CART 按钮 -->
              <div class="px-6 pt-5 pb-0">
                <DsButton
                  block
                  size="lg"
                  type="button"
                  :disabled="cart.selectedCount === 0 || Boolean(cart.loadError) || cart.loading || updatingIds.length > 0"
                  @click="goCheckout"
                >
                  去结算 ({{ cart.selectedCount }} 件)
                </DsButton>
              </div>

              <!-- 积分奖励 -->
              <div class="px-6 pt-4 pb-3">
                <div class="flex items-center gap-1 text-dark-300 text-xs">
                  <svg class="w-3.5 h-3.5 text-primary-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                  <span>满 <span class="text-primary-500 font-medium">¥{{ cart.commerceSettings.free_shipping_threshold }}</span> 享标准配送包邮</span>
                </div>
              </div>

              <!-- 预计送达 -->
              <div class="px-6 py-2">
                <div class="flex items-center gap-2 text-sm">
                  <span class="text-white font-medium">标准配送</span>
                  <span v-if="cart.shippingCost === 0" class="text-primary-500 font-bold text-xs">· 免运费</span>
                  <span v-else class="text-dark-500 font-bold text-xs">· 运费 ¥{{ cart.shippingCost }}</span>
                </div>
              </div>

              <!-- 门店自提链接 -->
              <div class="px-6 pt-1 pb-4">
                <router-link to="/store" class="flex items-center gap-1 text-primary-500 text-xs hover:underline group">
                  <span>查看胖虫线下自提点</span>
                  <svg class="w-3 h-3 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </router-link>
              </div>

              <!-- 分割线 -->
              <div class="mx-6 border-t border-dark-800"></div>

              <!-- 配送说明 -->
              <div class="px-6 py-4">
                <p class="text-sm text-dark-300">每一次升级，都值得认真对待。</p>
                <p class="text-xs text-dark-400 leading-relaxed mt-2">商品价格与库存将在下单时再次确认，支付前可查看完整订单金额。</p>
              </div>

              <!-- 分割线 -->
              <div class="mx-6 border-t border-dark-800"></div>

              <!-- 价格明细 -->
              <div class="px-6 py-4">
                <DsPriceSummary
                  :subtotal="cart.subtotal"
                  :shipping="cart.shippingCost"
                  :discount="cart.discountAmount"
                  :item-count="cart.selectedCount"
                  free-shipping-label="免运费"
                  :show-total="false"
                />
              </div>

              <!-- 分割线 -->
              <div class="mx-6 border-t border-dark-800"></div>

              <!-- 分期付款 -->
              <div class="px-6 py-3">
                <div class="bg-dark-800 rounded-xl px-3 py-2">
                  <p class="text-dark-400 text-xs leading-relaxed">
                    购买、配送或售后有疑问？<router-link to="/services#faq" class="text-primary-500 hover:underline">查看常见问题</router-link>
                  </p>
                </div>
              </div>

              <!-- 直购说明 -->
              <div class="px-6 pb-4">
                <p class="text-dark-500 text-xs italic text-center">
                  胖虫直购价 · 仅限官网
                </p>
              </div>
            </div>

            <!-- 查看配送选项 / 查看门店 -->
            <div class="mt-3 flex gap-4 px-1">
              <router-link to="/services#delivery" class="flex items-center gap-1.5 text-primary-500 text-xs hover:underline">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                <span>查看配送选项</span>
              </router-link>
              <router-link to="/store" class="flex items-center gap-1.5 text-primary-500 text-xs hover:underline">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>查看门店位置</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <DsDialog
      v-model:open="showDeleteModal"
      title="确认删除"
      :description="deleteMsg"
      size="sm"
    >
      <template #footer>
        <DsButton variant="ghost" type="button" :disabled="deleting" @click="showDeleteModal = false">取消</DsButton>
        <DsButton variant="danger" type="button" :loading="deleting" @click="executeDelete">删除</DsButton>
      </template>
    </DsDialog>

    <div v-if="toastMsg" class="fixed right-4 top-20 z-50 w-[min(22rem,calc(100vw-2rem))]">
      <DsToast
        :visible="Boolean(toastMsg)"
        :message="toastMsg"
        :tone="toastType"
        @dismiss="toastMsg = ''"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import OrderDiySnapshot from '@/components/OrderDiySnapshot.vue'
import { DsAlert, DsAsyncState, DsButton, DsCartLineItem, DsCheckbox, DsDialog, DsPriceSummary, DsToast } from '@/design-system'
import { hasCustomSnapshotDisplay } from '@/utils/orderSpecs'

const router = useRouter()
const cart = useCartStore()
const fallbackImage = '/assets/pangchong-product-fallback.png'

const showDeleteModal = ref(false)
const deleteMsg = ref('')
const deleteTarget = ref(null)
const deleteItemId = ref(null)
const deleting = ref(false)
const updatingIds = ref([])

const toastMsg = ref('')
const toastType = ref('success')
let toastTimer

function showToast(msg, type = 'success') {
  toastMsg.value = msg
  toastType.value = type
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 4000)
}
onUnmounted(() => clearTimeout(toastTimer))

const hasSelected = computed(() => cart.items.some(i => i.selected))

async function updateQuantity(item, delta) {
  if (updatingIds.value.includes(item.id)) return
  updatingIds.value.push(item.id)
  try {
    await cart.updateQuantity(item.id, item.quantity + delta)
  } catch (error) {
    showToast(error.displayMessage || error.message || '更新数量失败，请重试', 'danger')
  } finally {
    updatingIds.value = updatingIds.value.filter(id => id !== item.id)
  }
}

function confirmRemove(item) {
  deleteTarget.value = 'single'
  deleteItemId.value = item.id
  deleteMsg.value = `确定要删除「${item.name}」吗？`
  showDeleteModal.value = true
}

function confirmRemoveSelected() {
  deleteTarget.value = 'selected'
  deleteMsg.value = `确定要删除所选的 ${cart.items.filter(i => i.selected).length} 件商品吗？`
  showDeleteModal.value = true
}

async function executeDelete() {
  if (deleting.value) return
  deleting.value = true
  try {
    if (deleteTarget.value === 'single') await cart.removeItem(deleteItemId.value)
    else if (deleteTarget.value === 'selected') await cart.removeSelected()
    showToast('已删除所选商品')
  } catch (error) {
    showToast(error.displayMessage || error.message || '删除失败，请重试', 'danger')
  } finally {
    deleting.value = false
    showDeleteModal.value = false
    deleteTarget.value = null
    deleteItemId.value = null
  }
}

function goCheckout() {
  if (cart.selectedCount === 0 || cart.loadError || cart.loading || updatingIds.value.length) return
  if (cart.selectedItems.some(i => i.stock <= 0)) {
    showToast('请移除缺货商品后再结算', 'info')
    return
  }
  router.push('/checkout')
}
</script>
