<template>
  <DialogRoot :open="open" @update:open="handleOpenChange">
    <DialogPortal :force-mount="open">
      <DialogOverlay class="pc-dialog-layer" />
      <DialogContent
        v-bind="description ? {} : { 'aria-describedby': undefined }"
        class="pc-dialog"
        :data-size="size"
        @escape-key-down="guardDismiss"
        @pointer-down-outside="guardDismiss"
        @interact-outside="guardDismiss"
      >
        <header class="pc-dialog__header">
          <div>
            <DialogTitle class="pc-dialog__title">{{ title }}</DialogTitle>
            <DialogDescription v-if="description" class="pc-dialog__description">{{ description }}</DialogDescription>
          </div>
          <DialogClose v-if="dismissible" as-child>
            <button class="pc-dialog__close" type="button" aria-label="关闭对话框">×</button>
          </DialogClose>
        </header>
        <div class="pc-dialog__body"><slot /></div>
        <footer v-if="$slots.footer" class="pc-dialog__footer"><slot name="footer" /></footer>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<script setup>
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'

const props = defineProps({
  open: Boolean,
  title: {
    type: String,
    required: true,
  },
  description: String,
  size: {
    type: String,
    default: 'md',
    validator: value => ['sm', 'md', 'lg'].includes(value),
  },
  dismissible: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:open', 'close'])

function guardDismiss(event) {
  if (!props.dismissible) event.preventDefault()
}

function handleOpenChange(nextOpen) {
  if (!props.dismissible && !nextOpen) return
  emit('update:open', nextOpen)
  if (!nextOpen) emit('close')
}
</script>

<style scoped>
.pc-dialog-layer { position: fixed; z-index: var(--pc-z-index-modal); inset: 0; background: rgb(var(--pc-color-dark-950-rgb) / var(--pc-opacity-overlay)); }
.pc-dialog { position: fixed; z-index: calc(var(--pc-z-index-modal) + 1); top: 50%; left: 50%; width: min(100% - 2rem, 34rem); max-height: min(42rem, calc(100vh - 2rem)); overflow: auto; border: 1px solid var(--pc-color-semantic-border-default); border-radius: var(--pc-radius-lg); background: var(--pc-color-semantic-background-surface); color: var(--pc-color-semantic-text-primary); box-shadow: var(--pc-shadow-lg); transform: translate(-50%, -50%); }
.pc-dialog[data-size='sm'] { width: min(100% - 2rem, 26rem); }
.pc-dialog[data-size='lg'] { width: min(100% - 2rem, 52rem); }
.pc-dialog:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 3px; }
.pc-dialog__header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--pc-space-4); padding: var(--pc-space-6) var(--pc-space-6) 0; }
.pc-dialog__title, .pc-dialog__description { margin: 0; }
.pc-dialog__title { font-size: var(--pc-font-size-xl); font-weight: var(--pc-font-weight-bold); }
.pc-dialog__description { margin-top: var(--pc-space-2); color: var(--pc-color-semantic-text-muted); font-size: var(--pc-font-size-sm); line-height: var(--pc-font-line-height-normal); }
.pc-dialog__close { width: var(--pc-size-control-touch); height: var(--pc-size-control-touch); margin: calc(var(--pc-space-2) * -1); border: 0; border-radius: var(--pc-radius-md); background: transparent; color: var(--pc-color-semantic-text-muted); cursor: pointer; font-size: var(--pc-font-size-xl); line-height: 1; }
.pc-dialog__close:hover, .pc-dialog__close:focus-visible { background: var(--pc-color-semantic-background-elevated); color: var(--pc-color-semantic-text-primary); }
.pc-dialog__close:focus-visible { outline: 2px solid var(--pc-color-semantic-border-focus); outline-offset: 2px; }
.pc-dialog__body { padding: var(--pc-space-6); }
.pc-dialog__footer { display: flex; justify-content: flex-end; gap: var(--pc-space-3); padding: 0 var(--pc-space-6) var(--pc-space-6); }

@media (prefers-reduced-motion: no-preference) {
  .pc-dialog-layer[data-state='open'] { animation: pc-dialog-fade-in var(--pc-motion-duration-normal) var(--pc-motion-ease-standard); }
  .pc-dialog-layer[data-state='closed'] { animation: pc-dialog-fade-out var(--pc-motion-duration-fast) var(--pc-motion-ease-standard); }
  .pc-dialog[data-state='open'] { animation: pc-dialog-enter var(--pc-motion-duration-normal) var(--pc-motion-ease-standard); }
  .pc-dialog[data-state='closed'] { animation: pc-dialog-leave var(--pc-motion-duration-fast) var(--pc-motion-ease-standard); }
}

@keyframes pc-dialog-fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes pc-dialog-fade-out { from { opacity: 1; } to { opacity: 0; } }
@keyframes pc-dialog-enter { from { opacity: 0; transform: translate(-50%, calc(-50% + 8px)) scale(.985); } to { opacity: 1; transform: translate(-50%, -50%) scale(1); } }
@keyframes pc-dialog-leave { from { opacity: 1; transform: translate(-50%, -50%) scale(1); } to { opacity: 0; transform: translate(-50%, calc(-50% + 6px)) scale(.99); } }
</style>
