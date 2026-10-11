<template>
  <label class="pc-checkbox" :data-disabled="disabled || undefined">
    <input
      ref="input"
      class="pc-checkbox__input"
      type="checkbox"
      :checked="modelValue"
      :disabled="disabled"
      :aria-checked="mixed ? 'mixed' : String(modelValue)"
      :aria-describedby="description ? descriptionId : undefined"
      @change="emit('update:modelValue', $event.target.checked)"
    >
    <span class="pc-checkbox__box" aria-hidden="true"><span class="pc-checkbox__mark" /></span>
    <span class="pc-checkbox__content">
      <span class="pc-checkbox__label">{{ label }}</span>
      <span v-if="description" :id="descriptionId" class="pc-checkbox__description">{{ description }}</span>
    </span>
  </label>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'

let checkboxCounter = 0
const props = defineProps({
  modelValue: Boolean,
  label: { type: String, required: true },
  description: String,
  disabled: Boolean,
  mixed: Boolean,
})
const emit = defineEmits(['update:modelValue'])
const input = ref(null)
const descriptionId = `pc-checkbox-${++checkboxCounter}-description`

function syncIndeterminate() {
  if (input.value) input.value.indeterminate = props.mixed
}

onMounted(syncIndeterminate)
watch(() => props.mixed, () => nextTick(syncIndeterminate))
</script>

<style scoped>
.pc-checkbox { display: inline-flex; min-height: var(--pc-size-control-touch); align-items: center; gap: var(--pc-space-3); color: var(--pc-color-semantic-text-secondary); cursor: pointer; touch-action: manipulation; }
.pc-checkbox[data-disabled] { cursor: not-allowed; opacity: var(--pc-opacity-disabled); }
.pc-checkbox__input { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.pc-checkbox__box { display: grid; width: 1.25rem; height: 1.25rem; flex: 0 0 1.25rem; place-items: center; border: 2px solid var(--pc-color-semantic-border-strong); border-radius: var(--pc-radius-sm); background: transparent; }
.pc-checkbox__mark { width: .65rem; height: .35rem; border-bottom: 2px solid var(--pc-color-semantic-text-inverse); border-left: 2px solid var(--pc-color-semantic-text-inverse); transform: rotate(-45deg) scale(0); transition: transform var(--pc-motion-duration-fast) var(--pc-motion-ease-standard); }
.pc-checkbox__input:checked + .pc-checkbox__box, .pc-checkbox__input:indeterminate + .pc-checkbox__box { border-color: var(--pc-color-semantic-action-primary); background: var(--pc-color-semantic-action-primary); }
.pc-checkbox__input:checked + .pc-checkbox__box .pc-checkbox__mark { transform: rotate(-45deg) scale(1); }
.pc-checkbox__input:indeterminate + .pc-checkbox__box .pc-checkbox__mark { width: .65rem; height: 2px; border: 0; border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-text-inverse); transform: scale(1); }
.pc-checkbox__input:focus-visible + .pc-checkbox__box { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 3px; }
.pc-checkbox__content { display: grid; gap: var(--pc-space-1); }
.pc-checkbox__label { font-size: var(--pc-font-size-sm); }
.pc-checkbox__description { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); line-height: var(--pc-font-line-height-normal); }
@media (prefers-reduced-motion: reduce) { .pc-checkbox__mark { transition: none; } }
</style>
