<template>
  <component
    :is="as"
    class="pc-card"
    :class="{ 'pc-card--interactive': interactive }"
    :data-padding="padding"
  >
    <slot />
  </component>
</template>

<script setup>
defineProps({
  as: {
    type: [String, Object],
    default: 'section',
  },
  padding: {
    type: String,
    default: 'md',
    validator: value => ['none', 'sm', 'md', 'lg'].includes(value),
  },
  interactive: Boolean,
})
</script>

<style scoped>
.pc-card {
  overflow: hidden;
  border: 1px solid var(--pc-color-semantic-border-subtle);
  border-radius: var(--pc-radius-lg);
  background: var(--pc-color-semantic-background-surface);
  color: var(--pc-color-semantic-text-primary);
  box-shadow: var(--pc-shadow-sm);
}

.pc-card[data-padding='sm'] { padding: var(--pc-space-4); }
.pc-card[data-padding='md'] { padding: var(--pc-space-6); }
.pc-card[data-padding='lg'] { padding: var(--pc-space-8); }

.pc-card--interactive {
  transition:
    border-color var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    box-shadow var(--pc-motion-duration-normal) var(--pc-motion-ease-standard),
    transform var(--pc-motion-duration-normal) var(--pc-motion-ease-standard);
}

.pc-card--interactive:hover {
  transform: translateY(-2px);
  border-color: var(--pc-color-semantic-border-accent);
  box-shadow: var(--pc-shadow-md);
}
</style>
