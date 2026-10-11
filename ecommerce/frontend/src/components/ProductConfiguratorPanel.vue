<template>
  <aside class="config-panel" aria-label="3D 配置选项">
    <div class="config-panel__header">
      <div>
        <h2>3D 配置</h2>
        <p>切换外观、材质和查看角度。</p>
      </div>
      <DsIconButton label="重置 3D 视角" variant="secondary" size="sm" @click="$emit('reset-camera')">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 4v6h6M20 20v-6h-6M6.5 17.5A8 8 0 0117 6.5M17.5 6.5A8 8 0 016.5 17.5" />
        </svg>
      </DsIconButton>
    </div>

    <div class="config-panel__sections">
      <section class="config-section" aria-labelledby="config-color-label">
        <h3 id="config-color-label">颜色</h3>
        <div class="config-choice-list">
          <button
            v-for="variant in variants"
            :key="variant.id"
            class="config-choice"
            :class="{ 'config-choice--selected': selectedVariant === variant.id }"
            type="button"
            :aria-pressed="selectedVariant === variant.id"
            @click="$emit('update:selectedVariant', variant.id)"
          >
            <span class="config-choice__main">
              <span class="config-choice__swatch" :style="{ '--swatch-color': variant.hex }" aria-hidden="true" />
              <span class="config-choice__name">{{ variant.name }}</span>
            </span>
            <span v-if="variant.priceDiff" class="config-choice__price">+¥{{ variant.priceDiff.toLocaleString() }}</span>
          </button>
        </div>
      </section>

      <section class="config-section" aria-labelledby="config-material-label">
        <h3 id="config-material-label">材质</h3>
        <div class="config-choice-list">
          <button
            v-for="material in materials"
            :key="material.id"
            class="config-choice config-choice--stacked"
            :class="{ 'config-choice--selected': selectedMaterial === material.id }"
            type="button"
            :aria-pressed="selectedMaterial === material.id"
            @click="$emit('update:selectedMaterial', material.id)"
          >
            <span class="config-choice__name">{{ material.name }}</span>
            <span class="config-choice__description">{{ material.description }}</span>
          </button>
        </div>
      </section>

      <section class="config-section" aria-labelledby="config-camera-label">
        <h3 id="config-camera-label">视角</h3>
        <div class="config-camera-grid">
          <button
            v-for="preset in cameraPresets"
            :key="preset.id"
            class="config-choice config-choice--camera"
            :class="{ 'config-choice--selected': cameraPreset === preset.id }"
            type="button"
            :aria-pressed="cameraPreset === preset.id"
            @click="$emit('update:cameraPreset', preset.id)"
          >
            {{ preset.name }}
          </button>
        </div>
      </section>

      <section class="config-toggle-row" aria-labelledby="config-rotation-label">
        <div>
          <h3 id="config-rotation-label">自动旋转</h3>
          <p>系统减少动态效果时会自动停用。</p>
        </div>
        <DsToggle
          :model-value="autoRotate"
          label="切换 3D 自动旋转"
          @update:model-value="$emit('update:autoRotate', $event)"
        />
      </section>
    </div>
  </aside>
</template>

<script setup>
import { DsIconButton, DsToggle } from '@/design-system'

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

<style scoped>
.config-panel {
  min-width: 0;
  padding: var(--pc-space-4);
  border: 1px solid var(--pc-color-semantic-border-default);
  border-radius: var(--pc-radius-lg);
  background: var(--pc-color-semantic-background-canvas);
  color: var(--pc-color-semantic-text-primary);
}
.config-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--pc-space-3);
  margin-bottom: var(--pc-space-4);
}
.config-panel__header h2 { margin: 0; font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-bold); }
.config-panel__header p { margin: var(--pc-space-1) 0 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); line-height: var(--pc-font-line-height-normal); }
.config-panel__header svg { width: 1rem; height: 1rem; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2; }
.config-panel__sections { display: grid; gap: var(--pc-space-5); }
.config-section { display: grid; gap: var(--pc-space-2); }
.config-section h3, .config-toggle-row h3 { margin: 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); font-weight: var(--pc-font-weight-semibold); letter-spacing: 0.14em; text-transform: uppercase; }
.config-choice-list, .config-camera-grid { display: grid; gap: var(--pc-space-2); }
.config-camera-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.config-choice {
  display: flex;
  min-width: 0;
  min-height: var(--pc-size-control-touch);
  align-items: center;
  justify-content: space-between;
  gap: var(--pc-space-2);
  padding: var(--pc-space-2) var(--pc-space-3);
  border: 1px solid var(--pc-color-semantic-border-default);
  border-radius: var(--pc-radius-md);
  background: var(--pc-color-semantic-background-surface);
  color: var(--pc-color-semantic-text-secondary);
  text-align: left;
  cursor: pointer;
  touch-action: manipulation;
  transition: border-color var(--pc-motion-duration-fast) var(--pc-motion-ease-standard), background-color var(--pc-motion-duration-fast) var(--pc-motion-ease-standard), color var(--pc-motion-duration-fast) var(--pc-motion-ease-standard);
}
.config-choice:hover { border-color: var(--pc-color-semantic-border-strong); color: var(--pc-color-semantic-text-primary); }
.config-choice:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 2px; }
.config-choice--selected { border-color: var(--pc-color-semantic-action-primary); background: color-mix(in srgb, var(--pc-color-semantic-action-primary) 10%, transparent); color: var(--pc-color-semantic-text-accent); }
.config-choice__main { display: flex; min-width: 0; align-items: center; gap: var(--pc-space-2); }
.config-choice__swatch { width: 1.25rem; height: 1.25rem; flex: 0 0 1.25rem; border: 1px solid color-mix(in srgb, var(--pc-color-semantic-text-primary) 20%, transparent); border-radius: var(--pc-radius-full); background: var(--swatch-color); }
.config-choice__name { min-width: 0; overflow: hidden; font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-medium); text-overflow: ellipsis; white-space: nowrap; }
.config-choice__price, .config-choice__description { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); }
.config-choice--stacked { display: grid; justify-items: start; gap: var(--pc-space-1); }
.config-choice--stacked .config-choice__name { color: inherit; }
.config-choice--camera { justify-content: center; padding-inline: var(--pc-space-2); text-align: center; }
.config-toggle-row { display: flex; min-width: 0; align-items: center; justify-content: space-between; gap: var(--pc-space-4); padding: var(--pc-space-3); border: 1px solid var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-md); background: var(--pc-color-semantic-background-surface); }
.config-toggle-row p { margin: var(--pc-space-1) 0 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); line-height: var(--pc-font-line-height-normal); }
@media (max-width: 639px) { .config-camera-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (prefers-reduced-motion: reduce) { .config-choice { transition: none; } }
</style>
