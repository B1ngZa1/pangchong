<template>
  <div class="min-h-screen bg-black text-white">
    <div class="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 面包屑 -->
      <div class="flex items-center gap-2 text-xs text-[#888] mb-6">
        <router-link to="/" class="hover:text-primary-500 transition-colors">首页</router-link>
        <span>/</span>
        <router-link to="/products" class="hover:text-primary-500 transition-colors">全部商品</router-link>
        <span>/</span>
        <span class="text-[#ccc]">{{ product.name }}</span>
      </div>

      <div class="flex flex-col lg:flex-row gap-8">
        <!-- ==================== 左侧区域 ==================== -->
        <div class="flex-1 min-w-0 lg:max-w-[760px]">
          <!-- 产品标题 -->
          <div class="mb-6">
            <h1 class="text-2xl sm:text-3xl font-bold text-white leading-tight">
              Customize your {{ product.name }}
            </h1>
            <p class="text-[#888] text-sm mt-2">
              {{ product.tagline }}
              <a href="#" class="text-primary-500 hover:underline ml-1">Learn More <i class="fas fa-chevron-right text-[10px]"></i></a>
            </p>
          </div>

          <!-- 3D 产品配置区 -->
          <div class="mb-8 grid gap-4 xl:grid-cols-[minmax(0,1fr)_260px]">
            <Suspense>
              <Product3DViewer
                model-url="/models/pangchong.glb"
                :selected-variant="activeVariant"
                :selected-material="activeMaterial"
                :auto-rotate="autoRotate"
                :camera-preset="cameraPreset"
                :reset-key="viewerResetKey"
                :parts="configuratorParts"
              />
              <template #fallback>
                <div class="flex min-h-[360px] items-center justify-center rounded-lg border border-[#2A2A2A] bg-[#111] sm:min-h-[430px] lg:min-h-[520px]">
                  <div class="text-center">
                    <div class="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-[#2A2A2A] border-t-primary-500"></div>
                    <p class="text-sm text-[#CCCCCC]">正在准备 3D 视图</p>
                  </div>
                </div>
              </template>
            </Suspense>
            <ProductConfiguratorPanel
              v-model:selected-variant="selectedVariant"
              v-model:selected-material="selectedMaterial"
              v-model:auto-rotate="autoRotate"
              v-model:camera-preset="cameraPreset"
              :variants="colorOptions"
              :materials="materialOptions"
              :camera-presets="cameraPresets"
              @reset-camera="resetViewerCamera"
            />
          </div>

          <!-- ONLY AT PANGCHONG 徽章 -->
          <div class="inline-flex items-center gap-2 border border-primary-500/40 rounded-full px-4 py-1.5 mb-8">
            <span class="w-2 h-2 rounded-full bg-primary-500"></span>
            <span class="text-primary-500 text-xs font-medium tracking-wider uppercase">Only at Pangchong</span>
          </div>

          <!-- 规格列表 -->
          <div class="mb-8">
            <h2 class="text-lg font-bold mb-4">Specifications</h2>
            <div class="bg-[#0A0A0A] rounded-xl border border-[#2A2A2A] overflow-hidden">
              <div v-for="(spec, idx) in product.specs" :key="spec.label"
                class="flex items-start px-5 py-3.5"
                :class="idx < product.specs.length - 1 ? 'border-b border-[#1A1A1A]' : ''">
                <span class="w-40 flex-shrink-0 text-[#888] text-sm">{{ spec.label }}</span>
                <span class="text-white text-sm">{{ spec.value }}</span>
              </div>
            </div>
            <a href="#" class="inline-flex items-center gap-1 text-primary-500 text-xs mt-3 hover:underline">
              View All Specifications <i class="fas fa-chevron-right text-[10px]"></i>
            </a>
          </div>

          <!-- 特性区域 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-8">
            <div v-for="feat in features" :key="feat.title"
              class="bg-[#1A1A1A] rounded-xl p-4 border border-[#2A2A2A]">
              <div class="w-10 h-10 rounded-lg bg-[#222] flex items-center justify-center mb-3">
                <i :class="feat.icon" class="text-primary-500 text-lg"></i>
              </div>
              <h3 class="text-sm font-bold mb-1">{{ feat.title }}</h3>
              <p class="text-[#888] text-xs leading-relaxed">{{ feat.desc }}</p>
            </div>
          </div>

          <!-- 赠品信息 -->
          <div class="bg-[#0A0A0A] rounded-xl border border-[#2A2A2A] p-5 mb-8">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-lg bg-[#1A1A1A] border border-[#2A2A2A] flex items-center justify-center flex-shrink-0">
                <i class="fas fa-gamepad text-primary-500 text-xl"></i>
              </div>
              <div>
                <h3 class="text-sm font-bold mb-1">{{ bonus.title }}</h3>
                <p class="text-primary-500 text-xs font-medium mb-1">价值 {{ bonus.value }}</p>
                <p class="text-[#888] text-xs leading-relaxed">{{ bonus.desc }}</p>
                <p class="text-[#555] text-[10px] mt-2 italic">{{ bonus.footnote }}</p>
              </div>
            </div>
          </div>

          <!-- 搭配购买 -->
          <div class="mb-8">
            <h2 class="text-lg font-bold mb-4">Frequently Bought Together</h2>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div v-for="rec in recommendations" :key="rec.id"
                class="bg-[#0A0A0A] rounded-xl border border-[#2A2A2A] p-3 group hover:border-[#444] transition-colors">
                <div class="w-full aspect-square bg-[#1A1A1A] rounded-lg overflow-hidden mb-3 flex items-center justify-center">
                  <img v-if="rec.image" :src="rec.image" class="w-full h-full object-cover" />
                  <svg v-else class="w-10 h-10 text-[#333]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                      d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
                <h4 class="text-xs font-medium text-white truncate">{{ rec.name }}</h4>
                <p class="text-primary-500 text-xs font-bold mt-1">¥{{ rec.price.toLocaleString() }}</p>
                <a href="#" class="text-primary-500 text-[10px] hover:underline mt-1 inline-block">Learn More</a>
              </div>
            </div>
          </div>
        </div>

        <!-- ==================== 右侧区域 ==================== -->
        <div class="w-full lg:w-[400px] flex-shrink-0">
          <div class="lg:sticky lg:top-[80px]">
            <!-- 配置选项区 -->
            <div class="space-y-8 mb-6">

              <!-- 键盘布局 -->
              <div>
                <h3 class="text-sm font-bold text-white mb-3">Keyboard Layout</h3>
                <div class="flex flex-wrap gap-2">
                  <button v-for="opt in keyboardOptions" :key="opt.id" @click="selectedKeyboard = opt.id"
                    class="px-4 py-2.5 rounded-lg border text-sm transition-all"
                    :class="selectedKeyboard === opt.id
                      ? 'border-primary-500 bg-primary-500/10 text-primary-500 font-medium'
                      : 'border-[#2A2A2A] bg-[#111] text-[#ccc] hover:border-[#444]'">
                    {{ opt.name }}
                  </button>
                </div>
              </div>

              <!-- 延保服务 -->
              <div>
                <div class="flex items-center gap-2 mb-3">
                  <h3 class="text-sm font-bold text-white">Add PangchongCare Protection</h3>
                  <a href="#" class="text-primary-500 text-xs hover:underline">Check out the coverage at a glance</a>
                </div>
                <div class="space-y-2">
                  <label v-for="opt in warrantyOptions" :key="opt.id" @click="selectedWarranty = opt.id"
                    class="flex items-start gap-3 p-3.5 rounded-lg border cursor-pointer transition-all"
                    :class="selectedWarranty === opt.id
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-[#2A2A2A] bg-[#111] hover:border-[#444]'">
                    <div class="relative mt-0.5 flex-shrink-0">
                      <div class="w-5 h-5 rounded-full border-2 transition-colors"
                        :class="selectedWarranty === opt.id ? 'border-primary-500' : 'border-[#555]'">
                        <div v-if="selectedWarranty === opt.id"
                          class="absolute inset-[3px] rounded-full bg-primary-500"></div>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium" :class="selectedWarranty === opt.id ? 'text-primary-500' : 'text-white'">
                        {{ opt.name }}
                      </p>
                      <p class="text-[#888] text-xs mt-0.5">{{ opt.desc }}</p>
                    </div>
                    <span class="text-sm font-bold flex-shrink-0"
                      :class="selectedWarranty === opt.id ? 'text-primary-500' : 'text-white'">
                      {{ opt.price > 0 ? '+¥' + opt.price.toLocaleString() : '免费' }}
                    </span>
                  </label>
                </div>
              </div>

              <!-- 分割线 -->
              <div class="border-t border-[#2A2A2A]"></div>

              <!-- Top Picks 搭配购买 -->
              <div>
                <h3 class="text-sm font-bold text-white mb-3">Top Picks with Your Purchase</h3>
                <div class="space-y-2">
                  <label v-for="pick in topPicks" :key="pick.id"
                    class="flex items-start gap-3 p-3.5 rounded-lg border cursor-pointer transition-all"
                    :class="selectedPicks.includes(pick.id)
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-[#2A2A2A] bg-[#111] hover:border-[#444]'"
                    @click="togglePick(pick.id)">
                    <div class="relative mt-0.5 flex-shrink-0">
                      <div class="w-5 h-5 rounded border-2 transition-colors flex items-center justify-center"
                        :class="selectedPicks.includes(pick.id) ? 'border-primary-500 bg-primary-500' : 'border-[#555]'">
                        <svg v-if="selectedPicks.includes(pick.id)" class="w-3 h-3 text-dark-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    </div>
                    <div class="w-14 h-14 rounded-lg bg-[#1A1A1A] overflow-hidden flex-shrink-0 flex items-center justify-center">
                      <img v-if="pick.image" :src="pick.image" class="w-full h-full object-cover" />
                      <svg v-else class="w-6 h-6 text-[#333]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-white truncate">{{ pick.name }}</p>
                      <a href="#" class="text-primary-500 text-[10px] hover:underline" @click.stop>Learn More</a>
                    </div>
                    <span class="text-sm font-bold text-white flex-shrink-0">¥{{ pick.price.toLocaleString() }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- ==================== 购买面板（粘性） ==================== -->
            <div class="bg-[#111111] rounded-2xl border border-[#2A2A2A] shadow-[0_2px_8px_rgba(0,0,0,0.2)] overflow-hidden">
              <!-- 总价 -->
              <div class="px-5 pt-5 pb-0">
                <p class="text-primary-500 text-[36px] font-bold leading-none">
                  ¥{{ totalPrice.toLocaleString() }}
                </p>
              </div>

              <!-- ADD TO CART 按钮 -->
              <div class="px-5 pt-4 pb-0">
                <button @click="handleAddToCart"
                  class="w-full h-[48px] bg-primary-500 text-dark-950 text-base font-bold rounded-full transition-all duration-200 hover:bg-[#2e9e1e] hover:scale-[1.01] active:scale-[0.98]">
                  ADD TO CART
                </button>
              </div>

              <!-- 积分奖励 -->
              <div class="px-5 pt-4 pb-3">
                <div class="flex items-center gap-1 text-[#AAAAAA] text-xs">
                  <svg class="w-3.5 h-3.5 text-primary-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                  <span>最高可赚取 <span class="text-primary-500 font-medium">{{ pointsEarned }}</span> 胖虫积分</span>
                </div>
              </div>

              <!-- 预计送达 -->
              <div class="px-5 pb-2">
                <div class="flex items-center gap-2 text-sm">
                  <span class="text-white font-medium">{{ deliveryRange }}</span>
                  <span class="text-primary-500 font-bold text-xs">· 免运费</span>
                </div>
              </div>

              <!-- 门店自提 -->
              <div class="px-5 pb-4">
                <button class="flex items-center gap-1 text-primary-500 text-xs hover:underline group">
                  <span>查看胖虫线下自提点</span>
                  <svg class="w-3 h-3 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>

              <!-- 分割线 -->
              <div class="mx-5 border-t border-[#2A2A2A]"></div>

              <!-- 分期付款 -->
              <div class="px-5 py-3">
                <div class="bg-[#1A1A1A] rounded-xl px-3 py-2">
                  <p class="text-[#888] text-[11px] leading-relaxed">
                    首付 <span class="text-white font-medium">¥{{ monthlyPayment }}</span>/月 起
                    或 0% 费率分期 | <span class="text-primary-500 cursor-pointer hover:underline">了解更多</span>
                  </p>
                </div>
              </div>

              <!-- 直购说明 -->
              <div class="px-5 pb-4">
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

    <!-- Toast -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toastMsg"
          class="fixed top-20 right-6 z-[9999] bg-[#111] border border-[#2A2A2A] rounded-xl px-5 py-3 shadow-2xl flex items-center gap-3 max-w-xs">
          <svg class="w-5 h-5 text-primary-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm text-dark-200">{{ toastMsg }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import ProductConfiguratorPanel from '@/components/ProductConfiguratorPanel.vue'
import {
  cameraPresets,
  configuratorParts,
  materialOptions,
  productVariants as colorOptions,
} from '@/data/productConfigurator'

const router = useRouter()
const cart = useCartStore()
const Product3DViewer = defineAsyncComponent(() => import('@/components/Product3DViewer.vue'))

// ==================== 模拟产品数据 ====================
const product = {
  id: 'titan-2026',
  name: '胖虫·泰坦',
  tagline: '18 英寸旗舰游戏本 — 搭载最新 Intel® Core™ i9 处理器与 NVIDIA® GeForce RTX™ 5090 显卡',
  basePrice: 29999,
  specs: [
    { label: '处理器', value: 'Intel® Core™ i9-14900HX (24核32线程, 最高 5.8GHz)' },
    { label: '操作系统', value: 'Windows 11 Home (64位)' },
    { label: '显示屏', value: '18" QHD+ 240Hz IPS, 100% DCI-P3, G-Sync' },
    { label: '显卡', value: 'NVIDIA® GeForce RTX™ 5090 16GB GDDR7' },
    { label: '内存', value: '32GB DDR5-5600MHz (2×16GB)' },
    { label: '存储', value: '2TB PCIe Gen4 NVMe SSD (双 M.2 插槽)' },
    { label: '电池', value: '99.9Wh 锂聚合物电池' },
    { label: '重量', value: '约 2.8kg' },
  ],
}

const features = [
  { icon: 'fas fa-shipping-fast', title: '次日达发货', desc: '工作日下午 2 点前下单，次日送达（部分地区）' },
  { icon: 'fas fa-undo-alt', title: '无忧退换', desc: '7 天无理由退换，30 天质量问题包退' },
  { icon: 'fas fa-headset', title: '全面客户支持', desc: '7×24 小时在线客服，专属技术顾问一对一' },
]

const bonus = {
  title: 'PC Game Pass — 3 个月会员',
  value: '¥297',
  desc: '畅玩数百款高品质 PC 游戏，包括 EA Play 会员权益。购买即赠，开箱即玩。',
  footnote: '* 需要 Microsoft 账号。仅限新订阅用户。到期后自动续费，可随时取消。',
}

const recommendations = [
  { id: 'r1', name: '胖虫电竞鼠标 V3', price: 399, image: '' },
  { id: 'r2', name: '胖虫机械键盘 Pro', price: 899, image: '' },
  { id: 'r3', name: '胖虫 27" 4K 显示器', price: 3499, image: '' },
  { id: 'r4', name: '胖虫电竞耳机 X1', price: 599, image: '' },
]

const keyboardOptions = [
  { id: 'us', name: 'US Layout' },
  { id: 'uk', name: 'UK Layout' },
  { id: 'cn', name: '中文布局' },
  { id: 'jp', name: 'JP Layout' },
]

const warrantyOptions = [
  { id: 'essential', name: 'PangchongCare Essential', desc: '延长保修至 3 年，含意外损坏保护', price: 299 },
  { id: 'elite', name: 'PangchongCare Elite', desc: '延长保修至 5 年，含意外损坏 + 电池更换', price: 799 },
  { id: 'none', name: '不需要，谢谢', desc: '仅享受标准 1 年保修', price: 0 },
]

const topPicks = [
  { id: 'tp1', name: '胖虫 140W GaN 充电器', price: 349, image: '' },
  { id: 'tp2', name: '胖虫笔记本散热底座', price: 199, image: '' },
  { id: 'tp3', name: '胖虫 USB-C 扩展坞 12合1', price: 499, image: '' },
  { id: 'tp4', name: '胖虫笔记本内胆包 18寸', price: 129, image: '' },
  { id: 'tp5', name: '胖虫无线鼠标垫 (RGB)', price: 249, image: '' },
]

// ==================== 状态 ====================
const selectedVariant = ref('black')
const selectedMaterial = ref('matte')
const autoRotate = ref(true)
const cameraPreset = ref('front')
const viewerResetKey = ref(0)
const selectedKeyboard = ref('cn')
const selectedWarranty = ref('none')
const selectedPicks = ref([])
const toastMsg = ref('')

// ==================== 计算属性 ====================
const activeVariant = computed(() => colorOptions.find(o => o.id === selectedVariant.value) || colorOptions[0])
const activeMaterial = computed(() => materialOptions.find(o => o.id === selectedMaterial.value) || materialOptions[0])

const colorPriceDiff = computed(() => {
  return activeVariant.value?.priceDiff || 0
})

const warrantyPrice = computed(() => {
  const opt = warrantyOptions.find(o => o.id === selectedWarranty.value)
  return opt?.price || 0
})

const picksPrice = computed(() => {
  return selectedPicks.value.reduce((sum, id) => {
    const pick = topPicks.find(p => p.id === id)
    return sum + (pick?.price || 0)
  }, 0)
})

const totalPrice = computed(() => {
  return product.basePrice + colorPriceDiff.value + warrantyPrice.value + picksPrice.value
})

const pointsEarned = computed(() => Math.floor(totalPrice.value * 10).toLocaleString())

const deliveryRange = computed(() => {
  const now = new Date()
  const min = new Date(now.getTime() + 5 * 86400000)
  const max = new Date(now.getTime() + 7 * 86400000)
  const fmt = d => `${d.getMonth() + 1}月${d.getDate()}日`
  return `${fmt(min)} ~ ${fmt(max)}`
})

const monthlyPayment = computed(() => Math.ceil(totalPrice.value / 12).toLocaleString())

// ==================== 方法 ====================
function togglePick(id) {
  const idx = selectedPicks.value.indexOf(id)
  if (idx >= 0) {
    selectedPicks.value.splice(idx, 1)
  } else {
    selectedPicks.value.push(id)
  }
}

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2500)
}

function resetViewerCamera() {
  viewerResetKey.value += 1
}

function handleAddToCart() {
  // 组装配置描述
  const colorName = activeVariant.value?.name || ''
  const materialName = activeMaterial.value?.name || ''
  const keyName = keyboardOptions.find(o => o.id === selectedKeyboard.value)?.name || ''
  const warrantyName = warrantyOptions.find(o => o.id === selectedWarranty.value)?.name || ''
  const pickNames = selectedPicks.value.map(id => topPicks.find(p => p.id === id)?.name).filter(Boolean)

  const specs = {
    '颜色': colorName,
    '材质': materialName,
    '键盘布局': keyName,
  }
  if (selectedWarranty.value !== 'none') {
    specs['延保'] = warrantyName
  }
  if (pickNames.length > 0) {
    specs['配件'] = pickNames.join('、')
  }
  const configId = [
    product.id,
    selectedVariant.value,
    selectedMaterial.value,
    selectedKeyboard.value,
    selectedWarranty.value,
    ...selectedPicks.value.slice().sort(),
  ].join('_')

  // 添加主产品到购物车
  cart.addLocalItem({
    id: configId,
    name: product.name + '（' + colorName + ' / ' + keyName + '）',
    brand: '胖虫',
    model: '泰坦 2026',
    description: product.tagline,
    specs,
    price: totalPrice.value,
    image_url: '',
    stock: 99,
  })

  showToast('已添加到购物车')
  setTimeout(() => { router.push('/cart') }, 1200)
}
</script>

<style scoped>
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
