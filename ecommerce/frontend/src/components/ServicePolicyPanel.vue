<template>
  <article :id="section.id" class="policy-panel">
    <button
      class="policy-panel__summary"
      type="button"
      :aria-expanded="open"
      :aria-controls="`${section.id}-body`"
      @click="$emit('toggle', section.id)"
    >
      <span class="summary-index">{{ section.index }}</span>
      <span class="summary-title">
        <strong>{{ section.title }}</strong>
        <small>{{ section.eyebrow }}</small>
      </span>
      <span class="summary-copy">{{ section.summary }}</span>
      <svg class="summary-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" /></svg>
    </button>

    <div v-show="open" :id="`${section.id}-body`" class="policy-panel__body">
      <p class="policy-lead">{{ section.lead }}</p>
      <div class="clause-list">
        <section v-for="clause in section.clauses" :key="clause.title" class="clause-row">
          <div class="clause-row__title"><span>{{ clause.code }}</span><h3>{{ clause.title }}</h3></div>
          <div class="clause-row__body">
            <p>{{ clause.body }}</p>
            <ul v-if="clause.items?.length"><li v-for="item in clause.items" :key="item">{{ item }}</li></ul>
          </div>
        </section>
      </div>
      <div v-if="section.kind === 'faq'" class="faq-list">
        <details v-for="faq in faqs" :key="faq.question"><summary>{{ faq.question }}</summary><p>{{ faq.answer }}</p></details>
      </div>
      <slot name="cookie" />
    </div>
  </article>
</template>

<script setup>
defineProps({
  section: { type: Object, required: true },
  open: { type: Boolean, default: false },
  faqs: { type: Array, default: () => [] }
})

defineEmits(['toggle'])
</script>

<style scoped>
.policy-panel { border: 1px solid var(--pc-color-semantic-border-subtle); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-surface); overflow: hidden; }
.policy-panel__summary { display: grid; grid-template-columns: auto minmax(170px, 0.8fr) 1fr auto; gap: var(--pc-space-4); align-items: center; width: 100%; padding: var(--pc-space-5); text-align: left; color: var(--pc-color-semantic-text-primary); background: transparent; border: 0; cursor: pointer; }
.policy-panel__summary:hover { background: var(--pc-color-semantic-background-elevated); }
.policy-panel__summary:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: -3px; }
.summary-index { color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-bold); letter-spacing: .08em; }
.summary-title { display: grid; gap: var(--pc-space-1); }
.summary-title small, .summary-copy { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); }
.summary-copy { line-height: 1.6; }
.summary-icon { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 1.8; transition: transform var(--pc-motion-duration-fast) var(--pc-motion-ease-standard); }
.policy-panel__summary[aria-expanded="true"] .summary-icon { transform: rotate(180deg); }
.policy-panel__body { padding: 0 var(--pc-space-5) var(--pc-space-6); }
.policy-lead { color: var(--pc-color-semantic-text-muted); line-height: 1.75; }
.clause-list { display: grid; gap: var(--pc-space-4); }
.clause-row { display: grid; grid-template-columns: minmax(150px, .35fr) 1fr; gap: var(--pc-space-5); padding-top: var(--pc-space-4); border-top: 1px solid var(--pc-color-semantic-border-subtle); }
.clause-row__title { display: flex; gap: var(--pc-space-3); align-items: baseline; }
.clause-row__title span { color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-bold); letter-spacing: .08em; }
.clause-row__title h3 { margin: 0; font-size: var(--pc-font-size-md); }
.clause-row__body p, .clause-row__body li, .faq-list p { color: var(--pc-color-semantic-text-muted); line-height: 1.75; }
.clause-row__body ul { margin: var(--pc-space-3) 0 0; padding-left: 1.2rem; }
.faq-list { display: grid; gap: var(--pc-space-2); margin-top: var(--pc-space-5); }
.faq-list details { border-top: 1px solid var(--pc-color-semantic-border-subtle); padding: var(--pc-space-3) 0; }
.faq-list summary { cursor: pointer; font-weight: 650; }
.faq-list summary:focus-visible { outline: var(--ds-focus-ring); outline-offset: 3px; }
@media (max-width: 700px) {
  .policy-panel__summary { grid-template-columns: auto 1fr auto; gap: var(--pc-space-3); padding: var(--pc-space-4); }
  .summary-copy { grid-column: 2 / -1; }
  .policy-panel__body { padding: 0 var(--pc-space-4) var(--pc-space-5); }
  .clause-row { grid-template-columns: 1fr; gap: var(--ds-space-2); }
}
@media (prefers-reduced-motion: reduce) { .summary-icon { transition: none; } }
</style>
