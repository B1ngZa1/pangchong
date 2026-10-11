<template>
  <header class="pc-commerce-nav" :data-density="density">
    <nav class="pc-commerce-nav__global" :aria-label="globalLabel">
      <a class="pc-commerce-nav__brand" :href="brandHref">{{ brand }}</a>
      <ul class="pc-commerce-nav__primary">
        <li v-for="item in primaryItems" :key="item.id || item.label">
          <a :href="item.href || '#'" :aria-current="item.active ? 'page' : undefined">{{ item.label }}</a>
        </li>
      </ul>
      <div class="pc-commerce-nav__actions">
        <slot name="actions">
          <a v-if="searchHref" :href="searchHref" class="pc-commerce-nav__utility">{{ searchLabel }}</a>
        </slot>
      </div>
    </nav>
    <nav class="pc-commerce-nav__categories" :aria-label="categoryLabel">
      <ul>
        <li v-for="item in categoryItems" :key="item.id || item.label">
          <a :href="item.href || '#'" :aria-current="item.active ? 'page' : undefined">{{ item.label }}</a>
        </li>
      </ul>
    </nav>
  </header>
</template>

<script setup>
defineProps({
  brand: { type: String, default: 'PANGCHONG' },
  brandHref: { type: String, default: '/' },
  primaryItems: { type: Array, default: () => [] },
  categoryItems: { type: Array, default: () => [] },
  globalLabel: { type: String, default: '商城主导航' },
  categoryLabel: { type: String, default: '商品分类导航' },
  searchHref: { type: String, default: '' },
  searchLabel: { type: String, default: '搜索' },
  density: { type: String, default: 'comfortable', validator: value => ['comfortable', 'compact'].includes(value) },
})
</script>

<style scoped>
.pc-commerce-nav { min-width: 0; border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-canvas); color: var(--pc-color-semantic-text-primary); }
.pc-commerce-nav__global, .pc-commerce-nav__categories { display: flex; min-width: 0; align-items: center; }
.pc-commerce-nav__global { min-height: var(--pc-size-control-lg); gap: var(--pc-density-comfortable-gap); padding: var(--pc-space-3) var(--pc-density-comfortable-padding); border-bottom: 1px solid var(--pc-color-semantic-border-subtle); }
.pc-commerce-nav__brand { flex: 0 0 auto; color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-black); letter-spacing: .12em; text-decoration: none; }
.pc-commerce-nav__primary, .pc-commerce-nav__categories ul { display: flex; min-width: 0; align-items: center; gap: var(--pc-space-4); margin: 0; padding: 0; list-style: none; }
.pc-commerce-nav__primary a, .pc-commerce-nav__categories a, .pc-commerce-nav__utility { min-height: var(--pc-size-control-touch); display: inline-flex; align-items: center; color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-sm); text-decoration: none; white-space: nowrap; }
.pc-commerce-nav__primary a:hover, .pc-commerce-nav__categories a:hover, .pc-commerce-nav__utility:hover, .pc-commerce-nav__primary a[aria-current="page"], .pc-commerce-nav__categories a[aria-current="page"] { color: var(--pc-color-semantic-text-accent); }
.pc-commerce-nav__primary a:focus-visible, .pc-commerce-nav__categories a:focus-visible, .pc-commerce-nav__brand:focus-visible, .pc-commerce-nav__utility:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 3px; border-radius: var(--pc-radius-sm); }
.pc-commerce-nav__actions { display: flex; flex: 0 0 auto; margin-left: auto; }
.pc-commerce-nav__utility { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); }
.pc-commerce-nav__categories { overflow-x: auto; padding: 0 var(--pc-density-comfortable-padding); scrollbar-width: thin; }
.pc-commerce-nav__categories a { font-size: var(--pc-font-size-xs); }
.pc-commerce-nav[data-density="compact"] .pc-commerce-nav__global { gap: var(--pc-density-compact-gap); padding: var(--pc-space-2) var(--pc-density-compact-padding); }
.pc-commerce-nav[data-density="compact"] .pc-commerce-nav__categories ul { gap: var(--pc-density-compact-gap); }
.pc-commerce-nav[data-density="compact"] .pc-commerce-nav__categories { padding-inline: var(--pc-density-compact-padding); }
@media (max-width: 639px) {
  .pc-commerce-nav__global { gap: var(--pc-space-3); }
  .pc-commerce-nav__primary { gap: var(--pc-space-3); }
  .pc-commerce-nav__actions { display: none; }
}
</style>
