<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-5xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">结算</h1>

      <DsAsyncState v-if="cart.loading && cart.isEmpty" state="loading" loading-label="正在加载结算商品" />
      <DsAsyncState v-else-if="cart.loadError" state="error" error-title="购物车暂时无法加载" :error-description="cart.loadError" @retry="cart.fetchCart" />

      <!-- 空购物车 -->
      <div v-else-if="cart.selectedCount === 0" class="text-center py-20">
        <div class="text-7xl mb-6 opacity-30">🛒</div>
        <p class="text-dark-400 text-xl mb-2">{{ cart.isEmpty ? '购物车是空的' : '还没有选择结算商品' }}</p>
        <p class="text-dark-400 text-sm mb-8">{{ cart.isEmpty ? '发现适合你的硬件，开始下一次升级。' : '返回购物车，勾选有库存的商品后继续。' }}</p>
        <router-link :to="cart.isEmpty ? '/products' : '/cart'" class="inline-block px-8 py-3 bg-primary-500 text-dark-950 font-semibold rounded-xl hover:bg-primary-400 transition-colors">{{ cart.isEmpty ? '去购物' : '返回购物车' }}</router-link>
      </div>

      <div v-else>
        <DsAlert
          v-if="checkoutError"
          class="mb-5"
          title="结算暂未完成"
          :description="checkoutError"
          tone="danger"
          role="alert"
          dismissible
          @dismiss="checkoutError = ''"
        />

        <!-- 步骤导航：已完成步骤可回看，未完成步骤不可跳过 -->
        <DsStepIndicator v-model="currentStep" :steps="stepLabels" :allow-navigation="!submitting && !savingAddress" />

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- 左侧：步骤内容 -->
          <div class="lg:col-span-2">

            <!-- 第一步：配送信息 -->
            <div v-show="currentStep === 0" class="bg-dark-900 rounded-2xl border border-dark-800 p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-bold">配送信息</h2>
                <button v-if="!showNewAddress && addresses.length > 0" @click="showNewAddress = true"
                  class="text-xs text-primary-500 hover:underline">
                  <i class="fas fa-plus mr-1"></i>新增地址
                </button>
              </div>

              <DsAsyncState v-if="loadingAddresses" state="loading" loading-label="正在加载收货地址" />
              <DsAsyncState v-else-if="addressLoadError" state="error" error-title="收货地址加载失败" :error-description="addressLoadError" @retry="loadAddresses" />

              <!-- 已有地址列表 -->
              <fieldset v-else-if="addresses.length > 0 && !showNewAddress" class="mb-4 space-y-3 border-0 p-0">
                <legend class="sr-only">收货地址</legend>
                <DsChoiceCard
                  v-for="addr in addresses"
                  :key="addr.id"
                  v-model="selectedAddressId"
                  :value="addr.id"
                  :title="addr.recipient_name + ' ' + addr.phone"
                  :description="addr.province + ' ' + addr.city + ' ' + addr.district + ' ' + addr.address"
                  name="checkout-address"
                >
                  <template v-if="addr.is_default" #meta>
                    <span class="rounded bg-primary-500/20 px-1.5 py-0.5 text-[10px] text-primary-500">默认</span>
                  </template>
                </DsChoiceCard>
                <p v-if="errors.province" class="mt-1 text-xs text-red-400" role="alert">{{ errors.province }}</p>
              </fieldset>

              <!-- 新增地址表单（使用 AddressForm 组件） -->
              <div v-else-if="showNewAddress || addresses.length === 0">
                <AddressForm v-model="newAddr" :errors="errors" ref="addressFormRef" />

                <div v-if="addresses.length > 0" class="flex gap-2 mt-2">
                  <DsButton variant="ghost" type="button" :disabled="savingAddress" @click="showNewAddress = false; errors = {}">取消</DsButton>
                  <DsButton type="button" :loading="savingAddress" @click="saveNewAddress">保存地址</DsButton>
                </div>
              </div>
            </div>

            <!-- 第二步：配送方式 -->
            <div v-show="currentStep === 1" class="bg-dark-900 rounded-2xl border border-dark-800 p-6">
              <h2 class="text-xl font-bold mb-6">配送方式</h2>
              <fieldset class="space-y-3 border-0 p-0">
                <legend class="sr-only">配送方式</legend>
                <DsChoiceCard
                  v-for="method in deliveryMethods"
                  :key="method.id"
                  v-model="deliveryMethod"
                  :value="method.id"
                  :title="method.name"
                  :description="method.desc"
                  name="delivery-method"
                />
              </fieldset>
            </div>

            <!-- 第三步：支付方式 -->
            <div v-show="currentStep === 2" class="bg-dark-900 rounded-2xl border border-dark-800 p-6">
              <h2 class="text-xl font-bold mb-6">支付方式</h2>
              <fieldset class="space-y-3 border-0 p-0">
                <legend class="sr-only">支付方式</legend>
                <DsChoiceCard
                  v-for="method in paymentMethods"
                  :key="method.id"
                  v-model="paymentMethod"
                  :value="method.id"
                  :title="method.icon + ' ' + method.name"
                  :description="method.desc"
                  name="payment-method"
                />
              </fieldset>

              <div class="mt-4 flex flex-wrap items-center gap-4 text-dark-400 text-xs">
                <span><i class="fas fa-lock mr-1"></i>SSL安全加密</span>
                <router-link to="/services#returns" class="hover:text-primary-500">查看退换货说明</router-link>
              </div>
            </div>

            <!-- 第四步：订单确认 -->
            <div v-show="currentStep === 3" class="bg-dark-900 rounded-2xl border border-dark-800 p-6">
              <h2 class="text-xl font-bold mb-6">订单确认</h2>

              <!-- 收货信息 -->
              <div class="mb-6 p-4 bg-dark-950 rounded-xl border border-dark-800">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs text-dark-500 uppercase tracking-wider">收货信息</span>
                  <button @click="currentStep = 0" class="text-xs text-primary-500 hover:underline">修改</button>
                </div>
                <p class="text-sm font-medium">{{ selectedAddress?.recipient_name }} {{ selectedAddress?.phone }}</p>
                <p class="text-dark-400 text-xs mt-1">{{ selectedAddress?.province }} {{ selectedAddress?.city }} {{ selectedAddress?.district }} {{ selectedAddress?.address }}</p>
              </div>

              <!-- 配送与支付 -->
              <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="p-4 bg-dark-950 rounded-xl border border-dark-800">
                  <span class="text-xs text-dark-500 block mb-1">配送方式</span>
                  <p class="text-sm">{{ selectedDelivery?.name }}</p>
                </div>
                <div class="p-4 bg-dark-950 rounded-xl border border-dark-800">
                  <span class="text-xs text-dark-500 block mb-1">支付方式</span>
                  <p class="text-sm">{{ selectedPayment?.icon }} {{ selectedPayment?.name }}</p>
                </div>
              </div>

              <!-- 商品列表：复用购物车行项目的价格、规格、库存和 DIY 快照语义 -->
              <div class="space-y-3 mb-4">
                <DsCartLineItem
                  v-for="item in cart.selectedItems"
                  :key="item.id"
                  :item="item"
                  :selected="true"
                  :interactive="false"
                  compact
                  :fallback-image="fallbackImage"
                >
                  <template #details>
                    <OrderDiySnapshot v-if="hasCustomSnapshotDisplay(item)" :item="item" />
                  </template>
                </DsCartLineItem>
              </div>

              <!-- 备注 -->
              <div class="mt-4">
                <DsField
                  v-model="remark"
                  as="textarea"
                  label="订单备注（可选）"
                  placeholder="如有特殊要求请在此备注"
                  rows="2"
                  maxlength="200"
                />
              </div>
            </div>

            <!-- 步骤导航按钮 -->
            <div class="flex justify-between mt-6">
              <DsButton v-if="currentStep > 0" variant="ghost" type="button" :disabled="submitting || savingAddress" @click="currentStep--">上一步</DsButton>
              <div v-else></div>

              <DsButton v-if="currentStep < 3" size="lg" type="button" :loading="savingAddress" :disabled="loadingAddresses || Boolean(addressLoadError)" @click="nextStep">下一步</DsButton>
              <DsButton v-else size="lg" :loading="submitting" type="button" @click="submitOrder">提交订单</DsButton>
            </div>
          </div>

          <!-- 右侧：订单摘要 -->
          <div class="lg:col-span-1">
            <DsOrderSummary
              :items="cart.selectedItems"
              :subtotal="cart.subtotal"
              :shipping="deliveryCost"
              :discount="cart.discountAmount"
              :total="finalAmount"
              :fallback-image="fallbackImage"
            >
              <template #item-details="{ item }">
                <OrderDiySnapshot v-if="hasCustomSnapshotDisplay(item)" :item="item" />
              </template>
            </DsOrderSummary>
          </div>
        </div>
      </div>
    </div>

    <DsOrderSuccess
      :open="showSuccess"
      :order-no="orderNo"
      :paying="paying"
      :payment-error="paymentError"
      @update:open="showSuccess = $event"
      @pay="startPayment"
      @view-orders="goToOrders"
      @continue-shopping="continueShopping"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import { useUserStore } from '@/store/user'
