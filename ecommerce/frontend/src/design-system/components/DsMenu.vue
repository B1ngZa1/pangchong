<template>
  <div ref="rootRef" class="pc-menu">
    <slot name="trigger" :trigger-props="triggerProps" />

    <Transition name="pc-menu">
      <div
        v-if="open"
        :id="menuId"
        ref="menuRef"
        class="pc-menu__popover"
        :data-align="align"
        role="menu"
        :aria-label="label"
        tabindex="-1"
        @keydown="onMenuKeydown"
        @click="onMenuClick"
      >
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

let menuCounter = 0

const props = defineProps({
  open: Boolean,
  label: {
    type: String,
    default: '菜单',
  },
  align: {
    type: String,
    default: 'end',
    validator: value => ['start', 'end'].includes(value),
  },
  closeOnSelect: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:open', 'close'])
const rootRef = ref(null)
const menuRef = ref(null)
const triggerId = `pc-menu-${++menuCounter}-trigger`
const menuId = `pc-menu-${menuCounter}-content`

const triggerProps = computed(() => ({
  id: triggerId,
  type: 'button',
  'aria-haspopup': 'menu',
  'aria-expanded': String(props.open),
  'aria-controls': menuId,
  onClick: toggle,
  onKeydown: onTriggerKeydown,
}))

function menuItems() {
  return [...menuRef.value?.querySelectorAll('[role="menuitem"]:not([aria-disabled="true"]):not([disabled])') || []]
}

function focusTrigger() {
  rootRef.value?.querySelector(`[id="${triggerId}"]`)?.focus?.()
}

async function openMenu() {
  if (props.open) return
  emit('update:open', true)
  await nextTick()
  menuItems()[0]?.focus?.()
  if (!menuItems().length) menuRef.value?.focus?.()
}

function close({ restoreFocus = true } = {}) {
  if (!props.open) return
  const shouldRestoreFocus = restoreFocus && menuRef.value?.contains(document.activeElement)
  emit('update:open', false)
  emit('close')
  if (shouldRestoreFocus) {
    nextTick(() => focusTrigger())
  }
}

function toggle() {
  if (props.open) close()
  else openMenu()
}

function onTriggerKeydown(event) {
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault()
    openMenu()
  }
}

function onMenuKeydown(event) {
  if (event.key === 'Escape') {
    event.preventDefault()
    close()
    return
  }

  if (event.key === 'Tab') {
    close({ restoreFocus: false })
    return
  }

  const items = menuItems()
  if (!items.length) return
  const currentIndex = items.indexOf(document.activeElement)
  let nextIndex = currentIndex

  if (event.key === 'ArrowDown') nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0
  else if (event.key === 'ArrowUp') nextIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1
  else if (event.key === 'Home') nextIndex = 0
  else if (event.key === 'End') nextIndex = items.length - 1
  else return

  event.preventDefault()
  items[nextIndex]?.focus()
}

function onMenuClick(event) {
  if (!props.closeOnSelect) return
  const target = event.target instanceof HTMLElement ? event.target.closest('[role="menuitem"]') : null
  if (target && target.getAttribute('aria-disabled') !== 'true') close({ restoreFocus: false })
}

function onDocumentClick(event) {
  if (!props.open || !(event.target instanceof Node) || rootRef.value?.contains(event.target)) return
  close({ restoreFocus: false })
}

watch(() => props.open, async isOpen => {
  if (!isOpen) return
  await nextTick()
  menuItems()[0]?.focus?.()
}, { immediate: true })

onMounted(() => document.addEventListener('click', onDocumentClick))
onUnmounted(() => document.removeEventListener('click', onDocumentClick))
</script>

<style scoped>
.pc-menu { position: relative; display: inline-flex; min-width: 0; }
.pc-menu__popover { position: absolute; z-index: var(--pc-z-index-dropdown, 40); top: calc(100% + var(--pc-space-2)); min-width: 11rem; overflow: hidden; border: 1px solid var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-md); background: var(--pc-color-semantic-background-surface); box-shadow: var(--pc-shadow-lg); }
.pc-menu__popover[data-align='start'] { left: 0; }
.pc-menu__popover[data-align='end'] { right: 0; }
.pc-menu__popover:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 2px; }
.pc-menu-enter-active, .pc-menu-leave-active { transition: opacity var(--pc-motion-duration-fast) var(--pc-motion-ease-standard), transform var(--pc-motion-duration-fast) var(--pc-motion-ease-standard); transform-origin: top right; }
.pc-menu-enter-from, .pc-menu-leave-to { opacity: 0; transform: translateY(-4px) scale(.98); }
</style>
