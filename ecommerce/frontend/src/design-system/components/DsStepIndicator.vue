<template>
  <nav class="pc-step-indicator" :aria-label="ariaLabel">
    <ol class="pc-step-indicator__list">
      <li v-for="(step, index) in normalizedSteps" :key="step.id || index" class="pc-step-indicator__item">
        <button
          class="pc-step-indicator__step"
          :class="{
            'pc-step-indicator__step--active': index === modelValue,
            'pc-step-indicator__step--complete': index < modelValue,
          }"
          type="button"
          :aria-current="index === modelValue ? 'step' : undefined"
          :aria-label="`第${index + 1}步：${step.label}`"
          :disabled="!allowNavigation || index > modelValue"
          @click="select(index)"
        >
          <span class="pc-step-indicator__marker" aria-hidden="true">
            <span v-if="index < modelValue">✓</span>
            <span v-else>{{ index + 1 }}</span>
          </span>
          <span class="pc-step-indicator__label">{{ step.label }}</span>
        </button>
        <span
          v-if="index < normalizedSteps.length - 1"
          class="pc-step-indicator__connector"
          :class="{ 'pc-step-indicator__connector--complete': index < modelValue }"
          aria-hidden="true"
        />
      </li>
    </ol>
    <p class="pc-step-indicator__status" aria-live="polite">第{{ modelValue + 1 }}步，共{{ normalizedSteps.length }}步：{{ currentStep?.label }}</p>
  </nav>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  steps: {
    type: Array,
    required: true,
    validator: value => value.length > 0 && value.every(step => typeof step === 'string' || (step && step.label)),
  },
  modelValue: {
    type: Number,
    default: 0,
    validator: value => value >= 0,
  },
  ariaLabel: {
    type: String,
    default: '结算步骤',
  },
  allowNavigation: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue', 'change'])
const normalizedSteps = computed(() => props.steps.map((step, index) => typeof step === 'string' ? { id: String(index), label: step } : step))
const currentStep = computed(() => normalizedSteps.value[props.modelValue] || normalizedSteps.value[0])

function select(index) {
  if (!props.allowNavigation || index > props.modelValue || index === props.modelValue) return
  emit('update:modelValue', index)
  emit('change', index)
}
</script>

<style scoped>
.pc-step-indicator { display: grid; min-width: 0; gap: var(--pc-space-3); margin-bottom: var(--pc-space-10); }
.pc-step-indicator__list { display: flex; width: 100%; max-width: 100%; align-items: flex-start; justify-content: center; margin: 0; overflow-x: auto; padding: 0 var(--pc-space-2) var(--pc-space-2); list-style: none; scrollbar-width: thin; }
.pc-step-indicator__item { display: flex; min-width: 0; align-items: flex-start; }
.pc-step-indicator__step { display: inline-flex; min-width: var(--pc-size-control-touch); min-height: var(--pc-size-control-touch); align-items: center; gap: var(--pc-space-2); padding: 0; border: 0; background: transparent; color: var(--pc-color-semantic-text-muted); cursor: pointer; font: inherit; }
.pc-step-indicator__step:disabled { cursor: default; }
.pc-step-indicator__step:not(:disabled):hover .pc-step-indicator__label { color: var(--pc-color-semantic-text-primary); }
.pc-step-indicator__step:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 3px; border-radius: var(--pc-radius-sm); }
.pc-step-indicator__marker { display: grid; width: 2rem; height: 2rem; flex: 0 0 2rem; place-items: center; border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-bold); }
.pc-step-indicator__label { color: inherit; font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-semibold); white-space: nowrap; }
.pc-step-indicator__step--active, .pc-step-indicator__step--complete { color: var(--pc-color-semantic-text-accent); }
.pc-step-indicator__step--active .pc-step-indicator__marker, .pc-step-indicator__step--complete .pc-step-indicator__marker { background: var(--pc-color-semantic-action-primary); color: var(--pc-color-dark-950); }
.pc-step-indicator__connector { width: clamp(2rem, 5vw, 3.5rem); height: 2px; margin: 1rem var(--pc-space-3) 0; background: var(--pc-color-semantic-border-default); }
.pc-step-indicator__connector--complete { background: var(--pc-color-semantic-action-primary); }
.pc-step-indicator__status { margin: 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); text-align: center; }
@media (max-width: 639px) {
  .pc-step-indicator__list { justify-content: flex-start; }
  .pc-step-indicator__label { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; }
  .pc-step-indicator__connector { width: clamp(1rem, 10vw, 2rem); margin-inline: var(--pc-space-2); }
}
</style>