import { orderApi, paymentApi } from '@/api'
import { redirectToPayment } from '@/utils/payment'
import AddressForm from '@/components/AddressForm.vue'
import OrderDiySnapshot from '@/components/OrderDiySnapshot.vue'
import { DsAlert, DsAsyncState, DsButton, DsCartLineItem, DsChoiceCard, DsField, DsOrderSuccess, DsOrderSummary, DsStepIndicator } from '@/design-system'
import { hasCustomSnapshotDisplay } from '@/utils/orderSpecs'

const router = useRouter()
const cart = useCartStore()
const userStore = useUserStore()
const fallbackImage = '/assets/pangchong-product-fallback.png'

// 未登录跳转登录
onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push({ name: 'Login', query: { redirect: '/checkout' } })
    return
  }
  await loadAddresses()
})

async function loadAddresses() {
  loadingAddresses.value = true
  addressLoadError.value = ''
  try {
    await userStore.fetchAddresses()
    if (userStore.addresses.length > 0) {
      const defaultAddr = userStore.addresses.find(a => a.is_default) || userStore.addresses[0]
      selectedAddressId.value = defaultAddr.id
    }
  } catch (e) {
    addressLoadError.value = e.displayMessage || '请检查网络后重试，以免重复添加地址。'
  } finally {
    loadingAddresses.value = false
  }
}

