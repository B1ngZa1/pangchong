<template>
  <section
    v-if="status"
    class="pc-compatibility-status"
    :class="{ 'pc-compatibility-status--compact': compact }"
    :data-tone="status.tone || 'ok'"
    :role="isBlocking ? 'alert' : 'status'"
    aria-live="polite"
  >
    <div class="pc-compatibility-status__head">
      <span class="pc-compatibility-status__mark" aria-hidden="true" />
      <strong>{{ status.label }}</strong>
    </div>
    <ul v-if="status.issues?.length" class="pc-compatibility-status__issues">
      <li v-for="issue in status.issues" :key="issue.key || issue.title">
        <span>{{ issue.title }}</span>
        <span v-if="issue.message">：{{ issue.message }}</span>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: Object,
    default: null,
  },
  compact: Boolean,
})

const isBlocking = computed(() => ['warn', 'danger'].includes(props.status?.tone))
</script>

<style scoped>
.pc-compatibility-status {
  display: grid;
  gap: var(--pc-space-2);
  padding: var(--pc-space-3) var(--pc-space-4);
  border: 1px solid var(--pc-color-semantic-border-accent);
  border-radius: var(--pc-radius-md);
  background: var(--pc-color-semantic-background-elevated);
  color: var(--pc-color-semantic-text-secondary);
}

.pc-compatibility-status--compact { padding: var(--pc-space-2) var(--pc-space-3); }
.pc-compatibility-status__head { display: flex; align-items: center; gap: var(--pc-space-2); color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-sm); }
.pc-compatibility-status__mark { width: .5rem; height: .5rem; flex: 0 0 auto; border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-action-primary); }
.pc-compatibility-status__issues { display: grid; gap: var(--pc-space-1); margin: 0; padding-left: var(--pc-space-5); color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-xs); line-height: var(--pc-font-line-height-normal); }
.pc-compatibility-status[data-tone='pending'] { border-color: var(--pc-color-blue-500); }
.pc-compatibility-status[data-tone='pending'] .pc-compatibility-status__mark { background: var(--pc-color-blue-500); }
.pc-compatibility-status[data-tone='warn'] { border-color: var(--pc-color-semantic-border-warning); background: var(--pc-color-semantic-background-warning); }
.pc-compatibility-status[data-tone='warn'] .pc-compatibility-status__mark { background: var(--pc-color-amber-500); }
.pc-compatibility-status[data-tone='danger'] { border-color: var(--pc-color-semantic-border-danger); }
.pc-compatibility-status[data-tone='danger'] .pc-compatibility-status__mark { background: var(--pc-color-red-500); }
</style>
