<template>
  <div class="store-page">
    <section class="store-title">
      <router-link to="/products" class="store-back">返回商店</router-link>
      <p>线下购买与体验</p>
      <h1>胖虫电脑武汉门店</h1>
      <span>武汉市武昌区江盛路19号3号楼2楼</span>
    </section>

    <section class="store-hero" aria-label="胖虫武汉体验中心预览">
      <img :src="storeHeroImage" alt="胖虫电脑线下体验区" />
    </section>

    <section class="store-shell store-info">
      <div>
        <h2>到店信息</h2>
        <p>门店支持整机体验、配置咨询、DIY 配件确认、装机方案沟通和售后检测预约。</p>
      </div>
      <dl>
        <div>
          <dt>地址</dt>
          <dd>武汉市武昌区江盛路19号3号楼2楼</dd>
        </div>
        <div>
          <dt>营业时间</dt>
          <dd>周一至周六 09:00-21:00</dd>
        </div>
        <div>
          <dt>服务方式</dt>
          <dd>建议提前预约，便于预留体验机和技术顾问</dd>
        </div>
      </dl>
    </section>

    <section class="store-shell">
      <div class="section-heading">
        <p>今日到店体验</p>
        <h2>来店里，把配置方案当面说清楚。</h2>
      </div>
      <div class="store-card-row">
        <article v-for="card in storeCards" :key="card.title" class="store-card">
          <img :src="card.image" :alt="card.title" />
          <div>
            <p>{{ card.kicker }}</p>
            <h3>{{ card.title }}</h3>
            <span>{{ card.description }}</span>
          </div>
        </article>
      </div>
    </section>

    <section class="store-band">
      <div class="store-shell service-grid">
        <article v-for="item in serviceItems" :key="item.title">
          <span>{{ item.icon }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </section>

    <section class="store-shell split-section">
      <div>
        <p>电脑技术服务台</p>
        <h2>我们协助上手，也帮你把问题定位到具体部件。</h2>
        <router-link to="/services#tech-support">查看技术支持</router-link>
      </div>
      <img :src="supportImage" alt="电脑技术支持服务" />
    </section>

    <section class="store-shell">
      <div class="section-heading">
        <p>门店活动</p>
        <h2>从第一套配置到下一次升级，欢迎到店把问题和目标当面讲清楚。</h2>
      </div>
      <div class="activity-grid">
        <article v-for="activity in activityCards" :key="activity.title">
          <img :src="activity.image" :alt="activity.title" />
          <div>
            <p>{{ activity.kicker }}</p>
            <h3>{{ activity.title }}</h3>
            <router-link :to="activity.to">了解更多</router-link>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
const storeHeroImage = '/assets/pangchong-hero.png'
const productImage = '/assets/pangchong-product-fallback.png'
const supportImage = '/assets/pangchong-product-fallback.png'

const storeCards = [
  {
    kicker: '配置咨询',
    title: '把用途、预算和性能目标带来门店。',
    description: '现场确认整机、显示器、配件和升级空间。',
    image: productImage
  },
  {
    kicker: 'DIY 配件',
    title: 'CPU、GPU、主板等统一在 DIY 配件下查看。',
    description: '适合现场核对兼容性、功耗、散热和安装空间。',
    image: productImage
  },
  {
    kicker: '售后支持',
    title: '到店沟通检测流程和返修方案。',
    description: '复杂问题建议提前预约，减少等待时间。',
    image: productImage
  }
]

const serviceItems = [
  {
    icon: '01',
    title: '现场体验',
    description: '体验整机外观、键盘手感、屏幕表现和接口布局。'
  },
  {
    icon: '02',
    title: '当面选配',
    description: '技术顾问协助确认 CPU、GPU、内存、SSD、电源和散热方案。'
  },
  {
    icon: '03',
    title: '预约取机',
    description: '定制整机完成装机、系统调试和压力测试后可预约到店取机。'
  },
  {
    icon: '04',
    title: '售后沟通',
    description: '支持故障现象确认、检测建议、返修流程和保修政策说明。'
  }
]

const activityCards = [
  {
    kicker: '体验活动',
    title: '新品整机体验与性能讲解',
    image: productImage,
    to: '/products'
  },
  {
    kicker: '装机交流',
    title: 'DIY 配件搭配与兼容性说明',
    image: storeHeroImage,
    to: '/diy'
  }
]
</script>

<style scoped>
.store-page {
  min-height: 100vh;
  background: var(--pc-color-theme-store-canvas);
  color: var(--pc-color-theme-store-text);
}

.store-shell {
  width: min(980px, calc(100% - 32px));
  margin: 0 auto;
}

.store-title {
  position: relative;
  width: min(980px, calc(100% - 32px));
  margin: 0 auto;
  padding: 42px 0 34px;
  text-align: center;
}

.store-back {
  position: absolute;
  left: 0;
  top: 48px;
  color: var(--pc-color-theme-store-text);
  font-size: 14px;
  font-weight: 600;
}

.store-title p {
  margin: 0;
  color: var(--pc-color-theme-store-muted);
  font-size: 14px;
  font-weight: 600;
}

.store-title h1 {
  margin: 14px 0 8px;
  font-size: clamp(32px, 5vw, 56px);
  line-height: 1.05;
  font-weight: 800;
  letter-spacing: 0;
}

.store-title span {
  color: var(--pc-color-theme-store-muted);
  font-size: 15px;
}

.store-hero {
  height: clamp(280px, 46vw, 560px);
  overflow: hidden;
  background: var(--pc-color-theme-store-surface);
}

.store-hero img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.store-info {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.9fr);
  gap: 56px;
  padding: 56px 0 44px;
}

