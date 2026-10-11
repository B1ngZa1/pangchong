<template>
  <section class="pc-parts-inspector" :class="{ 'pc-parts-inspector--compact': compact }" :aria-labelledby="headingId">
    <div class="pc-parts-inspector__header">
      <div>
        <p v-if="eyebrow" class="pc-parts-inspector__eyebrow">{{ eyebrow }}</p>
        <h2 :id="headingId">{{ title }}</h2>
      </div>
      <button v-if="showPriceHistory" class="pc-parts-inspector__history" type="button" @click="$emit('toggle-history')">
        {{ priceHistoryLabel }}
      </button>
    </div>

    <p v-if="description" class="pc-parts-inspector__description">{{ description }}</p>

    <div v-if="parts.length" class="pc-parts-inspector__list" role="list" :aria-label="listLabel">
      <div v-for="part in parts" :key="part.id" role="listitem">
        <button
          class="pc-parts-inspector__part"
          :class="{ 'pc-parts-inspector__part--active': part.id === activeId }"
          type="button"
          :aria-pressed="part.id === activeId ? 'true' : 'false'"
          @click="$emit('select', part)"
        >
          <span class="pc-parts-inspector__part-copy">
            <span class="pc-parts-inspector__part-category">{{ part.category || '硬件' }}</span>
            <strong :title="part.name">{{ part.name }}</strong>
            <span v-if="part.status" class="pc-parts-inspector__part-status">{{ part.status }}</span>
          </span>
          <span class="pc-parts-inspector__part-price">{{ currency }}{{ formatPrice(part.price) }}</span>
        </button>
      </div>
    </div>
    <div v-else class="pc-parts-inspector__empty" role="status">
      <strong>{{ emptyTitle }}</strong>
      <p>{{ emptyDescription }}</p>
    </div>

    <slot name="footer" />
  </section>
</template>

<script setup>
import { useId } from 'vue'

const props = defineProps({
  parts: { type: Array, default: () => [] },
  activeId: { type: [String, Number], default: null },
  title: { type: String, default: '硬件清单' },
  eyebrow: { type: String, default: '配置检查器' },
  description: { type: String, default: '' },
  listLabel: { type: String, default: '已选硬件' },
  currency: { type: String, default: '¥' },
  compact: Boolean,
  showPriceHistory: Boolean,
  priceHistoryLabel: { type: String, default: '价格历史' },
  emptyTitle: { type: String, default: '还没有选择硬件' },
  emptyDescription: { type: String, default: '从左侧目录选择配件，检查器会在这里汇总。' },
})

defineEmits(['select', 'toggle-history'])

const headingId = `pc-parts-inspector-${useId()}`

function formatPrice(value) {
  return Number(value || 0).toLocaleString()
}
</script>

<style scoped>
.pc-parts-inspector { min-width: 0; color: var(--pc-color-semantic-text-primary); }
.pc-parts-inspector__header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--pc-space-3); }
.pc-parts-inspector__eyebrow { margin: 0 0 var(--pc-space-1); color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-bold); letter-spacing: .1em; text-transform: uppercase; }
.pc-parts-inspector h2 { margin: 0; font-size: var(--pc-font-size-lg); line-height: var(--pc-font-line-height-tight); }
.pc-parts-inspector__description { margin: var(--pc-space-3) 0 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); }
.pc-parts-inspector__history { min-height: var(--pc-size-control-touch); padding: 0 var(--pc-space-3); border: 1px solid var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-md); background: transparent; color: var(--pc-color-semantic-text-secondary); font: inherit; font-size: var(--pc-font-size-xs); cursor: pointer; }
.pc-parts-inspector__history:hover { border-color: var(--pc-color-semantic-border-accent); color: var(--pc-color-semantic-text-accent); }
.pc-parts-inspector__history:focus-visible, .pc-parts-inspector__part:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 2px; }
.pc-parts-inspector__list { display: grid; gap: var(--pc-density-compact-gap); margin-top: var(--pc-space-4); }
.pc-parts-inspector__part { display: flex; min-width: 0; align-items: center; justify-content: space-between; gap: var(--pc-space-3); min-height: var(--pc-size-control-touch); padding: var(--pc-space-3); border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: var(--pc-radius-md); background: var(--pc-color-semantic-background-canvas); color: inherit; text-align: left; font: inherit; cursor: pointer; }
.pc-parts-inspector__part:hover, .pc-parts-inspector__part--active { border-color: var(--pc-color-semantic-border-accent); background: var(--pc-color-semantic-background-elevated); }
.pc-parts-inspector__part-copy { display: grid; min-width: 0; gap: var(--pc-space-1); }
.pc-parts-inspector__part-category, .pc-parts-inspector__part-status { overflow: hidden; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); text-overflow: ellipsis; white-space: nowrap; }
.pc-parts-inspector__part strong { overflow: hidden; font-size: var(--pc-font-size-sm); text-overflow: ellipsis; white-space: nowrap; }
.pc-parts-inspector__part-price { flex: 0 0 auto; color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-bold); }
.pc-parts-inspector__empty { margin-top: var(--pc-space-4); padding: var(--pc-space-4); border: 1px dashed var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-md); color: var(--pc-color-semantic-text-secondary); }
.pc-parts-inspector__empty p { margin: var(--pc-space-2) 0 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); }
.pc-parts-inspector--compact .pc-parts-inspector__list { gap: var(--pc-space-2); }
</style>
