import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import AppNavbar from '@/components/AppNavbar.vue'

vi.mock('@/store', () => ({
  useCartStore: () => ({ totalItems: 0 }),
  useUserStore: () => ({
    isLoggedIn: false,
    isAdmin: false,
    user: null,
    logout: vi.fn(),
  }),
}))

const routes = [
  '/',
  '/products',
  '/products/:slug',
  '/services',
  '/store',
  '/diy',
  '/cart',
  '/orders',
  '/login',
  '/register',
].map((path) => ({ path, component: { template: '<div />' } }))

async function mountNavbar() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })

  await router.push('/')
  await router.isReady()

  const wrapper = mount(AppNavbar, {
    attachTo: document.body,
    global: { plugins: [router] },
  })

  return { router, wrapper }
}

function linkByText(wrapper, text) {
  return wrapper.findAll('a').find((link) => link.text().trim() === text)
}

async function openMenu(wrapper, text) {
  const link = linkByText(wrapper, text)
  expect(link, `missing navbar menu ${text}`).toBeTruthy()
  await link.trigger('focusin')
}

function megaMenuDestinations(wrapper) {
  return Object.fromEntries(
    wrapper.get('[data-qa="navbar-mega"]').findAll('a').map((link) => [
      link.text().trim(),
      link.attributes('href'),
    ]),
  )
}

describe('AppNavbar navigation contract', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('emits the shop filter and support shortcuts consumed by the target views', async () => {
    const { wrapper } = await mountNavbar()

    await openMenu(wrapper, '商店')
    expect(megaMenuDestinations(wrapper)).toMatchObject({
      '全部产品': '/products',
      '热门整机': '/products?tag=hot',
      '配送说明': '/services#delivery',
      '保修政策': '/services#warranty',
      '常见问题': '/services#faq',
    })

    await openMenu(wrapper, '电脑整机')
    expect(megaMenuDestinations(wrapper)).toMatchObject({
      '游戏本': '/products?category=gaming-laptop',
      '轻薄本': '/products?category=thin-laptop',
      '台式主机': '/products?category=desktop',
      '工作站': '/products?category=workstation',
      '电竞游戏': '/products?scene=gaming',
      '设计渲染': '/products?scene=creator',
      '学习办公': '/products?scene=office',
      '配置咨询': '/services#tech-support',
    })

    await openMenu(wrapper, '服务支持')
    expect(megaMenuDestinations(wrapper)).toMatchObject({
      '技术支持': '/services#tech-support',
      '保修政策': '/services#warranty',
      '配送说明': '/services#delivery',
      '常见问题': '/services#faq',
      '隐私政策': '/services#privacy',
      '用户协议': '/services#user-agreement',
      'Cookie 设置': '/services#cookie-settings',
    })

    wrapper.unmount()
  })

  it('trims search text and navigates with the keyword query parameter', async () => {
    const { router, wrapper } = await mountNavbar()
    const search = wrapper.get('.navbar-search')

    await search.get('input').setValue('  RTX 4070  ')
    await search.trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe('/products?keyword=RTX+4070')

    wrapper.unmount()
  })
})
