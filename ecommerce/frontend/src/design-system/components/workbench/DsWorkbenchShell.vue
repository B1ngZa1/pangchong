<template>
  <section class="pc-workbench-shell" :class="`pc-workbench-shell--${density}`" :data-density="density" :aria-label="ariaLabel">
    <aside class="pc-workbench-shell__nav" aria-label="工作台导航">
      <slot name="nav" />
    </aside>
    <div class="pc-workbench-shell__canvas">
      <slot name="canvas" />
    </div>
    <aside class="pc-workbench-shell__inspector" aria-label="配置检查器">
      <slot name="inspector" />
    </aside>
  </section>
</template>

<script setup>
defineProps({
  ariaLabel: { type: String, default: '配置工作台' },
  density: { type: String, default: 'compact', validator: (value) => ['comfortable', 'compact'].includes(value) },
})
</script>

<style scoped>
.pc-workbench-shell {
  display: grid;
  min-width: 0;
  grid-template-columns: var(--pc-layout-workbench-nav) minmax(var(--pc-layout-workbench-canvas-min), 1fr) var(--pc-layout-workbench-inspector);
  gap: var(--pc-layout-workbench-gap);
  align-items: stretch;
  padding: var(--pc-density-compact-padding);
  border: 1px solid var(--pc-color-semantic-border-subtle);
  border-radius: var(--pc-radius-xl);
  background: var(--pc-color-semantic-background-canvas);
  color: var(--pc-color-semantic-text-primary);
}

.pc-workbench-shell--comfortable { gap: var(--pc-density-comfortable-gap); padding: var(--pc-density-comfortable-padding); }
.pc-workbench-shell__nav, .pc-workbench-shell__canvas, .pc-workbench-shell__inspector { min-width: 0; }
.pc-workbench-shell__nav, .pc-workbench-shell__inspector { padding: var(--pc-density-compact-padding); border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-surface); }
.pc-workbench-shell__canvas { min-height: 24rem; padding: var(--pc-density-compact-padding); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-elevated); }
@media (max-width: 1023px) {
  .pc-workbench-shell { grid-template-columns: minmax(0, 1fr) minmax(14rem, 18rem); }
  .pc-workbench-shell__nav { grid-column: 1 / -1; }
}
@media (max-width: 639px) {
  .pc-workbench-shell { display: flex; flex-direction: column; gap: var(--pc-density-compact-gap); }
  .pc-workbench-shell__canvas { order: 2; min-height: 18rem; }
  .pc-workbench-shell__nav { order: 1; overflow-x: auto; }
  .pc-workbench-shell__inspector { order: 3; }
}
</style>
