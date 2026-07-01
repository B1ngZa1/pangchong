import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import api from '@/api'
import Products from '@/views/Products.vue'
import { buildProductListParams } from '@/utils/productCatalogFilters'

vi.mock('@/api', () => ({
  default: {
    get: vi.fn()
  }
}))

vi.mock('@/store', () => ({
  useCartStore: () => ({
    addToCart: vi.fn()
  }),
  useNotifyStore: () => ({
    show: vi.fn()
  })
}))

const categories = [
  { id: 'category-gaming', name: 'Gaming laptops', slug: 'laptop-gaming' },
  { id: 'category-thin', name: 'Thin laptops', slug: 'laptop-thin' },
  { id: 'category-desktop', name: 'Desktop PCs', slug: 'desktop' },
  { id: 'category-workstation', name: 'Workstations', slug: 'workstation' }
]

const product = {
  id: 'product-1',
  slug: 'pangchong-product',
  name: 'Pangchong Product',
  description: 'Regression fixture',
  category_id: 'category-gaming',
  price: 6999,
  original_price: 7999,
  image_url: '',
  specs: { cpu: 'i7' },
  is_featured: true
}

function mockApi() {
  api.get.mockImplementation((url) => {
    if (url === '/products/categories') return Promise.resolve(categories)
    if (url === '/products') {
      return Promise.resolve({
        items: [product],
        total: 1,
        page: 1,
        page_size: 20,
        pages: 1
      })
    }
    return Promise.reject(new Error(`Unexpected API request: ${url}`))
  })
}

function productRequests() {
  return api.get.mock.calls.filter(([url]) => url === '/products')
}

function lastProductParams() {
  return productRequests().at(-1)?.[1]?.params
}

async function mountProducts(query = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/products', component: Products },
      { path: '/products/:slug', component: { template: '<div />' } }
    ]
  })

  await router.push({ path: '/products', query })
  await router.isReady()

  const wrapper = mount(Products, {
    global: {
      plugins: [router]
    }
  })
  await flushPromises()
  return { router, wrapper }
}

describe('Products query-driven filters', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApi()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it.each([
    ['gaming-laptop', 'category-gaming'],
    ['thin-laptop', 'category-thin'],
    ['desktop', 'category-desktop'],
    ['workstation', 'category-workstation'],
  ])('maps navbar category=%s to catalog category %s', async (category, categoryId) => {
    const { wrapper } = await mountProducts({ category })

    expect(lastProductParams()).toMatchObject({
      page: 1,
      page_size: 20,
      category_id: categoryId
    })

    wrapper.unmount()
  })

  it('turns the hot tag route into a featured hot-product catalog request', async () => {
    const { wrapper } = await mountProducts({ tag: 'hot' })

    expect(lastProductParams()).toMatchObject({
      page: 1,
      page_size: 20,
      is_featured: true,
      brand: '胖虫',
      sort_by: 'sold_count',
      sort_order: 'desc'
    })
    expect(lastProductParams()).not.toHaveProperty('keyword')

    wrapper.unmount()
  })

  it.each([
    ['gaming', '游戏'],
    ['creator', '创作'],
    ['office', '办公'],
  ])('turns navbar scene=%s into a complete-system catalog filter', async (scene, keyword) => {
    const { wrapper } = await mountProducts({ scene })

    expect(lastProductParams()).toMatchObject({
      page: 1,
      page_size: 20,
      brand: '胖虫',
      keyword
    })

    wrapper.unmount()
  })

  it('keeps keyword search as the API keyword filter', async () => {
    const { wrapper } = await mountProducts({ keyword: 'RTX 4070' })

    expect(lastProductParams()).toMatchObject({
      page: 1,
      page_size: 20,
      keyword: 'RTX 4070'
    })

    wrapper.unmount()
  })

  it('refetches when a catalog query parameter changes', async () => {
    const { router, wrapper } = await mountProducts({ category: 'desktop' })
    vi.mocked(api.get).mockClear()
    mockApi()

    await router.push({ path: '/products', query: { category: 'thin-laptop' } })
    await flushPromises()

    expect(productRequests()).toHaveLength(1)
    expect(lastProductParams()).toMatchObject({
      page: 1,
      page_size: 20,
      category_id: 'category-thin'
    })

    wrapper.unmount()
  })
})

describe('buildProductListParams', () => {
  it('keeps an explicit keyword ahead of a scene-derived keyword', () => {
    expect(buildProductListParams({
      page: 2,
      currentCatId: null,
      query: { keyword: ' RTX ', scene: 'gaming' }
    })).toMatchObject({
      page: 2,
      page_size: 20,
      keyword: 'RTX'
    })
    expect(buildProductListParams({
      page: 2,
      currentCatId: null,
      query: { keyword: ' RTX ', scene: 'gaming' }
    })).not.toHaveProperty('brand')
  })
})
