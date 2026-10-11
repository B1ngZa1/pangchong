<template>
  <section class="pc-build-summary" :aria-labelledby="headingId">
    <div class="pc-build-summary__heading">
      <p v-if="eyebrow" class="pc-build-summary__eyebrow">{{ eyebrow }}</p>
      <h2 :id="headingId">{{ title }}</h2>
    </div>
    <dl class="pc-build-summary__metrics">
      <div v-for="metric in metricItems" :key="metric.id" class="pc-build-summary__metric" :data-tone="metric.tone">
        <dt>{{ metric.label }}</dt>
        <dd>{{ metric.display }}</dd>
      </div>
    </dl>
    <slot name="footer" />
  </section>
</template>

<script setup>
import { computed, useId } from 'vue'

const props = defineProps({
  title: { type: String, default: '配置摘要' },
  eyebrow: { type: String, default: '当前方案' },
  price: { type: [Number, String], default: 0 },
  compatibility: { type: String, default: '待验证' },
  power: { type: [Number, String], default: 0 },
  performance: { type: [Number, String], default: 0 },
  currency: { type: String, default: '¥' },
  compatibilityTone: { type: String, default: 'info' },
  powerTone: { type: String, default: 'warning' },
})

const headingId = `pc-build-summary-${useId()}`
const metricItems = computed(() => [
  { id: 'price', label: '总价', display: `${props.currency}${Number(props.price || 0).toLocaleString()}`, tone: 'positive' },
  { id: 'compatibility', label: '兼容性', display: props.compatibility, tone: props.compatibilityTone },
  { id: 'power', label: '预计功耗', display: `${props.power} W`, tone: props.powerTone },
  { id: 'performance', label: '性能评分', display: Number(props.performance || 0).toLocaleString(), tone: 'neutral' },
])
</script>

<style scoped>
.pc-build-summary { min-width: 0; padding: var(--pc-density-compact-padding); border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-surface); color: var(--pc-color-semantic-text-primary); }
.pc-build-summary__heading { margin-bottom: var(--pc-space-3); }
.pc-build-summary__eyebrow { margin: 0 0 var(--pc-space-1); color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-bold); letter-spacing: .1em; text-transform: uppercase; }
.pc-build-summary h2 { margin: 0; font-size: var(--pc-font-size-lg); line-height: var(--pc-font-line-height-tight); }
.pc-build-summary__metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin: 0; overflow: hidden; border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: var(--pc-radius-md); }
.pc-build-summary__metric { min-width: 0; display: grid; gap: var(--pc-space-2); padding: var(--pc-space-3); border-right: 1px solid var(--pc-color-semantic-border-subtle); }
.pc-build-summary__metric:last-child { border-right: 0; }
.pc-build-summary__metric dt { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); }
.pc-build-summary__metric dd { overflow: hidden; margin: 0; color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-md); font-weight: var(--pc-font-weight-bold); text-overflow: ellipsis; white-space: nowrap; }
.pc-build-summary__metric[data-tone="positive"] dd { color: var(--pc-color-semantic-text-accent); }
.pc-build-summary__metric[data-tone="warning"] dd { color: var(--pc-color-semantic-text-warning); }
.pc-build-summary__metric[data-tone="danger"] dd { color: var(--pc-color-semantic-text-danger); }
.pc-build-summary__metric[data-tone="info"] dd { color: var(--pc-color-semantic-text-info); }
@media (max-width: 639px) {
  .pc-build-summary__metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .pc-build-summary__metric:nth-child(2) { border-right: 0; }
  .pc-build-summary__metric:nth-child(-n + 2) { border-bottom: 1px solid var(--pc-color-semantic-border-subtle); }
}
</style>
