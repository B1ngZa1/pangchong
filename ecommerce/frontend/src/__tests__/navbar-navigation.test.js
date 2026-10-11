import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import AppNavbar from '@/components/AppNavbar.vue'

const userStoreMock = vi.hoisted(() => ({
  isLoggedIn: false,
  isAdmin: false,
  user: null,
  logout: vi.fn(),
}))

vi.mock('@/store', () => ({
  useCartStore: () => ({ totalItems: 0 }),
  useUserStore: () => userStoreMock,
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
  '/user/profile',
  '/admin/dashboard',
  '/login',
  '/register',
].map((path) => ({ path, component: { template: '<div />' } }))

async function mountNavbar(path = '/') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes,
  })

  await router.push(path)
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
    userStoreMock.isLoggedIn = false
    userStoreMock.isAdmin = false
    userStoreMock.user = null
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

  it('exposes the active route to assistive technology', async () => {
    const { wrapper } = await mountNavbar('/products')

    expect(linkByText(wrapper, '商店').attributes('aria-current')).toBe('page')
    expect(linkByText(wrapper, '电脑整机').attributes('aria-current')).toBeUndefined()
    expect(linkByText(wrapper, 'DIY 配件').attributes('aria-current')).toBeUndefined()

    await openMenu(wrapper, '商店')
    const menuLinks = wrapper.get('[data-qa="navbar-mega"]').findAll('a')
    const featuredLink = menuLinks.find((link) => link.text().trim() === '全部产品')
    const aliasLink = menuLinks.find((link) => link.text().trim() === '选购商品')
    expect(featuredLink.attributes('aria-current')).toBe('page')
    expect(aliasLink.attributes('aria-current')).toBeUndefined()

    wrapper.unmount()

    const filtered = await mountNavbar('/products?category=desktop')
    expect(linkByText(filtered.wrapper, '商店').attributes('aria-current')).toBeUndefined()
    expect(linkByText(filtered.wrapper, '电脑整机').attributes('aria-current')).toBe('page')
    await openMenu(filtered.wrapper, '电脑整机')
    const categoryLink = filtered.wrapper.get('[data-qa="navbar-mega"]').findAll('a').find((link) => link.text().trim() === '台式主机')
    expect(categoryLink.attributes('aria-current')).toBe('page')
    filtered.wrapper.unmount()
  })

  it('keeps the mobile navigation keyboard-contained and restores trigger focus', async () => {
    const { wrapper } = await mountNavbar('/')
    const trigger = wrapper.get('[aria-controls="mobile-navigation"]')

    expect(trigger.attributes('aria-expanded')).toBe('false')
    await trigger.trigger('click')
    await flushPromises()

    const panel = wrapper.get('#mobile-navigation')
    const links = panel.findAll('a')
    expect(trigger.attributes('aria-expanded')).toBe('true')
    expect(document.activeElement).toBe(links[0].element)

    await links[links.length - 1].trigger('keydown', { key: 'Tab' })
    expect(document.activeElement).toBe(links[0].element)

    await links[0].trigger('keydown', { key: 'Tab', shiftKey: true })
    expect(document.activeElement).toBe(links[links.length - 1].element)

    await links[links.length - 1].trigger('keydown', { key: 'Escape' })
    await flushPromises()
    expect(wrapper.find('#mobile-navigation').exists()).toBe(false)
    expect(trigger.attributes('aria-expanded')).toBe('false')
    expect(document.activeElement).toBe(trigger.element)

    wrapper.unmount()
  })

  it('moves focus into the mobile search and returns it on Escape', async () => {
    const { wrapper } = await mountNavbar('/')
    const trigger = wrapper.get('[aria-controls="mobile-search-panel"]')

    await trigger.trigger('click')
    await flushPromises()
    expect(trigger.attributes('aria-expanded')).toBe('true')
    expect(document.activeElement).toBe(wrapper.get('#mobile-search-panel input').element)

    await wrapper.get('#mobile-search-panel input').trigger('keydown', { key: 'Escape' })
    await flushPromises()
    expect(wrapper.find('#mobile-search-panel').exists()).toBe(false)
    expect(trigger.attributes('aria-expanded')).toBe('false')
    expect(document.activeElement).toBe(trigger.element)

    wrapper.unmount()
  })

  it('uses the shared menu contract for the authenticated user menu', async () => {
    userStoreMock.isLoggedIn = true
    userStoreMock.isAdmin = true
    userStoreMock.user = { nickname: '胖虫用户' }

    const { wrapper } = await mountNavbar('/')
    const trigger = wrapper.get('[aria-haspopup="menu"]')
    expect(trigger.attributes('aria-controls')).toMatch(/^pc-menu-/)
    expect(trigger.attributes('aria-expanded')).toBe('false')

    await trigger.trigger('click')
    await flushPromises()
    const menu = wrapper.get('[role="menu"]')
    const items = menu.findAll('[role="menuitem"]')
    expect(trigger.attributes('aria-expanded')).toBe('true')
    expect(items.map(item => item.text().trim())).toEqual(['我的订单', '个人中心', '管理后台', '退出登录'])
    expect(document.activeElement).toBe(items[0].element)

    await items[0].trigger('keydown', { key: 'ArrowDown' })
    expect(document.activeElement).toBe(items[1].element)
    await items[1].trigger('keydown', { key: 'Escape' })
    await flushPromises()
    expect(trigger.attributes('aria-expanded')).toBe('false')
    expect(document.activeElement).toBe(trigger.element)

    wrapper.unmount()
  })
})
