<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-7xl mx-auto px-4">
      <div class="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-primary-500">PANGCHONG DIY LAB</p>
          <h1 class="mt-3 text-3xl font-bold text-white md:text-4xl">DIY 装机配置器</h1>
          <p class="mt-3 max-w-3xl text-sm leading-6 text-dark-300">
            选择八大件时实时查看配件信息、兼容性、整机功耗、机箱冗余、价格走势和 3DMark 估算。
          </p>
        </div>
        <div class="grid grid-cols-3 gap-2 text-center text-xs text-dark-400">
          <div class="rounded-lg border border-dark-800 bg-dark-900 px-4 py-3">
            <p class="text-lg font-bold text-white">{{ selectedCount }}/{{ steps.length }}</p>
            <p>已选配件</p>
          </div>
          <div class="rounded-lg border border-dark-800 bg-dark-900 px-4 py-3">
            <p class="text-lg font-bold text-primary-500">{{ totalPower }}W</p>
            <p>估算功耗</p>
          </div>
          <div class="rounded-lg border border-dark-800 bg-dark-900 px-4 py-3">
            <p class="text-lg font-bold text-white">{{ estimated3DMark.toLocaleString() }}</p>
            <p>3DMark</p>
          </div>
        </div>
      </div>

      <div class="mb-10 overflow-x-auto pb-2">
        <div class="flex min-w-max items-center justify-center gap-2 sm:gap-4">
          <div
            v-for="(step, i) in steps"
            :key="step.key"
            class="flex cursor-pointer items-center gap-2 text-sm transition-colors"
            :class="currentStep >= i ? 'text-primary-500' : 'text-dark-500'"
            @click="currentStep = i"
          >
            <div
              class="flex h-8 w-8 items-center justify-center rounded-lg text-sm font-bold transition-colors"
              :class="currentStep >= i ? 'bg-primary-500 text-dark-950' : 'bg-dark-800'"
            >
              <span v-if="selected[i]">&#10003;</span>
              <span v-else>{{ i + 1 }}</span>
            </div>
            <span class="hidden md:inline">{{ step.label }}</span>
            <div v-if="i < steps.length - 1" class="h-px w-6 sm:w-10" :class="currentStep > i ? 'bg-primary-500' : 'bg-dark-800'"></div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div class="lg:col-span-2">
          <div class="rounded-lg border border-dark-800 bg-dark-900 p-5 md:p-6">
            <div class="mb-6 flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-primary-500">{{ steps[currentStep].key }}</p>
                <h2 class="mt-2 text-xl font-bold text-white">{{ steps[currentStep].label }}</h2>
                <p class="mt-1 text-sm text-dark-400">{{ steps[currentStep].desc }}</p>
              </div>
              <span class="rounded border border-dark-700 px-3 py-1 text-xs text-dark-400">{{ filteredProducts.length }} / {{ stepProducts.length }} 款</span>
            </div>

            <div class="mb-5 grid gap-3 md:grid-cols-4">
              <label class="block">
                <span class="text-xs text-dark-500">关键词</span>
                <input
                  v-model="filters.keyword"
                  class="mt-1 w-full rounded-lg border border-dark-700 bg-dark-950 px-3 py-2 text-sm text-white outline-none transition-colors placeholder:text-dark-600 focus:border-primary-500"
                  placeholder="型号 / 规格"
                >
              </label>
              <label class="block">
                <span class="text-xs text-dark-500">品牌</span>
                <select
                  v-model="filters.brand"
                  class="mt-1 w-full rounded-lg border border-dark-700 bg-dark-950 px-3 py-2 text-sm text-white outline-none transition-colors focus:border-primary-500"
                >
                  <option value="">全部品牌</option>
                  <option v-for="brand in availableBrands" :key="brand" :value="brand">{{ brand }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-xs text-dark-500">{{ currentSpecFilter.label }}</span>
                <select
                  v-model="filters.specValue"
                  class="mt-1 w-full rounded-lg border border-dark-700 bg-dark-950 px-3 py-2 text-sm text-white outline-none transition-colors focus:border-primary-500"
                >
                  <option value="">全部{{ currentSpecFilter.label }}</option>
                  <option v-for="value in availableSpecValues" :key="value" :value="value">{{ value }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-xs text-dark-500">排序</span>
                <select
                  v-model="filters.sort"
                  class="mt-1 w-full rounded-lg border border-dark-700 bg-dark-950 px-3 py-2 text-sm text-white outline-none transition-colors focus:border-primary-500"
                >
                  <option value="default">默认</option>
                  <option value="price-asc">价格从低到高</option>
                  <option value="price-desc">价格从高到低</option>
                  <option value="power-asc">功耗从低到高</option>
                  <option value="space-asc">尺寸从小到大</option>
                </select>
              </label>
            </div>

            <div v-if="selected[currentStep]" class="mb-5 rounded-lg border border-primary-500/30 bg-primary-500/10 p-4">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-xs text-primary-400">当前已选</p>
                  <h3 class="mt-1 text-base font-semibold text-white">{{ selected[currentStep].name }}</h3>
                  <div class="mt-3 grid gap-2 text-xs text-dark-300 sm:grid-cols-2">
                    <span v-for="item in specPairs(selected[currentStep], 8)" :key="item.key" class="rounded border border-white/10 bg-black/20 px-2 py-1">
                      {{ item.label }}: {{ item.value }}
                    </span>
                  </div>
                </div>
                <button class="rounded-lg border border-dark-700 px-3 py-2 text-xs text-dark-300 hover:border-primary-500 hover:text-primary-500" @click="removeCurrent">
                  移除
                </button>
              </div>
            </div>

            <div v-if="loading" class="flex justify-center py-16">
              <div class="h-10 w-10 animate-spin rounded-full border-b-2 border-t-2 border-primary-500"></div>
            </div>

            <div v-else-if="filteredProducts.length === 0" class="rounded-lg border border-dashed border-dark-700 py-16 text-center text-dark-500">
              <p class="text-sm">没有匹配的配件，换个品牌或规格试试。</p>
            </div>

            <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <article
                v-for="product in filteredProducts"
                :key="product.id"
                class="cursor-pointer rounded-lg border p-4 transition-all duration-200"
                :class="isSelected(product)
                  ? 'border-primary-500 bg-primary-500/10 shadow-lg shadow-primary-500/10'
                  : 'border-dark-800 bg-dark-950 hover:border-dark-600'"
                @click="selectItem(product)"
              >
                <div class="flex gap-3">
                  <div class="flex h-20 w-20 flex-shrink-0 items-center justify-center overflow-hidden rounded-lg bg-dark-900">
                    <img :src="product.image_url || fallbackImage" :alt="product.name" class="h-full w-full object-contain" loading="lazy" @error="handleImageError">
                  </div>
                  <div class="min-w-0 flex-1">
                    <div class="flex items-start justify-between gap-3">
                      <div class="min-w-0">
                        <p class="text-xs text-dark-500">{{ product.brand || '未知品牌' }}</p>
                        <h3 class="mt-1 line-clamp-2 text-sm font-semibold text-white">{{ product.name }}</h3>
                      </div>
                      <div class="text-right">
                        <p class="font-bold text-primary-500">¥{{ money(product.price) }}</p>
                        <p v-if="product.original_price && Number(product.original_price) > Number(product.price)" class="text-xs text-dark-600 line-through">¥{{ money(product.original_price) }}</p>
                      </div>
                    </div>
                    <p class="mt-2 line-clamp-2 text-xs leading-5 text-dark-500">{{ product.description }}</p>
                  </div>
                </div>

                <div class="mt-4 grid grid-cols-2 gap-2 text-xs text-dark-300">
                  <span v-for="item in specPairs(product, 6)" :key="item.key" class="rounded border border-white/10 bg-white/[0.03] px-2 py-1">
                    {{ item.label }}: {{ item.value }}
                  </span>
                </div>

                <div class="mt-4 flex items-center justify-between border-t border-dark-800 pt-3 text-xs">
                  <span :class="selectionAdvice(product).level === 'warn' ? 'text-yellow-400' : 'text-dark-400'">{{ selectionAdvice(product).text }}</span>
                  <span v-if="isSelected(product)" class="font-semibold text-primary-500">已选择</span>
                </div>
              </article>
            </div>

            <div class="mt-8 flex justify-between">
              <button
                class="rounded-lg bg-dark-800 px-5 py-2 text-sm text-dark-300 transition-colors hover:bg-dark-700 disabled:opacity-30"
                :disabled="currentStep === 0"
                @click="prevStep"
              >
                上一步
              </button>
              <button
                class="rounded-lg bg-primary-500 px-5 py-2 text-sm font-semibold text-dark-950 transition-colors hover:bg-primary-400 disabled:opacity-30"
                :disabled="currentStep === steps.length - 1"
                @click="nextStep"
              >
                下一步
              </button>
            </div>
          </div>
        </div>

        <aside class="lg:col-span-1">
          <div class="sticky top-24 space-y-4">
            <section class="rounded-lg border border-dark-800 bg-dark-900 p-5">
              <div class="mb-4 flex items-center justify-between">
                <h2 class="text-xl font-bold text-white">配置清单</h2>
                <button v-if="selectedCount > 0" class="text-xs text-dark-500 hover:text-red-400" @click="clearAll">清空</button>
              </div>

              <div class="space-y-1">
                <button
                  v-for="(step, i) in steps"
                  :key="step.key"
                  class="flex w-full items-center justify-between rounded-lg px-2 py-3 text-left transition-colors hover:bg-dark-950/70"
                  :class="currentStep === i ? 'bg-dark-950/80 ring-1 ring-primary-500/30' : ''"
                  @click="currentStep = i"
                >
                  <div class="min-w-0">
                    <p class="text-sm text-dark-300">{{ step.label }}</p>
                    <p v-if="selected[i]" class="mt-1 truncate text-xs text-white">{{ selected[i].name }}</p>
                    <p v-else class="mt-1 text-xs text-dark-600">未选择</p>
                  </div>
                  <p v-if="selected[i]" class="ml-3 flex-shrink-0 text-xs font-semibold text-primary-500">¥{{ money(selected[i].price) }}</p>
                </button>
              </div>

              <div class="mt-5 border-t border-dark-800 pt-4">
                <div class="mb-2 flex justify-between text-sm text-dark-400">
                  <span>已选 {{ selectedCount }} / {{ steps.length }} 件</span>
                  <span v-if="savedAmount > 0">节省 ¥{{ money(savedAmount) }}</span>
                </div>
                <div class="flex justify-between text-xl font-bold text-white">
                  <span>总计</span>
                  <span class="text-primary-500">¥{{ money(totalPrice) }}</span>
                </div>
              </div>

              <button
                class="mt-5 w-full rounded-lg py-3 text-sm font-semibold transition-all"
                :class="isComplete ? 'bg-primary-500 text-dark-950 hover:bg-primary-400' : 'bg-dark-800 text-dark-500'"
                :disabled="!isComplete"
                @click="addToCart"
              >
                {{ isComplete ? '整套加入购物车' : '请完成所有配件选择' }}
              </button>
            </section>

            <section class="rounded-lg border border-dark-800 bg-dark-900 p-5">
              <h2 class="text-base font-bold text-white">兼容性检查</h2>
              <div class="mt-4 space-y-2">
                <div
                  v-for="check in compatibilityChecks"
                  :key="check.key"
                  class="rounded-lg border px-3 py-2 text-xs"
                  :class="check.level === 'ok'
                    ? 'border-primary-500/30 bg-primary-500/10 text-primary-300'
                    : check.level === 'warn'
                      ? 'border-yellow-500/30 bg-yellow-500/10 text-yellow-300'
                      : 'border-dark-700 bg-dark-950 text-dark-400'"
                >
                  <p class="font-semibold">{{ check.title }}</p>
                  <p class="mt-1 leading-5">{{ check.message }}</p>
                </div>
              </div>
            </section>

            <section class="rounded-lg border border-dark-800 bg-dark-900 p-5">
              <h2 class="text-base font-bold text-white">完成后估算</h2>
              <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div class="rounded-lg bg-dark-950 p-3">
                  <p class="text-xs text-dark-500">整机功耗</p>
                  <p class="mt-1 text-lg font-bold text-white">{{ totalPower }}W</p>
                </div>
                <div class="rounded-lg bg-dark-950 p-3">
                  <p class="text-xs text-dark-500">电源冗余</p>
                  <p class="mt-1 text-lg font-bold" :class="psuHeadroom >= 150 ? 'text-primary-500' : 'text-yellow-400'">{{ psuHeadroomLabel }}</p>
                </div>
                <div class="rounded-lg bg-dark-950 p-3">
                  <p class="text-xs text-dark-500">显卡剩余空间</p>
                  <p class="mt-1 text-lg font-bold" :class="gpuSpaceHeadroom >= 30 ? 'text-primary-500' : 'text-yellow-400'">{{ gpuSpaceLabel }}</p>
                </div>
                <div class="rounded-lg bg-dark-950 p-3">
                  <p class="text-xs text-dark-500">3DMark 估算</p>
                  <p class="mt-1 text-lg font-bold text-white">{{ estimated3DMark.toLocaleString() }}</p>
                </div>
              </div>
              <p class="mt-3 text-xs leading-5 text-dark-500">跑分基于 CPU/GPU 型号规则估算，用于装机比较，不代表实测成绩。</p>
            </section>

            <section class="rounded-lg border border-dark-800 bg-dark-900 p-5">
              <div class="flex items-center justify-between">
                <h2 class="text-base font-bold text-white">价格走势</h2>
                <button class="rounded-lg border border-dark-700 px-3 py-1.5 text-xs text-dark-300 hover:border-primary-500 hover:text-primary-500" @click="refreshPriceHistory">
                  刷新
                </button>
              </div>
              <p class="mt-2 text-xs text-dark-500">{{ priceHistoryHint }}</p>
              <div class="mt-4 h-28 rounded-lg border border-dark-800 bg-dark-950 p-3">
                <svg viewBox="0 0 280 96" class="h-full w-full" role="img" aria-label="价格走势图">
                  <polyline v-if="chartPoints" :points="chartPoints" fill="none" stroke="#44D62C" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                  <line x1="0" y1="82" x2="280" y2="82" stroke="rgba(255,255,255,0.12)" />
                </svg>
              </div>
              <div class="mt-3 flex justify-between text-xs text-dark-400">
                <span>{{ priceRange.min }}</span>
                <span>{{ priceRange.max }}</span>
              </div>
            </section>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api, { marketApi } from '@/api'
import { useCartStore } from '@/store/cart'
import { useNotifyStore } from '@/store/notify'

const router = useRouter()
const cartStore = useCartStore()
const notify = useNotifyStore()
const fallbackImage = '/assets/pangchong-product-fallback.png'

const steps = [
  { key: 'cpu', label: '处理器 CPU', desc: '选择适合你需求的处理器', catId: 'd1000000-0000-0000-0000-000000000001', specKey: 'socket', specLabel: '插槽' },
  { key: 'gpu', label: '显卡 GPU', desc: '游戏与创作的核心动力', catId: 'd1000000-0000-0000-0000-000000000002', specKey: 'vram', specLabel: '显存' },
  { key: 'motherboard', label: '主板', desc: '连接所有配件的桥梁', catId: 'd1000000-0000-0000-0000-000000000003', specKey: 'form_factor', specLabel: '板型' },
  { key: 'ram', label: '内存 RAM', desc: '多任务处理的保障', catId: 'd1000000-0000-0000-0000-000000000004', specKey: 'capacity', specLabel: '容量' },
  { key: 'ssd', label: '固态硬盘 SSD', desc: '极速存储体验', catId: 'd1000000-0000-0000-0000-000000000005', specKey: 'capacity', specLabel: '容量' },
  { key: 'cooler', label: '散热器', desc: '保持冷静，释放性能', catId: 'd1000000-0000-0000-0000-000000000006', specKey: 'type', specLabel: '类型' },
  { key: 'psu', label: '电源 PSU', desc: '稳定供电的基石', catId: 'd1000000-0000-0000-0000-000000000007', specKey: 'wattage', specLabel: '功率' },
  { key: 'case', label: '机箱', desc: '颜值与空间的载体', catId: 'd1000000-0000-0000-0000-000000000008', specKey: 'type', specLabel: '机箱类型' }
]

const specLabels = {
  cores: '核心',
  arch: '架构',
  base_clock: '基础频率',
  boost_clock: '睿频',
  tdp: 'TDP',
  socket: '插槽',
  memory_support: '内存支持',
  gpu: 'GPU',
  vram: '显存',
  interface: '接口',
  power_connector: '供电',
  length: '长度',
  chipset: '芯片组',
  form_factor: '规格',
  memory: '内存',
  capacity: '容量',
  speed: '频率',
  type: '类型',
  radiator: '冷排',
  tdp_support: '散热能力',
  height: '高度',
  wattage: '功率',
  efficiency: '认证',
  modular: '模组',
  size: '尺寸',
  mb_support: '主板支持',
  gpu_length: '显卡限长',
  cooler_height: '散热限高'
}

const currentStep = ref(0)
const selected = ref({})
const allProducts = ref({})
const loading = ref(true)
const priceHistory = ref([])
const priceHistorySource = ref('local-estimate')
const filters = reactive({
  keyword: '',
  brand: '',
  specValue: '',
  sort: 'default'
})

const currentSpecFilter = computed(() => ({
  key: steps[currentStep.value].specKey,
  label: steps[currentStep.value].specLabel
}))

const stepProducts = computed(() => allProducts.value[steps[currentStep.value].catId] || [])
const selectedCount = computed(() => Object.keys(selected.value).length)
const isComplete = computed(() => selectedCount.value === steps.length)
const totalPrice = computed(() => Object.values(selected.value).reduce((sum, item) => sum + Number(item.price), 0))
const savedAmount = computed(() => Object.values(selected.value).reduce((sum, item) => sum + Math.max(Number(item.original_price || item.price) - Number(item.price), 0), 0))

const availableBrands = computed(() => uniqueValues(stepProducts.value.map(product => product.brand).filter(Boolean)))
const availableSpecValues = computed(() => uniqueValues(stepProducts.value.map(product => product.specs?.[currentSpecFilter.value.key]).filter(Boolean)))

const filteredProducts = computed(() => {
  const keyword = filters.keyword.trim().toLowerCase()
  const specKey = currentSpecFilter.value.key
  const result = stepProducts.value.filter((product) => {
    const specText = Object.values(product.specs || {}).join(' ').toLowerCase()
    const matchesKeyword = !keyword || `${product.name} ${product.description || ''} ${specText}`.toLowerCase().includes(keyword)
    const matchesBrand = !filters.brand || product.brand === filters.brand
    const matchesSpec = !filters.specValue || String(product.specs?.[specKey] || '').includes(filters.specValue)
    return matchesKeyword && matchesBrand && matchesSpec
  })

  return [...result].sort((a, b) => {
    if (filters.sort === 'price-asc') return Number(a.price) - Number(b.price)
    if (filters.sort === 'price-desc') return Number(b.price) - Number(a.price)
    if (filters.sort === 'power-asc') return productPower(a) - productPower(b)
    if (filters.sort === 'space-asc') return productSize(a) - productSize(b)
    return 0
  })
})

const totalPower = computed(() => {
  const base = Object.values(selected.value).reduce((sum, item) => sum + productPower(item), 0)
  return Math.round(base + (selectedCount.value > 0 ? 60 : 0))
})

const psuWattage = computed(() => parseNumber(selected.value[6]?.specs?.wattage))
const psuHeadroom = computed(() => psuWattage.value ? psuWattage.value - totalPower.value : 0)
const psuHeadroomLabel = computed(() => psuWattage.value ? `${psuHeadroom.value}W` : '待选择')

const gpuSpaceHeadroom = computed(() => {
  const caseLimit = parseNumber(selected.value[7]?.specs?.gpu_length)
  const gpuLength = parseNumber(selected.value[1]?.specs?.length)
  return caseLimit && gpuLength ? caseLimit - gpuLength : 0
})
const gpuSpaceLabel = computed(() => {
  const caseLimit = parseNumber(selected.value[7]?.specs?.gpu_length)
  const gpuLength = parseNumber(selected.value[1]?.specs?.length)
  return caseLimit && gpuLength ? `${gpuSpaceHeadroom.value}mm` : '待选择'
})

const estimated3DMark = computed(() => {
  const gpuScore = gpuScoreMap(selected.value[1])
  const cpuScore = cpuScoreMap(selected.value[0])
  if (!gpuScore && !cpuScore) return 0
  return Math.round(gpuScore * 0.82 + cpuScore * 0.18)
})

const compatibilityChecks = computed(() => {
  const cpu = selected.value[0]
  const gpu = selected.value[1]
  const mobo = selected.value[2]
  const ram = selected.value[3]
  const cooler = selected.value[5]
  const psu = selected.value[6]
  const pcCase = selected.value[7]
  const checks = []

  checks.push(makeCheck(
    'cpu-mobo',
    'CPU / 主板插槽',
    cpu && mobo,
    cpu?.specs?.socket === mobo?.specs?.socket,
    `CPU ${cpu?.specs?.socket || '-'}，主板 ${mobo?.specs?.socket || '-'}`,
    '请选择 CPU 和主板后检查插槽。'
  ))

  checks.push(makeCheck(
    'ram-mobo',
    '内存 / 主板类型',
    ram && mobo,
    String(mobo?.specs?.memory || '').includes(String(ram?.specs?.type || '')),
    `内存 ${ram?.specs?.type || '-'}，主板支持 ${mobo?.specs?.memory || '-'}`,
    '请选择内存和主板后检查 DDR 类型。'
  ))

  const moboForm = String(mobo?.specs?.form_factor || '')
  const caseMb = String(pcCase?.specs?.mb_support || '')
  checks.push(makeCheck(
    'mobo-case',
    '主板 / 机箱板型',
    mobo && pcCase,
    caseMb.includes(moboForm),
    `主板 ${moboForm || '-'}，机箱支持 ${caseMb || '-'}`,
    '请选择主板和机箱后检查板型。'
  ))

  const gpuLength = parseNumber(gpu?.specs?.length)
  const caseGpuLength = parseNumber(pcCase?.specs?.gpu_length)
  checks.push(makeCheck(
    'gpu-case',
    '显卡 / 机箱限长',
    gpu && pcCase && gpuLength && caseGpuLength,
    gpuLength <= caseGpuLength,
    `显卡 ${gpuLength || '-'}mm，机箱限长 ${caseGpuLength || '-'}mm，剩余 ${gpuSpaceHeadroom.value || 0}mm`,
    '请选择显卡和机箱后检查长度。'
  ))

  const coolerHeight = parseNumber(cooler?.specs?.height)
  const caseCoolerHeight = parseNumber(pcCase?.specs?.cooler_height)
  checks.push(makeCheck(
    'cooler-case',
    '散热器 / 机箱限高',
    cooler && pcCase,
    !coolerHeight || !caseCoolerHeight || coolerHeight <= caseCoolerHeight,
    coolerHeight ? `散热器 ${coolerHeight}mm，机箱限高 ${caseCoolerHeight || '-'}mm` : '水冷型号需人工确认冷排位。',
    '请选择散热器和机箱后检查高度。'
  ))

  checks.push(makeCheck(
    'psu-power',
    '电源 / 整机功耗',
    psu,
    psuHeadroom.value >= 150,
    `电源 ${psuWattage.value || '-'}W，估算功耗 ${totalPower.value}W，冗余 ${psuHeadroom.value || 0}W`,
    '请选择电源后检查功耗冗余。'
  ))

  return checks
})

const selectedPriceTarget = computed(() => selected.value[currentStep.value] || Object.values(selected.value)[0])
const priceHistoryHint = computed(() => {
  if (!selectedPriceTarget.value) return '选择一个配件后显示走势。'
  return priceHistorySource.value === 'tmapi'
    ? '数据来自 TMAPI 历史价格接口。'
    : '未配置外部 API token，当前展示本地估算曲线。'
})
const chartPoints = computed(() => {
  if (priceHistory.value.length === 0) return ''
  const prices = priceHistory.value.map(item => Number(item.price))
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = Math.max(max - min, 1)
  return priceHistory.value.map((item, index) => {
    const x = priceHistory.value.length === 1 ? 0 : (index / (priceHistory.value.length - 1)) * 280
    const y = 82 - ((Number(item.price) - min) / range) * 64
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
})
const priceRange = computed(() => {
  if (priceHistory.value.length === 0) return { min: '-', max: '-' }
  const prices = priceHistory.value.map(item => Number(item.price))
  return { min: `低 ¥${money(Math.min(...prices))}`, max: `高 ¥${money(Math.max(...prices))}` }
})

function uniqueValues(values) {
  return [...new Set(values.map(value => String(value)))].sort((a, b) => a.localeCompare(b, 'zh-CN'))
}

function money(value) {
  return Number(value || 0).toLocaleString()
}

function parseNumber(value) {
  const match = String(value || '').match(/\d+(\.\d+)?/)
  return match ? Number(match[0]) : 0
}

function productPower(product) {
  if (!product) return 0
  const specs = product.specs || {}
  if (specs.wattage) return 0
  return parseNumber(specs.tdp) || parseNumber(specs.tdp_support) * 0.15 || 8
}

function productSize(product) {
  if (!product) return 0
  return parseNumber(product.specs?.length) || parseNumber(product.specs?.height) || parseNumber(product.specs?.size)
}

function specPairs(product, limit = 6) {
  return Object.entries(product?.specs || {})
    .filter(([, value]) => value !== null && value !== undefined && value !== '')
    .slice(0, limit)
    .map(([key, value]) => ({ key, label: specLabels[key] || key, value }))
}

function makeCheck(key, title, ready, ok, okMessage, pendingMessage) {
  if (!ready) {
    return { key, title, level: 'pending', message: pendingMessage }
  }
  return {
    key,
    title,
    level: ok ? 'ok' : 'warn',
    message: ok ? okMessage : `${okMessage}，存在不兼容风险。`
  }
}

function gpuScoreMap(product) {
  const text = `${product?.name || ''} ${product?.model || ''} ${product?.specs?.gpu || ''}`.toLowerCase()
  if (text.includes('5090')) return 36000
  if (text.includes('5080')) return 28500
  if (text.includes('4090')) return 30000
  if (text.includes('5070 ti')) return 22500
  if (text.includes('5070')) return 18500
  if (text.includes('4070 ti')) return 22000
  if (text.includes('4070')) return 17500
  if (text.includes('4060')) return 10500
  if (text.includes('9070 xt')) return 23500
  if (text.includes('9070')) return 19500
  return product ? 12000 : 0
}

function cpuScoreMap(product) {
  const text = `${product?.name || ''} ${product?.model || ''}`.toLowerCase()
  if (text.includes('14900')) return 21000
  if (text.includes('14700')) return 18500
  if (text.includes('14600')) return 14500
  if (text.includes('12900')) return 16000
  if (text.includes('9900x')) return 18000
  if (text.includes('9700x')) return 15000
  if (text.includes('7800x3d')) return 15500
  if (text.includes('9600x')) return 12500
  return product ? 11000 : 0
}

function selectionAdvice(product) {
  const checks = []
  if (currentStep.value === 1 && selected.value[7]) {
    const left = parseNumber(selected.value[7].specs?.gpu_length) - parseNumber(product.specs?.length)
    if (left < 30) checks.push(`装入当前机箱仅剩 ${left}mm`)
  }
  if (currentStep.value === 2 && selected.value[0] && product.specs?.socket !== selected.value[0].specs?.socket) {
    checks.push('与当前 CPU 插槽不同')
  }
  if (currentStep.value === 6) {
    const headroom = parseNumber(product.specs?.wattage) - totalPower.value
    if (headroom < 150) checks.push(`电源冗余仅 ${headroom}W`)
  }
  if (currentStep.value === 7 && selected.value[1]) {
    const left = parseNumber(product.specs?.gpu_length) - parseNumber(selected.value[1].specs?.length)
    if (left < 30) checks.push(`显卡剩余空间 ${left}mm`)
  }
  return checks.length ? { level: 'warn', text: checks[0] } : { level: 'ok', text: '规格信息已展示，可加入配置比较' }
}

function handleImageError(event) {
  const image = event.target
  if (image instanceof HTMLImageElement && !image.src.endsWith(fallbackImage)) {
    image.src = fallbackImage
  }
}

function isSelected(product) {
  return selected.value[currentStep.value]?.id === product.id
}

function selectItem(product) {
  selected.value[currentStep.value] = product
  refreshPriceHistory()
}

function removeCurrent() {
  const next = { ...selected.value }
  delete next[currentStep.value]
  selected.value = next
}

function prevStep() {
  if (currentStep.value > 0) currentStep.value--
}

function nextStep() {
  if (currentStep.value < steps.length - 1) currentStep.value++
}

function clearAll() {
  selected.value = {}
  priceHistory.value = []
  currentStep.value = 0
}

async function addToCart() {
  if (!isComplete.value) return
  const blocking = compatibilityChecks.value.filter(check => check.level === 'warn')
  if (blocking.length > 0) {
    notify.show(`存在兼容风险：${blocking[0].title}`, 'warning')
    return
  }

  const items = Object.values(selected.value)
  const results = await Promise.allSettled(items.map(item => cartStore.addToCart(item.id, 1)))
  const failed = results.map((result, index) => result.status === 'rejected' ? items[index].name : null).filter(Boolean)
  if (failed.length === 0) {
    notify.show('所有配件已加入购物车', 'success')
    router.push('/cart')
  } else if (failed.length < items.length) {
    notify.show(`部分配件添加失败：${failed.join('、')}`, 'warning')
    router.push('/cart')
  } else {
    notify.show('添加失败，请重试', 'error')
  }
}

async function loadCategoryProducts(catId) {
  if (allProducts.value[catId]) return
  try {
    const res = await api.get('/products', { params: { category_id: catId, page: 1, page_size: 100, sort_by: 'price', sort_order: 'asc' } })
    allProducts.value[catId] = res?.items || []
  } catch (e) {
    console.error(`Failed to load category ${catId}:`, e)
    allProducts.value[catId] = []
  }
}

async function refreshPriceHistory() {
  const target = selectedPriceTarget.value
  if (!target) return
  try {
    const res = await marketApi.getPriceHistory(target.id, 30)
    priceHistory.value = res.points || []
    priceHistorySource.value = res.source || 'local-estimate'
  } catch (e) {
    console.error('Failed to load price history:', e)
    priceHistory.value = buildLocalPriceHistory(target)
    priceHistorySource.value = 'local-estimate'
  }
}

function buildLocalPriceHistory(product) {
  const current = Number(product.price || 0)
  const start = Number(product.original_price || current * 1.08)
  return Array.from({ length: 30 }, (_, index) => {
    const date = new Date()
    date.setDate(date.getDate() - (29 - index))
    const price = start - ((start - current) * index / 29) + ((index % 5) - 2) * start * 0.006
    return { date: date.toISOString().slice(0, 10), price: Math.max(price, 0).toFixed(2) }
  })
}

watch(currentStep, async (step) => {
  filters.keyword = ''
  filters.brand = ''
  filters.specValue = ''
  filters.sort = 'default'
  const catId = steps[step].catId
  if (!allProducts.value[catId]) {
    loading.value = true
    await loadCategoryProducts(catId)
    loading.value = false
  }
  refreshPriceHistory()
})

onMounted(async () => {
  loading.value = true
  await loadCategoryProducts(steps[0].catId)
  loading.value = false
})
</script>
