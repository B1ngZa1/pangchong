<template>
  <article class="pc-media-category-card" :class="{ 'pc-media-category-card--interactive': interactive }">
    <div class="pc-media-category-card__media">
      <img :src="imageSource" :alt="alt || title" loading="lazy" @error="handleImageError">
    </div>
    <div class="pc-media-category-card__body">
      <p v-if="eyebrow" class="pc-media-category-card__eyebrow">{{ eyebrow }}</p>
      <h3>{{ title }}</h3>
      <p v-if="description" class="pc-media-category-card__description">{{ description }}</p>
      <a class="pc-media-category-card__link" :href="href" :target="target" :rel="target === '_blank' ? 'noreferrer' : undefined">
        <span>{{ linkLabel }}</span>
        <span aria-hidden="true">→</span>
      </a>
    </div>
  </article>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  image: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  href: { type: String, default: '#' },
  linkLabel: { type: String, default: '了解系列' },
  alt: { type: String, default: '' },
  fallbackImage: { type: String, default: '/assets/pangchong-product-fallback.png' },
  target: { type: String, default: undefined },
  interactive: { type: Boolean, default: true },
})

const imageSource = ref(props.image)

function handleImageError() {
  if (imageSource.value !== props.fallbackImage) imageSource.value = props.fallbackImage
}
</script>

<style scoped>
.pc-media-category-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--pc-color-semantic-border-subtle);
  border-radius: var(--pc-radius-xl);
  background: var(--pc-color-semantic-background-surface);
  color: var(--pc-color-semantic-text-primary);
  box-shadow: var(--pc-shadow-sm);
}

.pc-media-category-card--interactive {
  transition:
    border-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    box-shadow var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    transform var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}

.pc-media-category-card--interactive:hover {
  border-color: var(--pc-color-semantic-border-accent);
  box-shadow: var(--pc-shadow-md);
  transform: translateY(-2px);
}

.pc-media-category-card:focus-within {
  border-color: var(--pc-color-semantic-border-focus);
  box-shadow: var(--pc-shadow-focus);
}

.pc-media-category-card__media {
  aspect-ratio: 16 / 10;
  overflow: hidden;
  background: var(--pc-color-semantic-background-elevated);
}

.pc-media-category-card__media img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--pc-motion-duration-slow) var(--pc-motion-ease-standard);
}

.pc-media-category-card--interactive:hover .pc-media-category-card__media img { transform: scale(1.03); }
.pc-media-category-card__body { display: flex; flex: 1; flex-direction: column; gap: var(--pc-space-2); padding: var(--pc-density-comfortable-padding); }
.pc-media-category-card__eyebrow { margin: 0; color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-bold); letter-spacing: .12em; text-transform: uppercase; }
.pc-media-category-card h3 { margin: 0; font-size: var(--pc-font-size-xl); line-height: var(--pc-font-line-height-tight); }
.pc-media-category-card__description { margin: 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); }
.pc-media-category-card__link { display: inline-flex; width: fit-content; align-items: center; gap: var(--pc-space-2); min-height: var(--pc-size-control-touch); margin-top: auto; color: var(--pc-color-semantic-text-accent); font-weight: var(--pc-font-weight-semibold); text-decoration: none; }
.pc-media-category-card__link:hover { color: var(--pc-color-semantic-action-primary-hover); }
.pc-media-category-card__link:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 3px; border-radius: var(--pc-radius-sm); }
@media (prefers-reduced-motion: reduce) {
  .pc-media-category-card--interactive, .pc-media-category-card__media img { transition: none; }
}
</style>
