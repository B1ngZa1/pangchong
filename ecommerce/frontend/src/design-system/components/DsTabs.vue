<template>
  <div class="pc-tabs" :data-orientation="orientation">
    <div
      class="pc-tabs__list"
      role="tablist"
      :aria-label="ariaLabel"
      :aria-orientation="orientation"
    >
      <button
        v-for="(tab, index) in tabs"
        :key="tab.id"
        :ref="element => setTabRef(element, index)"
        class="pc-tabs__tab"
        :class="{ 'pc-tabs__tab--active': activeId === tab.id }"
        type="button"
        role="tab"
        :id="`${baseId}-tab-${tab.id}`"
        :aria-controls="`${baseId}-panel-${tab.id}`"
        :aria-selected="activeId === tab.id"
        :tabindex="activeId === tab.id ? 0 : -1"
        :disabled="tab.disabled"
        @click="select(tab)"
        @keydown="onKeydown($event, index)"
      >
        {{ tab.label }}
        <span v-if="tab.count !== undefined" class="pc-tabs__count">{{ tab.count || '' }}</span>
      </button>
    </div>
    <div
      class="pc-tabs__panel"
      role="tabpanel"
      :id="`${baseId}-panel-${activeId}`"
      :aria-labelledby="`${baseId}-tab-${activeId}`"
      tabindex="0"
    >
      <slot :selected="activeId" :tab="activeTab" />
    </div>
  </div>
</template>

<script>
let tabsCounter = 0
</script>

<script setup>
import { computed, nextTick, ref } from 'vue'

const props = defineProps({
  tabs: {
    type: Array,
    required: true,
    validator: value => value.length > 0 && value.every(tab => tab && tab.id && tab.label),
  },
  modelValue: String,
  ariaLabel: {
    type: String,
    default: '内容分组',
  },
  orientation: {
    type: String,
    default: 'horizontal',
    validator: value => ['horizontal', 'vertical'].includes(value),
  },
})

const emit = defineEmits(['update:modelValue'])
const baseId = `pc-tabs-${++tabsCounter}`
const tabRefs = ref([])
const firstEnabledId = computed(() => props.tabs.find(tab => !tab.disabled)?.id || props.tabs[0].id)
const activeId = computed(() => props.tabs.some(tab => tab.id === props.modelValue && !tab.disabled) ? props.modelValue : firstEnabledId.value)
const activeTab = computed(() => props.tabs.find(tab => tab.id === activeId.value) || props.tabs[0])

function setTabRef(element, index) {
  if (element) tabRefs.value[index] = element
}

function select(tab) {
  if (tab.disabled) return
  emit('update:modelValue', tab.id)
}

function onKeydown(event, index) {
  const key = props.orientation === 'vertical'
    ? { next: 'ArrowDown', previous: 'ArrowUp' }
    : { next: 'ArrowRight', previous: 'ArrowLeft' }
  if (![key.next, key.previous, 'Home', 'End'].includes(event.key)) return
  event.preventDefault()
  const enabled = props.tabs.map((tab, tabIndex) => ({ tab, tabIndex })).filter(({ tab }) => !tab.disabled)
  const current = enabled.findIndex(({ tabIndex }) => tabIndex === index)
  let nextIndex = current
  if (event.key === 'Home') nextIndex = 0
  else if (event.key === 'End') nextIndex = enabled.length - 1
  else nextIndex = (current + (event.key === key.next ? 1 : -1) + enabled.length) % enabled.length
  const target = enabled[nextIndex]
  select(target.tab)
  nextTick(() => tabRefs.value[target.tabIndex]?.focus())
}
</script>

<style scoped>
.pc-tabs__list { display: flex; gap: var(--pc-space-1); border-bottom: 1px solid var(--pc-color-semantic-border-subtle); }
.pc-tabs[data-orientation='vertical'] { display: grid; grid-template-columns: minmax(9rem, auto) minmax(0, 1fr); gap: var(--pc-space-6); }
.pc-tabs[data-orientation='vertical'] .pc-tabs__list { flex-direction: column; border-right: 1px solid var(--pc-color-semantic-border-subtle); border-bottom: 0; }
.pc-tabs__tab { position: relative; min-height: 2.75rem; padding: 0 var(--pc-space-3); border: 0; border-radius: var(--pc-radius-sm) var(--pc-radius-sm) 0 0; background: transparent; color: var(--pc-color-semantic-text-muted); cursor: pointer; font: inherit; font-size: var(--pc-font-size-sm); font-weight: var(--pc-font-weight-semibold); }
.pc-tabs__tab:hover:not(:disabled) { color: var(--pc-color-semantic-text-primary); background: var(--pc-color-semantic-background-elevated); }
.pc-tabs__tab--active { color: var(--pc-color-semantic-text-primary); }
.pc-tabs__tab--active::after { position: absolute; right: var(--pc-space-3); bottom: -1px; left: var(--pc-space-3); height: 2px; border-radius: var(--pc-radius-full); background: var(--pc-color-semantic-action-primary); content: ''; }
.pc-tabs[data-orientation='vertical'] .pc-tabs__tab { border-radius: var(--pc-radius-sm); text-align: left; }
.pc-tabs[data-orientation='vertical'] .pc-tabs__tab--active::after { top: var(--pc-space-2); right: auto; bottom: var(--pc-space-2); left: 0; width: 2px; height: auto; }
.pc-tabs__tab:disabled { cursor: not-allowed; opacity: .48; }
.pc-tabs__tab:focus-visible, .pc-tabs__panel:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 2px; }
.pc-tabs__count { margin-left: var(--pc-space-1); color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-xs); }
.pc-tabs__panel { padding-top: var(--pc-space-5); }
</style>
