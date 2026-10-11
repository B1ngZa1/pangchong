<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="mx-auto max-w-7xl px-4">
      <nav aria-label="面包屑" class="mb-6 flex items-center gap-2 text-sm text-dark-400">
        <router-link to="/" class="hover:text-primary-400">首页</router-link>
        <span aria-hidden="true">/</span>
        <router-link to="/products" class="hover:text-primary-400">全部商品</router-link>
        <span aria-hidden="true">/</span>
        <span class="truncate text-dark-200">{{ product?.name || '商品详情' }}</span>
      </nav>
      <DsAsyncState :state="productState" loading-label="正在加载商品详情" empty-title="商品不存在或已下架" empty-description="返回商品目录，继续浏览其他配置。" error-title="商品详情加载失败" error-description="商品服务暂时不可用，请重试或返回商品目录。" retry-label="重试加载" @retry="loadProduct">
      <template #action>
        <DsButton v-if="productState === 'error'" variant="secondary" @click="loadProduct">重试加载</DsButton>
        <router-link v-else to="/products" class="btn-primary">返回商品目录</router-link>
      </template>
      <div class="grid grid-cols-1 gap-10 lg:grid-cols-2 lg:gap-12">
        <section class="self-start overflow-hidden rounded-lg border border-dark-800 bg-dark-900 lg:sticky lg:top-24">
          <div class="aspect-square overflow-hidden bg-dark-900">
            <img :src="mainImage" :alt="product.name" class="h-full w-full object-cover" @error="handleImageError">
          </div>
        </section>

        <section class="min-w-0">
          <h1 class="text-3xl font-bold text-white">{{ product.name }}</h1>
          <p class="mt-2 text-dark-400">{{ product.brand }} {{ product.model }}</p>

          <div class="mt-6 flex flex-wrap items-baseline gap-4">
            <span class="text-4xl font-bold text-primary-500">¥{{ Number(product.price).toLocaleString() }}</span>
            <span v-if="discount" class="text-xl text-dark-500 line-through">¥{{ Number(product.original_price).toLocaleString() }}</span>
            <span v-if="discount" class="inline-flex rounded border border-red-400/45 bg-dark-900 px-2 py-1 text-xs text-red-300">-{{ discount }}%</span>
          </div>

          <PriceProvenance :product="product" class="mt-5" />

          <p class="mt-6 leading-relaxed text-dark-300">{{ product.description || '高性能整机与配件，支持定制化选择。' }}</p>

          <div v-if="product.specs" class="mt-8 grid grid-cols-2 gap-3">
            <div v-for="(val, key) in product.specs" :key="key" class="min-w-0 break-words rounded-lg border border-dark-700 bg-dark-900 p-3">
              <span class="text-sm text-dark-400">{{ key }}</span>
              <p class="mt-1 text-sm font-medium text-white">{{ val }}</p>
            </div>
          </div>

          <div class="mt-8 flex flex-wrap items-center gap-4">
            <span class="text-dark-400">数量</span>
            <div class="flex items-center overflow-hidden rounded-md border border-dark-700 bg-dark-900">
              <DsIconButton label="减少数量" size="sm" :disabled="quantity <= 1" @click="quantity = Math.max(1, quantity - 1)">−</DsIconButton>
              <span class="min-w-[3rem] px-4 py-2 text-center text-white">{{ quantity }}</span>
              <DsIconButton label="增加数量" size="sm" :disabled="quantity >= Math.min(99, product.stock)" @click="quantity = Math.min(99, Math.min(product.stock, quantity + 1))">＋</DsIconButton>
            </div>
            <span class="text-sm text-dark-500">库存 {{ product.stock }} 件</span>
          </div>

          <div class="mt-8 flex flex-col gap-3 sm:flex-row">
            <DsButton block :loading="adding" :disabled="product.stock <= 0" @click="addToCart">加入购物车</DsButton>
            <DsButton block variant="secondary" :loading="adding" :disabled="product.stock <= 0" @click="buyNow">立即购买</DsButton>
          </div>
        </section>
      </div>
      </DsAsyncState>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore, useNotifyStore } from '@/store'
import api from '@/api'
import PriceProvenance from '@/components/PriceProvenance.vue'
import { DsAsyncState, DsButton, DsIconButton } from '@/design-system'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const notify = useNotifyStore()

const product = ref(null)
const productState = ref('loading')
const quantity = ref(1)
const adding = ref(false)
let loadRequest = 0

const fallbackImage = '/assets/pangchong-product-fallback.png'

const discount = computed(() => {
  if (Number(product.value?.original_price) > Number(product.value?.price)) {
    return Math.round((1 - product.value.price / product.value.original_price) * 100)
  }
  return 0
})

const mainImage = computed(() => {
  return product.value?.image_url || fallbackImage
})

function handleImageError(event) {
  if (event.target.src.endsWith(fallbackImage)) return
  event.target.src = fallbackImage
}

const addToCart = async () => {
  if (!product.value || adding.value) return false
  if (product.value.stock <= 0) {
    notify.show('当前商品库存不足', 'warning')
    return false
  }

  adding.value = true
  try {
    await cartStore.addToCart(product.value.id, quantity.value)
    notify.show('已添加到购物车', 'success')
    return true
  } catch (e) {
    notify.show(`添加失败：${e.displayMessage || e.response?.data?.detail || e.message}`, 'error')
    return false
  } finally {
    adding.value = false
  }
}

const buyNow = async () => {
  const success = await addToCart()
  if (success) router.push('/cart')
}

async function loadProduct() {
  const currentRequest = ++loadRequest
  productState.value = 'loading'
  quantity.value = 1
  try {
    const slug = route.params.slug
    const res = await api.get(`/products/slug/${slug}`)
    if (currentRequest !== loadRequest) return
    product.value = res?.data || res
    productState.value = product.value ? 'success' : 'empty'
  } catch (e) {
    if (currentRequest !== loadRequest) return
    product.value = null
    productState.value = e.response?.status === 404 ? 'empty' : 'error'
  }
}

watch(() => route.params.slug, loadProduct, { immediate: true })
onBeforeUnmount(() => { loadRequest++ })
</script>
