<template>
  <div class="home-page">
    <section
      data-qa="home-hero"
      class="hero-section"
      @mouseenter="heroHovered = true"
      @mouseleave="heroHovered = false"
    >
      <img
        :src="heroImage"
        alt="high performance gaming setup"
        class="hero-bg"
        :class="heroHovered ? 'is-muted' : ''"
      >
      <div class="hero-overlay" />
      <div
        data-qa="home-hero-fog"
        class="hero-fog"
        :class="heroHovered ? 'is-active' : ''"
      />

      <div class="hero-shell">
        <div class="hero-copy">
          <p class="hero-kicker">PANGCHONG PERFORMANCE LAB</p>
          <h1>
            极致性能
            <span>由你定义</span>
          </h1>
          <p class="hero-lead">
            胖虫科技专注高性能整机与 DIY 装机定制。我们提供蓝天准系统、主流一线配件和专业调校服务，帮助你稳定释放每一瓦性能。
          </p>
          <div class="hero-actions">
            <router-link to="/products" class="hero-btn hero-btn--primary">
              探索产品
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </router-link>
            <router-link to="/diy" class="hero-btn hero-btn--ghost">
              立即定制
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </router-link>
          </div>
        </div>

        <div class="hero-stage" aria-label="performance desktop preview">
          <div class="hero-stage__frame">
            <img :src="heroImage" alt="PANGCHONG performance desktop">
          </div>
        </div>

        <div class="hero-stats" aria-label="store metrics">
          <div
            v-for="stat in stats"
            :key="stat.label"
            class="hero-stat"
          >
            <div>
              <p>{{ stat.value }}</p>
              <span>{{ stat.label }}</span>
            </div>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path :d="stat.icon" />
            </svg>
          </div>
        </div>
      </div>
    </section>

    <section class="trust-rail" aria-label="service promises">
      <div class="trust-shell">
        <div v-for="point in trustPoints" :key="point.title" class="trust-item">
          <span />
          <div>
            <strong>{{ point.title }}</strong>
            <p>{{ point.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="featured-section">
      <div class="section-shell">
        <div class="section-head">
          <div>
            <h2>热门产品</h2>
            <p>经过压力测试与稳定性验证的推荐机型</p>
          </div>
          <router-link to="/products">
            查看全部
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </router-link>
        </div>

        <div v-if="loading" class="product-loading">
          <div />
        </div>

        <div v-else class="product-grid">
          <router-link
            v-for="product in hotProducts"
            :key="product.id"
            :to="`/products/${product.slug}`"
            class="product-card"
          >
            <div class="product-media">
              <img
                :src="product.image_url || fallbackImage"
                :alt="product.name"
                loading="lazy"
                @error="handleImageError"
              >
              <span>热销</span>
            </div>
            <div class="product-body">
              <p>{{ product.category_name || 'PANGCHONG SELECT' }}</p>
              <h3>{{ product.name }}</h3>
              <span class="product-subtitle">{{ product.description || '高性能整机与配件，支持定制。' }}</span>
              <div class="product-footer">
                <strong>¥{{ Number(product.price).toLocaleString() }}</strong>
                <span v-if="product.original_price">¥{{ Number(product.original_price).toLocaleString() }}</span>
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
const heroHovered = ref(false)

const heroImage = '/assets/pangchong-hero.png'
const fallbackImage = '/assets/pangchong-product-fallback.png'

function handleImageError(event) {
  if (event.target.src.endsWith(fallbackImage)) return
  event.target.src = fallbackImage
}

const stats = [
  {
    value: '50,000+',
    label: '累计服务用户',
    icon: 'M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75'
  },
  {
    value: '99%',
    label: '好评率',
    icon: 'M7 10v11M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z'
  },
  {
    value: '3 年',
    label: '整机质保',
    icon: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10ZM9 12l2 2 4-4'
  },
  {
    value: '72h',
    label: '出厂压力测试',
    icon: 'M12 2v10l4 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z'
  }
]

const trustPoints = [
  { title: '蓝天 Clevo 授权合作', description: '准系统渠道与整机调校经验沉淀' },
  { title: '专业散热与电压调校', description: '交付前完成稳定性与温控验证' },
  { title: '全国联保与远程支持', description: '订单、售后、技术支持统一跟进' },
  { title: '1 对 1 售后服务', description: '复杂问题由专人持续追踪' }
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

<style scoped>
.home-page {
  min-height: 100vh;
  overflow-x: hidden;
  background:
    radial-gradient(circle at 10% 0%, rgba(68, 214, 44, 0.12), transparent 30rem),
    radial-gradient(circle at 88% 18%, rgba(14, 116, 144, 0.16), transparent 34rem),
    #020617;
}

.hero-section {
  position: relative;
  min-height: 738px;
  overflow: hidden;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
  background: #020617;
}

.hero-bg,
.hero-overlay,
.hero-fog {
  position: absolute;
  inset: 0;
}

.hero-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 72% center;
  opacity: 0.42;
  transition: filter 0.7s ease, opacity 0.7s ease;
}

.hero-bg.is-muted {
  filter: brightness(0.74) saturate(0.82);
  opacity: 0.34;
}

.hero-overlay {
  background:
    linear-gradient(90deg, rgba(2, 6, 23, 0.98) 0%, rgba(2, 6, 23, 0.84) 42%, rgba(2, 6, 23, 0.42) 72%, rgba(2, 6, 23, 0.82) 100%),
    linear-gradient(180deg, rgba(2, 6, 23, 0.12), #020617 94%);
}

.hero-overlay::after {
  position: absolute;
  inset: 0;
  content: "";
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(180deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 88px 88px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.6), transparent 68%);
}

.hero-fog {
  background: rgba(2, 6, 23, 0);
  backdrop-filter: blur(0);
  transition: background-color 0.7s ease, backdrop-filter 0.7s ease;
}

.hero-fog.is-active {
  background: rgba(2, 6, 23, 0.16);
  backdrop-filter: blur(4px);
}

.hero-shell,
.trust-shell,
.section-shell {
  width: min(1280px, calc(100% - 64px));
  margin: 0 auto;
}

.hero-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 0.92fr) minmax(420px, 1fr);
  gap: 44px;
  align-items: center;
  min-height: 738px;
  padding: 62px 0 28px;
}

