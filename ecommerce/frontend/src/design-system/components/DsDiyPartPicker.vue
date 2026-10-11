<template>
  <article
    class="pc-diy-part-picker"
    :class="{ 'pc-diy-part-picker--selected': selected }"
    role="button"
    :aria-label="ariaLabel"
    :aria-pressed="selected"
    tabindex="0"
    @click="selectProduct"
    @keydown.enter.prevent="selectProduct"
    @keydown.space.prevent="selectProduct"
  >
    <div class="pc-diy-part-picker__media">
      <img :src="imageSource" :alt="product.name" loading="lazy" @error="handleImageError">
      <span v-if="selected" class="pc-diy-part-picker__selected-mark" aria-hidden="true">✓</span>
    </div>

    <div class="pc-diy-part-picker__body">
      <div class="pc-diy-part-picker__heading">
        <div class="pc-diy-part-picker__identity">
          <p class="pc-diy-part-picker__brand">{{ product.brand || '未知品牌' }}</p>
          <h3>{{ product.name }}</h3>
        </div>
        <div class="pc-diy-part-picker__price" aria-label="配件价格">
          <strong>{{ currency }}{{ formattedPrice }}</strong>
          <del v-if="discounted">{{ currency }}{{ formattedOriginalPrice }}</del>
        </div>
      </div>

      <p class="pc-diy-part-picker__description">{{ product.description || fallbackDescription }}</p>
      <PriceProvenance :product="product" compact class="pc-diy-part-picker__provenance" />

      <div v-if="specs.length" class="pc-diy-part-picker__specs" aria-label="配件规格摘要">
        <span v-for="entry in specs" :key="entry.key" class="pc-diy-part-picker__spec">
          {{ entry.label }}: {{ entry.value }}
        </span>
      </div>

      <div class="pc-diy-part-picker__footer">
        <span class="pc-diy-part-picker__advice" :data-tone="selectionAdvice.level">
          {{ selectionAdvice.text }}
        </span>
        <span v-if="selected" class="pc-diy-part-picker__selected-label">已选择</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import PriceProvenance from '@/components/PriceProvenance.vue'

const props = defineProps({
  product: { type: Object, required: true },
  selected: Boolean,
  specs: { type: Array, default: () => [] },
  selectionAdvice: {
    type: Object,
    default: () => ({ level: 'ok', text: '规格信息已展示，可加入配置比较' }),
  },
  fallbackImage: { type: String, default: '/assets/pangchong-product-fallback.png' },
  fallbackDescription: { type: String, default: '已整理关键规格与价格依据，可加入配置比较。' },
  currency: { type: String, default: '¥' },
})

const emit = defineEmits(['select'])
const imageSource = ref(props.product.image_url || props.fallbackImage)

const formattedPrice = computed(() => Number(props.product.price || 0).toLocaleString())
const formattedOriginalPrice = computed(() => Number(props.product.original_price || 0).toLocaleString())
const discounted = computed(() => Number(props.product.original_price || 0) > Number(props.product.price || 0))
const ariaLabel = computed(() => `${props.product.name}${props.selected ? '，已选择' : '，选择此配件'}`)

watch(() => props.product.image_url, (nextImage) => {
  imageSource.value = nextImage || props.fallbackImage
})

function selectProduct() {
  emit('select', props.product)
}

function handleImageError() {
  if (imageSource.value !== props.fallbackImage) imageSource.value = props.fallbackImage
}
</script>

