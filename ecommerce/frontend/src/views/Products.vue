<template>
  <div class="min-h-screen bg-dark-950">
    <div class="border-b border-dark-800 bg-dark-900 px-6 py-3 text-sm text-dark-400">
      <router-link to="/" class="transition-colors hover:text-primary-500">首页</router-link>
      <span class="mx-2">/</span>
      <span class="text-primary-500">{{ currentCategoryName }}</span>
    </div>

    <div class="flex flex-col lg:flex-row">
      <aside class="sticky top-20 hidden h-[calc(100vh-80px)] w-64 min-w-[256px] overflow-y-auto border-r border-dark-800 bg-dark-900 lg:block">
        <div class="p-4">
          <h3 class="mb-4 px-2 text-xs uppercase tracking-[0.18em] text-dark-500">产品分类</h3>

          <button
            :class="categoryClass(currentCatId === null)"
            @click="switchCategory(null)"
          >
            <span class="h-2 w-2 rounded-full bg-primary-500/80" />
            <span>全部商品</span>
            <span class="ml-auto rounded-full bg-white/5 px-2 py-0.5 text-xs text-dark-500">{{ totalCount }}</span>
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

      <main class="flex-1 p-6 lg:p-8 lg:pt-6">
        <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-bold text-white lg:text-3xl">{{ currentCategoryName }}</h1>
            <p class="mt-1 text-sm text-dark-500">共 {{ products.length }} 件商品</p>
          </div>
          <select v-model="sortBy" class="rounded-lg border border-dark-700 bg-dark-900 px-3 py-2 text-sm text-dark-300 outline-none focus:border-primary-500">
            <option value="default">默认排序</option>
            <option value="price-asc">价格从低到高</option>
            <option value="price-desc">价格从高到低</option>
            <option value="name">按名称排序</option>
          </select>
        </div>

        <div v-if="loading" class="flex justify-center py-20">
          <div class="h-12 w-12 animate-spin rounded-full border-b-2 border-t-2 border-primary-500" />
        </div>

        <div v-else-if="products.length === 0" class="rounded-lg border border-dark-800 bg-dark-900 p-10 text-center">
          <p class="text-dark-400">当前分类暂无商品，请切换其他分类查看。</p>
        </div>

        <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          <article
            v-for="product in sortedProducts"
            :key="product.id"
            class="group cursor-pointer overflow-hidden rounded-lg border border-dark-800 bg-dark-900 transition-all duration-300 hover:-translate-y-0.5 hover:border-primary-500/65 hover:shadow-[0_12px_40px_rgba(0,0,0,0.36)]"
            @click="$router.push(`/products/${product.slug}`)"
          >
            <div class="relative aspect-[4/3] overflow-hidden bg-dark-800">
              <img
                :src="product.image_url || getFallbackImage(product.category_id)"
                :alt="product.name"
                loading="lazy"
                class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
                @error="handleImageError($event, product.category_id)"
              >
              <span v-if="product.is_featured" class="absolute left-3 top-3 rounded border border-primary-500/60 bg-dark-950/75 px-2 py-1 text-[11px] font-medium text-primary-400">推荐</span>
              <span v-if="isDiscounted(product)" class="absolute right-3 top-3 rounded border border-red-400/45 bg-dark-950/75 px-2 py-1 text-[11px] font-medium text-red-300">特惠</span>
            </div>
            <div class="p-4">
              <p class="mb-1 text-[11px] uppercase tracking-[0.16em] text-primary-500">{{ getCatName(product.category_id) || '未分类' }}</p>
              <h3 class="mb-2 line-clamp-2 text-sm font-semibold text-white transition-colors group-hover:text-primary-400">{{ product.name }}</h3>
              <p class="mb-3 line-clamp-2 text-xs text-dark-500">{{ product.description || '高性能整机与配件，支持定制。' }}</p>
              <div v-if="product.specs" class="mb-3 flex flex-wrap gap-1.5">
                <span v-for="(val, key) in firstSpecs(product.specs)" :key="key" class="rounded bg-white/5 px-2 py-0.5 text-[11px] text-dark-300">{{ val }}</span>
              </div>
              <div class="flex items-center justify-between">
                <div>
                  <span class="text-lg font-semibold text-primary-500">¥{{ Number(product.price).toLocaleString() }}</span>
                  <span v-if="isDiscounted(product)" class="ml-2 text-xs text-dark-600 line-through">¥{{ Number(product.original_price).toLocaleString() }}</span>
                </div>
                <div class="flex gap-2">
                  <button class="rounded-md border border-primary-500 px-3 py-1.5 text-xs font-semibold text-primary-500 transition-all hover:bg-primary-500 hover:text-dark-950" @click.stop="addToCart(product)">加入购物车</button>
                  <button class="rounded-md border border-dark-600 px-3 py-1.5 text-xs font-semibold text-dark-300 transition-all hover:border-primary-500 hover:text-primary-400" @click.stop="$router.push(`/products/${product.slug}`)">详情</button>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-if="totalPages > 1" class="mt-8 flex justify-center gap-2">
          <button
            v-for="p in totalPages"
            :key="p"
            @click="page = p; fetchProducts()"
            :class="[
              'rounded-md px-4 py-2 text-sm transition-colors',
              page === p ? 'bg-primary-500 font-semibold text-dark-950' : 'bg-dark-800 text-dark-300 hover:bg-dark-700'
            ]"
          >
            {{ p }}
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import { useCartStore, useNotifyStore } from '@/store'
import { buildProductListParams, getCatalogQueryLabel, resolveCategoryId } from '@/utils/productCatalogFilters'