.store-info h2,
.section-heading h2,
.split-section h2 {
  margin: 0;
  color: var(--pc-color-theme-store-text);
  font-size: 30px;
  line-height: 1.18;
  font-weight: 800;
}

.store-info p,
.section-heading p,
.split-section p {
  margin: 12px 0 0;
  color: var(--pc-color-theme-store-muted);
  font-size: 15px;
  line-height: 1.7;
}

.store-info dl {
  display: grid;
  gap: 18px;
  margin: 0;
}

.store-info div {
  min-width: 0;
}

.store-info dt {
  color: var(--pc-color-theme-store-muted);
  font-size: 13px;
  font-weight: 700;
}

.store-info dd {
  margin: 6px 0 0;
  color: var(--pc-color-theme-store-text);
  font-size: 16px;
  font-weight: 700;
}

.section-heading {
  margin: 26px 0 24px;
  text-align: center;
}

.store-card-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.store-card,
.activity-grid article,
.split-section,
.service-grid article {
  overflow: hidden;
  border-radius: 8px;
  background: var(--pc-color-theme-store-surface);
}

.store-card img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

.store-card div,
.activity-grid div {
  padding: 22px;
}

.store-card p,
.activity-grid p {
  margin: 0 0 8px;
  color: var(--pc-color-theme-store-muted);
  font-size: 12px;
  font-weight: 700;
}

.store-card h3,
.activity-grid h3,
.service-grid h3 {
  margin: 0;
  color: var(--pc-color-theme-store-text);
  font-size: 18px;
  line-height: 1.35;
  font-weight: 800;
}

.store-card span,
.service-grid p {
  display: block;
  margin-top: 10px;
  color: var(--pc-color-theme-store-muted);
  font-size: 14px;
  line-height: 1.65;
}

.store-band {
  margin-top: 56px;
  padding: 56px 0;
  background: var(--pc-color-theme-store-surface);
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.service-grid article {
  border: 1px solid var(--pc-color-theme-store-border);
  padding: 28px 22px;
  text-align: center;
}

.service-grid span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin-bottom: 18px;
  border-radius: 999px;
  background: var(--pc-color-theme-store-action);
  color: var(--pc-color-theme-store-surface);
  font-size: 13px;
  font-weight: 800;
}

.split-section {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  align-items: center;
  margin-top: 56px;
}

.split-section div {
  padding: 42px;
}

.split-section a,
.activity-grid a {
  display: inline-flex;
  margin-top: 18px;
  color: var(--pc-color-theme-store-link);
  font-size: 14px;
  font-weight: 700;
}

.split-section img {
  width: 100%;
  height: 100%;
  min-height: 320px;
  object-fit: cover;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  padding-bottom: 70px;
}

.activity-grid img {
  width: 100%;
  aspect-ratio: 5 / 4;
  object-fit: cover;
}

@media (max-width: 900px) {
  .store-info,
  .store-card-row,
  .service-grid,
  .split-section,
  .activity-grid {
    grid-template-columns: 1fr;
  }

  .store-back {
    position: static;
    display: inline-flex;
    margin-bottom: 18px;
  }

  .store-title {
    text-align: left;
  }

  .section-heading {
    text-align: left;
  }
}
</style>
