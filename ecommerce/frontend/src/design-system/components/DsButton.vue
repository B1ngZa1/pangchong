<template>
  <button
    class="pc-button"
    :class="{ 'pc-button--block': block }"
    :data-variant="variant"
    :data-size="size"
    :type="type"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
  >
    <span v-if="loading" class="pc-button__spinner" aria-hidden="true" />
    <span class="pc-button__label"><slot /></span>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: value => ['primary', 'secondary', 'ghost', 'danger'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: value => ['sm', 'md', 'lg'].includes(value),
  },
  type: {
    type: String,
    default: 'button',
  },
  disabled: Boolean,
  loading: Boolean,
  block: Boolean,
})
</script>

<style scoped>
.pc-button {
  display: inline-flex;
  min-width: max-content;
  align-items: center;
  justify-content: center;
  gap: var(--pc-space-2);
  height: var(--pc-size-control-md);
  padding: 0 var(--pc-space-5);
  border: 1px solid transparent;
  border-radius: var(--pc-radius-md);
  color: var(--pc-color-semantic-text-inverse);
  font: inherit;
  font-size: var(--pc-font-size-sm);
  font-weight: var(--pc-font-weight-bold);
  line-height: 1;
  cursor: pointer;
  transition:
    background-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    border-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    transform var(--pc-motion-duration-fast) var(--pc-motion-ease-standard);
}

.pc-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.pc-button:active:not(:disabled) {
  transform: translateY(0);
}

.pc-button:focus-visible {
  outline: 2px solid var(--pc-color-semantic-border-focus);
  outline-offset: 2px;
  box-shadow: var(--pc-shadow-focus);
}

.pc-button:disabled {
  color: var(--pc-color-semantic-text-muted);
  background: var(--pc-color-semantic-action-disabled);
  cursor: not-allowed;
  opacity: var(--pc-opacity-disabled);
}

.pc-button[data-variant='primary'] {
  background: var(--pc-color-semantic-action-primary);
}

.pc-button[data-variant='primary']:hover:not(:disabled) {
  background: var(--pc-color-semantic-action-primary-hover);
}

.pc-button[data-variant='primary']:active:not(:disabled) {
  background: var(--pc-color-semantic-action-primary-active);
}

.pc-button[data-variant='secondary'] {
  border-color: var(--pc-color-semantic-border-default);
  background: var(--pc-color-semantic-action-secondary);
  color: var(--pc-color-semantic-text-primary);
}

.pc-button[data-variant='secondary']:hover:not(:disabled) {
  border-color: var(--pc-color-semantic-border-strong);
  background: var(--pc-color-semantic-action-secondary-hover);
}

.pc-button[data-variant='ghost'] {
  background: transparent;
  color: var(--pc-color-semantic-text-secondary);
}

.pc-button[data-variant='ghost']:hover:not(:disabled) {
  background: var(--pc-color-semantic-action-secondary);
  color: var(--pc-color-semantic-text-primary);
}

.pc-button[data-variant='danger'] {
  background: var(--pc-color-red-500);
  color: var(--pc-color-dark-50);
}

.pc-button[data-size='sm'] {
  height: var(--pc-size-control-sm);
  padding: 0 var(--pc-space-3);
  font-size: var(--pc-font-size-xs);
}

.pc-button[data-size='lg'] {
  height: var(--pc-size-control-lg);
  padding: 0 var(--pc-space-6);
  font-size: var(--pc-font-size-md);
}

.pc-button--block {
  width: 100%;
}

.pc-button__spinner {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: var(--pc-radius-full);
  animation: pc-button-spin var(--pc-motion-duration-loading) var(--pc-motion-ease-linear) infinite;
}

@keyframes pc-button-spin {
  to { transform: rotate(360deg); }
}
</style>
