<template>
  <form class="pc-search-field" :class="{ 'pc-search-field--compact': compact }" role="search" @submit.prevent="submit">
    <DsField
      v-model="value"
      class="pc-search-field__field"
      :label="label"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :type="type"
    />
    <DsIconButton
      class="pc-search-field__submit"
      :label="submitLabel"
      type="submit"
      variant="primary"
      size="sm"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M5 12h14M13 6l6 6-6 6" />
      </svg>
    </DsIconButton>
  </form>
</template>

<script setup>
import { computed } from 'vue'
import DsField from './DsField.vue'
import DsIconButton from './DsIconButton.vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '搜索',
  },
  placeholder: String,
  submitLabel: {
    type: String,
    default: '提交搜索',
  },
  autocomplete: {
    type: String,
    default: 'off',
  },
  type: {
    type: String,
    default: 'search',
  },
  compact: Boolean,
})

const emit = defineEmits(['update:modelValue', 'submit'])
const value = computed({
  get: () => props.modelValue,
  set: nextValue => emit('update:modelValue', nextValue),
})

function submit() {
  emit('submit', props.modelValue.trim())
}
</script>

<style scoped>
.pc-search-field { position: relative; display: flex; align-items: flex-end; gap: var(--pc-space-2); }
.pc-search-field__field { min-width: 0; flex: 1; }
.pc-search-field__field :deep(.pc-field__label) { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.pc-search-field__submit { flex: 0 0 auto; }
.pc-search-field__submit :deep(svg) { width: 1rem; height: 1rem; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.pc-search-field--compact .pc-search-field__field :deep(.pc-field__control) { height: var(--pc-size-control-md); padding-inline: var(--pc-space-3); }
</style>
