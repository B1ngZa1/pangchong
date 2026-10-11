<template>
  <nav class="pc-pagination" :aria-label="ariaLabel">
    <button
      class="pc-pagination__control"
      type="button"
      :disabled="disabled || page <= 1"
      :aria-label="previousLabel"
      @click="goTo(page - 1)"
    >
      <span aria-hidden="true">‹</span>
      <span class="pc-pagination__control-label">{{ previousLabel }}</span>
    </button>

    <ol class="pc-pagination__list">
      <li v-for="item in pageItems" :key="item.key">
        <span v-if="item.type === 'ellipsis'" class="pc-pagination__ellipsis" aria-hidden="true">…</span>
        <button
          v-else
          class="pc-pagination__page"
          type="button"
          :aria-label="`${pageLabel}${item.value}${pageSuffix}`"
          :aria-current="item.value === page ? 'page' : undefined"
          :disabled="disabled"
          @click="goTo(item.value)"
        >
          {{ item.value }}
        </button>
      </li>
    </ol>

    <button
      class="pc-pagination__control"
      type="button"
      :disabled="disabled || page >= totalPages"
      :aria-label="nextLabel"
      @click="goTo(page + 1)"
    >
      <span class="pc-pagination__control-label">{{ nextLabel }}</span>
      <span aria-hidden="true">›</span>
    </button>
  </nav>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: {
    type: Number,
    default: 1,
  },
  totalPages: {
    type: Number,
    required: true,
    validator: value => value >= 1,
  },
  maxVisible: {
    type: Number,
    default: 7,
    validator: value => value >= 5 && value % 2 === 1,
  },
  ariaLabel: {
    type: String,
    default: '分页',
  },
  pageLabel: {
    type: String,
    default: '第',
  },
  pageSuffix: {
    type: String,
    default: '页',
  },
  previousLabel: {
    type: String,
    default: '上一页',
  },
  nextLabel: {
    type: String,
    default: '下一页',
  },
  disabled: Boolean,
})

const emit = defineEmits(['update:page', 'change'])

const normalizedPage = computed(() => Math.min(Math.max(props.page, 1), props.totalPages))
const pageItems = computed(() => {
  const total = props.totalPages
  const current = normalizedPage.value
  const visible = Math.min(props.maxVisible, total)
  if (visible >= total) {
    return Array.from({ length: total }, (_, index) => ({ type: 'page', value: index + 1, key: `page-${index + 1}` }))
  }

  const middle = visible - 2
  const half = Math.floor(middle / 2)
  let start = Math.max(2, current - half)
  let end = Math.min(total - 1, start + middle - 1)
  start = Math.max(2, end - middle + 1)

  const items = [{ type: 'page', value: 1, key: 'page-1' }]
  if (start > 2) items.push({ type: 'ellipsis', key: 'ellipsis-start' })
  for (let value = start; value <= end; value += 1) items.push({ type: 'page', value, key: `page-${value}` })
  if (end < total - 1) items.push({ type: 'ellipsis', key: 'ellipsis-end' })
  items.push({ type: 'page', value: total, key: `page-${total}` })
  return items
})

function goTo(value) {
  if (props.disabled) return
  const nextPage = Math.min(Math.max(value, 1), props.totalPages)
  if (nextPage === normalizedPage.value) return
  emit('update:page', nextPage)
  emit('change', nextPage)
}
</script>

<style scoped>
.pc-pagination { display: flex; align-items: center; justify-content: center; gap: var(--pc-space-2); min-width: 0; }
.pc-pagination__list { display: flex; align-items: center; gap: var(--pc-space-1); margin: 0; padding: 0; list-style: none; }
.pc-pagination__control,
.pc-pagination__page { display: inline-flex; min-width: var(--pc-size-control-touch); height: var(--pc-size-control-touch); align-items: center; justify-content: center; gap: var(--pc-space-1); border: 1px solid transparent; border-radius: var(--pc-radius-md); background: transparent; color: var(--pc-color-semantic-text-secondary); font: inherit; font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-semibold); cursor: pointer; }
.pc-pagination__control { padding: 0 var(--pc-space-2); }
.pc-pagination__control:hover:not(:disabled),
.pc-pagination__page:hover:not(:disabled) { border-color: var(--pc-color-semantic-border-default); background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-primary); }
.pc-pagination__page[aria-current='page'] { border-color: var(--pc-color-semantic-action-primary); background: var(--pc-color-semantic-action-primary); color: var(--pc-color-semantic-text-inverse); }
.pc-pagination__control:focus-visible,
.pc-pagination__page:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 2px; }
.pc-pagination__control:disabled,
.pc-pagination__page:disabled { cursor: not-allowed; opacity: var(--pc-opacity-disabled); }
.pc-pagination__ellipsis { display: inline-flex; min-width: var(--pc-size-control-touch); height: var(--pc-size-control-touch); align-items: center; justify-content: center; color: var(--pc-color-semantic-text-muted); }
@media (max-width: 639px) {
  .pc-pagination__control-label { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
  .pc-pagination { gap: var(--pc-space-1); }
}
</style>
