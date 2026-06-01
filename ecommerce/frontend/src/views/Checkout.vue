<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-5xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">结算</h1>

      <!-- 空购物车 -->
      <div v-if="cart.isEmpty" class="text-center py-20">
        <div class="text-7xl mb-6 opacity-30">🛒</div>
        <p class="text-dark-400 text-xl mb-2">购物车是空的</p>
        <p class="text-dark-600 text-sm mb-8">请先添加商品</p>
        <router-link to="/products" class="inline-block px-8 py-3 bg-primary-500 text-dark-950 font-semibold rounded-xl hover:bg-primary-400 transition-colors">去购物</router-link>
      </div>

      <div v-else>
        <!-- 步骤导航 -->
        <div class="flex items-center justify-center gap-3 sm:gap-6 mb-10">
          <div v-for="(step, i) in stepLabels" :key="i"
            class="flex items-center gap-2 cursor-pointer"
            :class="currentStep >= i ? 'text-primary-500' : 'text-dark-500'"
            @click="goToStep(i)">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors"
              :class="currentStep > i ? 'bg-primary-500 text-dark-950' : currentStep === i ? 'bg-primary-500 text-dark-950' : 'bg-dark-800'">
              <i v-if="currentStep > i" class="fas fa-check text-xs"></i>
              <span v-else>{{ i + 1 }}</span>
            </div>
            <span class="hidden sm:inline text-sm">{{ step }}</span>
            <div v-if="i < stepLabels.length - 1" class="w-8 sm:w-14 h-0.5" :class="currentStep > i ? 'bg-primary-500' : 'bg-dark-800'"></div>
          </div>
        </div>

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

              <!-- 已有地址列表 -->
              <div v-if="addresses.length > 0 && !showNewAddress" class="space-y-3 mb-4">
                <label v-for="addr in addresses" :key="addr.id"
                  class="flex items-start gap-3 p-4 rounded-xl cursor-pointer transition-all border"
                  :class="selectedAddressId === addr.id ? 'border-primary-500 bg-primary-500/5' : 'border-dark-800 hover:border-dark-600'">
                  <input type="radio" v-model="selectedAddressId" :value="addr.id" class="accent-primary-500 mt-1" />
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-sm">{{ addr.recipient_name }}</span>
                      <span class="text-dark-500 text-xs">{{ addr.phone }}</span>
                      <span v-if="addr.is_default" class="text-[10px] bg-primary-500/20 text-primary-500 px-1.5 py-0.5 rounded">默认</span>
                    </div>
                    <p class="text-dark-400 text-xs mt-1">{{ addr.province }} {{ addr.city }} {{ addr.district }} {{ addr.address }}</p>
                  </div>
                </label>
                <p v-if="errors.province" class="text-red-400 text-xs mt-1">{{ errors.province }}</p>
              </div>

              <!-- 新增地址表单（使用 AddressForm 组件） -->
              <div v-if="showNewAddress || addresses.length === 0">
                <AddressForm v-model="newAddr" :errors="errors" ref="addressFormRef" />

                <div v-if="addresses.length > 0" class="flex gap-2 mt-2">
                  <button @click="showNewAddress = false; errors = {}"
                    class="px-4 py-2 rounded-lg text-sm bg-dark-800 text-dark-300 hover:bg-dark-700">取消</button>
                  <button @click="saveNewAddress" :disabled="savingAddress"
                    class="px-4 py-2 rounded-lg text-sm bg-primary-500 text-dark-950 font-semibold hover:bg-primary-400 disabled:opacity-50">
                    {{ savingAddress ? '保存中...' : '保存地址' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 第二步：配送方式 -->
            <div v-show="currentStep === 1" class="bg-dark-900 rounded-2xl border border-dark-800 p-6">
              <h2 class="text-xl font-bold mb-6">配送方式</h2>
              <div class="space-y-3">
                <label v-for="method in deliveryMethods" :key="method.id"
                  class="flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all border"
                  :class="deliveryMethod === method.id ? 'border-primary-500 bg-primary-500/5' : 'border-dark-800 hover:border-dark-600'">
                  <input type="radio" v-model="deliveryMethod" :value="method.id" class="accent-primary-500" />
                  <div class="flex-1">
                    <p class="font-medium text-sm">{{ method.name }}</p>
                    <p class="text-dark-500 text-xs mt-0.5">{{ method.desc }}</p>
                  </div>
                </label>
              </div>
            </div>

            <!-- 第三步：支付方式 -->
            <div v-show="currentStep === 2" class="bg-dark-900 rounded-2xl border border-dark-800 p-6">
              <h2 class="text-xl font-bold mb-6">支付方式</h2>
              <div class="space-y-3">
                <label v-for="method in paymentMethods" :key="method.id"
                  class="flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all border"
                  :class="paymentMethod === method.id ? 'border-primary-500 bg-primary-500/5' : 'border-dark-800 hover:border-dark-600'">
                  <input type="radio" v-model="paymentMethod" :value="method.id" class="accent-primary-500" />
                  <span class="text-xl">{{ method.icon }}</span>
                  <div class="flex-1">
                    <p class="font-medium text-sm">{{ method.name }}</p>
                    <p class="text-dark-500 text-xs mt-0.5">{{ method.desc }}</p>
                  </div>
                </label>
              </div>

              <div class="mt-4 flex items-center gap-4 text-dark-600 text-xs">
                <span><i class="fas fa-lock mr-1"></i>SSL安全加密</span>
                <span><i class="fas fa-undo mr-1"></i>7天无理由退换</span>
                <span><i class="fas fa-shield-alt mr-1"></i>正品保障</span>
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

              <!-- 商品列表 -->
              <div class="space-y-3 mb-4">
                <div v-for="item in cart.selectedItems" :key="item.id"
                  class="flex items-center gap-3 py-3 border-b border-dark-800 last:border-0">
                  <div class="w-12 h-12 bg-dark-800 rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden">
                    <img v-if="item.image_url" :src="item.image_url" :alt="item.name" class="w-full h-full object-cover" />
                    <span v-else class="text-xl opacity-40">📦</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium truncate">{{ item.name }}</p>
                    <p class="text-dark-500 text-xs">x{{ item.quantity }}</p>
                  </div>
                  <span class="text-sm font-bold">¥{{ (Number(item.price) * item.quantity).toLocaleString() }}</span>
                </div>
              </div>

              <!-- 备注 -->
              <div class="mt-4">
                <label class="text-sm text-dark-400 block mb-1.5">订单备注（可选）</label>
                <textarea v-model="remark" placeholder="如有特殊要求请在此备注" rows="2"
                  class="w-full bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-4 py-2.5 text-sm focus:border-primary-500 outline-none resize-none"></textarea>
              </div>
            </div>

            <!-- 步骤导航按钮 -->
            <div class="flex justify-between mt-6">
              <button v-if="currentStep > 0" @click="currentStep--"
                class="px-6 py-2.5 rounded-lg text-sm bg-dark-800 text-dark-300 hover:bg-dark-700 transition-colors">
                <i class="fas fa-arrow-left mr-2"></i>上一步
              </button>
              <div v-else></div>

              <button v-if="currentStep < 3" @click="nextStep"
                class="px-8 py-2.5 rounded-lg text-sm bg-primary-500 text-dark-950 font-semibold hover:bg-primary-400 transition-colors">
                下一步<i class="fas fa-arrow-right ml-2"></i>
              </button>
              <button v-else @click="submitOrder" :disabled="submitting"
                class="px-10 py-3 rounded-xl text-sm font-bold transition-all"
                :class="submitting ? 'bg-dark-700 text-dark-400 cursor-wait' : 'bg-primary-500 text-dark-950 hover:bg-primary-400'">
                <span v-if="submitting"><i class="fas fa-spinner fa-spin mr-2"></i>提交中...</span>
                <span v-else><i class="fas fa-check-circle mr-2"></i>提交订单</span>
              </button>
            </div>
          </div>

          <!-- 右侧：订单摘要 -->
          <div class="lg:col-span-1">
            <div class="bg-dark-900 rounded-2xl border border-dark-800 p-6 sticky top-24">
              <h2 class="text-xl font-bold mb-4">订单摘要</h2>

              <div class="space-y-2.5 text-sm max-h-60 overflow-y-auto mb-4">
                <div v-for="item in cart.selectedItems" :key="item.id" class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-dark-800 rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden">
                    <img v-if="item.image_url" :src="item.image_url" :alt="item.name" class="w-full h-full object-cover" />
                    <span v-else class="text-lg opacity-40">📦</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs truncate">{{ item.name }}</p>
                    <p class="text-dark-500 text-[10px]">x{{ item.quantity }}</p>
                  </div>
                  <span class="text-xs font-medium">¥{{ (Number(item.price) * item.quantity).toLocaleString() }}</span>
                </div>
              </div>

              <hr class="border-dark-700 my-4">

              <div class="space-y-2 text-sm">
                <div class="flex justify-between text-dark-300">
                  <span>商品金额</span>
                  <span>¥{{ cart.subtotal.toLocaleString() }}</span>
                </div>
                <div class="flex justify-between text-dark-300">
                  <span>运费</span>
                  <span>{{ deliveryCost === 0 ? '包邮' : '¥' + deliveryCost }}</span>
                </div>
                <div v-if="cart.discountAmount > 0" class="flex justify-between text-primary-500">
                  <span>优惠减免</span>
                  <span>-¥{{ cart.discountAmount.toLocaleString() }}</span>
                </div>
              </div>

              <hr class="border-dark-700 my-4">

              <div class="flex justify-between text-xl font-bold">
                <span>应付金额</span>
                <span class="text-primary-500">¥{{ finalAmount.toLocaleString() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 订单成功弹窗 -->
    <Teleport to="body">
      <div v-if="showSuccess" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="bg-dark-900 rounded-2xl border border-dark-700 p-8 w-[90vw] max-w-md shadow-2xl text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-primary-500/20 rounded-full flex items-center justify-center">
            <i class="fas fa-check text-3xl text-primary-500"></i>
          </div>
          <h3 class="text-xl font-bold mb-2">订单提交成功！</h3>
          <p class="text-dark-400 text-sm mb-1">订单号：{{ orderNo }}</p>
          <p class="text-dark-500 text-xs mb-6">请在30分钟内完成支付</p>
          <div class="flex gap-3 justify-center">
            <button @click="startPayment" :disabled="paying"
              class="px-6 py-2.5 rounded-lg text-sm bg-primary-500 text-dark-950 font-semibold hover:bg-primary-400 disabled:opacity-50">
              {{ paying ? '支付创建中...' : '去支付' }}
            </button>
            <router-link to="/orders" @click="showSuccess = false"
              class="px-6 py-2.5 rounded-lg text-sm bg-dark-800 text-dark-300 hover:bg-dark-700">查看订单</router-link>
            <router-link to="/" @click="showSuccess = false"
              class="px-6 py-2.5 rounded-lg text-sm bg-dark-800 text-dark-300 hover:bg-dark-700">继续购物</router-link>
          </div>
        </div>
      </div>
    </Teleport>
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

const router = useRouter()
const cart = useCartStore()
const userStore = useUserStore()

// 未登录跳转登录
onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push({ name: 'Login', query: { redirect: '/checkout' } })
    return
  }
  try {
    await userStore.fetchAddresses()
    if (userStore.addresses.length > 0) {
      const defaultAddr = userStore.addresses.find(a => a.is_default) || userStore.addresses[0]
      selectedAddressId.value = defaultAddr.id
    }
  } catch (e) {
    console.warn('加载地址失败:', e)
  }
})

const currentStep = ref(0)
const stepLabels = ['配送信息', '配送方式', '支付方式', '订单确认']

// 地址相关
const addresses = computed(() => userStore.addresses)
const selectedAddressId = ref(null)
const selectedAddress = computed(() => addresses.value.find(a => a.id === selectedAddressId.value))
const showNewAddress = ref(false)
const savingAddress = ref(false)
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

const deliveryMethods = [
  { id: 'standard', name: '标准配送', desc: '3-5个工作日送达', cost: 20 },
  { id: 'express', name: '快递配送', desc: '1-3个工作日送达', cost: 40 },
  { id: 'nextday', name: '次日达', desc: '仅限部分城市', cost: 80 },
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
const showSuccess = ref(false)
const orderNo = ref('')
const createdOrderId = ref(null)

const selectedDelivery = computed(() => deliveryMethods.find(m => m.id === deliveryMethod.value))
const selectedPayment = computed(() => paymentMethods.find(m => m.id === paymentMethod.value))
const deliveryCost = computed(() => cart.shippingCost)
const finalAmount = computed(() => cart.totalAmount)

// 根据选中地址自动设置运费地区
watch(() => selectedAddress.value?.province, (p) => {
  if (['西藏', '新疆'].some(x => p?.includes(x))) {
    cart.setShippingRegion('西藏新疆')
  } else if (['浙江省', '江苏省', '上海市'].some(x => p?.includes(x))) {
    cart.setShippingRegion('江浙沪')
  } else {
    cart.setShippingRegion('其他地区')
  }
})

function goToStep(step) {
  if (step < currentStep.value) currentStep.value = step
}

function validateStep(step) {
  errors.value = {}
  if (step === 0) {
    if (showNewAddress.value || addresses.value.length === 0) {
      // 使用 AddressForm 组件的验证
      if (addressFormRef.value) {
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
  if (!validateStep(0)) return
  savingAddress.value = true
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
  } catch (e) {
    const detail = e.response?.data?.detail
    if (typeof detail === 'string') {
      alert(detail)
    } else if (Array.isArray(detail)) {
      const fieldErrors = {}
      detail.forEach(err => {
        const field = err.loc?.[err.loc.length - 1]
        if (field) fieldErrors[field] = err.msg
      })
      errors.value = fieldErrors
    } else {
      alert('保存地址失败，请重试')
    }
  } finally {
    savingAddress.value = false
  }
}

function nextStep() {
  if (!validateStep(currentStep.value)) return
  currentStep.value++
}

async function submitOrder() {
  if (!validateStep(0)) {
    currentStep.value = 0
    return
  }

  // 如果正在新增地址但还没保存，先保存
  if (showNewAddress.value || addresses.value.length === 0) {
    await saveNewAddress()
    if (!selectedAddressId.value) return
  }

  submitting.value = true
  try {
    const backendItems = cart.items.filter(i => !i.id.startsWith('local_'))
    const selectedBackendItems = cart.selectedItems.filter(i => !i.id.startsWith('local_'))
    const selectedLocalItems = cart.selectedItems.filter(i => i.id.startsWith('local_'))
    const cartItemIds = backendItems.length > 0 && selectedBackendItems.length === backendItems.length
      ? null
      : selectedBackendItems.map(i => i.id)
    const customItems = selectedLocalItems.map(i => ({
      product_name: i.name,
      product_image: i.image_url || null,
      product_specs: i.specs || {},
      price: Number(i.price),
      quantity: i.quantity,
    }))

    const data = await orderApi.createOrder({
      address_id: selectedAddressId.value,
      remark: remark.value || null,
      cart_item_ids: cartItemIds,
      custom_items: customItems,
    })

    orderNo.value = data.order_no
    createdOrderId.value = data.id

    cart.removeLocalItems(selectedLocalItems.map(i => i.id))
    await cart.fetchCart()
    cart.removeCoupon()

    showSuccess.value = true
  } catch (e) {
    alert('提交失败：' + (e.message || '请重试'))
  } finally {
    submitting.value = false
  }
}

async function startPayment() {
  if (!createdOrderId.value) return
  paying.value = true
  try {
    const payment = await paymentApi.createPayment(createdOrderId.value, {
      payment_method: paymentMethod.value,
    })
    showSuccess.value = false
    redirectToPayment(payment)
  } catch (e) {
    alert('创建支付失败：' + (e.displayMessage || e.message || '请重试'))
  } finally {
    paying.value = false
  }
}
</script>
