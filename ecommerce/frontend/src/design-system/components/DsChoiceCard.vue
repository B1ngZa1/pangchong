<template>
  <label
    class="pc-choice-card"
    :data-selected="selected || undefined"
    :data-disabled="disabled || undefined"
  >
    <input
      class="pc-choice-card__input"
      :id="fieldId"
      :name="name"
      :type="type"
      :value="value"
      :checked="selected"
      :disabled="disabled"
      :aria-describedby="description ? descriptionId : undefined"
      @change="select"
    >
    <span class="pc-choice-card__indicator" aria-hidden="true"></span>
    <span class="pc-choice-card__content">
      <span class="pc-choice-card__topline">
        <span class="pc-choice-card__title">{{ title }}</span>
        <span v-if="$slots.meta" class="pc-choice-card__meta"><slot name="meta" /></span>
      </span>
      <span v-if="description" :id="descriptionId" class="pc-choice-card__description">{{ description }}</span>
      <span v-if="$slots.default" class="pc-choice-card__details"><slot /></span>
    </span>
    <span v-if="$slots.trailing" class="pc-choice-card__trailing"><slot name="trailing" /></span>
  </label>
</template>

<script>
let choiceCounter = 0
</script>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean, Array],
    default: '',
  },
  value: {
    type: [String, Number, Boolean],
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  description: String,
  name: String,
  type: {
    type: String,
    default: 'radio',
    validator: value => ['radio', 'checkbox'].includes(value),
  },
  disabled: Boolean,
  id: String,
})

const emit = defineEmits(['update:modelValue', 'change'])
const generatedId = 'pc-choice-card-' + (++choiceCounter)
const fieldId = computed(() => props.id || generatedId)
const descriptionId = computed(() => fieldId.value + '-description')
const selected = computed(() => {
  if (props.type === 'checkbox' && Array.isArray(props.modelValue)) {
    return props.modelValue.includes(props.value)
  }
  return props.modelValue === props.value
})

function select(event) {
  if (props.type === 'checkbox') {
    const current = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    const next = event.target.checked
      ? [...new Set([...current, props.value])]
      : current.filter(item => item !== props.value)
    emit('update:modelValue', next)
    emit('change', next)
    return
  }
  emit('update:modelValue', props.value)
  emit('change', props.value)
}
</script>

<style scoped>
.pc-choice-card {
  position: relative;
  display: flex;
  min-width: 0;
  align-items: flex-start;
  gap: var(--pc-space-3);
  padding: var(--pc-space-4);
  border: 1px solid var(--pc-color-semantic-border-default);
  border-radius: var(--pc-radius-lg);
  background: var(--pc-color-semantic-background-surface);
  color: var(--pc-color-semantic-text-primary);
  cursor: pointer;
  transition:
    border-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    background-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    box-shadow var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}
.pc-choice-card:hover:not([data-disabled]) { border-color: var(--pc-color-semantic-border-strong); }
.pc-choice-card[data-selected] {
  border-color: var(--pc-color-semantic-action-primary);
  background: color-mix(in srgb, var(--pc-color-semantic-action-primary) 10%, transparent);
  box-shadow: var(--pc-shadow-focus);
}
.pc-choice-card[data-disabled] { cursor: not-allowed; opacity: var(--pc-opacity-disabled); }
.pc-choice-card__input {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
.pc-choice-card__indicator {
  display: grid;
  width: 1.25rem;
  height: 1.25rem;
  flex: 0 0 1.25rem;
  margin-top: 0.125rem;
  place-items: center;
  border: 2px solid var(--pc-color-semantic-border-strong);
  border-radius: var(--pc-radius-full);
  background: transparent;
}
.pc-choice-card[data-selected] .pc-choice-card__indicator {
  border-color: var(--pc-color-semantic-action-primary);
  background: var(--pc-color-semantic-action-primary);
  box-shadow: inset 0 0 0 3px var(--pc-color-semantic-background-surface);
}
.pc-choice-card[data-disabled] .pc-choice-card__indicator { border-color: var(--pc-color-semantic-border-default); }
.pc-choice-card__content { display: grid; min-width: 0; flex: 1; gap: var(--pc-space-1); }
.pc-choice-card__topline { display: flex; flex-wrap: wrap; align-items: center; gap: var(--pc-space-2); }
.pc-choice-card__title { font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-semibold); }
.pc-choice-card__meta, .pc-choice-card__trailing { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); }
.pc-choice-card__description, .pc-choice-card__details { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); line-height: var(--pc-font-line-height-normal); }
.pc-choice-card__input:focus-visible + .pc-choice-card__indicator { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 3px; }
.pc-choice-card__trailing { margin-left: auto; text-align: right; }
</style>
