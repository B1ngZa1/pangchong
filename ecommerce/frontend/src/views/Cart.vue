<template>
  <div class="min-h-screen bg-black">
    <div class="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-white">购物车
          <span class="text-dark-500 text-base font-normal ml-2">({{ cart.totalItems }})</span>
        </h1>
      </div>

      <!-- 空购物车 -->
      <div v-if="cart.isEmpty" class="flex flex-col items-center justify-center py-24">
        <div class="w-32 h-32 rounded-full bg-dark-900 flex items-center justify-center mb-8">
          <svg class="w-16 h-16 text-dark-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <p class="text-dark-400 text-xl mb-2">购物车还是空的</p>
        <p class="text-[#888] text-sm mb-8">去发现心仪的配件吧</p>
        <router-link to="/products"
          class="inline-flex items-center gap-2 px-8 py-3.5 bg-primary-500 text-dark-950 font-bold rounded-full hover:bg-[#2e9e1e] transition-all hover:scale-[1.01] active:scale-[0.98]">
          <i class="fas fa-arrow-right"></i>去逛逛
        </router-link>
      </div>

      <!-- 购物车主体 -->
      <div v-else class="flex flex-col lg:flex-row gap-8">
        <!-- 左侧：商品清单 -->
        <div class="flex-1 min-w-0">
          <!-- 全选工具栏 -->
          <div class="flex items-center justify-between mb-4">
            <label class="flex items-center gap-3 cursor-pointer group">
              <div class="relative">
                <input type="checkbox" :checked="cart.allSelected" @change="cart.toggleSelectAll()"
                  class="peer w-5 h-5 rounded border-2 border-[#444] bg-transparent appearance-none cursor-pointer checked:border-primary-500 checked:bg-primary-500 transition-all" />
                <svg class="absolute inset-0 w-5 h-5 text-dark-950 opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span class="text-sm text-[#AAAAAA] group-hover:text-white transition-colors">全选</span>
            </label>
            <button v-if="hasSelected" @click="confirmRemoveSelected"
              class="flex items-center gap-1.5 text-xs text-[#888] hover:text-red-400 transition-colors px-3 py-1.5 rounded-lg hover:bg-red-500/10">
              <i class="fas fa-trash-alt"></i>删除所选
            </button>
          </div>

          <!-- 商品列表 -->
          <div class="space-y-0">
            <div v-for="(item, idx) in cart.items" :key="item.id"
              class="group py-6 transition-opacity"
              :class="{ 'opacity-40 pointer-events-none': item.stock <= 0, 'border-b border-[#2A2A2A]': idx < cart.items.length - 1 }">

              <div class="flex gap-5">
                <!-- 勾选 -->
                <div class="flex items-start pt-1">
                  <div class="relative">
                    <input type="checkbox" :checked="item.selected" :disabled="item.stock <= 0"
                      @change="cart.toggleSelect(item.id)"
                      class="peer w-5 h-5 rounded border-2 border-[#444] bg-transparent appearance-none cursor-pointer checked:border-primary-500 checked:bg-primary-500 transition-all disabled:opacity-30" />
                    <svg class="absolute inset-0 w-5 h-5 text-dark-950 opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity"
                      fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>

                <!-- 缩略图 120x120 -->
                <div class="w-[120px] h-[120px] flex-shrink-0 bg-[#222] rounded-lg overflow-hidden">
                  <img v-if="item.image_url" :src="item.image_url" :alt="item.name"
                    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
                  <div v-else class="w-full h-full flex items-center justify-center text-[#444]">
                    <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                  </div>
                </div>

                <!-- 信息区 -->
                <div class="flex-1 min-w-0 flex flex-col justify-between">
                  <div>
                    <div class="flex items-start justify-between gap-3">
                      <div class="min-w-0">
                        <h3 class="font-bold text-white text-base leading-snug">{{ item.name }}</h3>
                        <p v-if="item.brand || item.model" class="text-[#AAAAAA] text-xs mt-1">
                          {{ item.brand }} {{ item.model }}
                        </p>
                        <div class="flex flex-wrap gap-1.5 mt-2" v-if="item.specs && Object.keys(item.specs).length > 0">
                          <span v-for="(val, key) in firstSpecs(item.specs)" :key="key"
                            class="text-[12px] text-[#AAAAAA] bg-[#1A1A1A] px-2 py-0.5 rounded">
                            {{ val }}
                          </span>
                        </div>
                      </div>
                      <!-- 删除 -->
                      <button @click="confirmRemove(item)"
                        class="text-[#888] hover:text-red-400 transition-colors flex-shrink-0 p-1">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>

                    <!-- 库存状态 -->
                    <div class="mt-2">
                      <span v-if="item.stock <= 0"
                        class="text-[10px] bg-red-500/15 text-red-400 px-2 py-0.5 rounded font-medium">暂时缺货</span>
                      <span v-else-if="item.stock <= 5"
                        class="text-[10px] bg-yellow-500/15 text-yellow-400 px-2 py-0.5 rounded font-medium">仅剩 {{ item.stock }} 件</span>
                    </div>
                  </div>

                  <div class="flex items-center justify-between mt-3">
                    <!-- 价格 -->
                    <div class="flex items-baseline gap-2">
                      <span class="text-primary-500 font-bold text-sm">¥{{ Number(item.price).toLocaleString() }}</span>
                      <span v-if="item.original_price && item.original_price > item.price"
                        class="text-[#666] text-xs line-through">¥{{ Number(item.original_price).toLocaleString() }}</span>
                    </div>

                    <!-- 数量控制器 + 小计 -->
                    <div class="flex items-center gap-4">
                      <!-- 数量控制器 -->
                      <div class="flex items-center h-[36px] rounded bg-[#1A1A1A] overflow-hidden">
                        <button @click="cart.updateQuantity(item.id, item.quantity - 1)"
                          :disabled="item.quantity <= 1 || item.stock <= 0"
                          class="w-[32px] h-full flex items-center justify-center text-white hover:text-primary-500 disabled:opacity-30 transition-colors text-sm">
                          -
                        </button>
                        <div class="w-[36px] h-full flex items-center justify-center bg-[#111] text-white text-sm font-medium border-x border-[#2A2A2A]">
                          {{ item.quantity }}
                        </div>
                        <button @click="cart.updateQuantity(item.id, item.quantity + 1)"
                          :disabled="item.quantity >= Math.min(99, item.stock) || item.stock <= 0"
                          class="w-[32px] h-full flex items-center justify-center text-white hover:text-primary-500 disabled:opacity-30 transition-colors text-sm">
                          +
                        </button>
                      </div>
                      <!-- 小计 -->
                      <div class="text-right min-w-[80px]">
                        <span class="text-base font-bold text-primary-500">¥{{ (Number(item.price) * item.quantity).toLocaleString() }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 底部操作栏 -->
          <div class="flex items-center justify-between mt-6 pt-6 border-t border-[#2A2A2A]">
            <router-link to="/products"
              class="flex items-center gap-2 text-[#888] hover:text-primary-500 text-sm transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              继续购物
            </router-link>
            <span class="text-[#666] text-xs">已选 {{ cart.selectedCount }} 件</span>
          </div>
        </div>

        <!-- 右侧：订单摘要 – 雷蛇精确尺寸 -->
        <div class="w-full lg:w-[400px] flex-shrink-0">
          <div class="sticky top-24">
            <!-- 主卡片 -->
            <div class="bg-[#111111] rounded-2xl border border-[#2A2A2A] shadow-[0_2px_8px_rgba(0,0,0,0.2)] overflow-hidden">

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
                <button @click="goCheckout"
                  class="w-full h-[48px] bg-primary-500 text-dark-950 text-base font-bold rounded-full transition-all duration-200 hover:bg-[#2e9e1e] hover:scale-[1.01] active:scale-[0.98] disabled:opacity-40 disabled:hover:scale-100 disabled:hover:bg-primary-500 disabled:cursor-not-allowed"
                  :disabled="cart.selectedCount === 0">
                  去结算 ({{ cart.selectedCount }} 件)
                </button>
              </div>

              <!-- 积分奖励 -->
              <div class="px-6 pt-4 pb-3">
                <div class="flex items-center gap-1 text-[#AAAAAA] text-xs">
                  <svg class="w-3.5 h-3.5 text-primary-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                  <span>最高可赚取 <span class="text-primary-500 font-medium">{{ pointsEarned }}</span> 胖虫积分</span>
                </div>
              </div>

              <!-- 预计送达 -->
              <div class="px-6 py-2">
                <div class="flex items-center gap-2 text-sm">
                  <span class="text-white font-medium">{{ deliveryRange }}</span>
                  <span v-if="cart.shippingCost === 0" class="text-primary-500 font-bold text-xs">· 免运费</span>
                  <span v-else class="text-dark-500 font-bold text-xs">· 运费 ¥{{ cart.shippingCost }}</span>
                </div>
              </div>

              <!-- 门店自提链接 -->
              <div class="px-6 pt-1 pb-4">
                <button class="flex items-center gap-1 text-primary-500 text-xs hover:underline group">
                  <span>查看胖虫线下自提点</span>
                  <svg class="w-3 h-3 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>

              <!-- 优惠码 -->
              <div class="px-6 pb-4">
                <div v-if="cart.coupon.code" class="flex items-center justify-between bg-primary-500/10 border border-primary-500/20 rounded-lg px-3 py-2">
                  <div class="flex items-center gap-2">
                    <svg class="w-3.5 h-3.5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    <span class="text-primary-500 text-sm font-medium">{{ cart.coupon.code }}</span>
                    <span class="text-primary-500/70 text-xs">-¥{{ cart.coupon.discount }}</span>
                  </div>
                  <button @click="cart.removeCoupon()" class="text-[#666] hover:text-red-400 transition-colors p-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div v-else class="flex gap-2">
                  <input v-model="couponInput" placeholder="输入优惠码" @keyup.enter="applyCoupon"
                    class="flex-1 h-10 bg-[#1A1A1A] text-white border-0 rounded-lg px-3 text-sm outline-none focus:ring-1 focus:ring-primary-500/50 placeholder:text-[#555]" />
                  <button @click="applyCoupon"
                    class="w-20 h-10 bg-primary-500 text-dark-950 text-sm font-bold rounded-lg hover:bg-[#2e9e1e] transition-colors">
                    应用
                  </button>
                </div>
                <p v-if="couponMsg" :class="['text-xs mt-2', couponSuccess ? 'text-primary-500' : 'text-red-400']">
                  {{ couponMsg }}
                </p>
              </div>

              <!-- 分割线 -->
              <div class="mx-6 border-t border-[#2A2A2A]"></div>

              <!-- 配送地区 -->
              <div class="px-6 py-4">
                <label class="text-[11px] text-[#888] block mb-2 uppercase tracking-wider">配送地区</label>
                <select v-model="shippingRegion" @change="cart.setShippingRegion(shippingRegion)"
                  class="w-full h-10 bg-[#1A1A1A] text-white border-0 rounded-lg px-3 text-sm outline-none focus:ring-1 focus:ring-primary-500/50 appearance-none cursor-pointer">
                  <option v-for="rate in shippingRates" :key="rate.name" :value="rate.name">
                    {{ rate.name }} {{ rate.cost === 0 ? '(包邮)' : '(¥' + rate.cost + ')' }}
                  </option>
                </select>
              </div>

              <!-- 分割线 -->
              <div class="mx-6 border-t border-[#2A2A2A]"></div>

              <!-- 价格明细 -->
              <div class="px-6 py-4 space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-[#888]">商品金额 ({{ cart.selectedCount }} 件)</span>
                  <span class="text-white">¥{{ cart.subtotal.toLocaleString() }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-[#888]">运费</span>
                  <span :class="cart.shippingCost === 0 ? 'text-primary-500 font-medium' : 'text-white'">
                    {{ cart.shippingCost === 0 ? '免运费' : '¥' + cart.shippingCost }}
                  </span>
                </div>
                <div v-if="cart.discountAmount > 0" class="flex justify-between text-sm">
                  <span class="text-primary-500">优惠减免</span>
                  <span class="text-primary-500">-¥{{ cart.discountAmount.toLocaleString() }}</span>
                </div>
              </div>

              <!-- 分割线 -->
              <div class="mx-6 border-t border-[#2A2A2A]"></div>

              <!-- 分期付款 -->
              <div class="px-6 py-3">
                <div class="bg-[#1A1A1A] rounded-xl px-3 py-2">
                  <p class="text-[#888] text-[11px] leading-relaxed">
                    首付 <span class="text-white font-medium">¥{{ monthlyPayment }}</span>/月 起
                    或 0% 费率分期 | <span class="text-primary-500 cursor-pointer hover:underline">了解更多</span>
                  </p>
                </div>
              </div>

              <!-- 直购说明 -->
              <div class="px-6 pb-4">
                <p class="text-[#666] text-[10px] italic text-center">
                  胖虫直购价 · 仅限官网
                </p>
              </div>
            </div>

            <!-- 查看配送选项 / 查看门店 -->
            <div class="mt-3 flex gap-4 px-1">
              <button class="flex items-center gap-1.5 text-primary-500 text-xs hover:underline">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                <span>查看配送选项</span>
              </button>
              <button class="flex items-center gap-1.5 text-primary-500 text-xs hover:underline">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>查看门店位置</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDeleteModal" class="fixed inset-0 z-[9999] flex items-center justify-center">
          <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="showDeleteModal = false"></div>
          <div class="relative bg-[#111] rounded-2xl border border-[#2A2A2A] p-6 w-[90vw] max-w-sm shadow-2xl">
            <h3 class="text-lg font-bold text-white mb-2">确认删除</h3>
            <p class="text-[#888] text-sm mb-6">{{ deleteMsg }}</p>
            <div class="flex gap-3 justify-end">
              <button @click="showDeleteModal = false"
                class="px-5 py-2.5 rounded-full text-sm bg-[#1A1A1A] text-[#AAA] border border-[#2A2A2A] hover:border-[#444] transition-colors">
                取消
              </button>
              <button @click="executeDelete"
                class="px-5 py-2.5 rounded-full text-sm bg-red-500 text-white hover:bg-red-600 transition-colors font-medium">
                删除
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Toast -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toastMsg"
          class="fixed top-20 right-6 z-[9999] bg-[#111] border border-[#2A2A2A] rounded-xl px-5 py-3 shadow-2xl flex items-center gap-3 max-w-xs">
          <svg v-if="toastType === 'success'" class="w-5 h-5 text-primary-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-5 h-5 text-blue-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm text-dark-200">{{ toastMsg }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'

const router = useRouter()
const cart = useCartStore()

const shippingRegion = ref(cart.shippingRegion)
const shippingRates = cart.getShippingRates()

const couponInput = ref('')
const couponMsg = ref('')
const couponSuccess = ref(false)

const showDeleteModal = ref(false)
const deleteMsg = ref('')
const deleteTarget = ref(null)
const deleteItemId = ref(null)

const toastMsg = ref('')
const toastType = ref('success')

function showToast(msg, type = 'success') {
  toastMsg.value = msg
  toastType.value = type
  setTimeout(() => { toastMsg.value = '' }, 2500)
}

function firstSpecs(specs) {
  if (!specs || typeof specs !== 'object') return {}
  const keys = Object.keys(specs).slice(0, 3)
  const r = {}; keys.forEach(k => { r[k] = specs[k] }); return r
}

const hasSelected = computed(() => cart.items.some(i => i.selected))

const pointsEarned = computed(() => Math.floor(cart.totalAmount * 10).toLocaleString())

const deliveryRange = computed(() => {
  const now = new Date()
  const min = new Date(now.getTime() + 5 * 86400000)
  const max = new Date(now.getTime() + 7 * 86400000)
  const fmt = d => `${d.getMonth() + 1}月${d.getDate()}日`
  return `${fmt(min)} ~ ${fmt(max)}`
})

const monthlyPayment = computed(() => Math.ceil(cart.totalAmount / 12).toLocaleString())

function applyCoupon() {
  const result = cart.applyCoupon(couponInput.value)
  couponMsg.value = result.message
  couponSuccess.value = result.success
  if (result.success) couponInput.value = ''
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

function executeDelete() {
  if (deleteTarget.value === 'single') {
    cart.removeItem(deleteItemId.value)
    showToast('已删除商品')
  } else if (deleteTarget.value === 'selected') {
    cart.removeSelected()
    showToast('已删除所选商品')
  }
  showDeleteModal.value = false
  deleteTarget.value = null
  deleteItemId.value = null
}

function goCheckout() {
  if (cart.selectedCount === 0) return
  if (cart.selectedItems.some(i => i.stock <= 0)) {
    showToast('请移除缺货商品后再结算', 'info')
    return
  }
  router.push('/checkout')
}
</script>

<style scoped>
.modal-enter-active { transition: all 0.25s ease; }
.modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from { opacity: 0; }
.modal-leave-to { opacity: 0; }
.modal-enter-from .relative { transform: scale(0.95); }
.modal-leave-to .relative { transform: scale(0.95); }

.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
