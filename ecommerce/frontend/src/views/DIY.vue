<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="max-w-7xl mx-auto px-4">
      <div class="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-primary-500">PANGCHONG 装机实验室</p>
          <h1 class="mt-3 text-3xl font-bold text-white md:text-4xl">DIY 装机配置器</h1>
          <p class="mt-3 max-w-3xl text-sm leading-6 text-dark-300">
            选择八大件，实时核对兼容性、功耗、机箱空间与价格走势，并查看性能估算。
          </p>
        </div>
        <DsBuildSummary
          class="w-full lg:max-w-2xl"
          eyebrow="当前配置"
          title="装机摘要"
          :price="totalPrice"
          :compatibility="compatibilitySummary.label"
          :compatibility-tone="compatibilitySummary.tone"
          :power="totalPower"
          :performance="estimated3DMark"
        >
          <template #footer>
            <p class="mt-3 text-xs text-dark-400">已选 {{ selectedCount }} / {{ steps.length }} 件配件</p>
          </template>
        </DsBuildSummary>
      </div>

      <DsStepIndicator
        v-model="currentStep"
        :steps="steps"
        aria-label="DIY 装机步骤"
      />

      <section class="mb-8" aria-labelledby="diy-workbench-title">
        <div class="mb-3 flex flex-col gap-3 rounded-lg border border-dark-800 bg-dark-900 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p id="diy-workbench-title" class="text-sm font-semibold text-white">装机工作台</p>
            <p class="mt-1 text-xs text-dark-400">3D 预览用于理解外观和装配位置；配置、核价与交易仍以清单为准。</p>
          </div>
          <div class="inline-flex self-start rounded-lg border border-dark-700 bg-dark-950 p-1" aria-label="装机工作台模式">
            <button
              class="rounded-md px-3 py-1.5 text-xs font-semibold transition-colors disabled:cursor-wait disabled:opacity-60"
              :class="viewerMode === '3d' ? 'bg-primary-500 text-dark-950' : 'text-dark-300 hover:text-white'"
              :disabled="viewerState === 'retrying'"
              data-testid="diy-3d-mode-button"
              @click="open3dMode"
            >
              {{ viewerState === 'failed' ? '重试 3D' : viewerState === 'retrying' ? '正在重试 3D' : '3D 工作台' }}
            </button>
            <button
              class="rounded-md px-3 py-1.5 text-xs font-semibold transition-colors"
              :class="viewerMode === 'list' ? 'bg-white text-dark-950' : 'text-dark-300 hover:text-white'"
              data-testid="diy-list-mode-button"
              @click="openListMode"
            >
              配置清单
            </button>
          </div>
        </div>

        <div
          v-if="viewerMode === 'list'"
          class="rounded-lg border border-dark-800 bg-dark-900 p-4 md:p-6"
          data-testid="diy-list-mode"
        >
          <div
            v-if="viewerFailure"
            class="mb-5 flex flex-col gap-4 rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4 sm:flex-row sm:items-start sm:justify-between"
            role="status"
            aria-live="polite"
            data-testid="diy-viewer-fallback"
          >
            <div>
              <p class="font-semibold text-yellow-100">{{ viewerFailure.title }}</p>
              <p class="mt-1 text-sm leading-6 text-yellow-100/80">{{ viewerFailure.message }}</p>
              <p v-if="viewerFailure.missingNodes?.length" class="mt-2 text-xs text-yellow-200/70">
                缺少节点：{{ viewerFailure.missingNodes.join('、') }}
              </p>
              <p v-if="viewerFailure.emptyNodes?.length" class="mt-1 text-xs text-yellow-200/70">
                空节点：{{ viewerFailure.emptyNodes.join('、') }}
              </p>
            </div>
            <button
              class="flex-shrink-0 rounded-lg border border-yellow-300/40 px-4 py-2 text-xs font-semibold text-yellow-100 transition-colors hover:bg-yellow-300/10 disabled:cursor-wait disabled:opacity-60"
              :disabled="viewerState === 'retrying'"
              data-testid="diy-viewer-retry"
              @click="retryViewer"
            >
              {{ viewerState === 'retrying' ? '后台重试中…' : '重试 3D（清单保持可用）' }}
            </button>
          </div>

          <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-primary-500">当前配置</p>
              <h2 class="mt-2 text-xl font-bold text-white">当前配置清单</h2>
              <p class="mt-1 text-sm text-dark-400">点击任一行可继续选择或更换配件。</p>
            </div>
            <span class="self-start rounded border px-3 py-1.5 text-xs font-semibold" :class="compatibilitySummary.className" data-testid="diy-list-compatibility">
              {{ compatibilitySummary.label }}
            </span>
          </div>

          <div class="overflow-hidden rounded-lg border border-dark-800">
            <button
              v-for="(step, i) in steps"
              :key="step.key"
              class="diy-config-row grid w-full gap-2 border-b border-dark-800 bg-dark-950 px-4 py-3 text-left transition-colors last:border-b-0 hover:bg-dark-900 sm:items-center"
              :class="currentStep === i ? 'ring-1 ring-inset ring-primary-500/40' : ''"
              :data-testid="`diy-list-part-${step.key}`"
              @click="currentStep = i"
            >
              <span class="text-sm font-semibold text-dark-300">{{ step.label }}</span>
              <span v-if="selected[i]" class="min-w-0 truncate text-sm text-white">{{ selected[i].name }}</span>
              <span v-else class="text-sm text-dark-600">尚未选择</span>
              <span v-if="selected[i]" class="text-sm font-semibold text-primary-500 sm:text-right">¥{{ money(selected[i].price) }}</span>
              <span v-else class="text-xs text-dark-600 sm:text-right">—</span>
              <span class="text-xs font-semibold text-primary-400 sm:text-right">{{ selected[i] ? '更换' : '选择' }}</span>
            </button>
          </div>

          <div class="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
            <div class="rounded-lg border border-dark-800 bg-dark-950 p-4">
              <p class="text-sm font-semibold text-white">兼容性状态</p>
              <div class="mt-3 grid gap-2 sm:grid-cols-2">
                <div v-for="check in compatibilityChecks" :key="check.key" class="rounded border border-dark-800 px-3 py-2 text-xs text-dark-300">
                  <p class="font-semibold">{{ check.title }} · {{ check.level === 'ok' ? '通过' : check.level === 'warn' ? '需处理' : '待验证' }}</p>
                  <p class="mt-1 leading-5 text-dark-500">{{ check.message }}</p>
                </div>
              </div>
            </div>

            <div class="rounded-lg border border-primary-500/25 bg-primary-500/[0.06] p-4">
              <div class="flex items-end justify-between gap-3">
                <div>
                  <p class="text-xs text-dark-400">当前核价总计</p>
                  <p class="mt-1 text-2xl font-bold text-primary-500" data-testid="diy-list-total">¥{{ money(totalPrice) }}</p>
                </div>
                <p class="text-right text-xs text-dark-400">{{ selectedCount }} / {{ steps.length }} 件</p>
              </div>
              <p class="mt-3 text-xs leading-5 text-dark-400" data-testid="diy-list-price-status">{{ diyPriceVerificationLabel }}</p>
              <div class="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
                <button
                  class="rounded-lg bg-primary-500 px-4 py-2.5 text-sm font-semibold text-dark-950 transition-colors hover:bg-primary-400 disabled:cursor-not-allowed disabled:bg-dark-800 disabled:text-dark-500"
                  :disabled="!isComplete"
                  data-testid="diy-list-add-cart"
                  @click="addToCart"
                >
                  {{ isComplete ? '整套加入购物车' : '完成选件后加入购物车' }}
                </button>
                <button
                  class="rounded-lg border border-primary-500 px-4 py-2.5 text-sm font-semibold text-primary-400 transition-colors hover:bg-primary-500/10 disabled:cursor-not-allowed disabled:border-dark-700 disabled:text-dark-600"
                  :disabled="!isComplete"
                  data-testid="diy-list-checkout"
                  @click="checkoutNow"
                >
                  加入并前往结算
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="viewerMode === '3d' || viewerState === 'retrying'" class="grid gap-4 xl:grid-cols-[minmax(0,1fr)_280px]">
          <Suspense>
            <Product3DViewer
              v-if="viewerState !== 'failed'"
              :key="viewerAttemptKey"
              :model-url="activeModelUrl"
              :model-scale="activeCaseModel.scale"
              :model-position="activeCaseModel.position"
              :model-rotation="activeCaseModel.rotation"
              :asset-license="activeCaseModel.license"
              :asset-source-url="activeCaseModel.sourceUrl"
              :selected-variant="activeVariant"
              :selected-material="activeMaterial"
              :auto-rotate="autoRotate"
              :camera-preset="cameraPreset"
              :reset-key="viewerResetKey"
              :parts="viewerParts"
              :active="viewerMode === '3d' || viewerState === 'retrying'"
              @failure="handleViewerFailure"
              @ready="handleViewerReady"
            />
            <template #fallback>
              <div class="flex min-h-[360px] items-center justify-center rounded-lg border border-dark-800 bg-dark-900 sm:min-h-[430px] lg:min-h-[520px]">
                <DsAsyncState state="loading" loading-label="正在准备 3D 装机视图" />
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
      </section>

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
              <DsField v-model="filters.keyword" label="关键词" placeholder="型号 / 规格" />
              <DsField
                v-model="filters.brand"
                as="select"
                label="品牌"
                placeholder="全部品牌"
                :options="availableBrands.map(brand => ({ value: brand, label: brand }))"
              />
              <DsField
                v-model="filters.specValue"
                as="select"
                :label="currentSpecFilter.label"
                :placeholder="'全部' + currentSpecFilter.label"
                :options="availableSpecValues.map(value => ({ value, label: value }))"
              />
              <DsField
                v-model="filters.sort"
                as="select"
                label="排序"
                :options="[
                  { value: 'default', label: '默认' },
                  { value: 'price-asc', label: '价格从低到高' },
                  { value: 'price-desc', label: '价格从高到低' },
                  { value: 'power-asc', label: '功耗从低到高' },
                  { value: 'space-asc', label: '尺寸从小到大' },
                ]"
              />
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

            <DsAsyncState
              v-else
              :state="categoryState"
              loading-label="正在加载配件"
              empty-title="没有匹配的配件"
              empty-description="换个品牌或规格试试，或清除筛选后继续浏览。"
              error-title="配件加载失败"
              error-description="商品服务暂时不可用；可以重试，或先查看已保存的配置清单。"
              retry-label="重试加载配件"
              @retry="retryCurrentCategory"
            >
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <DsDiyPartPicker
                v-for="product in filteredProducts"
                :key="product.id"
                :product="product"
                :selected="isSelected(product)"
                :specs="specPairs(product, 6)"
                :selection-advice="selectionAdvice(product)"
                :fallback-image="fallbackImage"
                @select="selectItem"
              />
              </div>
            </DsAsyncState>

            <div class="mt-8 flex justify-between">
              <DsButton
                variant="secondary"
                :disabled="currentStep === 0"
                @click="prevStep"
              >
                上一步
              </DsButton>
              <DsButton
                :disabled="currentStep === steps.length - 1"
                @click="nextStep"
              >
                下一步
              </DsButton>
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
                <div v-if="appearancePriceDiff > 0" class="mb-2 flex justify-between text-sm text-dark-400">
                  <span>3D 外观升级</span>
                  <span>¥{{ money(appearancePriceDiff) }}</span>
                </div>
                <div class="flex justify-between text-xl font-bold text-white">
                  <span>总计</span>
                  <span class="text-primary-500">¥{{ money(totalPrice) }}</span>
                </div>
                <p class="mt-3 text-xs leading-5 text-dark-500">{{ diyPriceVerificationLabel }}</p>
              </div>

                <DsButton block class="mt-5" :disabled="!isComplete" @click="addToCart">
                  {{ isComplete ? '整套加入购物车' : '请完成所有配件选择' }}
                </DsButton>
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
                <h2 class="text-base font-bold text-white">价格来源与记录</h2>
                <button
                  class="rounded-lg border border-dark-700 px-3 py-1.5 text-xs text-dark-300 hover:border-primary-500 hover:text-primary-500 disabled:cursor-not-allowed disabled:opacity-40"
                  :disabled="!selectedPriceTarget || priceHistoryLoading"
                  @click="refreshPriceHistory"
                >
                  {{ priceHistoryLoading ? '核验中...' : '刷新' }}
                </button>
              </div>
              <PriceProvenance v-if="selectedPriceTarget" :product="selectedPriceTarget" compact class="mt-3 rounded-lg border border-dark-800 bg-dark-950 p-3" />
              <p class="mt-2 text-xs text-dark-500">{{ priceHistoryHint }}</p>
              <div class="mt-4 h-28 rounded-lg border border-dark-800 bg-dark-950 p-3">
                <div v-if="!chartPoints" class="flex h-full items-center justify-center text-xs text-dark-500">
                  {{ priceHistoryEmptyLabel }}
                </div>
                <svg v-else viewBox="0 0 280 96" class="h-full w-full" role="img" aria-label="价格走势图">
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
import { computed, defineAsyncComponent, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { marketApi } from '@/api'
import { useCartStore } from '@/store/cart'
import { useNotifyStore } from '@/store/notify'
import ProductConfiguratorPanel from '@/components/ProductConfiguratorPanel.vue'
import PriceProvenance from '@/components/PriceProvenance.vue'
import { DsAsyncState, DsBuildSummary, DsButton, DsDiyPartPicker, DsField, DsStepIndicator } from '@/design-system'
import {
  cameraPresets,
  materialOptions,
  productVariants as colorOptions,
} from '@/data/productConfigurator'
import {
  getPriceProvenance,
  getTraceablePricePoints,
  summarizePriceProvenance,
} from '@/utils/priceProvenance'
import { DIY_VIEWER_LOAD_TIMEOUT_MS, getDiyViewerFailure } from '@/utils/diyViewerResilience'

const router = useRouter()
const route = useRoute()
const cartStore = useCartStore()
const notify = useNotifyStore()
const fallbackImage = '/assets/pangchong-product-fallback.png'
const Product3DViewer = defineAsyncComponent(() => import('@/components/Product3DViewer.vue'))

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
const partAliases = {
  memory: 'ram',
  cooling: 'cooler',
}

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

const currentStep = ref(stepIndexFromPart(route.query.part))
const selected = ref({})
const allProducts = ref({})
const categoryLoadStates = ref({})
const categoryRequests = new Map()
const priceHistory = ref([])
const priceHistorySource = ref('unavailable')
const priceHistoryLoading = ref(false)
const priceHistoryError = ref(false)
let priceHistoryRequestId = 0
const filters = reactive({
  keyword: '',
  brand: '',
  specValue: '',
  sort: 'default'
})
const selectedVariant = ref('black')
const selectedMaterial = ref('matte')
const autoRotate = ref(true)
const cameraPreset = ref('front')
const viewerResetKey = ref(0)
const viewerAttemptKey = ref(0)
const viewerMode = ref('3d')
const viewerState = ref('loading')
const viewerFailure = ref(null)
const viewerRetryRequested = ref(false)
let viewerBudgetTimeoutId

const currentSpecFilter = computed(() => ({
  key: steps[currentStep.value].specKey,
  label: steps[currentStep.value].specLabel
}))

const stepProducts = computed(() => allProducts.value[steps[currentStep.value].catId] || [])
const selectedCount = computed(() => Object.keys(selected.value).length)
const isComplete = computed(() => selectedCount.value === steps.length)
const selectedPartsTotal = computed(() => Object.values(selected.value).reduce((sum, item) => sum + Number(item.price), 0))
const activeVariant = computed(() => colorOptions.find(option => option.id === selectedVariant.value) || colorOptions[0])
const activeMaterial = computed(() => materialOptions.find(option => option.id === selectedMaterial.value) || materialOptions[0])
const activeCaseModel = computed(() => {
  const product = selected.value[7] || {}
  return {
    url: product.model_3d_url || '',
    scale: Number(product.model_3d_scale || 1),
    position: product.model_3d_position || [0, 0, 0],
    rotation: product.model_3d_rotation || [0, 0, 0],
    license: product.asset_license || '',
    sourceUrl: product.asset_source_url || '',
  }
})
const activeModelUrl = computed(() => activeCaseModel.value.url)
const appearancePriceDiff = computed(() => activeVariant.value?.priceDiff || 0)
const totalPrice = computed(() => selectedPartsTotal.value + appearancePriceDiff.value)
const savedAmount = computed(() => Object.values(selected.value).reduce((sum, item) => sum + Math.max(Number(item.original_price || item.price) - Number(item.price), 0), 0))
const priceVerificationSummary = computed(() => summarizePriceProvenance(Object.values(selected.value)))
const diyPriceVerificationLabel = computed(() => {
  const { total, verified } = priceVerificationSummary.value
  if (total === 0) return '选择配件后显示售价来源与核验覆盖。'
  if (verified === total) return `已选 ${total} 件配件均带完整核价来源；总价按当前售价计算。`
  if (verified === 0) return `已选 ${total} 件配件暂无可验证价格来源；总价仍按当前售价计算。`
  return `已选 ${total} 件中 ${verified} 件已核价，其余售价来源暂不可验证。`
})

const viewerParts = computed(() => steps.map((step, index) => {
  const product = selected.value[index]
  return {
    id: step.key,
    type: step.key,
    name: step.label,
    shortName: step.label.replace(/\s.+$/, ''),
    selected: Boolean(product),
    productId: product?.id || null,
    productName: product?.name || '',
    brand: product?.brand || '',
    specs: product?.specs || {},
    modelUrl: product?.model_3d_url || '',
    visible: true,
  }
}))

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

const categoryState = computed(() => {
  const state = categoryLoadStates.value[steps[currentStep.value].catId]
  if (!state || state === 'loading') return 'loading'
  if (state === 'error') return 'error'
  return filteredProducts.value.length ? 'success' : 'empty'
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

const compatibilitySummary = computed(() => {
  const warnings = compatibilityChecks.value.filter(check => check.level === 'warn').length
  const pending = compatibilityChecks.value.filter(check => check.level === 'pending').length
  if (warnings > 0) {
    return {
      label: `${warnings} 项兼容风险`,
      tone: 'warning',
      className: 'border-yellow-500/30 bg-yellow-500/10 text-yellow-300',
    }
  }
  if (pending > 0) {
    return {
      label: `${pending} 项待验证`,
      tone: 'info',
      className: 'border-dark-700 bg-dark-950 text-dark-400',
    }
  }
  return {
    label: '已选配置通过当前检查',
    tone: 'positive',
    className: 'border-primary-500/30 bg-primary-500/10 text-primary-300',
  }
})

const selectedPriceTarget = computed(() => selected.value[currentStep.value] || Object.values(selected.value)[0])
const priceHistoryHint = computed(() => {
  if (!selectedPriceTarget.value) return '选择一个配件后显示走势。'
  if (priceHistoryLoading.value) return '正在检查来源完整的价格记录。'
  if (priceHistoryError.value) return '历史价格暂时无法加载，请稍后重试。'
  if (priceHistory.value.length > 0 && priceHistorySource.value === 'database') {
    return `已找到 ${priceHistory.value.length} 条来源完整的平台核价记录。`
  }
  if (priceHistory.value.length > 0 && priceHistorySource.value === 'external-provider') {
    return `已找到 ${priceHistory.value.length} 条来源完整的外部行情记录。`
  }
  if (getPriceProvenance(selectedPriceTarget.value).isVerified) {
    return '当前售价已核验，但暂无来源完整的历史价格记录。'
  }
  return '当前售价来源尚未完成核验，暂无可验证的历史价格记录。'
})
const priceHistoryEmptyLabel = computed(() => {
  if (!selectedPriceTarget.value) return '选择配件后查看价格记录'
  if (priceHistoryLoading.value) return '正在加载价格记录'
  if (priceHistoryError.value) return '价格记录暂时不可用'
  return '暂无可验证的历史价格'
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

function stepIndexFromPart(part) {
  const raw = Array.isArray(part) ? part[0] : part
  const key = String(raw || '').trim().toLowerCase()
  const normalized = partAliases[key] || key
  const index = steps.findIndex(step => step.key === normalized)
  return index >= 0 ? index : 0
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

function isSelected(product) {
  return selected.value[currentStep.value]?.id === product.id
}

function selectItem(product) {
  selected.value[currentStep.value] = product
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
  priceHistorySource.value = 'unavailable'
  priceHistoryError.value = false
  currentStep.value = 0
}

function resetViewerCamera() {
  viewerResetKey.value += 1
}

function handleViewerFailure(failure) {
  clearViewerBudget()
  viewerFailure.value = getDiyViewerFailure(failure?.reason, failure)
  viewerState.value = 'failed'
  viewerRetryRequested.value = false
  viewerMode.value = 'list'
}

function handleViewerReady() {
  clearViewerBudget()
  const shouldOpenViewer = viewerRetryRequested.value
  viewerState.value = 'ready'
  viewerFailure.value = null
  viewerRetryRequested.value = false
  if (shouldOpenViewer) viewerMode.value = '3d'
}

function retryViewer() {
  if (viewerState.value === 'retrying') return
  viewerState.value = 'retrying'
  viewerRetryRequested.value = true
  viewerAttemptKey.value += 1
  startViewerBudget()
}

function startViewerBudget() {
  clearViewerBudget()
  viewerBudgetTimeoutId = window.setTimeout(() => {
    if (!['loading', 'retrying'].includes(viewerState.value)) return
    handleViewerFailure({
      reason: 'load-timeout',
      elapsedMs: DIY_VIEWER_LOAD_TIMEOUT_MS,
      stage: 'viewer-shell',
    })
  }, DIY_VIEWER_LOAD_TIMEOUT_MS)
}

function clearViewerBudget() {
  if (!viewerBudgetTimeoutId) return
  window.clearTimeout(viewerBudgetTimeoutId)
  viewerBudgetTimeoutId = undefined
}

function open3dMode() {
  if (viewerState.value === 'failed') {
    retryViewer()
    return
  }
  viewerMode.value = '3d'
}

function openListMode() {
  viewerMode.value = 'list'
  viewerRetryRequested.value = false
}

function buildConfigName() {
  const cpu = selected.value[0]?.model || selected.value[0]?.name || 'CPU 待定'
  const gpu = selected.value[1]?.model || selected.value[1]?.name || 'GPU 待定'
  return clipText(`胖虫 DIY 整机配置 · ${cpu} / ${gpu}`, 180)
}

function buildDiySnapshot() {
  const parts = steps.map((step, index) => {
    const product = selected.value[index]
    return {
      key: step.key,
      label: step.label,
      category_id: step.catId,
      product_id: product?.id || null,
      name: product?.name || '',
      brand: product?.brand || '',
      model: product?.model || '',
      price: Number(product?.price || 0),
      original_price: product?.original_price != null ? Number(product.original_price) : null,
      image_url: product?.image_url || '',
      model_3d_url: product?.model_3d_url || '',
      model_3d_scale: Number(product?.model_3d_scale || 1),
      model_3d_position: product?.model_3d_position || null,
      model_3d_rotation: product?.model_3d_rotation || null,
      asset_license: product?.asset_license || '',
      asset_source_url: product?.asset_source_url || '',
      specs: product?.specs || {},
    }
  })

  return {
    type: 'diy_pc',
    configuration_id: 'diy-pc',
    version: 1,
    created_at: new Date().toISOString(),
    parts,
    appearance: {
      variant_id: selectedVariant.value,
      variant_name: activeVariant.value?.name || '',
      material_id: selectedMaterial.value,
      material_name: activeMaterial.value?.name || '',
      camera_preset: cameraPreset.value,
      auto_rotate: autoRotate.value,
      price_diff: appearancePriceDiff.value,
      model_url: activeModelUrl.value,
    },
    metrics: {
      total_power_w: totalPower.value,
      psu_headroom_w: psuHeadroom.value,
      gpu_space_headroom_mm: gpuSpaceHeadroom.value,
      estimated_3dmark: estimated3DMark.value,
      compatibility: compatibilityChecks.value.map(check => ({
        key: check.key,
        title: check.title,
        level: check.level,
        message: check.message,
      })),
    },
    pricing: {
      parts_total: selectedPartsTotal.value,
      appearance_price_diff: appearancePriceDiff.value,
      saved_amount: savedAmount.value,
      total: totalPrice.value,
    },
  }
}

function buildOrderSpecs(snapshot) {
  const specs = {
    '配置类型': 'DIY 装机整机',
    '3D 外观': `${snapshot.appearance.variant_name} / ${snapshot.appearance.material_name}`,
  }

  snapshot.parts.forEach((part) => {
    specs[part.label] = part.brand ? `${part.brand} ${part.name}` : part.name
  })

  specs['估算功耗'] = `${snapshot.metrics.total_power_w}W`
  specs['电源冗余'] = psuHeadroomLabel.value
  specs['显卡空间'] = gpuSpaceLabel.value
  specs['3DMark'] = snapshot.metrics.estimated_3dmark.toLocaleString()
  if (snapshot.pricing.appearance_price_diff > 0) {
    specs['外观差价'] = `¥${money(snapshot.pricing.appearance_price_diff)}`
  }
  return specs
}

function buildConfigId(snapshot) {
  const raw = [
    snapshot.type,
    ...snapshot.parts.map(part => part.product_id || 'none'),
    snapshot.appearance.variant_id,
    snapshot.appearance.material_id,
  ].join('|')
  return `diy_${stableHash(raw)}`
}

function stableHash(text) {
  let hash = 0
  for (let i = 0; i < text.length; i += 1) {
    hash = ((hash << 5) - hash) + text.charCodeAt(i)
    hash |= 0
  }
  return Math.abs(hash).toString(36)
}

function clipText(text, limit) {
  return text.length > limit ? `${text.slice(0, limit - 1)}…` : text
}

async function addConfiguredItem(destination) {
  if (!isComplete.value) return
  const blocking = compatibilityChecks.value.filter(check => check.level === 'warn')
  if (blocking.length > 0) {
    notify.show(`存在兼容风险：${blocking[0].title}`, 'warning')
    return
  }

  const snapshot = buildDiySnapshot()
  cartStore.addCustomItem({
    id: buildConfigId(snapshot),
    name: buildConfigName(),
    brand: '胖虫',
    model: 'DIY 装机整机',
    description: '基于 DIY 装机配置器生成的整机定制快照',
    specs: buildOrderSpecs(snapshot),
    snapshot,
    custom_type: 'diy_pc',
    price: totalPrice.value,
    original_price: savedAmount.value > 0 ? totalPrice.value + savedAmount.value : null,
    image_url: selected.value[7]?.image_url || selected.value[1]?.image_url || fallbackImage,
    stock: 99,
  })

  notify.show('DIY 整机配置已作为一件定制商品加入购物车', 'success')
  router.push(destination)
}

async function addToCart() {
  return addConfiguredItem('/cart')
}

async function checkoutNow() {
  return addConfiguredItem('/checkout')
}

async function loadCategoryProducts(catId) {
  if (categoryLoadStates.value[catId] === 'success') return
  if (categoryRequests.has(catId)) return categoryRequests.get(catId)

  categoryLoadStates.value[catId] = 'loading'
  const request = (async () => {
    try {
      const res = await api.get('/products', { params: { category_id: catId, page: 1, page_size: 100, sort_by: 'price', sort_order: 'asc' } })
      allProducts.value[catId] = res?.items || []
      categoryLoadStates.value[catId] = 'success'
    } catch (e) {
      console.warn(`Failed to load category ${catId}:`, e)
      categoryLoadStates.value[catId] = 'error'
    } finally {
      categoryRequests.delete(catId)
    }
  })()
  categoryRequests.set(catId, request)
  return request
}

async function retryCurrentCategory() {
  const catId = steps[currentStep.value].catId
  await loadCategoryProducts(catId)
}

async function refreshPriceHistory() {
  const requestId = ++priceHistoryRequestId
  const target = selectedPriceTarget.value
  priceHistory.value = []
  priceHistorySource.value = 'unavailable'
  priceHistoryError.value = false
  if (!target) {
    priceHistoryLoading.value = false
    return
  }
  priceHistoryLoading.value = true
  priceHistoryError.value = false
  try {
    const res = await marketApi.getPriceHistory(target.id, 30)
    if (requestId !== priceHistoryRequestId) return
    const points = getTraceablePricePoints(res.points)
    priceHistory.value = points
    priceHistorySource.value = points.length > 0 ? (res.source || 'unavailable') : 'unavailable'
  } catch (e) {
    if (requestId !== priceHistoryRequestId) return
    console.warn('Failed to load price history:', e)
    priceHistory.value = []
    priceHistorySource.value = 'unavailable'
    priceHistoryError.value = true
  } finally {
    if (requestId === priceHistoryRequestId) priceHistoryLoading.value = false
  }
}

watch(currentStep, async (step) => {
  filters.keyword = ''
  filters.brand = ''
  filters.specValue = ''
  filters.sort = 'default'
  const catId = steps[step].catId
  await loadCategoryProducts(catId)
})

watch(() => selectedPriceTarget.value?.id, refreshPriceHistory)

watch(() => route.query.part, (part) => {
  const nextStep = stepIndexFromPart(part)
  if (nextStep !== currentStep.value) {
    currentStep.value = nextStep
  }
})

onMounted(async () => {
  if (viewerState.value === 'loading') startViewerBudget()
  await loadCategoryProducts(steps[currentStep.value].catId)
})

onBeforeUnmount(clearViewerBudget)
</script>

<style scoped>
@media (min-width: 640px) {
  .diy-config-row {
    grid-template-columns: 150px minmax(0, 1fr) 110px 72px;
  }
}
</style>
