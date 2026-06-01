<template>
  <transition name="toast">
    <div
      v-if="notify.visible"
      class="fixed top-20 right-4 z-50 w-[min(92vw,360px)]"
    >
      <div
        :class="[
          'flex items-center gap-3 border p-4 shadow-2xl backdrop-blur rounded-lg',
          panelClass
        ]"
      >
        <span class="inline-block h-2.5 w-2.5 rounded-full" :class="dotClass" />
        <span class="text-sm text-white/95 leading-5">{{ notify.message }}</span>
        <button
          @click="notify.close"
          class="ml-auto text-white/60 transition-colors hover:text-white"
          aria-label="close notification"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue'
import { useNotifyStore } from '@/store'

const notify = useNotifyStore()

const panelClass = computed(() => {
  if (notify.type === 'success') return 'border-primary-500/45 bg-dark-900/90'
  if (notify.type === 'error') return 'border-red-500/45 bg-dark-900/90'
  if (notify.type === 'warning') return 'border-yellow-500/45 bg-dark-900/90'
  return 'border-sky-500/45 bg-dark-900/90'
})

const dotClass = computed(() => {
  if (notify.type === 'success') return 'bg-primary-500'
  if (notify.type === 'error') return 'bg-red-500'
  if (notify.type === 'warning') return 'bg-yellow-400'
  return 'bg-sky-400'
})
</script>

<style scoped>
.toast-enter-active {
  animation: slideIn 0.22s ease-out;
}

.toast-leave-active {
  animation: fadeOut 0.18s ease-in;
}

@keyframes slideIn {
  from {
    transform: translateX(12px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}
</style>
