import { defineStore } from 'pinia'
import { ref } from 'vue'

export type NotifyType = 'success' | 'error' | 'warning' | 'info'

export const useNotifyStore = defineStore('notify', () => {
  const visible = ref(false)
  const message = ref('')
  const type = ref<NotifyType>('info')
  let timer: ReturnType<typeof setTimeout> | null = null

  function show(nextMessage: string, nextType: NotifyType = 'info', duration = 2600) {
    if (!nextMessage?.trim()) return
    if (timer) clearTimeout(timer)

    message.value = nextMessage
    type.value = nextType
    visible.value = true

    if (duration > 0) {
      timer = setTimeout(() => {
        visible.value = false
        timer = null
      }, duration)
    }
  }

  function close() {
    visible.value = false
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  return { visible, message, type, show, close }
})

