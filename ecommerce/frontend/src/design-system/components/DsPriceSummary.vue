<template>
  <div class="pc-price-summary">
    <dl class="pc-price-summary__totals" :aria-label="label">
      <div>
        <dt>{{ subtotalLabel }}<template v-if="itemCount !== null"> ({{ itemCount }} 件)</template></dt>
        <dd>¥{{ formatMoney(subtotal) }}</dd>
      </div>
      <div>
        <dt>运费</dt>
        <dd>{{ Number(shipping) === 0 ? freeShippingLabel : `¥${formatMoney(shipping)}` }}</dd>
      </div>
      <div v-if="discountValue > 0" class="pc-price-summary__discount">
        <dt>{{ discountLabel }}</dt>
        <dd>-¥{{ formatMoney(discountValue) }}</dd>
      </div>
    </dl>

    <div v-if="showTotal" class="pc-price-summary__total">
      <span>{{ totalLabel }}</span>
      <strong>¥{{ formatMoney(total) }}</strong>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, default: '价格摘要' },
  subtotal: { type: [Number, String], default: 0 },
  shipping: { type: [Number, String], default: 0 },
  discount: { type: [Number, String], default: 0 },
  total: { type: [Number, String], default: 0 },
  itemCount: { type: [Number, String], default: null },
  subtotalLabel: { type: String, default: '商品金额' },
  discountLabel: { type: String, default: '优惠减免' },
  freeShippingLabel: { type: String, default: '包邮' },
  totalLabel: { type: String, default: '应付金额' },
  showTotal: { type: Boolean, default: true },
})

const discountValue = computed(() => Number(props.discount) || 0)

function formatMoney(value) {
  return Number(value || 0).toLocaleString()
}
</script>

<style scoped>
.pc-price-summary { min-width: 0; color: var(--pc-color-semantic-text-primary); }
.pc-price-summary__totals { display: grid; gap: var(--pc-space-2); margin: 0; padding: var(--pc-space-4) 0; border-top: 1px solid var(--pc-color-semantic-border-default); border-bottom: 1px solid var(--pc-color-semantic-border-default); font-size: var(--pc-font-size-sm); }
.pc-price-summary__totals div { display: flex; justify-content: space-between; gap: var(--pc-space-4); color: var(--pc-color-semantic-text-secondary); }
.pc-price-summary__totals dt, .pc-price-summary__totals dd { margin: 0; }
.pc-price-summary__totals dd { color: var(--pc-color-semantic-text-primary); font-weight: var(--pc-font-weight-semibold); }
.pc-price-summary__totals .pc-price-summary__discount, .pc-price-summary__totals .pc-price-summary__discount dd { color: var(--pc-color-semantic-text-accent); }
.pc-price-summary__total { display: flex; align-items: baseline; justify-content: space-between; gap: var(--pc-space-4); padding: var(--pc-space-5) 0 var(--pc-space-2); font-weight: var(--pc-font-weight-bold); }
.pc-price-summary__total strong { color: var(--pc-color-semantic-text-accent); font-size: var(--pc-font-size-xl); }
</style>
