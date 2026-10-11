import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { DsBadge, DsButton, DsCard, DsEmptyState, DsField } from '@/design-system'

describe('PANGCHONG design system primitives', () => {
  it('exposes button variants, size and loading semantics', () => {
    const wrapper = mount(DsButton, {
      props: { variant: 'secondary', size: 'lg', loading: true },
      slots: { default: '保存设置' },
    })

    const button = wrapper.get('button')
    expect(button.attributes('data-variant')).toBe('secondary')
    expect(button.attributes('data-size')).toBe('lg')
    expect(button.attributes('aria-busy')).toBe('true')
    expect(button.attributes()).toHaveProperty('disabled')
    expect(button.text()).toContain('保存设置')
  })

  it('wires field label, hint and model updates accessibly', async () => {
    const wrapper = mount(DsField, {
      props: {
        id: 'email',
        label: '邮箱',
        hint: '用于接收订单更新',
        modelValue: '',
        'onUpdate:modelValue': value => wrapper.setProps({ modelValue: value }),
      },
    })

    const input = wrapper.get('input')
    expect(wrapper.get('label').attributes('for')).toBe('email')
    expect(input.attributes('aria-describedby')).toBe('email-hint')
    await input.setValue('hello@example.com')
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['hello@example.com'])
  })

  it('renders the shared card, badge and empty-state contracts', () => {
    expect(mount(DsCard, { slots: { default: '内容' } }).text()).toBe('内容')
    expect(mount(DsBadge, { props: { tone: 'warning' }, slots: { default: '待验证' } }).attributes('data-tone')).toBe('warning')
    expect(mount(DsEmptyState, { props: { title: '暂无商品', description: '稍后再试' } }).text()).toContain('稍后再试')
  })

  it('supports select fields with disabled and invalid states', async () => {
    const wrapper = mount(DsField, {
      props: {
        id: 'province',
        label: '省份',
        as: 'select',
        options: ['湖北省', { value: '上海市', label: '上海市' }],
        error: '请选择省份',
        required: true,
      },
    })

    const select = wrapper.get('select')
    expect(select.attributes('aria-invalid')).toBe('true')
    expect(select.findAll('option')).toHaveLength(3)
    await select.setValue('上海市')
    expect(wrapper.emitted('update:modelValue')).toEqual([['上海市']])
    expect(wrapper.get('[role="alert"]').text()).toBe('请选择省份')
  })
})
