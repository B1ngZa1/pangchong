<template>
  <section class="pc-order-summary" :aria-labelledby="titleId">
    <h2 :id="titleId" class="pc-order-summary__title">{{ title }}</h2>

    <div v-if="items.length" class="pc-order-summary__items" aria-label="已选商品">
      <DsCartLineItem
        v-for="item in items"
        :key="item.id"
        :item="item"
        :selected="true"
        :interactive="false"
        compact
        heading-tag="h3"
        :fallback-image="fallbackImage"
      >
        <template #details>
          <slot name="item-details" :item="item" />
        </template>
      </DsCartLineItem>
    </div>
    <p v-else class="pc-order-summary__empty">暂无已选商品</p>

    <DsPriceSummary
      :subtotal="subtotal"
      :shipping="shipping"
      :discount="discount"
      :total="total"
    />
  </section>
</template>

<script setup>
import DsCartLineItem from './DsCartLineItem.vue'
import DsPriceSummary from './DsPriceSummary.vue'

let summaryCounter = 0

const props = defineProps({
  items: { type: Array, default: () => [] },
  title: { type: String, default: '订单摘要' },
  subtotal: { type: [Number, String], default: 0 },
  shipping: { type: [Number, String], default: 0 },
  discount: { type: [Number, String], default: 0 },
  total: { type: [Number, String], default: 0 },
  fallbackImage: { type: String, default: '/assets/pangchong-product-fallback.png' },
})

const titleId = `pc-order-summary-${++summaryCounter}`
</script>

<style scoped>
.pc-order-summary { position: sticky; top: 6rem; overflow: hidden; border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-surface); color: var(--pc-color-semantic-text-primary); box-shadow: var(--pc-shadow-sm); }
.pc-order-summary__title { margin: 0; padding: var(--pc-space-6) var(--pc-space-6) var(--pc-space-4); font-size: var(--pc-font-size-xl); font-weight: var(--pc-font-weight-bold); }
.pc-order-summary__items { max-height: 16rem; overflow-y: auto; padding: 0 var(--pc-space-6); }
.pc-order-summary__items :deep(.pc-cart-line-item) { border-bottom-color: var(--pc-color-semantic-border-subtle); }
.pc-order-summary__items :deep(.pc-cart-line-item__status) { display: none; }
.pc-order-summary__empty { margin: 0; padding: var(--pc-space-4) var(--pc-space-6); color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); }
.pc-order-summary :deep(.pc-price-summary) { margin: var(--pc-space-4) var(--pc-space-6) 0; }
.pc-order-summary :deep(.pc-price-summary__total) { padding-bottom: var(--pc-space-2); }
@media (max-width: 1023px) { .pc-order-summary { position: static; } }
</style>
