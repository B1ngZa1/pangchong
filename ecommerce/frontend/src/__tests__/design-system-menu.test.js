import { h, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import DsMenu from '@/design-system/components/DsMenu.vue'

function mountMenu(props = {}) {
  return mount(DsMenu, {
    attachTo: document.body,
    props,
    slots: {
      trigger: ({ triggerProps }) => h('button', { ...triggerProps }, '账户'),
      default: () => [
        h('button', { type: 'button', role: 'menuitem' }, '我的订单'),
        h('a', { href: '/profile', role: 'menuitem' }, '个人中心'),
      ],
    },
  })
}

describe('DsMenu contract', () => {
  it('exposes menu relationship and opens with the first item focused', async () => {
    const wrapper = mountMenu({ open: false })
    const trigger = wrapper.get('button')

    expect(trigger.attributes('aria-haspopup')).toBe('menu')
    expect(trigger.attributes('aria-expanded')).toBe('false')

    await trigger.trigger('click')
    expect(wrapper.emitted('update:open')).toEqual([[true]])
    await wrapper.setProps({ open: true })
    await nextTick()

    expect(trigger.attributes('aria-expanded')).toBe('true')
    expect(document.activeElement?.textContent).toBe('我的订单')
    expect(wrapper.get('[role="menu"]').attributes('aria-label')).toBe('菜单')
    wrapper.unmount()
  })

  it('supports arrow navigation and restores focus after Escape', async () => {
    const wrapper = mountMenu({ open: true, label: '账户菜单' })
    await nextTick()
    const items = wrapper.findAll('[role="menuitem"]')
    expect(document.activeElement).toBe(items[0].element)

    await items[0].trigger('keydown', { key: 'ArrowDown' })
    expect(document.activeElement).toBe(items[1].element)
    await items[1].trigger('keydown', { key: 'ArrowUp' })
    expect(document.activeElement).toBe(items[0].element)

    await items[0].trigger('keydown', { key: 'Escape' })
    await nextTick()
    expect(wrapper.emitted('update:open')).toEqual([[false]])
    expect(document.activeElement).toBe(wrapper.get('[aria-haspopup="menu"]').element)
    wrapper.unmount()
  })

  it('closes before normal Tab navigation leaves the menu', async () => {
    const wrapper = mountMenu({ open: true })
    await nextTick()
    const firstItem = wrapper.get('[role="menuitem"]')
    await firstItem.trigger('keydown', { key: 'Tab' })

    expect(wrapper.emitted('update:open')).toEqual([[false]])
    wrapper.unmount()
  })
})
