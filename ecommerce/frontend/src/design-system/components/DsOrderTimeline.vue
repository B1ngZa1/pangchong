<template>
  <section class="pc-order-timeline" :aria-labelledby="titleId">
    <header class="pc-order-timeline__header">
      <div>
        <p v-if="eyebrow" class="pc-order-timeline__eyebrow">{{ eyebrow }}</p>
        <h2 :id="titleId">{{ title }}</h2>
      </div>
      <span v-if="currentLabel" class="pc-order-timeline__current">{{ currentLabel }}</span>
    </header>

    <ol class="pc-order-timeline__list">
      <li
        v-for="(event, index) in normalizedEvents"
        :key="event.id || index"
        class="pc-order-timeline__item"
        :data-state="event.state"
        :aria-current="['current', 'cancelled', 'refunded'].includes(event.state) ? 'step' : undefined"
      >
        <span class="pc-order-timeline__rail" aria-hidden="true">
          <span class="pc-order-timeline__marker">
            <span v-if="event.state === 'complete'">✓</span>
            <span v-else-if="event.state === 'cancelled'">!</span>
            <span v-else-if="event.state === 'refunded'">↺</span>
            <span v-else>{{ index + 1 }}</span>
          </span>
        </span>
        <div class="pc-order-timeline__content">
          <div class="pc-order-timeline__topline">
            <h3>{{ event.label }}</h3>
            <time v-if="event.timestamp" :datetime="event.timestamp">{{ formatTimestamp(event.timestamp) }}</time>
          </div>
          <p v-if="event.description">{{ event.description }}</p>
        </div>
      </li>
    </ol>
  </section>
</template>

<script>
let timelineCounter = 0
</script>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  events: {
    type: Array,
    required: true,
    validator: value => value.length > 0 && value.every(event => event && event.label),
  },
  title: {
    type: String,
    default: '订单进度',
  },
  eyebrow: {
    type: String,
    default: '履约状态',
  },
  currentLabel: String,
})

const titleId = `pc-order-timeline-${++timelineCounter}-title`
const normalizedEvents = computed(() => props.events.map((event, index) => ({
  id: event.id || String(index),
  label: event.label,
  description: event.description,
  timestamp: event.timestamp,
  state: ['complete', 'current', 'upcoming', 'cancelled', 'refunded'].includes(event.state) ? event.state : 'upcoming',
})))

function formatTimestamp(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<style scoped>
.pc-order-timeline { display: grid; gap: var(--pc-space-5); }
.pc-order-timeline__header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--pc-space-4); }
.pc-order-timeline__header h2, .pc-order-timeline__eyebrow, .pc-order-timeline__topline h3, .pc-order-timeline__content p { margin: 0; }
.pc-order-timeline__eyebrow { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-semibold); letter-spacing: 0.08em; text-transform: uppercase; }
.pc-order-timeline__header h2 { margin-top: var(--pc-space-1); font-size: var(--pc-font-size-lg); font-weight: var(--pc-font-weight-bold); }
.pc-order-timeline__current { flex: 0 0 auto; padding: var(--pc-space-2) var(--pc-space-3); border: 1px solid var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-semibold); }
.pc-order-timeline__list { display: grid; margin: 0; padding: 0; list-style: none; }
.pc-order-timeline__item { display: grid; grid-template-columns: 2.5rem minmax(0, 1fr); min-height: 4.5rem; column-gap: var(--pc-space-3); }
.pc-order-timeline__rail { position: relative; display: flex; justify-content: center; }
.pc-order-timeline__rail::after { position: absolute; top: 2rem; bottom: -0.25rem; width: 2px; background: var(--pc-color-semantic-border-default); content: ''; }
.pc-order-timeline__item:last-child .pc-order-timeline__rail::after { display: none; }
.pc-order-timeline__marker { z-index: 1; display: grid; width: 2rem; height: 2rem; place-items: center; border: 1px solid var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-background-surface); color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-bold); }
.pc-order-timeline__content { min-width: 0; padding-bottom: var(--pc-space-5); }
.pc-order-timeline__topline { display: flex; align-items: baseline; justify-content: space-between; gap: var(--pc-space-3); }
.pc-order-timeline__topline h3 { color: var(--pc-color-semantic-text-secondary); font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-semibold); }
.pc-order-timeline__topline time { flex: 0 0 auto; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); }
.pc-order-timeline__content p { margin-top: var(--pc-space-1); color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); line-height: var(--pc-font-line-height-relaxed); }
.pc-order-timeline__item[data-state='complete'] .pc-order-timeline__marker, .pc-order-timeline__item[data-state='current'] .pc-order-timeline__marker { border-color: var(--pc-color-semantic-action-primary); background: var(--pc-color-semantic-action-primary); color: var(--pc-color-semantic-text-inverse); }
.pc-order-timeline__item[data-state='current'] .pc-order-timeline__marker { box-shadow: var(--pc-shadow-focus); }
.pc-order-timeline__item[data-state='current'] .pc-order-timeline__topline h3 { color: var(--pc-color-semantic-text-primary); }
.pc-order-timeline__item[data-state='cancelled'] .pc-order-timeline__marker { border-color: var(--pc-color-semantic-border-danger); background: var(--pc-color-semantic-background-danger); color: var(--pc-color-semantic-text-danger); }
.pc-order-timeline__item[data-state='cancelled'] .pc-order-timeline__topline h3 { color: var(--pc-color-semantic-text-danger); }
.pc-order-timeline__item[data-state='refunded'] .pc-order-timeline__marker { border-color: var(--pc-color-semantic-border-danger); background: var(--pc-color-semantic-background-danger); color: var(--pc-color-semantic-text-danger); }
.pc-order-timeline__item[data-state='refunded'] .pc-order-timeline__topline h3 { color: var(--pc-color-semantic-text-danger); }
@media (max-width: 639px) {
  .pc-order-timeline__header { align-items: flex-start; }
  .pc-order-timeline__current { max-width: 8rem; text-align: right; }
  .pc-order-timeline__topline { display: grid; gap: var(--pc-space-1); }
}
</style>