const currentStep = ref(0)
const stepLabels = ['配送信息', '配送方式', '支付方式', '订单确认']

// 地址相关
const addresses = computed(() => userStore.addresses)
const selectedAddressId = ref(null)
const selectedAddress = computed(() => addresses.value.find(a => a.id === selectedAddressId.value))
const showNewAddress = ref(false)
const savingAddress = ref(false)
const loadingAddresses = ref(true)
const addressLoadError = ref('')
const addressFormRef = ref(null)
const newAddr = ref({
  recipient_name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  address: '',
  postal_code: '',
  is_default: false,
})
const errors = ref({})
const checkoutError = ref('')

const deliveryMethods = [
  { id: 'standard', name: '标准配送', desc: '按订单金额计算运费，发货后可在订单中查看物流。' },
]
const deliveryMethod = ref('standard')

const paymentMethods = [
  { id: 'alipay', name: '支付宝', desc: '推荐使用支付宝扫码支付', icon: '💳' },
  { id: 'wechat', name: '微信支付', desc: '使用微信扫码支付', icon: '💬' },
]
const paymentMethod = ref('alipay')

const remark = ref('')
const submitting = ref(false)
const paying = ref(false)
const paymentError = ref('')
const showSuccess = ref(false)
const orderNo = ref('')
const createdOrderId = ref(null)
const orderIdempotencyKey = ref(createIdempotencyKey())

const selectedDelivery = computed(() => deliveryMethods.find(m => m.id === deliveryMethod.value))
const selectedPayment = computed(() => paymentMethods.find(m => m.id === paymentMethod.value))
const deliveryCost = computed(() => cart.shippingCost)
const finalAmount = computed(() => cart.totalAmount)

function isCustomCartItem(item) {
  return cart.isCustomItem(item)
}

function createIdempotencyKey() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID()
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (char) => {
    const random = Math.floor(Math.random() * 16)
    const value = char === 'x' ? random : ((random & 0x3) | 0x8)
    return value.toString(16)
  })
}

function buildCustomOrderReference(item) {
  const snapshot = item.snapshot || {}
  return {
    configuration: {
      configuration_id: snapshot.configuration_id || 'diy-pc',
      version: Number(snapshot.version || 1),
      variant_id: snapshot.appearance?.variant_id,
      material_id: snapshot.appearance?.material_id,
      parts: (snapshot.parts || []).map(part => ({
        slot_id: part.key,
        product_id: part.product_id,
        quantity: Number(part.quantity || 1),
      })),
    },
    quantity: item.quantity,
  }
}

async function promoteSelectedLocalProducts() {
  const localProducts = cart.selectedItems.filter(item =>
    cart.isLocalItem(item) && !isCustomCartItem(item)
  )

  for (const item of localProducts) {
    await cart.addToCart(item.product_id, item.quantity)
    cart.removeLocalItems([item.id])
  }
}