<style scoped>
.pc-diy-part-picker { display: flex; min-width: 0; flex-direction: column; overflow: hidden; border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-canvas); color: var(--pc-color-semantic-text-primary); cursor: pointer; transition: border-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard), box-shadow var(--pc-motion-duration-normal) var(--pc-motion-ease-standard), transform var(--pc-motion-duration-normal) var(--pc-motion-ease-standard); }
.pc-diy-part-picker:hover { transform: translateY(-2px); border-color: var(--pc-color-semantic-border-accent); box-shadow: var(--pc-shadow-md); }
.pc-diy-part-picker:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 3px; box-shadow: var(--pc-shadow-focus); }
.pc-diy-part-picker--selected { border-color: var(--pc-color-semantic-border-accent); background: var(--pc-color-semantic-background-accent); box-shadow: var(--pc-shadow-md); }
.pc-diy-part-picker__media { position: relative; display: grid; height: 7rem; place-items: center; overflow: hidden; background: var(--pc-color-semantic-background-elevated); }
.pc-diy-part-picker__media img { width: 100%; height: 100%; object-fit: contain; transition: transform var(--pc-motion-duration-slow) var(--pc-motion-ease-standard); }
.pc-diy-part-picker:hover .pc-diy-part-picker__media img { transform: scale(1.04); }
.pc-diy-part-picker__selected-mark { position: absolute; top: var(--pc-space-3); right: var(--pc-space-3); display: grid; width: var(--pc-size-control-touch); height: var(--pc-size-control-touch); place-items: center; border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-action-primary); color: var(--pc-color-semantic-text-inverse); font-weight: var(--pc-font-weight-bold); box-shadow: var(--pc-shadow-sm); }
.pc-diy-part-picker__body { display: flex; min-width: 0; flex: 1; flex-direction: column; gap: var(--pc-space-3); padding: var(--pc-space-5); }
.pc-diy-part-picker__heading { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--pc-space-3); }
.pc-diy-part-picker__identity { min-width: 0; }
.pc-diy-part-picker__brand { margin: 0 0 var(--pc-space-1); color: var(--pc-color-semantic-text-subtle); font-size: var(--pc-font-size-xs); }
.pc-diy-part-picker h3 { display: -webkit-box; overflow: hidden; margin: 0; color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-md); font-weight: var(--pc-font-weight-semibold); line-height: var(--pc-font-line-height-tight); -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.pc-diy-part-picker__price { display: flex; flex: 0 0 auto; flex-direction: column; align-items: flex-end; gap: var(--pc-space-1); }
.pc-diy-part-picker__price strong { color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-lg); font-weight: var(--pc-font-weight-bold); }
.pc-diy-part-picker__price del { color: var(--pc-color-semantic-text-subtle); font-size: var(--pc-font-size-xs); }
.pc-diy-part-picker__description { display: -webkit-box; overflow: hidden; min-height: calc(var(--pc-font-size-sm) * var(--pc-font-line-height-normal) * 2); margin: 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.pc-diy-part-picker__provenance { min-height: 2.75rem; }
.pc-diy-part-picker__specs { display: flex; flex-wrap: wrap; gap: var(--pc-space-1); }
.pc-diy-part-picker__spec { padding: var(--pc-space-1) var(--pc-space-2); border-radius: var(--pc-radius-sm); background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-xs); }
.pc-diy-part-picker__footer { display: flex; min-height: var(--pc-size-control-touch); align-items: center; justify-content: space-between; gap: var(--pc-space-3); margin-top: auto; padding-top: var(--pc-space-3); border-top: 1px solid var(--pc-color-semantic-border-subtle); font-size: var(--pc-font-size-xs); }
.pc-diy-part-picker__advice { min-width: 0; overflow: hidden; color: var(--pc-color-semantic-text-muted); text-overflow: ellipsis; white-space: nowrap; }
.pc-diy-part-picker__advice[data-tone='warn'] { color: var(--pc-color-semantic-text-warning); }
.pc-diy-part-picker__selected-label { flex: 0 0 auto; color: var(--pc-color-semantic-text-accent); font-weight: var(--pc-font-weight-semibold); }
@media (max-width: 480px) { .pc-diy-part-picker__body { padding: var(--pc-space-4); } .pc-diy-part-picker__heading { flex-direction: column; } .pc-diy-part-picker__price { align-items: flex-start; } }
</style>
