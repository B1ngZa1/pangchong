<template>
  <Transition name="pc-toast">
    <div
      v-if="visible"
      class="pc-toast"
      :data-tone="tone"
      :role="tone === 'danger' ? 'alert' : 'status'"
      aria-live="polite"
    >
      <span class="pc-toast__mark" aria-hidden="true" />
      <p>{{ message }}</p>
      <DsIconButton
        v-if="dismissible"
        label="关闭通知"
        variant="ghost"
        size="sm"
        type="button"
        @click="$emit('dismiss')"
      >
        ×
      </DsIconButton>
    </div>
  </Transition>
</template>

<script setup>
import DsIconButton from './DsIconButton.vue'

defineProps({
  visible: Boolean,
  message: {
    type: String,
    required: true,
  },
  tone: {
    type: String,
    default: 'info',
    validator: value => ['neutral', 'info', 'success', 'warning', 'danger'].includes(value),
  },
  dismissible: {
    type: Boolean,
    default: true,
  },
})

defineEmits(['dismiss'])
</script>

<style scoped>
.pc-toast {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: var(--pc-space-3);
  align-items: center;
  padding: var(--pc-space-3) var(--pc-space-4);
  border: 1px solid var(--pc-color-semantic-border-default);
  border-radius: var(--pc-radius-md);
  background: var(--pc-color-semantic-background-elevated);
  color: var(--pc-color-semantic-text-primary);
  box-shadow: var(--pc-shadow-md);
}

.pc-toast p { margin: 0; color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); }
.pc-toast__mark { width: .5rem; height: .5rem; border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-text-info); }
.pc-toast[data-tone='success'] { border-color: var(--pc-color-semantic-border-accent); }
.pc-toast[data-tone='success'] .pc-toast__mark { background: var(--pc-color-semantic-action-primary); }
.pc-toast[data-tone='warning'] { border-color: var(--pc-color-semantic-border-warning); }
.pc-toast[data-tone='warning'] .pc-toast__mark { background: var(--pc-color-amber-500); }
.pc-toast[data-tone='danger'] { border-color: var(--pc-color-semantic-border-danger); }
.pc-toast[data-tone='danger'] .pc-toast__mark { background: var(--pc-color-red-500); }
.pc-toast:focus-within { box-shadow: var(--pc-shadow-focus), var(--pc-shadow-md); }

.pc-toast-enter-active { animation: pc-toast-in var(--pc-motion-duration-fast) var(--pc-motion-ease-standard); }
.pc-toast-leave-active { animation: pc-toast-out var(--pc-motion-duration-fast) var(--pc-motion-ease-exit); }
@keyframes pc-toast-in { from { opacity: 0; transform: translateY(-.5rem); } to { opacity: 1; transform: translateY(0); } }
@keyframes pc-toast-out { from { opacity: 1; } to { opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  .pc-toast-enter-active, .pc-toast-leave-active { animation: none; }
}
</style>
