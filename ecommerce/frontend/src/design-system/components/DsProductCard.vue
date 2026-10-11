<template>
  <article
    class="pc-product-card"
    :class="{ 'pc-product-card--interactive': interactive }"
    :data-interactive="interactive || undefined"
    :tabindex="interactive ? 0 : undefined"
    @click="selectProduct"
    @keydown.enter.self.prevent="selectProduct"
    @keydown.space.self.prevent="selectProduct"
  >
    <div class="pc-product-card__media">
      <img
        :src="imageSource"
        :alt="product.name"
        loading="lazy"
        decoding="async"
        @error="handleImageError"
      >
      <div class="pc-product-card__badges">
        <slot name="badges">
          <DsBadge v-if="product.is_featured" tone="accent">推荐</DsBadge>
          <DsBadge v-if="discounted" tone="danger">特惠</DsBadge>
        </slot>
      </div>
    </div>

    <div class="pc-product-card__body">
      <p v-if="categoryLabel" class="pc-product-card__category">{{ categoryLabel }}</p>
      <h2>{{ product.name }}</h2>
      <p class="pc-product-card__description">{{ product.description || fallbackDescription }}</p>

      <div v-if="specEntries.length" class="pc-product-card__specs" aria-label="商品规格摘要">
        <span v-for="entry in specEntries" :key="entry.key">{{ entry.value }}</span>
      </div>

      <div class="pc-product-card__footer">
        <div class="pc-product-card__price" aria-label="商品价格">
          <strong>{{ currency }}{{ formattedPrice }}</strong>
          <del v-if="discounted">{{ currency }}{{ formattedOriginalPrice }}</del>
        </div>
        <slot name="actions" :product="product" />
      </div>
      <slot name="provenance" :product="product" />
    </div>
  </article>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import DsBadge from './DsBadge.vue'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
  categoryLabel: String,
  fallbackImage: {
    type: String,
    default: '/assets/pangchong-product-fallback.png',
  },
  fallbackDescription: {
    type: String,
    default: '高性能整机与配件，支持定制。',
  },
  currency: {
    type: String,
    default: '¥',
  },
  interactive: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['select'])
const imageSource = ref(props.product.image_url || props.fallbackImage)
watch(() => [props.product.image_url, props.fallbackImage], () => {
  imageSource.value = props.product.image_url || props.fallbackImage
})

const discounted = computed(() => props.product.original_price && Number(props.product.original_price) > Number(props.product.price))
const formattedPrice = computed(() => Number(props.product.price || 0).toLocaleString())
const formattedOriginalPrice = computed(() => Number(props.product.original_price || 0).toLocaleString())
const specEntries = computed(() => {
  if (!props.product.specs || typeof props.product.specs !== 'object') return []
  return Object.entries(props.product.specs).slice(0, 4).map(([key, value]) => ({ key, value }))
})

function selectProduct() {
  if (props.interactive) emit('select', props.product)
}

function handleImageError() {
  if (imageSource.value !== props.fallbackImage) imageSource.value = props.fallbackImage
}
</script>

<style scoped>
.pc-product-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--pc-color-semantic-border-subtle);
  border-radius: var(--pc-radius-lg);
  background: var(--pc-color-semantic-background-surface);
  color: var(--pc-color-semantic-text-primary);
  box-shadow: var(--pc-shadow-sm);
}

.pc-product-card--interactive {
  cursor: pointer;
  transition:
    border-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    box-shadow var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    transform var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}

.pc-product-card--interactive:hover {
  transform: translateY(-2px);
  border-color: var(--pc-color-semantic-border-accent);
  box-shadow: var(--pc-shadow-md);
}

.pc-product-card:focus-visible {
  outline: 2px solid var(--pc-color-semantic-border-focus);
  outline-offset: 3px;
  box-shadow: var(--pc-shadow-focus);
}

.pc-product-card__media {
  position: relative;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: var(--pc-color-semantic-background-elevated);
}

.pc-product-card__media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--pc-motion-duration-slow) var(--pc-motion-ease-standard);
}

.pc-product-card--interactive:hover .pc-product-card__media img { transform: scale(1.03); }
.pc-product-card__badges { position: absolute; inset: var(--pc-space-3) var(--pc-space-3) auto; display: flex; flex-wrap: wrap; gap: var(--pc-space-2); }
.pc-product-card__body { display: flex; flex: 1; flex-direction: column; min-width: 0; padding: var(--pc-space-5); }
.pc-product-card__category { margin: 0 0 var(--pc-space-1); color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-bold); letter-spacing: .12em; text-transform: uppercase; }
.pc-product-card h2 { display: -webkit-box; overflow: hidden; margin: 0 0 var(--pc-space-2); color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-md); font-weight: var(--pc-font-weight-semibold); line-height: var(--pc-font-line-height-tight); -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.pc-product-card__description { display: -webkit-box; overflow: hidden; min-height: calc(var(--pc-font-size-sm) * var(--pc-font-line-height-normal) * 2); margin: 0 0 var(--pc-space-3); color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.pc-product-card__specs { display: flex; flex-wrap: wrap; gap: var(--pc-space-1); margin-bottom: var(--pc-space-3); }
.pc-product-card__specs span { padding: var(--pc-space-1) var(--pc-space-2); border-radius: var(--pc-radius-sm); background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-xs); }
.pc-product-card__footer { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--pc-space-3); margin-top: auto; padding-top: var(--pc-space-3); }
.pc-product-card__price { display: flex; min-width: 0; flex-wrap: wrap; align-items: baseline; gap: var(--pc-space-2); }
.pc-product-card__price strong { color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-lg); font-weight: var(--pc-font-weight-bold); }
.pc-product-card__price del { color: var(--pc-color-semantic-text-subtle); font-size: var(--pc-font-size-xs); }
</style>
