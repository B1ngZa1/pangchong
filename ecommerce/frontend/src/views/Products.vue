<template>
  <div class="min-h-screen bg-dark-950">
    <div class="border-b border-dark-800 bg-dark-900 px-6 py-3 text-sm text-dark-400">
      <router-link to="/" class="transition-colors hover:text-primary-500">首页</router-link>
      <span class="mx-2">/</span>
      <span class="text-primary-500">{{ currentCategoryName }}</span>
    </div>

    <div class="mx-auto flex max-w-[1440px] flex-col lg:flex-row">
      <aside class="sticky top-16 hidden h-[calc(100vh-64px)] w-56 min-w-[224px] overflow-y-auto border-r border-dark-800 bg-dark-900 lg:block">
        <div class="p-4">
          <h3 class="mb-4 px-2 text-xs uppercase tracking-[0.18em] text-dark-500">产品分类</h3>

          <button
            :class="categoryClass(currentCatId === null)"
            @click="switchCategory(null)"
          >
            <span class="h-2 w-2 rounded-full bg-primary-500/80" />
            <span>全部商品</span>
          </button>

          <button
            v-for="cat in categories"
            :key="cat.id"
            :class="categoryClass(currentCatId === cat.id)"
            @click="switchCategory(cat.id)"
          >
            <span class="h-2 w-2 rounded-full" :class="currentCatId === cat.id ? 'bg-primary-500' : 'bg-dark-600'" />
            <span>{{ cat.name }}</span>
          </button>
        </div>
      </aside>

      <div class="sticky top-16 z-30 flex w-full gap-2 overflow-x-auto whitespace-nowrap border-b border-dark-800 bg-dark-900 px-4 py-2 lg:hidden">
        <button
          :class="mobileCatClass(currentCatId === null)"
          @click="switchCategory(null)"
        >
          全部
        </button>
        <button
          v-for="cat in categories"
          :key="cat.id"
          :class="mobileCatClass(currentCatId === cat.id)"
          @click="switchCategory(cat.id)"
        >
          {{ cat.name }}
        </button>
      </div>

      <section class="min-w-0 flex-1 px-4 py-8 sm:px-6 lg:px-8" aria-label="商品目录">
        <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-bold text-white lg:text-3xl">{{ currentCategoryName }}</h1>
            <p v-if="requestState === 'success' || requestState === 'empty'" class="mt-2 text-sm text-dark-400">共 {{ totalCount }} 件商品 · 找到适合你的性能之选</p>
            <p v-else-if="requestState === 'error'" class="mt-1 text-sm text-red-300">商品数据暂不可用</p>
          </div>
          <DsField
            v-model="sortBy"
            class="w-full sm:w-48"
            as="select"
            label="排序方式"
            :options="sortOptions"
            @update:model-value="changeSort"
          />
        </div>

        <div v-if="hasFilters" class="mb-6 flex flex-wrap items-center gap-3 text-sm">
          <span class="rounded-md border border-dark-700 bg-dark-900 px-3 py-2 text-dark-300">{{ activeFilterLabel }}</span>
          <button type="button" class="px-2 py-2 text-primary-400 hover:text-primary-300" @click="clearFilters">清除筛选</button>
        </div>

        <DsAsyncState
          :state="requestState"
          :error-description="requestError"
          empty-title="没有找到符合条件的商品"
          empty-description="试试其他关键词，或清除筛选继续浏览。"
          @retry="fetchProducts"
        >
          <template #action>
            <DsButton v-if="requestState === 'empty'" variant="secondary" size="sm" type="button" @click="clearFilters">
              查看全部商品
            </DsButton>
            <DsButton v-else-if="requestState === 'error'" variant="secondary" size="sm" type="button" @click="fetchProducts">
              重新加载
            </DsButton>
          </template>

          <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
          <DsProductCard
            v-for="product in products"
            :key="product.id"
            :product="product"
            :category-label="getCatName(product.category_id) || '未分类'"
            :fallback-image="getFallbackImage(product.category_id)"
            @select="$router.push(`/products/${product.slug}`)"
          >
            <template #actions="{ product: cardProduct }">
              <div class="flex shrink-0 gap-2" @click.stop>
                <DsButton variant="primary" size="sm" type="button" :loading="addingIds.has(cardProduct.id)" :disabled="cardProduct.stock <= 0" @click.stop="addToCart(cardProduct)">{{ cardProduct.stock <= 0 ? '暂时缺货' : '加入购物车' }}</DsButton>
                <DsButton variant="secondary" size="sm" type="button" @click.stop="$router.push(`/products/${cardProduct.slug}`)">详情</DsButton>
              </div>
            </template>
            <template #provenance="{ product: cardProduct }">
              <PriceProvenance :product="cardProduct" compact class="mt-3 border-t border-dark-800 pt-3" />
            </template>
          </DsProductCard>
          </div>
        </DsAsyncState>

        <DsPagination
          v-if="totalPages > 1"
          :page="page"
          class="mt-8"
          :total-pages="totalPages"
          :disabled="loading"
          @change="changePage"
        />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useCartStore, useNotifyStore } from '@/store'
import PriceProvenance from '@/components/PriceProvenance.vue'
import { DsAsyncState, DsButton, DsField, DsPagination, DsProductCard } from '@/design-system'
import { buildProductListParams, getCatalogQueryLabel, resolveCategoryId } from '@/utils/productCatalogFilters'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const notify = useNotifyStore()

