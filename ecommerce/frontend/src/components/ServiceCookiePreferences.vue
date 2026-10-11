<template>
  <div class="service-cookie-control">
    <div class="service-cookie-table">
      <div v-for="option in options" :key="option.key" class="service-cookie-option">
        <div class="service-cookie-option__text">
          <strong>{{ option.title }}</strong>
          <small>{{ option.description }}</small>
          <em>{{ option.purpose }}</em>
        </div>
        <DsToggle
          :model-value="Boolean(modelValue[option.key])"
          :label="option.title"
          :disabled="option.required"
          :show-state="true"
          :on-label="option.required ? '始终开启' : '已开启'"
          :off-label="'已关闭'"
          @update:model-value="setPreference(option.key, $event)"
        />
      </div>
    </div>

    <div class="service-cookie-footer">
      <p v-if="saved">Cookie 偏好已保存到当前浏览器。</p>
      <p v-else>除必要 Cookie 外，你可以随时调整偏好；更改仅影响当前浏览器。</p>
      <DsButton type="button" size="sm" @click="$emit('save')">保存 Cookie 设置</DsButton>
    </div>
  </div>
</template>

<script setup>
import DsButton from '@/design-system/components/DsButton.vue'
import DsToggle from '@/design-system/components/DsToggle.vue'

const props = defineProps({
  options: {
    type: Array,
    default: () => [],
  },
  modelValue: {
    type: Object,
    default: () => ({}),
  },
  saved: Boolean,
})

const emit = defineEmits(['update:modelValue', 'save'])

function setPreference(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}
</script>

<style scoped>
.service-cookie-control { border-top: 1px solid var(--pc-color-semantic-border-subtle); }
.service-cookie-table { display: grid; }
.service-cookie-option {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--pc-space-6);
  align-items: center;
  min-height: 6rem;
  padding: var(--pc-space-4) var(--pc-space-6);
  border-bottom: 1px solid var(--pc-color-semantic-border-subtle);
}
.service-cookie-option__text { display: grid; gap: var(--pc-space-1); }
.service-cookie-option strong { color: var(--pc-color-semantic-text-primary); font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-bold); }
.service-cookie-option small, .service-cookie-option em { color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); font-style: normal; line-height: var(--pc-font-line-height-normal); }
.service-cookie-option em { color: var(--pc-color-semantic-text-accent); }
.service-cookie-footer { display: flex; align-items: center; justify-content: space-between; gap: var(--pc-space-4); padding: var(--pc-space-4) var(--pc-space-6); }
.service-cookie-footer p { margin: 0; color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); line-height: var(--pc-font-line-height-normal); }
@media (max-width: 639px) {
  .service-cookie-option { grid-template-columns: 1fr; gap: var(--pc-space-3); }
  .service-cookie-option :deep(.pc-toggle) { justify-content: flex-start; }
  .service-cookie-footer { align-items: flex-start; flex-direction: column; }
}
</style>
