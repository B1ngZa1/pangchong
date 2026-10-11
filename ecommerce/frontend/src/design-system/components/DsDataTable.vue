<template>
  <div class="pc-data-table">
    <div class="pc-data-table__scroll" role="region" :aria-label="label" tabindex="0">
      <slot />
    </div>
    <slot name="footer" />
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
})
</script>

<style scoped>
.pc-data-table { min-width: 0; }
.pc-data-table__scroll { max-width: 100%; overflow: auto; overscroll-behavior-inline: contain; }
.pc-data-table__scroll:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: -2px; }
.pc-data-table__scroll :slotted(table) { width: 100%; min-width: 48rem; border-collapse: collapse; font-size: var(--pc-font-size-sm); }
.pc-data-table__scroll :slotted(th) { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-semibold); text-align: left; white-space: nowrap; }
.pc-data-table__scroll :slotted(td), .pc-data-table__scroll :slotted(th) { padding: var(--pc-space-3) var(--pc-space-4); border-bottom: 1px solid var(--pc-color-semantic-border-subtle); }
.pc-data-table__scroll :slotted(tbody tr:hover) { background: var(--pc-color-semantic-background-elevated); }
.pc-data-table__scroll :slotted(tbody tr:last-child td) { border-bottom: 0; }
@media (max-width: 639px) {
  .pc-data-table__scroll :slotted(table) { min-width: 42rem; }
}
</style>
