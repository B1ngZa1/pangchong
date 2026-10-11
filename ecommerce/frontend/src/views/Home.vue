<template>
  <div class="home-page">
    <section data-qa="home-hero" class="hero-section" aria-labelledby="hero-title">
      <img
        :src="heroImage"
        alt="黑色工作台上的高性能台式电脑和笔记本"
        class="hero-media"
        fetchpriority="high"
        width="1536"
        height="1024"
      >
      <div class="hero-scrim" aria-hidden="true" />

      <div class="hero-shell">
        <div class="hero-copy">
          <h1 id="hero-title">极致性能<br><span>由你定义</span></h1>
          <p class="hero-lead">
            从第一颗处理器，到属于你的整台电脑。精选性能整机，自由搭配一线配件，让每一份预算都用在热爱上。
          </p>
          <div class="hero-actions">
            <router-link to="/products" class="hero-btn hero-btn--primary">
              探索产品
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            </router-link>
            <router-link to="/diy" class="hero-btn hero-btn--secondary">
              立即定制
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <section class="category-rail" aria-label="快捷选购">
      <div class="section-shell category-grid">
        <router-link v-for="category in categories" :key="category.label" :to="category.to" class="category-link">
          <div>
            <strong>{{ category.label }}</strong>
            <p>{{ category.description }}</p>
          </div>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
        </router-link>
      </div>
    </section>

    <section class="featured-section" aria-labelledby="featured-title">
      <div class="section-shell">
        <div class="section-head">
          <div>
            <p class="section-label">精选系列</p>
            <h2 id="featured-title">热门产品</h2>
            <p>从日常高效到全力以赴，找到你的下一台电脑。</p>
          </div>
          <router-link to="/products" class="section-link">
            查看全部
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
          </router-link>
        </div>

        <DsAsyncState
          :state="featuredState"
          loading-label="正在加载热门产品"
          empty-title="暂时没有热门产品"
          empty-description="可以先浏览全部产品，或稍后重试。"
          error-title="热门产品加载失败"
          error-description="商品服务暂时不可用；你仍可以浏览 DIY 配件和服务支持。"
          retry-label="重试加载"
          @retry="loadFeaturedProducts"
        >
          <div class="product-grid">
            <DsProductCard
              v-for="product in hotProducts"
              :key="product.id"
              :product="product"
              :fallback-image="fallbackImage"
              @select="$router.push(`/products/${product.slug}`)"
            >
              <template #actions>
                <router-link :to="`/products/${product.slug}`" class="product-detail-link" @click.stop>
                  查看详情 <span aria-hidden="true">↗</span>
                </router-link>
              </template>
            </DsProductCard>
          </div>
        </DsAsyncState>
      </div>
    </section>

    <section class="trust-rail" aria-label="选购与服务">
      <div class="section-shell trust-grid">
        <div v-for="point in trustPoints" :key="point.title" class="trust-item">
          <span aria-hidden="true" />
          <div>
            <strong>{{ point.title }}</strong>
            <p>{{ point.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="build-section" aria-labelledby="build-title">
      <div class="section-shell build-shell">
        <div>
          <h2 id="build-title">好电脑，从你的想法开始。</h2>
          <p>挑选配件、查看兼容性、预览整机外观。你的下一台电脑，由你亲手定义。</p>
        </div>
        <router-link to="/diy" class="hero-btn hero-btn--primary">
          开始我的装机
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { productApi } from '@/api'
import { DsAsyncState, DsProductCard } from '@/design-system'

const featuredState = ref('loading')
const hotProducts = ref([])

const heroImage = '/assets/pangchong-hero-v2.jpg'
const fallbackImage = '/assets/pangchong-product-fallback.png'

const categories = [
  { label: '游戏本', description: '随时开启下一场', to: '/products?category=gaming-laptop' },
  { label: '台式主机', description: '给热爱更多性能', to: '/products?category=desktop' },
  { label: '轻薄办公', description: '轻装上阵，高效随行', to: '/products?category=thin-laptop' },
  { label: 'DIY 装机', description: '每一处，都合你心意', to: '/diy' }
]

const trustPoints = [
  { title: '自由搭配', description: '按用途与预算挑选配件' },
  { title: '兼容提示', description: '选件时同步查看搭配建议' },
  { title: '价格明细', description: '配置清单与费用清晰呈现' },
  { title: '服务支持', description: '配送、保修、技术帮助一站查阅' }
]

async function loadFeaturedProducts() {
  featuredState.value = 'loading'
  try {
    hotProducts.value = await productApi.getHotProducts(4)
    featuredState.value = hotProducts.value.length ? 'success' : 'empty'
  } catch {
    hotProducts.value = []
    featuredState.value = 'error'
  }
}

onMounted(loadFeaturedProducts)
</script>

<style scoped>
.home-page { min-height: 100vh; overflow-x: clip; background: var(--pc-color-semantic-background-canvas); }
.hero-section { position: relative; min-height: min(690px, calc(100vh - 72px)); overflow: hidden; background: #05070b; }
.hero-media, .hero-scrim { position: absolute; inset: 0; width: 100%; height: 100%; }
.hero-media { object-fit: cover; object-position: center; }
.hero-scrim { background: linear-gradient(90deg, #05070b 0%, rgb(5 7 11 / 0.92) 28%, rgb(5 7 11 / 0.28) 59%, rgb(5 7 11 / 0.08) 100%); }
.section-shell, .hero-shell { width: min(1280px, calc(100% - 64px)); margin: 0 auto; }
.hero-shell { position: relative; z-index: 1; display: flex; min-height: min(690px, calc(100vh - 72px)); align-items: center; padding: 64px 0; }
.hero-copy { max-width: 610px; }
.hero-copy h1 { margin: 0; color: #f5f7f8; font-size: clamp(52px, 6.2vw, 80px); font-weight: 750; letter-spacing: -0.07em; line-height: 1.02; }
.hero-copy h1 span { color: var(--pc-color-semantic-action-primary); }
.hero-lead { max-width: 470px; margin: 30px 0 0; color: rgb(var(--pc-color-dark-50-rgb) / 0.76); font-size: 17px; line-height: 1.8; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 36px; }
.hero-btn { display: inline-flex; min-width: 160px; min-height: 50px; align-items: center; justify-content: center; gap: 10px; border: 1px solid transparent; border-radius: 8px; font-size: 15px; font-weight: 750; transition: transform var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), background-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), border-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard); }
.hero-btn:hover { transform: translateY(-1px); }
.hero-btn svg, .section-link svg, .category-link svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2; }
.hero-btn--primary { background: var(--pc-color-semantic-action-primary); color: var(--pc-color-semantic-text-inverse); }
.hero-btn--primary:hover { background: var(--pc-color-brand-600); }
.hero-btn--secondary { border-color: rgb(var(--pc-color-dark-50-rgb) / 0.24); background: rgb(5 7 11 / 0.18); color: var(--pc-color-semantic-text-primary); }
.hero-btn--secondary:hover { border-color: rgb(var(--pc-color-dark-50-rgb) / 0.52); }
.hero-btn:focus-visible, .category-link:focus-visible, .section-link:focus-visible, .product-detail-link:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 4px; }
.category-rail { border-bottom: 1px solid var(--pc-color-semantic-border-subtle); background: #090c11; }
.category-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); }
.category-link { display: flex; min-height: 104px; align-items: center; justify-content: space-between; gap: 16px; padding: 20px 24px; border-right: 1px solid var(--pc-color-semantic-border-subtle); color: var(--pc-color-semantic-text-primary); transition: background-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard); }
.category-link:first-child { padding-left: 0; }
.category-link:last-child { border-right: 0; }
.category-link:hover { background: rgb(var(--pc-color-brand-500-rgb) / 0.06); color: var(--pc-color-semantic-action-primary); }
.category-link strong { display: block; font-size: 17px; font-weight: 700; }
.category-link p { margin: 7px 0 0; color: var(--pc-color-semantic-text-muted); font-size: 13px; }
.category-link svg { flex: 0 0 auto; color: var(--pc-color-semantic-action-primary); }
.featured-section { padding: 104px 0 64px; background: linear-gradient(180deg, #080b10 0%, var(--pc-color-semantic-background-canvas) 100%); }
.section-head { display: flex; align-items: end; justify-content: space-between; gap: 28px; margin-bottom: 30px; }
.section-label { margin: 0 0 10px; color: var(--pc-color-semantic-action-primary); font-size: 12px; font-weight: 750; letter-spacing: 0.12em; }
.section-head h2 { margin: 0; color: var(--pc-color-semantic-text-primary); font-size: clamp(32px, 3.2vw, 42px); font-weight: 700; letter-spacing: -0.045em; line-height: 1.12; }
.section-head p:last-child { margin: 14px 0 0; color: var(--pc-color-semantic-text-muted); font-size: 15px; }
.section-link { display: inline-flex; align-items: center; gap: 8px; padding-bottom: 4px; color: var(--pc-color-semantic-action-primary); font-size: 14px; font-weight: 750; white-space: nowrap; }
.product-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.product-detail-link { display: inline-flex; align-items: center; gap: 8px; padding: 8px 0; color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-sm); }
.product-detail-link:hover { color: var(--pc-color-semantic-text-accent); }
.trust-rail { padding: 36px 0; background: var(--pc-color-semantic-background-canvas); }
.trust-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-top: 1px solid var(--pc-color-semantic-border-subtle); border-bottom: 1px solid var(--pc-color-semantic-border-subtle); }
.trust-item { display: flex; min-height: 92px; align-items: center; gap: 14px; padding: 18px 22px; border-right: 1px solid var(--pc-color-semantic-border-subtle); }
.trust-item:first-child { padding-left: 0; }
.trust-item:last-child { border-right: 0; }
.trust-item > span { width: 8px; height: 8px; flex: 0 0 auto; border-radius: 50%; background: var(--pc-color-semantic-action-primary); }
.trust-item strong { color: var(--pc-color-semantic-text-primary); font-size: 14px; font-weight: 700; }
.trust-item p { margin: 5px 0 0; color: var(--pc-color-semantic-text-subtle); font-size: 12px; line-height: 1.5; }
.build-section { padding: 36px 0 88px; background: var(--pc-color-semantic-background-canvas); }
.build-shell { display: flex; align-items: center; justify-content: space-between; gap: 32px; padding: 48px; border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: 12px; background: #0b1013; }
.build-shell h2 { margin: 0 0 12px; color: var(--pc-color-semantic-text-primary); font-size: clamp(28px, 3vw, 38px); font-weight: 700; letter-spacing: -0.045em; line-height: 1.15; }
.build-shell > div > p { max-width: 570px; margin: 0; color: var(--pc-color-semantic-text-muted); font-size: 15px; line-height: 1.8; }
.build-shell .hero-btn { flex: 0 0 auto; }
@media (max-width: 960px) {
  .category-grid, .trust-grid, .product-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .category-link:nth-child(2), .trust-item:nth-child(2) { border-right: 0; }
  .category-link:nth-child(-n + 2), .trust-item:nth-child(-n + 2) { border-bottom: 1px solid var(--pc-color-semantic-border-subtle); }
  .category-link:nth-child(3), .trust-item:nth-child(3) { padding-left: 0; }
}
@media (max-width: 640px) {
  .section-shell, .hero-shell { width: min(100% - 40px, 1280px); }
  .hero-section, .hero-shell { min-height: 620px; }
  .hero-media { object-position: 66% center; }
  .hero-scrim { background: linear-gradient(90deg, rgb(5 7 11 / 0.96) 0%, rgb(5 7 11 / 0.78) 62%, rgb(5 7 11 / 0.44) 100%); }
  .hero-copy h1 { font-size: clamp(48px, 14vw, 64px); letter-spacing: -0.075em; }
  .hero-lead { max-width: 360px; margin-top: 24px; font-size: 15px; line-height: 1.75; }
  .hero-actions { gap: 10px; margin-top: 28px; }
  .hero-btn { min-width: 0; flex: 1; }
  .category-link { min-height: 92px; padding: 16px 12px; }
  .category-link:first-child, .category-link:nth-child(3) { padding-left: 0; }
  .category-link strong { font-size: 15px; }
  .category-link p { font-size: 12px; }
  .category-link svg { width: 16px; height: 16px; }
  .featured-section { padding: 70px 0 36px; }
  .section-head { align-items: flex-start; flex-direction: column; margin-bottom: 24px; }
  .section-head h2 { font-size: 34px; }
  .section-head p:last-child { font-size: 14px; }
  .trust-rail { padding: 24px 0; }
  .trust-item { min-height: 78px; padding: 14px 12px; }
  .trust-item:first-child, .trust-item:nth-child(3) { padding-left: 0; }
  .trust-item p { font-size: 11px; }
  .build-section { padding: 24px 0 48px; }
  .build-shell { align-items: stretch; flex-direction: column; padding: 28px 24px; gap: 26px; }
  .build-shell h2 { font-size: 30px; }
  .build-shell .hero-btn { flex: none; }
}
</style>
