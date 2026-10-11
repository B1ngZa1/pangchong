<template>
  <div
    class="pc-async-state"
    :data-state="state"
    :role="state === 'error' ? 'alert' : 'status'"
    :aria-live="state === 'error' ? 'assertive' : 'polite'"
    :aria-busy="state === 'loading' ? 'true' : undefined"
  >
    <template v-if="state === 'success'">
      <slot />
    </template>

    <template v-else-if="state === 'partial'">
      <div class="pc-async-state__partial">
        <div>
          <strong>{{ partialTitle }}</strong>
          <p>{{ partialDescription }}</p>
        </div>
        <slot name="action" />
      </div>
      <slot />
    </template>

    <template v-else-if="state === 'loading'">
      <div class="pc-async-state__loading" :aria-label="loadingLabel">
        <DsSkeleton variant="rect" />
        <DsSkeleton width="72%" />
        <DsSkeleton width="48%" />
      </div>
    </template>

    <template v-else-if="state === 'empty'">
      <div class="pc-async-state__message">
        <h2>{{ emptyTitle }}</h2>
        <p v-if="emptyDescription">{{ emptyDescription }}</p>
        <slot name="action" />
      </div>
    </template>

    <template v-else>
      <div class="pc-async-state__message">
        <h2>{{ errorTitle }}</h2>
        <p v-if="errorDescription">{{ errorDescription }}</p>
        <slot name="action">
          <DsButton variant="secondary" size="sm" type="button" @click="$emit('retry')">{{ retryLabel }}</DsButton>
        </slot>
      </div>
    </template>
  </div>
</template>

<script setup>
import DsButton from './DsButton.vue'
import DsSkeleton from './DsSkeleton.vue'

defineProps({
  state: {
    type: String,
    default: 'loading',
    validator: value => ['loading', 'success', 'empty', 'error', 'partial'].includes(value),
  },
  loadingLabel: {
    type: String,
    default: '正在加载内容',
  },
  emptyTitle: {
    type: String,
    default: '暂无内容',
  },
  emptyDescription: String,
  errorTitle: {
    type: String,
    default: '加载失败',
  },
  errorDescription: {
    type: String,
    default: '请检查网络后重试。',
  },
  retryLabel: {
    type: String,
    default: '重新加载',
  },
  partialTitle: {
    type: String,
    default: '部分内容暂不可用',
  },
  partialDescription: {
    type: String,
    default: '已展示可用内容，稍后可以再次尝试。',
  },
})

defineEmits(['retry'])
</script>

<style scoped>
.pc-async-state { min-width: 0; }
.pc-async-state__loading { display: grid; gap: var(--pc-space-3); padding: var(--pc-space-4) 0; }
.pc-async-state__loading .pc-skeleton[data-variant='rect'] { min-height: 10rem; }
.pc-async-state__message { display: grid; min-height: 12rem; place-items: center; align-content: center; gap: var(--pc-space-3); padding: var(--pc-space-8); border: 1px dashed var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-surface); text-align: center; }
.pc-async-state__message h2, .pc-async-state__message p { margin: 0; }
.pc-async-state__message h2 { font-size: var(--pc-font-size-lg); font-weight: var(--pc-font-weight-bold); }
.pc-async-state__message p { max-width: 32rem; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-relaxed); }
.pc-async-state__partial { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--pc-space-4); margin-bottom: var(--pc-space-4); padding: var(--pc-space-3) var(--pc-space-4); border: 1px solid var(--pc-color-semantic-border-warning); border-radius: var(--pc-radius-md); background: var(--pc-color-semantic-background-warning); }
.pc-async-state__partial strong { color: var(--pc-color-semantic-text-warning); font-size: var(--pc-font-size-sm); }
.pc-async-state__partial p { margin: var(--pc-space-1) 0 0; color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-xs); }
</style>
