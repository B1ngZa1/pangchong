<template>
  <article class="pc-cart-line-item" :class="{ 'pc-cart-line-item--disabled': disabled, 'pc-cart-line-item--compact': compact, 'pc-cart-line-item--preview': !interactive }">
    <label v-if="interactive" class="pc-cart-line-item__select">
      <input
        type="checkbox"
        :checked="selected"
        :disabled="disabled"
        :aria-label="`选择${item.name}`"
        @change="$emit('toggle')"
      >
    </label>

    <div class="pc-cart-line-item__media">
      <img v-if="imageSource" :src="imageSource" :alt="item.name" loading="lazy" @error="handleImageError">
      <span v-else aria-hidden="true">⌁</span>
    </div>

    <div class="pc-cart-line-item__body">
      <div class="pc-cart-line-item__heading">
        <div class="pc-cart-line-item__identity">
          <div class="pc-cart-line-item__name-row">
            <component :is="headingTag" class="pc-cart-line-item__name">{{ item.name }}</component>
            <span v-if="item.item_type === 'custom'" class="pc-cart-line-item__custom">定制</span>
          </div>
          <p v-if="item.brand || item.model">{{ item.brand }} {{ item.model }}</p>
          <div v-if="specEntries.length" class="pc-cart-line-item__specs" aria-label="商品规格摘要">
            <span v-for="entry in specEntries" :key="entry.key">{{ entry.value }}</span>
          </div>
        </div>
        <button v-if="interactive" class="pc-cart-line-item__remove" type="button" :aria-label="`删除${item.name}`" @click="$emit('remove')">×</button>
      </div>

      <div class="pc-cart-line-item__status" :data-tone="stockTone">
        <span class="pc-cart-line-item__status-mark" aria-hidden="true" />
        {{ stockLabel }}
      </div>

      <slot name="details" :item="item" />

      <div class="pc-cart-line-item__footer">
        <div class="pc-cart-line-item__prices" aria-label="商品价格">
          <strong>¥{{ formattedPrice }}</strong>
          <del v-if="discounted">¥{{ formattedOriginalPrice }}</del>
        </div>

        <div v-if="interactive" class="pc-cart-line-item__controls">
          <div class="pc-cart-line-item__stepper" role="group" :aria-label="`${item.name}数量`">
            <button type="button" :aria-label="`减少${item.name}数量`" :disabled="disabled || item.quantity <= 1" @click="$emit('decrement')">−</button>
            <output aria-live="polite" aria-atomic="true" :aria-label="`当前数量 ${item.quantity}`">{{ item.quantity }}</output>
            <button type="button" :aria-label="`增加${item.name}数量`" :disabled="disabled || item.quantity >= maxQuantity" @click="$emit('increment')">＋</button>
          </div>
          <strong class="pc-cart-line-item__subtotal">¥{{ subtotal }}</strong>
        </div>
        <output v-else class="pc-cart-line-item__readonly-quantity" :aria-label="`${item.name}数量 ${item.quantity}`">×{{ item.quantity }}</output>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  selected: Boolean,
  disabled: Boolean,
  interactive: { type: Boolean, default: true },
  compact: Boolean,
  headingTag: { type: String, default: 'h2', validator: (value) => ['h2', 'h3', 'div'].includes(value) },
  fallbackImage: { type: String, default: '/assets/pangchong-product-fallback.png' },
})

defineEmits(['toggle', 'remove', 'decrement', 'increment'])

const imageSource = ref(props.item.image_url || props.fallbackImage)
const stock = computed(() => Number(props.item.stock || 0))
const maxQuantity = computed(() => Math.max(1, Math.min(99, stock.value)))
const stockTone = computed(() => stock.value <= 0 ? 'danger' : stock.value <= 5 ? 'warn' : 'ok')
const stockLabel = computed(() => stock.value <= 0 ? '暂时缺货' : stock.value <= 5 ? `仅剩 ${stock.value} 件` : '有库存')
const discounted = computed(() => Number(props.item.original_price || 0) > Number(props.item.price || 0))
const formattedPrice = computed(() => Number(props.item.price || 0).toLocaleString())
const formattedOriginalPrice = computed(() => Number(props.item.original_price || 0).toLocaleString())
const subtotal = computed(() => (Number(props.item.price || 0) * Number(props.item.quantity || 0)).toLocaleString())
const specEntries = computed(() => Object.entries(props.item.specs || {}).slice(0, 3).map(([key, value]) => ({ key, value })))

function handleImageError() {
  if (imageSource.value !== props.fallbackImage) imageSource.value = props.fallbackImage
}
</script>