.hero-copy {
  max-width: 660px;
}

.hero-kicker {
  margin: 0 0 18px;
  color: #44d62c;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.28em;
}

.hero-copy h1 {
  margin: 0;
  color: #fff;
  font-size: clamp(52px, 7vw, 92px);
  line-height: 0.94;
  font-weight: 950;
}

.hero-copy h1 span {
  display: block;
  color: #44d62c;
}

.hero-lead {
  max-width: 620px;
  margin: 26px 0 0;
  color: #cbd5e1;
  font-size: 17px;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 34px;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-width: 172px;
  min-height: 52px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 850;
  transition: transform 0.18s ease, border-color 0.18s ease, background-color 0.18s ease, color 0.18s ease;
}

.hero-btn:hover {
  transform: translateY(-1px);
}

.hero-btn svg,
.section-head svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

.hero-btn--primary {
  background: #44d62c;
  color: #020617;
  box-shadow: 0 18px 48px rgba(68, 214, 44, 0.24);
}

.hero-btn--ghost {
  border: 1px solid rgba(203, 213, 225, 0.28);
  background: rgba(2, 6, 23, 0.42);
  color: #f8fafc;
  backdrop-filter: blur(18px);
}

.hero-btn--ghost:hover {
  border-color: rgba(68, 214, 44, 0.72);
  color: #44d62c;
}

.hero-stage {
  position: relative;
  align-self: stretch;
  min-height: 420px;
}

.hero-stage::before {
  position: absolute;
  right: 4%;
  bottom: 8%;
  left: 8%;
  height: 34%;
  content: "";
  background: rgba(68, 214, 44, 0.28);
  filter: blur(60px);
}

.hero-stage__frame {
  position: absolute;
  right: 0;
  bottom: 7%;
  width: min(100%, 620px);
  aspect-ratio: 1.16;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.48);
  box-shadow: 0 34px 90px rgba(0, 0, 0, 0.46), inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.hero-stage__frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: right center;
  filter: contrast(1.08) saturate(1.05);
}

.hero-stats {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-top: 4px;
}

.hero-stat {
  display: flex;
  min-height: 98px;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.64);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(18px);
}

.hero-stat p {
  margin: 0;
  color: #44d62c;
  font-size: 30px;
  line-height: 1;
  font-weight: 900;
}

.hero-stat span {
  display: block;
  margin-top: 8px;
  color: #94a3b8;
  font-size: 13px;
}

.hero-stat svg {
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  fill: none;
  stroke: #44d62c;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
  opacity: 0.9;
}

.trust-rail {
  padding: 18px 0 8px;
  background: #020617;
}

