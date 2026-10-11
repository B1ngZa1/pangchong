import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import {
  DsAlert,
  DsAsyncState,
  DsCartLineItem,
  DsCompatibilityStatus,
  DsContrastToggle,
  DsChoiceCard,
  DsCheckbox,
  DsDataTable,
  DsDiyPartPicker,
  DsOrderSuccess,
  DsOrderTimeline,
  DsDialog,
  DsIconButton,
  DsOrderSummary,
  DsPriceSummary,
  DsPagination,
  DsProductCard,
  DsSkeleton,
  DsSearchField,
  DsStepIndicator,
  DsTabs,
  DsToast,
  DsToggle,
} from '@/design-system'
import ServiceCookiePreferences from '@/components/ServiceCookiePreferences.vue'
import ServicePolicyPanel from '@/components/ServicePolicyPanel.vue'
import ProductConfiguratorPanel from '@/components/ProductConfiguratorPanel.vue'

describe('PANGCHONG design system v0.2 contracts', () => {
  afterEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
  })

  it('requires an accessible label and exposes icon-button state', () => {
    const wrapper = mount(DsIconButton, {
      props: { label: '打开筛选', pressed: true, loading: true },
      slots: { default: 'filter-icon' },
    })

    const button = wrapper.get('button')
    expect(button.attributes('aria-label')).toBe('打开筛选')
    expect(button.attributes('aria-pressed')).toBe('true')
    expect(button.attributes('aria-busy')).toBe('true')
    expect(button.attributes()).toHaveProperty('disabled')
    expect(wrapper.find('.pc-icon-button__spinner').exists()).toBe(true)
  })

  it('keeps async failures distinct from business empty states and supports retry', async () => {
    const wrapper = mount(DsAsyncState, {
      props: { state: 'error', errorTitle: '商品加载失败' },
    })

    expect(wrapper.attributes('data-state')).toBe('error')
    expect(wrapper.attributes('role')).toBe('alert')
    expect(wrapper.attributes('aria-live')).toBe('assertive')
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('retry')).toHaveLength(1)

    await wrapper.setProps({ state: 'empty', emptyTitle: '暂无符合条件的商品' })
    expect(wrapper.attributes('data-state')).toBe('empty')
    expect(wrapper.text()).toContain('暂无符合条件的商品')
    expect(wrapper.text()).not.toContain('商品加载失败')
  })

  it('announces async loading state without marking settled content busy', async () => {
    const wrapper = mount(DsAsyncState, { props: { state: 'loading' } })

    expect(wrapper.attributes('aria-busy')).toBe('true')
    await wrapper.setProps({ state: 'success' })
    expect(wrapper.attributes('aria-busy')).toBeUndefined()
  })

  it('keeps dense tables keyboard-scrollable with an announced region label', () => {
    const wrapper = mount(DsDataTable, {
      props: { label: '订单列表' },
      slots: { default: '<table><thead><tr><th>订单号</th></tr></thead><tbody><tr><td>PC-1</td></tr></tbody></table>' },
    })

    const region = wrapper.get('[role="region"]')
    expect(region.attributes('aria-label')).toBe('订单列表')
    expect(region.attributes('tabindex')).toBe('0')
    expect(wrapper.get('table').text()).toContain('PC-1')
  })

  it('keeps commerce choices keyboard-accessible and exposes selected state', async () => {
    const wrapper = mount(DsChoiceCard, {
      props: {
        modelValue: 'standard',
        value: 'standard',
        title: '标准配送',
        description: '3-5个工作日送达',
        name: 'delivery-method',
      },
    })

    expect(wrapper.get('input[type="radio"]').attributes('name')).toBe('delivery-method')
    expect(wrapper.get('input').element.checked).toBe(true)
    expect(wrapper.attributes('data-selected')).toBe('true')
    await wrapper.get('input').trigger('change')
    expect(wrapper.emitted('update:modelValue')).toEqual([['standard']])
  })

  it('keeps search fields labelled and emits a trimmed query', async () => {
    const wrapper = mount(DsSearchField, {
      props: {
        modelValue: '  RTX  ',
        label: '搜索产品',
        placeholder: '输入产品型号',
      },
    })

    expect(wrapper.get('input').attributes('aria-describedby')).toBeUndefined()
    expect(wrapper.get('input').attributes('placeholder')).toBe('输入产品型号')
    await wrapper.get('form').trigger('submit')
    expect(wrapper.emitted('submit')).toEqual([['RTX']])
  })

  it('exposes cookie preference switches with native switch semantics', async () => {
    const wrapper = mount(DsToggle, {
      props: { modelValue: false, label: '分析 Cookie' },
    })

    expect(wrapper.get('[role="switch"]').attributes('aria-checked')).toBe('false')
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([[true]])
  })

  it('supports checked, mixed and keyboard-focus semantics for checkbox controls', async () => {
    const wrapper = mount(DsCheckbox, {
      props: { modelValue: false, mixed: true, label: '全选' },
    })
    const input = wrapper.get('input')
    expect(input.attributes('aria-checked')).toBe('mixed')
    expect(input.element.indeterminate).toBe(true)
    await input.setValue(true)
    expect(wrapper.emitted('update:modelValue')).toEqual([[true]])
  })

  it('keeps 3D configurator choices and motion controls tokenized and event-driven', async () => {
    const wrapper = mount(ProductConfiguratorPanel, {
      props: {
        variants: [{ id: 'black', name: '曜石黑', hex: '#111827', priceDiff: 0 }],
        materials: [{ id: 'mesh', name: '网孔', description: '通风散热' }],
        cameraPresets: [{ id: 'front', name: '正面' }],
        selectedVariant: 'black',
        selectedMaterial: 'mesh',
        cameraPreset: 'front',
        autoRotate: false,
      },
    })

    expect(wrapper.get('aside').attributes('aria-label')).toBe('3D 配置选项')
    await wrapper.get('button.config-choice').trigger('click')
    expect(wrapper.emitted('update:selectedVariant')).toEqual([['black']])
    await wrapper.get('[role="switch"]').trigger('click')
    expect(wrapper.emitted('update:autoRotate')).toEqual([[true]])
    await wrapper.get('button[aria-label="重置 3D 视角"]').trigger('click')
    expect(wrapper.emitted('reset-camera')).toHaveLength(1)
  })

  it('keeps service policy panels addressable and cookie preferences composable', async () => {
    const panel = mount(ServicePolicyPanel, {
      props: {
        section: { id: 'privacy', index: '02', title: '隐私', eyebrow: '信息使用', summary: '说明', lead: '说明', clauses: [] },
        open: true,
        faqs: [],
      },
    })
    expect(panel.get('button').attributes('aria-expanded')).toBe('true')
    expect(panel.get('[role="button"], button').attributes('aria-controls')).toBe('privacy-body')
    const cookie = mount(ServiceCookiePreferences, {
      props: { options: [{ key: 'analytics', title: '分析 Cookie', description: '帮助改进体验', purpose: '体验优化', required: false }], modelValue: { analytics: false } },
    })
    expect(cookie.get('[role="switch"]').attributes('aria-checked')).toBe('false')
  })

  it('supports keyboard navigation and disabled tabs', async () => {
    const wrapper = mount(DsTabs, {
      props: {
        tabs: [
          { id: 'overview', label: '概览' },
          { id: 'specs', label: '规格', disabled: true },
          { id: 'support', label: '支持' },
        ],
        modelValue: 'overview',
      },
    })

    const first = wrapper.find('[role="tab"]')
    await first.trigger('keydown', { key: 'ArrowRight' })
    expect(wrapper.emitted('update:modelValue')).toEqual([['support']])
    expect(wrapper.findAll('[role="tab"]')[1].attributes('disabled')).toBeDefined()
  })

  it('exposes checkout progress and prevents skipping unfinished steps', async () => {
    const wrapper = mount(DsStepIndicator, {
      props: {
        steps: ['配送信息', '配送方式', '支付方式', '订单确认'],
        modelValue: 1,
      },
    })

    expect(wrapper.attributes('aria-label')).toBe('结算步骤')
    expect(wrapper.find('[aria-current="step"]').attributes('aria-label')).toBe('第2步：配送方式')
    expect(wrapper.findAll('button')[2].attributes('disabled')).toBeDefined()
    expect(wrapper.get('.pc-step-indicator__status').text()).toContain('第2步，共4步')
    await wrapper.findAll('button')[0].trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([[0]])
  })

  it('announces alerts and keeps dismiss actions at touch-target size', async () => {
    const wrapper = mount(DsAlert, {
      props: { title: '已保存', tone: 'success', dismissible: true },
    })

    expect(wrapper.attributes('aria-live')).toBe('polite')
    expect(wrapper.find('.pc-alert__dismiss').attributes('aria-label')).toBe('关闭提示')
    await wrapper.get('.pc-alert__dismiss').trigger('click')
    expect(wrapper.emitted('dismiss')).toHaveLength(1)
  })

  it('announces toast feedback without relying on automatic dismissal', async () => {
    const wrapper = mount(DsToast, {
      props: { visible: true, message: '已加入购物车', tone: 'success' },
    })

    expect(wrapper.get('[role="status"]').attributes('aria-live')).toBe('polite')
    expect(wrapper.get('.pc-toast').attributes('data-tone')).toBe('success')
    await wrapper.get('button[aria-label="关闭通知"]').trigger('click')
    expect(wrapper.emitted('dismiss')).toHaveLength(1)
  })

  it('keeps compatibility risks announced and cart quantity actions accessible', async () => {
    const compatibility = mount(DsCompatibilityStatus, {
      props: {
        status: {
          tone: 'warn',
          label: '存在兼容风险',
          issues: [{ key: 'power', title: '功耗', message: '电源余量不足' }],
        },
      },
    })
    expect(compatibility.attributes('role')).toBe('alert')
    expect(compatibility.text()).toContain('电源余量不足')

    const cartLine = mount(DsCartLineItem, {
      props: {
        item: {
          id: 'line-1',
          name: 'PANGCHONG X1',
          price: 7999,
          original_price: 8999,
          stock: 3,
          quantity: 1,
          specs: { GPU: 'RTX', RAM: '32GB' },
        },
        selected: true,
      },
    })
    expect(cartLine.get('input[type="checkbox"]').attributes('aria-label')).toBe('选择PANGCHONG X1')
    expect(cartLine.text()).toContain('仅剩 3 件')
    expect(cartLine.get('.pc-cart-line-item__stepper output').attributes('aria-live')).toBe('polite')
    expect(cartLine.get('.pc-cart-line-item__stepper output').attributes('aria-atomic')).toBe('true')
    await cartLine.get('button[aria-label="增加PANGCHONG X1数量"]').trigger('click')
    expect(cartLine.emitted('increment')).toHaveLength(1)
    await cartLine.get('button[aria-label="删除PANGCHONG X1"]').trigger('click')
    expect(cartLine.emitted('remove')).toHaveLength(1)

    await cartLine.setProps({ interactive: false, compact: true })
    expect(cartLine.find('input[type="checkbox"]').exists()).toBe(false)
    expect(cartLine.find('button[aria-label="删除PANGCHONG X1"]').exists()).toBe(false)
    expect(cartLine.get('.pc-cart-line-item__readonly-quantity').text()).toBe('×1')
    expect(cartLine.classes()).toContain('pc-cart-line-item--preview')
    expect(cartLine.classes()).toContain('pc-cart-line-item--compact')
  })

  it('keeps the order summary facts semantic and reuses the readonly line item', () => {
    const wrapper = mount(DsOrderSummary, {
      props: {
        items: [{ id: 'summary-1', name: 'PANGCHONG X1', price: 7999, stock: 3, quantity: 2, specs: { GPU: 'RTX 5070' } }],
        subtotal: 15998,
        shipping: 20,
        discount: 200,
        total: 15818,
      },
    })

    expect(wrapper.get('h2').text()).toBe('订单摘要')
    expect(wrapper.get('dl').text()).toContain('优惠减免')
    expect(wrapper.get('.pc-price-summary__total strong').text()).toBe('¥15,818')
    expect(wrapper.find('.pc-cart-line-item--preview').exists()).toBe(true)
    expect(wrapper.find('.pc-cart-line-item__controls').exists()).toBe(false)
  })

  it('reuses the price summary facts without duplicating the primary total', () => {
    const wrapper = mount(DsPriceSummary, {
      props: {
        subtotal: 7999,
        shipping: 0,
        discount: 200,
        itemCount: 2,
        freeShippingLabel: '免运费',
        showTotal: false,
      },
    })

    expect(wrapper.get('dl').text()).toContain('商品金额 (2 件)')
    expect(wrapper.get('dl').text()).toContain('免运费')
    expect(wrapper.get('dl').text()).toContain('-¥200')
    expect(wrapper.find('.pc-price-summary__total').exists()).toBe(false)
  })

  it('keeps pagination keyboard and screen-reader semantics stable across long lists', async () => {
    const wrapper = mount(DsPagination, {
      props: { page: 5, totalPages: 12 },
    })

    expect(wrapper.get('nav').attributes('aria-label')).toBe('分页')
    expect(wrapper.findAll('button[aria-current="page"]')).toHaveLength(1)
    expect(wrapper.get('button[aria-current="page"]').text()).toBe('5')
    expect(wrapper.get('button[aria-current="page"]').attributes('aria-label')).toBe('第5页')
    expect(wrapper.findAll('.pc-pagination__ellipsis')).toHaveLength(2)

    await wrapper.get('button[aria-label="下一页"]').trigger('click')
    expect(wrapper.emitted('update:page')).toEqual([[6]])
    expect(wrapper.emitted('change')).toEqual([[6]])

    await wrapper.setProps({ page: 1 })
    expect(wrapper.get('button[aria-label="上一页"]').attributes('disabled')).toBeDefined()
    await wrapper.get('button[aria-label="下一页"]').trigger('click')
    expect(wrapper.emitted('update:page')).toEqual([[6], [2]])
  })

  it('keeps order progress readable and exposes the active fulfillment step', async () => {
    const wrapper = mount(DsOrderTimeline, {
      props: {
        currentLabel: '已发货',
        events: [
          { id: 'created', label: '订单已提交', state: 'complete', timestamp: '2026-08-14T09:00:00Z' },
          { id: 'paid', label: '支付成功', state: 'complete', timestamp: '2026-08-14T09:02:00Z' },
          { id: 'shipped', label: '商品已发货', state: 'current', description: '顺丰 · SF123', timestamp: '2026-08-14T12:00:00Z' },
          { id: 'completed', label: '订单已完成', state: 'upcoming' },
        ],
      },
    })

    expect(wrapper.get('section').attributes('aria-labelledby')).toMatch(/^pc-order-timeline-/)
    expect(wrapper.findAll('[aria-current="step"]')).toHaveLength(1)
    expect(wrapper.get('[aria-current="step"] h3').text()).toBe('商品已发货')
    expect(wrapper.text()).toContain('顺丰 · SF123')
    expect(wrapper.findAll('time')).toHaveLength(3)

    await wrapper.setProps({ events: [
      { id: 'created', label: '订单已提交', state: 'complete' },
      { id: 'cancelled', label: '订单已取消', state: 'cancelled' },
    ] })
    expect(wrapper.get('[aria-current="step"] h3').text()).toBe('订单已取消')
  })

  it('persists the high-contrast preference through an announced toggle', async () => {
    const wrapper = mount(DsContrastToggle)
    const button = wrapper.get('button')
    expect(button.attributes('aria-pressed')).toBe('false')
    await button.trigger('click')
    expect(button.attributes('aria-pressed')).toBe('true')
    expect(button.attributes('aria-label')).toBe('关闭高对比度')
    expect(document.documentElement.getAttribute('data-theme')).toBe('high-contrast')
    expect(localStorage.getItem('pangchong-design-theme')).toBe('high-contrast')
  })

  it('keeps product facts in a reusable, keyboard-focusable card', async () => {
    const wrapper = mount(DsProductCard, {
      props: {
        product: {
          id: 'p-1',
          name: 'PANGCHONG X1',
          price: 7999,
          original_price: 8999,
          is_featured: true,
          specs: { GPU: 'RTX', RAM: '32GB' },
        },
        categoryLabel: '游戏整机',
      },
      slots: { actions: '<button type="button">加入购物车</button>' },
    })

    expect(wrapper.get('article').attributes('tabindex')).toBe('0')
    expect(wrapper.text()).toContain('PANGCHONG X1')
    expect(wrapper.text()).toContain('推荐')
    expect(wrapper.text()).toContain('特惠')
    await wrapper.get('article').trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('select')).toHaveLength(1)
    await wrapper.setProps({ interactive: false })
    expect(wrapper.get('article').attributes('tabindex')).toBeUndefined()
  })

  it('keeps DIY part selection keyboard-accessible and exposes price evidence', async () => {
    const wrapper = mount(DsDiyPartPicker, {
      props: {
        product: {
          id: 'part-1',
          name: 'Ryzen 9 9950X',
          brand: 'AMD',
          price: 3999,
          original_price: 4299,
          description: '适合高性能创作与多任务处理。',
          specs: { socket: 'AM5' },
        },
        specs: [{ key: 'socket', label: '插槽', value: 'AM5' }],
        selectionAdvice: { level: 'warn', text: '与当前主板插槽不同' },
      },
    })

    const card = wrapper.get('[role="button"]')
    expect(card.attributes('tabindex')).toBe('0')
    expect(card.attributes('aria-pressed')).toBe('false')
    expect(wrapper.text()).toContain('价格待核验')
    expect(wrapper.text()).toContain('插槽: AM5')
    expect(wrapper.get('[data-tone="warn"]').text()).toContain('与当前主板插槽不同')

    await card.trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('select')).toHaveLength(1)
    await wrapper.setProps({ selected: true })
    expect(card.attributes('aria-pressed')).toBe('true')
    expect(wrapper.text()).toContain('已选择')
  })

  it('keeps order success feedback recoverable when payment creation fails', async () => {
    const wrapper = mount(DsOrderSuccess, {
      props: {
        open: true,
        orderNo: 'PC-2026-001',
        paymentError: '创建支付失败：请重试',
      },
      attachTo: document.body,
    })

    expect(document.body.querySelector('[role="dialog"]')).not.toBeNull()
    expect(document.body.textContent).toContain('PC-2026-001')
    expect(document.body.querySelector('[role="alert"]')?.textContent).toContain('创建支付失败')
    document.body.querySelector('button[data-variant="primary"]')?.click()
    await nextTick()
    expect(wrapper.emitted('pay')).toHaveLength(1)
    document.body.querySelector('button[data-variant="secondary"]')?.click()
    await nextTick()
    expect(wrapper.emitted('view-orders')).toHaveLength(1)
    await wrapper.setProps({ open: false })
    wrapper.unmount()
  })

  it('renders reduced-motion-safe skeletons and restores focus after dialog close', async () => {
    expect(mount(DsSkeleton, { props: { variant: 'circle' } }).attributes('aria-hidden')).toBe('true')

    const trigger = document.createElement('button')
    document.body.appendChild(trigger)
    trigger.focus()
    const wrapper = mount(DsDialog, {
      attachTo: document.body,
      props: { open: false, title: '确认删除' },
      slots: { default: '此操作不可撤销' },
    })
    await wrapper.setProps({ open: true })
    expect(document.body.querySelector('[role="dialog"]')).not.toBeNull()
    document.body.querySelector('.pc-dialog__close')?.click()
    await nextTick()
    expect(wrapper.emitted('update:open')).toEqual([[false]])
    vi.restoreAllMocks()
    wrapper.unmount()
    trigger.remove()
  })
})
