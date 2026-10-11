<template>
  <DsDialog
    :open="open"
    title="订单提交成功"
    :description="orderDescription"
    size="sm"
    @update:open="$emit('update:open', $event)"
  >
    <div class="pc-order-success__body" role="status" aria-live="polite">
      <div class="pc-order-success__icon" aria-hidden="true">✓</div>
      <p class="pc-order-success__headline">订单已创建</p>
      <p class="pc-order-success__hint">请在 30 分钟内完成支付，支付状态会同步到订单中心。</p>
    </div>

    <p v-if="paymentError" class="pc-order-success__error" role="alert">
      {{ paymentError }}
    </p>

    <template #footer>
      <DsButton variant="primary" :loading="paying" @click="$emit('pay')">
        {{ paying ? '支付创建中...' : '去支付' }}
      </DsButton>
      <DsButton variant="secondary" @click="$emit('view-orders')">查看订单</DsButton>
      <DsButton variant="ghost" @click="$emit('continue-shopping')">继续购物</DsButton>
    </template>
  </DsDialog>
</template>

<script setup>
import { computed } from 'vue'
import DsButton from './DsButton.vue'
import DsDialog from './DsDialog.vue'

const props = defineProps({
  open: Boolean,
  orderNo: { type: String, default: '' },
  paying: Boolean,
  paymentError: { type: String, default: '' },
})

defineEmits(['update:open', 'pay', 'view-orders', 'continue-shopping'])

const orderDescription = computed(() => props.orderNo ? `订单号：${props.orderNo}` : '订单号生成中')
</script>

<style scoped>
.pc-order-success__body { display: grid; justify-items: center; gap: var(--pc-space-3); text-align: center; }
.pc-order-success__icon { display: grid; width: 4rem; height: 4rem; place-items: center; border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-background-accent); color: var(--pc-color-semantic-text-inverse); font-size: var(--pc-font-size-3xl); font-weight: var(--pc-font-weight-bold); }
.pc-order-success__headline { margin: 0; color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-lg); font-weight: var(--pc-font-weight-bold); }
.pc-order-success__hint { max-width: 26rem; margin: 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); }
.pc-order-success__error { margin: var(--pc-space-4) 0 0; padding: var(--pc-space-3); border: 1px solid var(--pc-color-semantic-border-danger); border-radius: var(--pc-radius-md); background: var(--pc-color-semantic-background-danger); color: var(--pc-color-semantic-text-danger); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); }
@media (max-width: 480px) { .pc-order-success__body { justify-items: start; text-align: left; } .pc-order-success__icon { width: 3.5rem; height: 3.5rem; } }
</style>
