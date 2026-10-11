<template>
  <aside
    class="pc-alert"
    :data-tone="tone"
    :role="role"
    aria-live="polite"
    :aria-labelledby="titleId"
  >
    <div class="pc-alert__mark" aria-hidden="true"><slot name="icon">!</slot></div>
    <div class="pc-alert__content">
      <h2 :id="titleId">{{ title }}</h2>
      <p v-if="description">{{ description }}</p>
      <div v-if="$slots.action" class="pc-alert__action"><slot name="action" /></div>
    </div>
    <button
      v-if="dismissible"
      class="pc-alert__dismiss"
      type="button"
      aria-label="关闭提示"
      @click="$emit('dismiss')"
    >
      ×
    </button>
  </aside>
</template>

<script>
let alertCounter = 0
</script>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: String,
  tone: {
    type: String,
    default: 'info',
    validator: value => ['neutral', 'info', 'success', 'warning', 'danger'].includes(value),
  },
  role: {
    type: String,
    default: 'status',
    validator: value => ['status', 'alert'].includes(value),
  },
  dismissible: Boolean,
})

defineEmits(['dismiss'])

const titleId = computed(() => `pc-alert-${++alertCounter}-title`)
</script>

<style scoped>
.pc-alert {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: var(--pc-space-3);
  align-items: start;
  padding: var(--pc-space-4);
  border: 1px solid var(--pc-color-semantic-border-default);
  border-radius: var(--pc-radius-md);
  background: var(--pc-color-semantic-background-surface);
  color: var(--pc-color-semantic-text-primary);
}

.pc-alert__mark {
  display: grid;
  width: 1.5rem;
  height: 1.5rem;
  place-items: center;
  border-radius: var(--pc-radius-full);
  background: var(--pc-color-semantic-background-info);
  color: var(--pc-color-semantic-text-info);
  font-size: var(--pc-font-size-sm);
  font-weight: var(--pc-font-weight-bold);
}

.pc-alert[data-tone='success'] .pc-alert__mark {
  background: rgb(var(--pc-color-brand-900-rgb) / var(--pc-opacity-status));
  color: var(--pc-color-brand-300);
}

.pc-alert[data-tone='warning'] .pc-alert__mark {
  background: rgb(var(--pc-color-amber-900-rgb) / var(--pc-opacity-status));
  color: var(--pc-color-amber-300);
}

.pc-alert[data-tone='danger'] .pc-alert__mark {
  background: rgb(var(--pc-color-red-900-rgb) / var(--pc-opacity-status));
  color: var(--pc-color-red-400);
}

.pc-alert__content h2,
.pc-alert__content p { margin: 0; }
.pc-alert__content h2 { font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-bold); }
.pc-alert__content p { margin-top: var(--pc-space-1); color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); }
.pc-alert__action { margin-top: var(--pc-space-3); }

.pc-alert__dismiss {
  width: var(--pc-size-control-touch);
  height: var(--pc-size-control-touch);
  margin: calc(var(--pc-space-2) * -1);
  border: 0;
  border-radius: var(--pc-radius-md);
  background: transparent;
  color: var(--pc-color-semantic-text-muted);
  cursor: pointer;
  font-size: 1.5rem;
  line-height: 1;
}

.pc-alert__dismiss:hover,
.pc-alert__dismiss:focus-visible { color: var(--pc-color-semantic-text-primary); background: var(--pc-color-semantic-background-elevated); }
.pc-alert__dismiss:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 2px; }
</style>
