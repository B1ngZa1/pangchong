<template>
  <div v-if="display" class="mt-3 border-t border-dark-700 pt-3">
    <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
      <div class="flex flex-wrap items-center gap-2">
        <p class="text-[11px] font-semibold text-primary-500">{{ display.title }}</p>
        <span v-if="display.createdAt" class="text-[10px] text-dark-500">{{ display.createdAt }}</span>
      </div>
    </div>

    <DsCompatibilityStatus v-if="display.compatibility" :status="display.compatibility" compact />

    <div v-if="display.appearance" class="mb-2 text-[11px] leading-5">
      <span class="text-dark-500">{{ display.appearance.label }}：</span>
      <span class="text-dark-200">{{ display.appearance.value }}</span>
      <span v-if="display.appearance.details.length" class="ml-2 text-dark-500">
        {{ display.appearance.details.join(' · ') }}
      </span>
    </div>

    <div v-if="display.parts.length" class="grid gap-x-4 gap-y-2 sm:grid-cols-2">
      <div v-for="part in display.parts" :key="part.key || part.label" class="min-w-0">
        <div class="flex items-center gap-1.5 text-[11px]">
          <span class="flex-shrink-0 text-dark-500">{{ part.label }}</span>
          <span v-if="part.price" class="text-dark-600">{{ part.price }}</span>
        </div>
        <p class="truncate text-xs font-medium text-dark-200">{{ part.name }}</p>
        <p v-if="part.meta" class="truncate text-[10px] text-dark-500">{{ part.meta }}</p>
      </div>
    </div>

    <div v-if="display.customType !== 'diy_pc' && display.highlights.length" class="mt-3 flex flex-wrap gap-1.5">
      <span v-for="item in display.highlights" :key="item.key"
        class="rounded border border-white/5 bg-dark-950/35 px-2 py-0.5 text-[10px] text-dark-300">
        {{ item.label }}：{{ item.value }}
      </span>
    </div>

    <div v-if="display.metrics.length || display.pricing.length" class="mt-3 flex flex-wrap gap-1.5">
      <span v-for="metric in display.metrics" :key="metric.key"
        class="rounded border border-white/5 bg-dark-950/35 px-2 py-0.5 text-[10px] text-dark-300">
        {{ metric.label }}：{{ metric.value }}
      </span>
      <span v-for="price in display.pricing" :key="price.key"
        class="rounded border border-primary-500/20 bg-primary-500/10 px-2 py-0.5 text-[10px] text-primary-400">
        {{ price.label }}：{{ price.value }}
      </span>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { buildCustomSnapshotDisplay } from '@/utils/orderSpecs'
import { DsCompatibilityStatus } from '@/design-system'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})

const display = computed(() => buildCustomSnapshotDisplay(props.item))

</script>
