<template>
  <button
    class="pc-icon-button"
    :class="{ 'pc-icon-button--block': block }"
    :data-variant="variant"
    :data-size="size"
    :type="type"
    :disabled="disabled || loading"
    :aria-label="label"
    :aria-pressed="pressed === undefined ? undefined : String(pressed)"
    :aria-busy="loading || undefined"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="pc-icon-button__spinner" aria-hidden="true" />
    <span v-else class="pc-icon-button__icon" aria-hidden="true"><slot /></span>
  </button>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  variant: {
    type: String,
    default: 'ghost',
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
  pressed: {
    type: Boolean,
    default: undefined,
  },
})

defineEmits(['click'])
</script>

<style scoped>
.pc-icon-button {
  display: inline-grid;
  width: var(--pc-size-control-md);
  height: var(--pc-size-control-md);
  flex: 0 0 auto;
  place-items: center;
  padding: 0;
  border: 1px solid transparent;
  border-radius: var(--pc-radius-md);
  background: transparent;
  color: var(--pc-color-semantic-text-secondary);
  cursor: pointer;
  transition:
    background-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    border-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    transform var(--pc-motion-duration-fast) var(--pc-motion-ease-standard);
}

.pc-icon-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.pc-icon-button:active:not(:disabled) {
  transform: translateY(0);
}

.pc-icon-button:focus-visible {
  outline: 2px solid var(--pc-color-semantic-border-focus);
  outline-offset: 2px;
  box-shadow: var(--pc-shadow-focus);
}

.pc-icon-button:disabled {
  color: var(--pc-color-semantic-text-muted);
  cursor: not-allowed;
  opacity: var(--pc-opacity-muted);
}

.pc-icon-button[data-variant='primary'] {
  background: var(--pc-color-semantic-action-primary);
  color: var(--pc-color-semantic-text-inverse);
}

.pc-icon-button[data-variant='primary']:hover:not(:disabled) {
  background: var(--pc-color-semantic-action-primary-hover);
}

.pc-icon-button[data-variant='secondary'] {
  border-color: var(--pc-color-semantic-border-default);
  background: var(--pc-color-semantic-action-secondary);
  color: var(--pc-color-semantic-text-primary);
}

.pc-icon-button[data-variant='secondary']:hover:not(:disabled),
.pc-icon-button[data-variant='ghost']:hover:not(:disabled) {
  border-color: var(--pc-color-semantic-border-strong);
  background: var(--pc-color-semantic-action-secondary-hover);
  color: var(--pc-color-semantic-text-primary);
}

.pc-icon-button[data-variant='danger'] {
  background: var(--pc-color-red-500);
  color: var(--pc-color-dark-50);
}

.pc-icon-button[data-size='sm'] {
  width: var(--pc-size-control-sm);
  height: var(--pc-size-control-sm);
}

.pc-icon-button[data-size='lg'] {
  width: var(--pc-size-control-lg);
  height: var(--pc-size-control-lg);
}

.pc-icon-button--block {
  width: 100%;
}

.pc-icon-button__icon,
.pc-icon-button__spinner {
  display: inline-grid;
  width: 1.125rem;
  height: 1.125rem;
  place-items: center;
}

.pc-icon-button__spinner {
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: var(--pc-radius-full);
  animation: pc-icon-button-spin var(--pc-motion-duration-loading) var(--pc-motion-ease-linear) infinite;
}

@keyframes pc-icon-button-spin {
  to { transform: rotate(360deg); }
}
</style>
