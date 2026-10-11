import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import Cart from '@/views/Cart.vue'
import { useCartStore } from '@/store/cart'

const routes = ['/cart', '/products', '/services', '/store', '/checkout']
  .map(path => ({ path, component: { template: '<div />' } }))

async function mountCart() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const cart = useCartStore()
  cart.addLocalItem({ id: 'cart-navigation-product', name: '测试商品', price: 1299, stock: 5 })
  const router = createRouter({ history: createMemoryHistory(), routes })
  await router.push('/cart')
  await router.isReady()
  const wrapper = mount(Cart, { global: { plugins: [pinia, router] } })
  return { wrapper, router }
}

describe('Cart navigation contract', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('turns summary destinations into real recoverable links', async () => {
    const { wrapper } = await mountCart()

    const hrefByText = text => wrapper.findAll('a').find(link => link.text().includes(text))?.attributes('href')
    expect(hrefByText('查看胖虫线下自提点')).toBe('/store')
    expect(hrefByText('查看配送选项')).toBe('/services#delivery')
    expect(hrefByText('查看门店位置')).toBe('/store')
    expect(hrefByText('查看常见问题')).toBe('/services#faq')

    wrapper.unmount()
  })
})
