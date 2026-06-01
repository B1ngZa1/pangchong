<template>
  <aside class="rounded-lg border border-[#2A2A2A] bg-[#0C0C0C] p-4">
    <div class="mb-4 flex items-start justify-between gap-3">
      <div>
        <h2 class="text-sm font-bold text-white">3D 配置</h2>
        <p class="mt-1 text-xs leading-5 text-[#8A8A8A]">切换外观、材质和查看角度。</p>
      </div>
      <button
        type="button"
        class="inline-flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg border border-[#2A2A2A] text-[#BBBBBB] transition-colors hover:border-primary-500 hover:text-primary-500 active:bg-primary-500/10"
        aria-label="重置 3D 视角"
        @click="$emit('reset-camera')"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v6h6M20 20v-6h-6M6.5 17.5A8 8 0 0117 6.5M17.5 6.5A8 8 0 016.5 17.5" />
        </svg>
      </button>
    </div>

    <div class="space-y-5">
      <section>
        <h3 class="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-[#777]">颜色</h3>
        <div class="grid grid-cols-1 gap-2">
          <button
            v-for="variant in variants"
            :key="variant.id"
            type="button"
            class="flex min-h-11 w-full items-center justify-between rounded-lg border px-3 py-2 text-left transition-all focus:outline-none focus:ring-2 focus:ring-primary-500/60"
            :class="selectedVariant === variant.id
              ? 'border-primary-500 bg-primary-500/10 text-primary-500'
              : 'border-[#2A2A2A] bg-[#111] text-[#D0D0D0] hover:border-[#555]'"
            :aria-pressed="selectedVariant === variant.id"
            @click="$emit('update:selectedVariant', variant.id)"
          >
            <span class="flex min-w-0 items-center gap-2">
              <span class="h-5 w-5 flex-shrink-0 rounded-full border border-white/20" :style="{ backgroundColor: variant.hex }"></span>
              <span class="truncate text-sm font-medium">{{ variant.name }}</span>
            </span>
            <span v-if="variant.priceDiff" class="ml-2 flex-shrink-0 text-xs text-[#999]">+¥{{ variant.priceDiff.toLocaleString() }}</span>
          </button>
        </div>
      </section>

      <section>
        <h3 class="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-[#777]">材质</h3>
        <div class="grid grid-cols-1 gap-2">
          <button
            v-for="material in materials"
            :key="material.id"
            type="button"
            class="rounded-lg border px-3 py-2 text-left transition-all focus:outline-none focus:ring-2 focus:ring-primary-500/60"
            :class="selectedMaterial === material.id
              ? 'border-primary-500 bg-primary-500/10'
              : 'border-[#2A2A2A] bg-[#111] hover:border-[#555]'"
            :aria-pressed="selectedMaterial === material.id"
            @click="$emit('update:selectedMaterial', material.id)"
          >
            <span class="block text-sm font-medium" :class="selectedMaterial === material.id ? 'text-primary-500' : 'text-white'">{{ material.name }}</span>
            <span class="mt-0.5 block text-xs leading-5 text-[#888]">{{ material.description }}</span>
          </button>
        </div>
      </section>

      <section>
        <h3 class="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-[#777]">视角</h3>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="preset in cameraPresets"
            :key="preset.id"
            type="button"
            class="rounded-lg border px-2 py-2 text-sm transition-all focus:outline-none focus:ring-2 focus:ring-primary-500/60"
            :class="cameraPreset === preset.id
              ? 'border-primary-500 bg-primary-500/10 text-primary-500'
              : 'border-[#2A2A2A] bg-[#111] text-[#D0D0D0] hover:border-[#555]'"
            :aria-pressed="cameraPreset === preset.id"
            @click="$emit('update:cameraPreset', preset.id)"
          >
            {{ preset.name }}
          </button>
        </div>
      </section>

      <section class="flex items-center justify-between gap-4 rounded-lg border border-[#2A2A2A] bg-[#111] px-3 py-3">
        <div class="min-w-0">
          <h3 class="text-sm font-medium text-white">自动旋转</h3>
          <p class="mt-0.5 text-xs text-[#888]">系统减少动态效果时会自动停用。</p>
        </div>
        <button
          type="button"
          class="relative h-7 w-12 flex-shrink-0 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500/60"
          :class="autoRotate ? 'bg-primary-500' : 'bg-[#333]'"
          role="switch"
          :aria-checked="autoRotate"
          aria-label="切换 3D 自动旋转"
          @click="$emit('update:autoRotate', !autoRotate)"
        >
          <span
            class="absolute top-1 h-5 w-5 rounded-full bg-white shadow transition-transform"
            :class="autoRotate ? 'translate-x-6' : 'translate-x-1'"
          ></span>
        </button>
      </section>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  variants: { type: Array, required: true },
  materials: { type: Array, required: true },
  cameraPresets: { type: Array, required: true },
  selectedVariant: { type: String, required: true },
  selectedMaterial: { type: String, required: true },
  cameraPreset: { type: String, required: true },
  autoRotate: { type: Boolean, required: true },
})

defineEmits([
  'update:selectedVariant',
  'update:selectedMaterial',
  'update:cameraPreset',
  'update:autoRotate',
  'reset-camera',
])
</script>
