<template>
  <span
    class="pc-skeleton"
    :data-variant="variant"
    :style="styleObject"
    aria-hidden="true"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'text',
    validator: value => ['text', 'rect', 'circle'].includes(value),
  },
  width: {
    type: String,
    default: undefined,
  },
  height: {
    type: String,
    default: undefined,
  },
})

const styleObject = computed(() => ({
  width: props.width,
  height: props.height,
}))
</script>

<style scoped>
.pc-skeleton {
  display: block;
  width: 100%;
  height: var(--pc-font-size-md);
  border-radius: var(--pc-radius-sm);
  background:
    linear-gradient(90deg,
      var(--pc-color-semantic-background-elevated) 20%,
      var(--pc-color-semantic-border-default) 50%,
      var(--pc-color-semantic-background-elevated) 80%);
  background-size: 200% 100%;
  animation: pc-skeleton-shimmer var(--pc-motion-duration-shimmer) var(--pc-motion-ease-standard) infinite;
}

.pc-skeleton[data-variant='rect'] {
  min-height: 6rem;
  border-radius: var(--pc-radius-md);
}

.pc-skeleton[data-variant='circle'] {
  width: 3rem;
  height: 3rem;
  border-radius: var(--pc-radius-full);
}

@keyframes pc-skeleton-shimmer {
  to { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .pc-skeleton { animation: none; }
}
</style>
