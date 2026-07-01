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
})
