<template>
  <div class="pc-field" :data-invalid="Boolean(error) || undefined">
    <label :for="fieldId" class="pc-field__label">
      {{ label }}
      <span v-if="required" aria-hidden="true">*</span>
    </label>
    <select
      v-if="as === 'select'"
      :id="fieldId"
      class="pc-field__control"
      :name="name"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :aria-invalid="Boolean(error) || undefined"
      :aria-describedby="descriptionId"
      :autocomplete="autocomplete"
      @change="$emit('update:modelValue', $event.target.value); $emit('change', $event)"
    >
      <option value="">{{ placeholder || `选择${label}` }}</option>
      <option v-for="option in normalizedOptions" :key="option.value" :value="option.value" :disabled="option.disabled">
        {{ option.label }}
      </option>
    </select>
    <textarea
      v-else-if="as === 'textarea'"
      :id="fieldId"
      class="pc-field__control pc-field__control--textarea"
      :name="name"
      :value="modelValue"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :inputmode="inputmode"
      :disabled="disabled"
      :required="required"
      :rows="rows"
      :aria-invalid="Boolean(error) || undefined"
      :aria-describedby="descriptionId"
      :autocomplete="autocomplete"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <input
      v-else
      :id="fieldId"
      class="pc-field__control"
      :name="name"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :inputmode="inputmode"
      :disabled="disabled"
      :required="required"
      :aria-invalid="Boolean(error) || undefined"
      :aria-describedby="descriptionId"
      :autocomplete="autocomplete"
      @input="$emit('update:modelValue', $event.target.value)"
    >
    <p v-if="error" :id="errorId" class="pc-field__error" role="alert">{{ error }}</p>
    <p v-else-if="hint" :id="hintId" class="pc-field__hint">{{ hint }}</p>
  </div>
</template>

<script>
let fieldCounter = 0
</script>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  id: String,
  name: String,
  label: {
    type: String,
    required: true,
  },
  modelValue: {
    type: [String, Number],
    default: '',
  },
  type: {
    type: String,
    default: 'text',
  },
  as: {
    type: String,
    default: 'input',
    validator: value => ['input', 'select', 'textarea'].includes(value),
  },
  options: {
    type: Array,
    default: () => [],
  },
  rows: {
    type: [String, Number],
    default: 3,
  },
  autocomplete: String,
  inputmode: String,
  maxlength: [String, Number],
  placeholder: String,
  hint: String,
  error: String,
  required: Boolean,
  disabled: Boolean,
})

defineEmits(['update:modelValue', 'change'])

const generatedId = `pc-field-${++fieldCounter}`
const fieldId = computed(() => props.id || generatedId)
const hintId = computed(() => `${fieldId.value}-hint`)
const errorId = computed(() => `${fieldId.value}-error`)
const descriptionId = computed(() => props.error ? errorId.value : (props.hint ? hintId.value : undefined))
const normalizedOptions = computed(() => props.options.map(option => {
  if (typeof option === 'string') return { value: option, label: option, disabled: false }
  return { value: String(option.value ?? ''), label: option.label ?? option.value ?? '', disabled: Boolean(option.disabled) }
}))
</script>

<style scoped>
.pc-field {
  display: grid;
  gap: var(--pc-space-2);
}

.pc-field__label {
  color: var(--pc-color-semantic-text-secondary);
  font-size: var(--pc-font-size-sm);
  font-weight: var(--pc-font-weight-semibold);
}

.pc-field__label span,
.pc-field__error {
  color: var(--pc-color-semantic-text-danger);
}

.pc-field__control {
  width: 100%;
  height: var(--pc-size-control-lg);
  padding: 0 var(--pc-space-4);
  border: 1px solid var(--pc-color-semantic-border-default);
  border-radius: var(--pc-radius-md);
  background: var(--pc-color-semantic-background-elevated);
  color: var(--pc-color-semantic-text-primary);
  font: inherit;
  font-size: var(--pc-font-size-md);
  transition:
    border-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    box-shadow var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}

.pc-field__control--textarea {
  height: auto;
  min-height: calc(var(--pc-size-control-lg) * 2);
  padding-top: var(--pc-space-3);
  padding-bottom: var(--pc-space-3);
  resize: vertical;
}

.pc-field__control::placeholder {
  color: var(--pc-color-semantic-text-subtle);
}

.pc-field__control:focus-visible {
  outline: 0;
  border-color: var(--pc-color-semantic-border-focus);
  box-shadow: var(--pc-shadow-focus);
}

.pc-field[data-invalid] .pc-field__control {
  border-color: var(--pc-color-semantic-border-danger);
}

.pc-field__control:disabled {
  cursor: not-allowed;
  opacity: var(--pc-opacity-disabled);
}

.pc-field__hint,
.pc-field__error {
  margin: 0;
  font-size: var(--pc-font-size-xs);
  line-height: var(--pc-font-line-height-normal);
}

.pc-field__hint {
  color: var(--pc-color-semantic-text-muted);
}
</style>
