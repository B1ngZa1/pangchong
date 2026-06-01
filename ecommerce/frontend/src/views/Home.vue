<template>
  <div>
    <section class="relative overflow-hidden border-b border-dark-800">
      <img
        :src="heroImage"
        alt="high performance gaming setup"
        class="absolute inset-0 h-full w-full object-cover"
      >
      <div class="absolute inset-0 bg-[linear-gradient(110deg,rgba(2,6,23,0.92),rgba(2,6,23,0.72)_48%,rgba(2,6,23,0.88))]" />
      <div class="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="max-w-2xl">
          <p class="mb-4 text-xs font-semibold uppercase tracking-[0.24em] text-primary-400">PANGCHONG PERFORMANCE LAB</p>
          <h1 class="text-4xl font-bold leading-tight text-white md:text-6xl">
            极致性能
            <span class="block text-primary-500">由你定义</span>
          </h1>
          <p class="mt-6 max-w-xl text-base leading-7 text-dark-300 md:text-lg">
            胖虫科技专注高性能整机与 DIY 装机定制。我们提供蓝天准系统、主流一线配件和专业调校服务，帮助你稳定释放每一瓦性能。
          </p>
          <div class="mt-8 flex flex-col gap-3 sm:flex-row">
            <router-link to="/products" class="btn-primary px-7 py-3.5 text-base">探索产品</router-link>
            <router-link to="/diy" class="btn-outline px-7 py-3.5 text-base">立即定制</router-link>
          </div>
        </div>

        <div class="mt-14 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div v-for="stat in stats" :key="stat.label" class="rounded-lg border border-dark-700/80 bg-dark-900/60 p-4 backdrop-blur">
            <p class="text-2xl font-bold text-primary-500">{{ stat.value }}</p>
            <p class="mt-1 text-xs text-dark-400">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="border-b border-dark-800 bg-dark-900">
      <div class="mx-auto grid max-w-7xl grid-cols-1 gap-3 px-4 py-5 text-sm text-dark-300 sm:grid-cols-2 sm:px-6 lg:grid-cols-5 lg:px-8">
        <span v-for="point in trustPoints" :key="point" class="inline-flex items-center gap-2">
          <span class="inline-block h-1.5 w-1.5 rounded-full bg-primary-500" />
          {{ point }}
        </span>
      </div>
    </section>

    <section class="py-14 sm:py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mb-8 flex items-end justify-between">
          <div>
            <h2 class="text-2xl font-bold text-white sm:text-3xl">热门产品</h2>
            <p class="mt-2 text-sm text-dark-400">经过压力测试与稳定性验证的推荐机型</p>
          </div>
          <router-link to="/products" class="hidden text-sm text-primary-500 transition-colors hover:text-primary-400 sm:block">查看全部</router-link>
        </div>

        <div v-if="loading" class="flex justify-center py-12">
          <div class="h-11 w-11 animate-spin rounded-full border-b-2 border-t-2 border-primary-500" />
        </div>

        <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <router-link
            v-for="product in hotProducts"
            :key="product.id"
            :to="`/products/${product.slug}`"
            class="card group"
          >
            <div class="relative aspect-[4/3] overflow-hidden bg-dark-900">
              <img
                :src="product.image_url || fallbackImage"
                :alt="product.name"
                loading="lazy"
                class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
              >
              <span class="absolute left-3 top-3 rounded border border-primary-500/60 bg-dark-950/70 px-2 py-1 text-[11px] font-medium text-primary-400">热销</span>
            </div>
            <div class="p-4">
              <h3 class="line-clamp-2 text-sm font-medium text-white transition-colors group-hover:text-primary-400">
                {{ product.name }}
              </h3>
              <div class="mt-3 flex items-center justify-between">
                <div>
                  <span class="text-lg font-semibold text-primary-500">¥{{ Number(product.price).toLocaleString() }}</span>
                  <span v-if="product.original_price" class="ml-2 text-xs text-dark-500 line-through">¥{{ Number(product.original_price).toLocaleString() }}</span>
                </div>
                <span class="text-xs text-dark-500">已售 {{ product.sold_count }}</span>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { productApi } from '@/api'

const loading = ref(false)
const hotProducts = ref([])

const heroImage = '/assets/pangchong-hero.png'
const fallbackImage = '/assets/pangchong-product-fallback.png'

const stats = [
  { value: '50,000+', label: '累计服务用户' },
  { value: '99%', label: '好评率' },
  { value: '3 年', label: '整机质保' },
  { value: '72h', label: '出厂压力测试' }
]

const trustPoints = [
  '蓝天 Clevo 授权合作',
  '专业散热与电压调校',
  '全国联保与远程支持',
  '顺丰安全运输',
  '1 对 1 售后服务'
]

onMounted(async () => {
  loading.value = true
  try {
    hotProducts.value = await productApi.getHotProducts(8)
  } catch (error) {
    console.error('获取热门商品失败:', error)
  } finally {
    loading.value = false
  }
})
</script>
