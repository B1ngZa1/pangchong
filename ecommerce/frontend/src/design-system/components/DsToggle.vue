<template>
  <button
    class="pc-toggle"
    :class="{ 'pc-toggle--checked': modelValue }"
    type="button"
    role="switch"
    :aria-checked="String(modelValue)"
    :aria-label="label"
    :disabled="disabled"
    @click="$emit('update:modelValue', !modelValue)"
  >
    <span class="pc-toggle__track" aria-hidden="true">
      <span class="pc-toggle__thumb" />
    </span>
    <span v-if="showState" class="pc-toggle__state">{{ modelValue ? onLabel : offLabel }}</span>
  </button>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  label: {
    type: String,
    required: true,
  },
  disabled: Boolean,
  showState: {
    type: Boolean,
    default: true,
  },
  onLabel: {
    type: String,
    default: '已开启',
  },
  offLabel: {
    type: String,
    default: '已关闭',
  },
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.pc-toggle {
  display: inline-flex;
  min-height: var(--pc-size-control-touch);
  align-items: center;
  justify-content: flex-end;
  gap: var(--pc-space-2);
  border: 0;
  background: transparent;
  color: var(--pc-color-semantic-text-secondary);
  cursor: pointer;
  font: inherit;
}
.pc-toggle:disabled { cursor: not-allowed; opacity: var(--pc-opacity-disabled); }
.pc-toggle:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 3px; border-radius: var(--pc-radius-md); }
.pc-toggle__track {
  position: relative;
  display: inline-flex;
  width: 2.75rem;
  height: 1.5rem;
  align-items: center;
  padding: 0.125rem;
  border-radius: var(--pc-radius-full);
  background: var(--pc-color-semantic-action-disabled);
  transition: background-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}
.pc-toggle--checked .pc-toggle__track { background: var(--pc-color-semantic-action-primary); }
.pc-toggle__thumb {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: var(--pc-radius-full);
  background: var(--pc-color-semantic-text-primary);
  box-shadow: var(--pc-shadow-sm);
  transform: translateX(0);
  transition: transform var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}
.pc-toggle--checked .pc-toggle__thumb { transform: translateX(1.25rem); }
.pc-toggle__state { min-width: 3.5rem; text-align: right; font-size: var(--pc-font-size-xs); }
@media (prefers-reduced-motion: reduce) {
  .pc-toggle__track, .pc-toggle__thumb { transition: none; }
}
</style>
