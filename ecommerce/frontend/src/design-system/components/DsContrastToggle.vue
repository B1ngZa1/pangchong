<template>
  <DsIconButton
    :label="highContrast ? '关闭高对比度' : '开启高对比度'"
    :pressed="highContrast"
    type="button"
    @click="toggle"
  >
    Aa
  </DsIconButton>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import DsIconButton from './DsIconButton.vue'
import { applyDesignTheme, getStoredDesignTheme, toggleDesignTheme } from '../theme'

const highContrast = ref(false)

onMounted(() => {
  highContrast.value = getStoredDesignTheme() === 'high-contrast'
  applyDesignTheme(highContrast.value ? 'high-contrast' : 'default')
})

function toggle() {
  const nextTheme = toggleDesignTheme(highContrast.value ? 'high-contrast' : 'default')
  highContrast.value = nextTheme === 'high-contrast'
}
</script>
