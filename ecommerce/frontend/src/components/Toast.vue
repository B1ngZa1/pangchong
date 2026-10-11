<template>
  <div v-if="notify.visible" class="fixed right-4 top-20 z-[var(--pc-z-index-toast)] w-[min(92vw,360px)]">
    <DsToast
      :visible="notify.visible"
      :message="notify.message"
      :tone="toastTone"
      @dismiss="notify.close"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotifyStore } from '@/store'
import { DsToast } from '@/design-system'

const notify = useNotifyStore()
const toastTone = computed(() => {
  if (notify.type === 'error') return 'danger'
  return ['neutral', 'info', 'success', 'warning', 'danger'].includes(notify.type)
    ? notify.type
    : 'info'
})
</script>