function validateStep(step) {
  errors.value = {}
  if (step === 0) {
    if (showNewAddress.value || addresses.value.length === 0) {
      // 使用 AddressForm 组件的验证
      if (addressFormRef.value && typeof addressFormRef.value.validate === 'function') {
        const errs = addressFormRef.value.validate()
        if (Object.keys(errs).length > 0) {
          errors.value = errs
          return false
        }
      }
      return true
    } else {
      if (!selectedAddressId.value) {
        errors.value.province = '请选择收货地址'
        return false
      }
    }
  }
  return true
}

async function saveNewAddress() {
  if (savingAddress.value || !validateStep(0)) return false
  savingAddress.value = true
  checkoutError.value = ''
  errors.value = {}
  try {
    const addr = await userStore.createAddress(newAddr.value)
    selectedAddressId.value = addr.id
    showNewAddress.value = false
    newAddr.value = {
      recipient_name: '',
      phone: '',
      province: '',
      city: '',
      district: '',
      address: '',
      postal_code: '',
      is_default: false,
    }
    return true
  } catch (e) {
    checkoutError.value = e.displayMessage || e.response?.data?.detail || '保存地址失败，请重试'
    const detail = e.response?.data?.detail
    if (Array.isArray(detail)) {
      const fieldErrors = {}
      detail.forEach(err => {
        const field = err.loc?.[err.loc.length - 1]
        if (field) fieldErrors[field] = err.msg
      })
      errors.value = fieldErrors
    }
    return false
  } finally {
    savingAddress.value = false
  }
}

async function nextStep() {
  if (savingAddress.value || submitting.value || loadingAddresses.value || addressLoadError.value) return
  if (!validateStep(currentStep.value)) return
  if (currentStep.value === 0 && (showNewAddress.value || addresses.value.length === 0)) {
    if (!await saveNewAddress()) return
  }
  currentStep.value = Math.min(3, currentStep.value + 1)
}

async function submitOrder() {
  if (submitting.value || savingAddress.value || createdOrderId.value) return
  if (cart.selectedCount === 0 || cart.loadError) {
    checkoutError.value = '请返回购物车确认商品和库存后重试。'
    return
  }
  checkoutError.value = ''
  if (!validateStep(0)) {
    currentStep.value = 0
    return
  }

  // 如果正在新增地址但还没保存，先保存
  if (showNewAddress.value || addresses.value.length === 0) {
    if (!await saveNewAddress()) {
      currentStep.value = 0
      return
    }
  }

  submitting.value = true
  paymentError.value = ''
  try {
    await promoteSelectedLocalProducts()

    const backendItems = cart.items.filter(i => !cart.isLocalItem(i) && !isCustomCartItem(i))
    const selectedBackendItems = cart.selectedItems.filter(i => !cart.isLocalItem(i) && !isCustomCartItem(i))
    const selectedCustomItems = cart.selectedItems.filter(isCustomCartItem)
    const cartItemIds = backendItems.length > 0 && selectedBackendItems.length === backendItems.length
      ? null
      : selectedBackendItems.map(i => i.id)
    const customItems = selectedCustomItems.map(buildCustomOrderReference)

    const data = await orderApi.createOrder({
      address_id: selectedAddressId.value,
      remark: remark.value || null,
      cart_item_ids: cartItemIds,
      custom_items: customItems,
      idempotency_key: orderIdempotencyKey.value,
    })

    orderNo.value = data.order_no
    createdOrderId.value = data.id

    cart.removeLocalItems(selectedCustomItems.filter(i => cart.isLocalItem(i)).map(i => i.id))
    await cart.fetchCart()
    cart.removeCoupon()

    showSuccess.value = true
  } catch (e) {
    checkoutError.value = '提交失败：' + (e.displayMessage || e.message || '请重试')
  } finally {
    submitting.value = false
  }
}

async function startPayment() {
  if (!createdOrderId.value || paying.value) return
  paying.value = true
  paymentError.value = ''
  try {
    const payment = await paymentApi.createPayment(createdOrderId.value, {
      payment_method: paymentMethod.value,
    })
    redirectToPayment(payment)
    showSuccess.value = false
  } catch (e) {
    paymentError.value = '创建支付失败：' + (e.displayMessage || e.message || '请重试')
  } finally {
    paying.value = false
  }
}

function goToOrders() {
  showSuccess.value = false
  router.push('/orders')
}

function continueShopping() {
  showSuccess.value = false
  router.push('/')
}
</script>