.trust-shell {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.48);
}

.trust-item {
  display: flex;
  gap: 14px;
  min-height: 82px;
  align-items: center;
  padding: 18px 22px;
  border-right: 1px solid rgba(148, 163, 184, 0.14);
}

.trust-item:last-child {
  border-right: 0;
}

.trust-item > span {
  width: 10px;
  height: 10px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: #44d62c;
  box-shadow: 0 0 24px rgba(68, 214, 44, 0.64);
}

.trust-item strong {
  color: #f8fafc;
  font-size: 14px;
  font-weight: 850;
}

.trust-item p {
  margin: 5px 0 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}

.featured-section {
  padding: 46px 0 78px;
  background:
    linear-gradient(180deg, #020617, #030b13 46%, #020617),
    #020617;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.section-head h2 {
  margin: 0;
  color: #fff;
  font-size: clamp(30px, 3.6vw, 44px);
  line-height: 1.1;
  font-weight: 950;
}

.section-head p {
  margin: 10px 0 0;
  color: #94a3b8;
  font-size: 14px;
}

.section-head a {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #44d62c;
  font-size: 14px;
  font-weight: 850;
}

.product-loading {
  display: grid;
  min-height: 220px;
  place-items: center;
}

.product-loading > div {
  width: 44px;
  height: 44px;
  border: 2px solid rgba(68, 214, 44, 0.2);
  border-top-color: #44d62c;
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.product-card {
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.54));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.product-card:hover {
  transform: translateY(-3px);
  border-color: rgba(68, 214, 44, 0.5);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.3);
}

.product-media {
  position: relative;
  aspect-ratio: 1.14;
  overflow: hidden;
  background: radial-gradient(circle at 50% 30%, rgba(68, 214, 44, 0.16), transparent 58%), #071016;
}

.product-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.45s ease, filter 0.45s ease;
}

.product-card:hover .product-media img {
  transform: scale(1.035);
  filter: saturate(1.08);
}

.product-media span {
  position: absolute;
  top: 14px;
  left: 14px;
  padding: 5px 8px;
  border: 1px solid rgba(68, 214, 44, 0.46);
  border-radius: 6px;
  background: rgba(2, 6, 23, 0.66);
  color: #44d62c;
  font-size: 11px;
  font-weight: 850;
  backdrop-filter: blur(12px);
}

.product-body {
  padding: 18px;
}

.product-body > p {
  margin: 0 0 8px;
  color: #44d62c;
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.product-body h3 {
  display: -webkit-box;
  min-height: 42px;
  margin: 0;
  overflow: hidden;
  color: #f8fafc;
  font-size: 16px;
  line-height: 1.35;
  font-weight: 850;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.product-subtitle {
  display: -webkit-box;
  min-height: 40px;
  margin-top: 10px;
  overflow: hidden;
  color: #64748b;
  font-size: 12px;
  line-height: 1.65;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.product-footer {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 16px;
}

.product-footer strong {
  color: #44d62c;
  font-size: 18px;
  font-weight: 900;
}

.product-footer span {
  color: #475569;
  font-size: 12px;
  text-decoration: line-through;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1080px) {
  .hero-section,
  .hero-shell {
    min-height: auto;
  }

  .hero-shell {
    grid-template-columns: 1fr;
    padding-top: 64px;
  }

  .hero-stage {
    min-height: 340px;
  }

  .hero-stage__frame {
    position: relative;
    width: 100%;
  }

  .hero-stats,
  .trust-shell,
  .product-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .trust-item:nth-child(2) {
    border-right: 0;
  }
}

@media (max-width: 640px) {
  .hero-shell,
  .trust-shell,
  .section-shell {
    width: min(100% - 24px, 1280px);
  }

  .hero-section {
    min-height: auto;
  }

  .hero-shell {
    gap: 28px;
    padding: 54px 0 28px;
  }

  .hero-kicker {
    letter-spacing: 0.22em;
  }

  .hero-copy h1 {
    font-size: 48px;
  }

  .hero-lead {
    font-size: 15px;
  }

  .hero-actions,
  .hero-btn {
    width: 100%;
  }

  .hero-stage {
    display: none;
  }

  .hero-stats,
  .product-grid {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-stat {
    min-height: 104px;
    padding: 18px;
  }

  .hero-stat p {
    font-size: 26px;
  }

  .trust-item,
  .trust-item:nth-child(2) {
    border-right: 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.14);
  }

  .trust-item:last-child {
    border-bottom: 0;
  }

  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
