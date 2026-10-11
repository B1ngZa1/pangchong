<template>
  <section class="pc-empty-state" :aria-labelledby="titleId">
    <div v-if="$slots.visual" class="pc-empty-state__visual" aria-hidden="true">
      <slot name="visual" />
    </div>
    <h2 :id="titleId">{{ title }}</h2>
    <p v-if="description">{{ description }}</p>
    <div v-if="$slots.action" class="pc-empty-state__action">
      <slot name="action" />
    </div>
  </section>
</template>

<script>
let emptyStateCounter = 0
</script>

<script setup>
const props = defineProps({
  id: String,
  title: {
    type: String,
    required: true,
  },
  description: String,
})

const titleId = props.id ? `${props.id}-title` : `pc-empty-state-${++emptyStateCounter}-title`
</script>

<style scoped>
.pc-empty-state {
  display: grid;
  min-height: 16rem;
  place-items: center;
  align-content: center;
  gap: var(--pc-space-3);
  padding: var(--pc-space-8);
  border: 1px dashed var(--pc-color-semantic-border-default);
  border-radius: var(--pc-radius-lg);
  background: var(--pc-color-semantic-background-surface);
  text-align: center;
}

.pc-empty-state__visual {
  margin-bottom: var(--pc-space-2);
  color: var(--pc-color-semantic-text-accent);
}

.pc-empty-state h2 {
  margin: 0;
  color: var(--pc-color-semantic-text-primary);
  font-size: var(--pc-font-size-xl);
  font-weight: var(--pc-font-weight-bold);
}

.pc-empty-state p {
  max-width: 32rem;
  margin: 0;
  color: var(--pc-color-semantic-text-muted);
  font-size: var(--pc-font-size-sm);
  line-height: var(--pc-font-line-height-relaxed);
}

.pc-empty-state__action {
  margin-top: var(--pc-space-3);
}
</style>