<style scoped>
.pc-cart-line-item { display: grid; grid-template-columns: auto 7.5rem minmax(0, 1fr); gap: var(--pc-space-5); padding: var(--pc-space-6) 0; border-bottom: 1px solid var(--pc-color-semantic-border-subtle); }
.pc-cart-line-item--disabled { opacity: var(--pc-opacity-disabled); }
.pc-cart-line-item--compact { padding: var(--pc-space-3) 0; gap: var(--pc-space-3); }
.pc-cart-line-item--preview { grid-template-columns: 4rem minmax(0, 1fr); }
.pc-cart-line-item__select { display: flex; min-width: var(--pc-size-control-touch); min-height: var(--pc-size-control-touch); align-items: flex-start; justify-content: center; padding-top: var(--pc-space-1); }
.pc-cart-line-item__select input { width: var(--pc-size-control-sm); height: var(--pc-size-control-sm); accent-color: var(--pc-color-semantic-action-primary); }
.pc-cart-line-item__media { display: grid; width: 7.5rem; height: 7.5rem; place-items: center; overflow: hidden; border-radius: var(--pc-radius-md); background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-subtle); font-size: var(--pc-font-size-3xl); }
.pc-cart-line-item__media img { width: 100%; height: 100%; object-fit: cover; }
.pc-cart-line-item__body { display: flex; min-width: 0; flex-direction: column; justify-content: space-between; gap: var(--pc-space-3); }
.pc-cart-line-item__heading, .pc-cart-line-item__footer { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--pc-space-4); }
.pc-cart-line-item__identity { min-width: 0; }
.pc-cart-line-item__name-row { display: flex; flex-wrap: wrap; align-items: center; gap: var(--pc-space-2); }
.pc-cart-line-item__name { margin: 0; color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-md); font-weight: var(--pc-font-weight-bold); line-height: var(--pc-font-line-height-tight); }
.pc-cart-line-item__identity > p { margin: var(--pc-space-1) 0 0; color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-xs); }
.pc-cart-line-item__custom { padding: var(--pc-space-1) var(--pc-space-2); border-radius: var(--pc-radius-sm); background: var(--pc-color-semantic-background-accent); color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xs); }
.pc-cart-line-item__specs { display: flex; flex-wrap: wrap; gap: var(--pc-space-1); margin-top: var(--pc-space-2); }
.pc-cart-line-item__specs span { padding: var(--pc-space-1) var(--pc-space-2); border-radius: var(--pc-radius-sm); background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-xs); }
.pc-cart-line-item__remove { width: var(--pc-size-control-touch); height: var(--pc-size-control-touch); margin: calc(var(--pc-space-2) * -1); border: 0; border-radius: var(--pc-radius-md); background: transparent; color: var(--pc-color-semantic-text-muted); cursor: pointer; font-size: var(--pc-font-size-xl); }
.pc-cart-line-item__remove:hover, .pc-cart-line-item__remove:focus-visible { background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-primary); }
.pc-cart-line-item__remove:focus-visible, .pc-cart-line-item__stepper button:focus-visible, .pc-cart-line-item__select input:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 2px; }
.pc-cart-line-item__status { display: inline-flex; width: fit-content; align-items: center; gap: var(--pc-space-2); color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-semibold); }
.pc-cart-line-item__status[data-tone='warn'] { color: var(--pc-color-semantic-text-warning); }
.pc-cart-line-item__status[data-tone='danger'] { color: var(--pc-color-semantic-text-danger); }
.pc-cart-line-item__status-mark { width: .5rem; height: .5rem; border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-action-primary); }
.pc-cart-line-item__status[data-tone='warn'] .pc-cart-line-item__status-mark { background: var(--pc-color-amber-500); }
.pc-cart-line-item__status[data-tone='danger'] .pc-cart-line-item__status-mark { background: var(--pc-color-red-500); }
.pc-cart-line-item__footer { align-items: center; }
.pc-cart-line-item__prices { display: flex; align-items: baseline; gap: var(--pc-space-2); }
.pc-cart-line-item__prices strong, .pc-cart-line-item__subtotal { color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-md); font-weight: var(--pc-font-weight-bold); }
.pc-cart-line-item__prices del { color: var(--pc-color-semantic-text-subtle); font-size: var(--pc-font-size-xs); }
.pc-cart-line-item__controls { display: flex; align-items: center; gap: var(--pc-space-4); }
.pc-cart-line-item__stepper { display: inline-grid; grid-template-columns: var(--pc-size-control-touch) 2.25rem var(--pc-size-control-touch); min-height: var(--pc-size-control-touch); overflow: hidden; border: 1px solid var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-sm); background: var(--pc-color-semantic-background-elevated); }
.pc-cart-line-item__stepper button, .pc-cart-line-item__stepper output { display: grid; place-items: center; min-width: 0; border: 0; background: transparent; color: var(--pc-color-semantic-text-primary); font: inherit; font-size: var(--pc-font-size-sm); }
.pc-cart-line-item__stepper button { cursor: pointer; }
.pc-cart-line-item__stepper button:hover:not(:disabled) { background: var(--pc-color-semantic-background-accent); color: var(--pc-color-semantic-text-accent); }
.pc-cart-line-item__stepper button:disabled { cursor: not-allowed; opacity: var(--pc-opacity-muted); }
.pc-cart-line-item__stepper output { border-inline: 1px solid var(--pc-color-semantic-border-default); }
.pc-cart-line-item__readonly-quantity { color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-sm); white-space: nowrap; }
.pc-cart-line-item--compact .pc-cart-line-item__media { width: 4rem; height: 4rem; }
.pc-cart-line-item--compact .pc-cart-line-item__body { gap: var(--pc-space-2); }
.pc-cart-line-item--compact .pc-cart-line-item__status { font-size: var(--pc-font-size-xs); }
.pc-cart-line-item--compact .pc-cart-line-item__prices strong { font-size: var(--pc-font-size-sm); }
@media (max-width: 640px) {
  .pc-cart-line-item { grid-template-columns: auto 5.5rem minmax(0, 1fr); gap: var(--pc-space-3); }
  .pc-cart-line-item__media { width: 5.5rem; height: 5.5rem; }
  .pc-cart-line-item--preview { grid-template-columns: 4rem minmax(0, 1fr); }
  .pc-cart-line-item__footer { align-items: flex-start; flex-direction: column; }
  .pc-cart-line-item__controls { width: 100%; justify-content: space-between; }
}
</style>
