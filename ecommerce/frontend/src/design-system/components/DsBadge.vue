<template>
  <span class="pc-badge" :data-tone="tone"><slot /></span>
</template>

<script setup>
defineProps({
  tone: {
    type: String,
    default: 'neutral',
    validator: value => ['neutral', 'accent', 'success', 'warning', 'danger', 'info'].includes(value),
  },
})
</script>

<style scoped>
.pc-badge {
  display: inline-flex;
  min-height: 1.5rem;
  align-items: center;
  gap: var(--pc-space-1);
  padding: 0 var(--pc-space-2);
  border: 1px solid var(--pc-color-semantic-border-default);
  border-radius: var(--pc-radius-full);
  background: var(--pc-color-semantic-background-elevated);
  color: var(--pc-color-semantic-text-secondary);
  font-size: var(--pc-font-size-xs);
  font-weight: var(--pc-font-weight-semibold);
  line-height: 1;
}

.pc-badge[data-tone='accent'],
.pc-badge[data-tone='success'] {
  border-color: var(--pc-color-brand-700);
  background: rgb(var(--pc-color-brand-900-rgb) / var(--pc-opacity-status));
  color: var(--pc-color-brand-300);
}

.pc-badge[data-tone='warning'] {
  border-color: var(--pc-color-amber-500);
  background: rgb(var(--pc-color-amber-900-rgb) / var(--pc-opacity-status));
  color: var(--pc-color-amber-300);
}

.pc-badge[data-tone='danger'] {
  border-color: var(--pc-color-red-500);
  background: rgb(var(--pc-color-red-900-rgb) / var(--pc-opacity-status));
  color: var(--pc-color-red-400);
}

.pc-badge[data-tone='info'] {
  border-color: var(--pc-color-blue-500);
  background: rgb(var(--pc-color-blue-900-rgb) / var(--pc-opacity-status));
  color: var(--pc-color-blue-300);
}
</style>
