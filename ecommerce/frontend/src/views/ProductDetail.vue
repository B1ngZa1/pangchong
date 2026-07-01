<template>
  <div class="min-h-screen bg-dark-950 py-8">
    <div class="mx-auto max-w-7xl px-4">
      <div v-if="loading" class="py-20 text-center text-dark-400">加载中...</div>
      <div v-else-if="!product" class="py-20 text-center text-dark-400">商品不存在或已下架</div>
      <div v-else class="grid grid-cols-1 gap-10 lg:grid-cols-2 lg:gap-12">
        <section class="overflow-hidden rounded-lg border border-dark-800 bg-dark-900">
          <div class="aspect-square overflow-hidden bg-dark-900">
            <img :src="mainImage" :alt="product.name" class="h-full w-full object-cover" @error="handleImageError">
          </div>
        </section>

        <section>
          <h1 class="text-3xl font-bold text-white">{{ product.name }}</h1>
          <p class="mt-2 text-dark-400">{{ product.brand }} {{ product.model }}</p>

          <div class="mt-6 flex items-baseline gap-4">
            <span class="text-4xl font-bold text-primary-500">¥{{ Number(product.price).toLocaleString() }}</span>
            <span v-if="product.original_price" class="text-xl text-dark-500 line-through">¥{{ Number(product.original_price).toLocaleString() }}</span>
            <span v-if="discount" class="inline-flex rounded border border-red-400/45 bg-dark-900 px-2 py-1 text-xs text-red-300">-{{ discount }}%</span>
          </div>

          <p class="mt-6 leading-relaxed text-dark-300">{{ product.description || '高性能整机与配件，支持定制化选择。' }}</p>

          <div v-if="product.specs" class="mt-8 grid grid-cols-2 gap-3">
            <div v-for="(val, key) in product.specs" :key="key" class="rounded-lg border border-dark-700 bg-dark-900 p-3">
              <span class="text-sm text-dark-400">{{ key }}</span>
              <p class="mt-1 text-sm font-medium text-white">{{ val }}</p>
            </div>
          </div>

          <div class="mt-8 flex items-center gap-4">
            <span class="text-dark-400">数量</span>
            <div class="flex items-center overflow-hidden rounded-md border border-dark-700 bg-dark-900">
              <button @click="quantity = Math.max(1, quantity - 1)" class="px-4 py-2 text-dark-300 transition-colors hover:text-primary-500">-</button>
              <span class="min-w-[3rem] px-4 py-2 text-center text-white">{{ quantity }}</span>
              <button @click="quantity = Math.min(99, Math.min(product.stock, quantity + 1))" class="px-4 py-2 text-dark-300 transition-colors hover:text-primary-500">+</button>
            </div>
            <span class="text-sm text-dark-500">库存 {{ product.stock }} 件</span>
          </div>

          <div class="mt-8 flex gap-4">
            <button @click="addToCart" class="btn-primary flex-1 py-3.5 text-base" :disabled="adding || product.stock <= 0">
              {{ adding ? '添加中...' : '加入购物车' }}
            </button>
            <button @click="buyNow" class="btn-outline flex-1 py-3.5 text-base" :disabled="adding || product.stock <= 0">立即购买</button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore, useNotifyStore } from '@/store'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const notify = useNotifyStore()

const product = ref(null)
const loading = ref(true)
const quantity = ref(1)
const adding = ref(false)

const fallbackImage = '/assets/pangchong-product-fallback.png'

const discount = computed(() => {
  if (product.value?.original_price && product.value.original_price > 0) {
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
  if (!product.value) return false
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

onMounted(async () => {
  try {
    const slug = route.params.slug
    const res = await api.get(`/products/slug/${slug}`)
    product.value = res?.data || res
  } catch (e) {
    console.error(e)
    notify.show('商品加载失败，请稍后重试', 'error')
  } finally {
    loading.value = false
  }
})
</script>
