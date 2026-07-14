<template>
  <div
    class="price-provenance"
    :class="{ 'price-provenance--compact': compact }"
    :data-verification-state="provenance.state"
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
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 8px;
  background: rgba(2, 6, 23, 0.48);
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
  gap: 10px;
}

.price-provenance__status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 11px;
  font-weight: 750;
}

.price-provenance__status > span {
  width: 6px;
  height: 6px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: #64748b;
}

.price-provenance__status--verified {
  color: #86ef7a;
}

.price-provenance__status--verified > span {
  background: #44d62c;
  box-shadow: 0 0 12px rgba(68, 214, 44, 0.56);
}

.price-provenance__eyebrow {
  color: #64748b;
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.price-provenance__source,
.price-provenance__unavailable {
  margin: 9px 0 0;
  color: #cbd5e1;
  font-size: 12px;
  line-height: 1.6;
}

.price-provenance__source a,
.price-provenance__source strong {
  margin-left: 4px;
  color: #44d62c;
  font-weight: 700;
}

.price-provenance__source a:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.price-provenance__unavailable {
  color: #94a3b8;
}

.price-provenance__meta {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 11px;
  line-height: 1.55;
}

.price-provenance--compact .price-provenance__source,
.price-provenance--compact .price-provenance__unavailable {
  margin-top: 5px;
}
</style>