const route = useRoute()
const cartStore = useCartStore()
const notify = useNotifyStore()

const loading = ref(true)
const sortBy = ref('default')
const currentCatId = ref(null)
const categories = ref([])
const products = ref([])
const page = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

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

const sortedProducts = computed(() => {
  const items = [...products.value]
  if (sortBy.value === 'price-asc') items.sort((a, b) => Number(a.price) - Number(b.price))
  else if (sortBy.value === 'price-desc') items.sort((a, b) => Number(b.price) - Number(a.price))
  else if (sortBy.value === 'name') items.sort((a, b) => a.name.localeCompare(b.name))
  return items
})

function categoryClass(active) {
  return [
    'mb-1 flex w-full items-center gap-3 rounded-md border-l-2 px-3 py-2.5 text-left text-sm transition-all',
    active
      ? 'border-primary-500 bg-primary-500/10 text-primary-500'
      : 'border-transparent text-dark-300 hover:bg-white/[0.02] hover:text-white'
  ]
}

function mobileCatClass(active) {
  return [
    'shrink-0 rounded-full px-4 py-2 text-xs transition-all',
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

function handleImageError(event, catId) {
  const fallback = getFallbackImage(catId)
  if (event.target.src.endsWith(fallback)) return
  event.target.src = fallback
}

function firstSpecs(specs) {
  if (!specs || typeof specs !== 'object') return {}
  const keys = Object.keys(specs).slice(0, 4)
  const result = {}
  keys.forEach(k => { result[k] = specs[k] })
  return result
}

function isDiscounted(product) {
  return product.original_price && Number(product.original_price) > Number(product.price)
}

async function addToCart(product) {
  try {
    await cartStore.addToCart(product.id, 1)
    notify.show(`已将「${product.name}」加入购物车`, 'success')
  } catch (e) {
    notify.show(`添加失败：${e.displayMessage || e.message || '请重试'}`, 'error')
  }
}

function switchCategory(catId) {
  currentCatId.value = catId
  page.value = 1
  fetchProducts()
}

function syncCategoryFromRoute() {
  currentCatId.value = resolveCategoryId(route.query.category, categories.value)
}

async function fetchCategories() {
  try {
    const res = await api.get('/products/categories')
    categories.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.error('fetchCategories error:', e)
  }
}

async function fetchProducts() {
  loading.value = true
  try {
    const params = buildProductListParams({
      page: page.value,
      currentCatId: currentCatId.value,
      query: route.query
    })
    const res = await api.get('/products', { params })
    products.value = res?.items || []
    totalPages.value = res?.pages || 1
    if (!currentCatId.value) totalCount.value = res?.total || 0
  } catch (e) {
    console.error('fetchProducts error:', e)
    products.value = []
    notify.show('商品加载失败，请稍后重试', 'error')
  } finally {
    loading.value = false
  }
}

watch(() => [
  route.query.keyword,
  route.query.tag,
  route.query.scene,
  route.query.category
], () => {
  syncCategoryFromRoute()
  page.value = 1
  fetchProducts()
})

onMounted(async () => {
  await fetchCategories()
  syncCategoryFromRoute()
  await fetchProducts()
})
</script>
