<template>
  <div
    class="price-provenance"
    :class="{ 'price-provenance--compact': compact }"
    :data-verification-state="provenance.state"
    aria-label="价格依据"
  >
    <div class="price-provenance__head">
      <span class="price-provenance__status" :class="`price-provenance__status--${provenance.state}`">
        <span aria-hidden="true" />
        {{ provenance.statusLabel }}
      </span>
      <span v-if="!compact" class="price-provenance__eyebrow">价格依据</span>
    </div>

    <template v-if="provenance.isVerified">
      <p class="price-provenance__source">
        来源
        <a
          v-if="!compact"
          :href="provenance.sourceUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ provenance.sourceName }}
          <span class="sr-only">（在新窗口打开）</span>
        </a>
        <strong v-else>{{ provenance.sourceName }}</strong>
      </p>
      <p class="price-provenance__meta">核价于 {{ provenance.checkedAtLabel }}</p>
    </template>

    <template v-else>
      <p class="price-provenance__unavailable">{{ provenance.unavailableMessage }}</p>
      <p v-if="!compact" class="price-provenance__meta">当前售价可用于结算，但不会标记为已核验或历史低价。</p>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getPriceProvenance } from '@/utils/priceProvenance'

const props = defineProps({
  product: {
    type: Object,
    default: () => ({}),
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

const provenance = computed(() => getPriceProvenance(props.product))
</script>

<style scoped>
.price-provenance {
  padding: var(--pc-space-4);
  border: 1px solid var(--pc-color-semantic-border-subtle);
  border-radius: var(--pc-radius-md);
  background: var(--pc-color-semantic-background-canvas);
}

.price-provenance--compact {
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
}

.price-provenance__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--pc-space-3);
}

.price-provenance__status {
  display: inline-flex;
  align-items: center;
  gap: var(--pc-space-2);
  color: var(--pc-color-semantic-text-muted);
  font-size: var(--pc-font-size-xs);
  font-weight: var(--pc-font-weight-semibold);
}

.price-provenance__status > span {
  width: 0.375rem;
  height: 0.375rem;
  flex: 0 0 auto;
  border-radius: var(--pc-radius-full);
  background: var(--pc-color-semantic-text-subtle);
}

.price-provenance__status--verified {
  color: var(--pc-color-semantic-text-accent);
}

.price-provenance__status--verified > span {
  background: var(--pc-color-semantic-action-primary);
}

.price-provenance__eyebrow {
  color: var(--pc-color-semantic-text-subtle);
  font-size: var(--pc-font-size-xs);
  font-weight: var(--pc-font-weight-semibold);
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.price-provenance__source,
.price-provenance__unavailable {
  margin: var(--pc-space-3) 0 0;
  color: var(--pc-color-semantic-text-secondary);
  font-size: var(--pc-font-size-sm);
  line-height: var(--pc-font-line-height-normal);
}

.price-provenance__source a,
.price-provenance__source strong {
  margin-left: var(--pc-space-1);
  color: var(--pc-color-semantic-text-accent);
  font-weight: var(--pc-font-weight-bold);
}

.price-provenance__source a:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.price-provenance__unavailable {
  color: var(--pc-color-semantic-text-muted);
}

.price-provenance__meta {
  margin: var(--pc-space-1) 0 0;
  color: var(--pc-color-semantic-text-subtle);
  font-size: var(--pc-font-size-xs);
  line-height: var(--pc-font-line-height-normal);
}

.price-provenance--compact .price-provenance__source,
.price-provenance--compact .price-provenance__unavailable {
  margin-top: var(--pc-space-1);
}
</style>