const loading = ref(true)
const requestState = ref('loading')
const requestError = ref('')
const sortBy = ref('default')
const sortOptions = [
  { value: 'default', label: '默认排序' },
  { value: 'price-asc', label: '价格从低到高' },
  { value: 'price-desc', label: '价格从高到低' },
  { value: 'name', label: '按名称排序' },
]
const currentCatId = ref(null)
const categories = ref([])
const products = ref([])
const page = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const addingIds = ref(new Set())
let requestId = 0
let ready = false
const hasFilters = computed(() => Boolean(currentCatId.value || route.query.keyword || route.query.scene || route.query.tag))
const activeFilterLabel = computed(() => [currentCatId.value && getCatName(currentCatId.value), getCatalogQueryLabel(route.query)].filter(Boolean).join(' / '))

const FALLBACK_IMAGES = {
  default: '/assets/pangchong-product-fallback.png',
  'a1b2c3d4-e5f6-7890-abcd-ef1234567890': '/assets/pangchong-product-fallback.png',
  'b2c3d4e5-f6a7-8901-bcde-f12345678901': '/assets/pangchong-product-fallback.png',
  'c3d4e5f6-a7b8-9012-cdef-123456789012': '/assets/pangchong-hero.png'
}

const currentCategoryName = computed(() => {
  if (currentCatId.value) {
    const cat = categories.value.find(c => c.id === currentCatId.value)
    if (cat) return cat.name
  }

  return getCatalogQueryLabel(route.query) || '全部商品'
})

function categoryClass(active) {
  return [
    'mb-1 flex w-full items-center gap-3 rounded-md border-l-2 px-3 py-2.5 text-left text-sm transition-colors',
    active
      ? 'border-primary-500 bg-primary-500/10 text-primary-500'
      : 'border-transparent text-dark-300 hover:bg-white/[0.02] hover:text-white'
  ]
}

function mobileCatClass(active) {
  return [
    'shrink-0 rounded-full px-4 py-2 text-xs transition-colors',
    active
      ? 'bg-primary-500 font-semibold text-dark-950'
      : 'bg-dark-800 text-dark-300'
  ]
}

function getCatName(catId) {
  const c = categories.value.find(x => x.id === catId)
  return c ? c.name : ''
}

function getFallbackImage(catId) {
  return FALLBACK_IMAGES[catId] || FALLBACK_IMAGES.default
}

async function addToCart(product) {
  if (addingIds.value.has(product.id) || product.stock <= 0) return
  addingIds.value.add(product.id)
  try {
    await cartStore.addToCart(product.id, 1)
    notify.show(`已将「${product.name}」加入购物车`, 'success')
  } catch (e) {
    notify.show(`添加失败：${e.displayMessage || e.message || '请重试'}`, 'error')
  } finally {
    addingIds.value.delete(product.id)
  }
}

function switchCategory(catId) {
  const { category, page: oldPage, scene, tag, ...rest } = route.query
  const cat = categories.value.find(item => item.id === catId)
  router.push({ path: '/products', query: { ...rest, ...(catId ? { category: cat?.slug || catId } : {}) } })
}

function clearFilters() {
  router.push({ path: '/products', query: sortBy.value === 'default' ? {} : { sort: sortBy.value } })
}

function changeSort(value) {
  router.push({ query: { ...route.query, sort: value === 'default' ? undefined : value, page: undefined } })
}

function changePage(value) {
  router.push({ query: { ...route.query, page: value > 1 ? value : undefined } })
}

function syncCategoryFromRoute() {
  currentCatId.value = resolveCategoryId(route.query.category, categories.value)
  sortBy.value = sortOptions.some(option => option.value === route.query.sort) ? route.query.sort : 'default'
  const requestedPage = Number(route.query.page)
  page.value = Number.isSafeInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1
}

async function fetchCategories() {
  try {
    const res = await api.get('/products/categories')
    categories.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.warn('fetchCategories unavailable:', e)
  }
}

async function fetchProducts() {
  const currentRequest = ++requestId
  loading.value = true
  requestState.value = 'loading'
  requestError.value = ''
  try {
    const params = buildProductListParams({
      page: page.value,
      currentCatId: currentCatId.value,
      query: route.query
    })
    if (sortBy.value === 'price-asc' || sortBy.value === 'price-desc') {
      params.sort_by = 'price'
      params.sort_order = sortBy.value === 'price-asc' ? 'asc' : 'desc'
    } else if (sortBy.value === 'name') {
      params.sort_by = 'name'
      params.sort_order = 'asc'
    }
    const res = await api.get('/products', { params })
    if (currentRequest !== requestId) return
    products.value = res?.items || []
    totalPages.value = res?.pages || 1
    totalCount.value = res?.total || 0
    if (page.value > totalPages.value) {
      router.replace({ query: { ...route.query, page: totalPages.value > 1 ? totalPages.value : undefined } })
      return
    }
    requestState.value = products.value.length ? 'success' : 'empty'
  } catch (e) {
    if (currentRequest !== requestId) return
    products.value = []
    totalPages.value = 1
    requestError.value = '商品服务暂时不可用，请检查网络后重试。'
    requestState.value = 'error'
    notify.show('商品加载失败，请稍后重试', 'error')
  } finally {
    if (currentRequest === requestId) loading.value = false
  }
}

watch(() => route.query, () => {
  if (!ready) return
  syncCategoryFromRoute()
  fetchProducts()
})

onMounted(async () => {
  await fetchCategories()
  ready = true
  syncCategoryFromRoute()
  await fetchProducts()
})
onBeforeUnmount(() => { requestId++; ready = false })
</script>
