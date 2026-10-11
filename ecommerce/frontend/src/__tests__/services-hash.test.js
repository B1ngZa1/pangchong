import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import Services from '@/views/Services.vue'

function createServicesRouter(initialPath) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/services',
        name: 'Services',
        component: Services,
      },
    ],
  })

  return router.push(initialPath).then(() => router)
}

function sectionSummary(wrapper, id) {
  return wrapper.get(`#${id} .policy-panel__summary`)
}

describe('Services hash-driven panels', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  const navbarSectionIds = [
    'tech-support',
    'warranty',
    'delivery',
    'faq',
    'privacy',
    'user-agreement',
    'cookie-settings',
  ]

  it.each(navbarSectionIds)(
    'opens %s on first load',
    async (sectionId) => {
      const router = await createServicesRouter(`/services#${sectionId}`)
      const wrapper = mount(Services, {
        attachTo: document.body,
        global: { plugins: [router] },
      })

      expect(sectionSummary(wrapper, sectionId).attributes('aria-expanded')).toBe('true')

      wrapper.unmount()
    },
  )

  it('opens each target after in-app hash navigation', async () => {
    const router = await createServicesRouter('/services')
    const wrapper = mount(Services, {
      attachTo: document.body,
      global: { plugins: [router] },
    })

    for (const sectionId of navbarSectionIds) {
      const summary = sectionSummary(wrapper, sectionId)
      if (summary.attributes('aria-expanded') === 'true') {
        await summary.trigger('click')
      }

      await router.push(`/services#${sectionId}`)
      await wrapper.vm.$nextTick()

      expect(sectionSummary(wrapper, sectionId).attributes('aria-expanded')).toBe('true')
    }

    wrapper.unmount()
  })

  it('routes a recognized support search to the matching policy section', async () => {
    const router = await createServicesRouter('/services')
    const wrapper = mount(Services, {
      attachTo: document.body,
      global: { plugins: [router] },
    })

    await wrapper.get('input[placeholder="搜索订单、故障、保修或配送问题"]').setValue('保修')
    await wrapper.get('form.pc-search-field').trigger('submit')
    await wrapper.vm.$nextTick()
    await new Promise(resolveNextTick => setTimeout(resolveNextTick, 0))

    expect(router.currentRoute.value.hash).toBe('#warranty')
    expect(wrapper.text()).toContain('已定位到「保修政策」。')
    expect(sectionSummary(wrapper, 'warranty').attributes('aria-expanded')).toBe('true')

    wrapper.unmount()
  })

  it('keeps cookie preference changes and save feedback inside the service contract', async () => {
    const router = await createServicesRouter('/services#cookie-settings')
    const wrapper = mount(Services, {
      attachTo: document.body,
      global: { plugins: [router] },
    })
    const cookiePanel = wrapper.get('#cookie-settings')
    const switches = cookiePanel.findAll('[role="switch"]')

    expect(switches).toHaveLength(4)
    expect(switches[0].attributes('aria-checked')).toBe('true')
    expect(switches[0].attributes('disabled')).toBeDefined()
    expect(switches[1].attributes('aria-checked')).toBe('true')

    await switches[1].trigger('click')
    expect(cookiePanel.findAll('[role="switch"]')[1].attributes('aria-checked')).toBe('false')

    await cookiePanel.get('.service-cookie-footer button').trigger('click')
    expect(JSON.parse(localStorage.getItem('pangchong-cookie-preferences')).preference).toBe(false)
    expect(cookiePanel.text()).toContain('Cookie 偏好已保存到当前浏览器。')

    wrapper.unmount()
  })

  it('keeps the service surface on named design tokens', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/Services.vue'), 'utf8')
    const tokens = readFileSync(resolve(process.cwd(), 'src/design-system/tokens/tokens.css'), 'utf8')

    expect(source).not.toMatch(/#[0-9a-f]{3,8}\b/i)
    expect(source).not.toMatch(/rgba?\(\s*(?!var\()/i)
    expect(source).toContain('var(--pc-color-theme-service-canvas)')
    expect(source).toContain('var(--pc-color-theme-service-surface)')
    expect(source).toContain('var(--pc-color-theme-service-text-primary)')
    expect(tokens).toContain('--pc-color-theme-service-canvas: #050505;')
    expect(tokens).toContain('--pc-color-theme-service-print-border: #d1d5db;')
  })
})
