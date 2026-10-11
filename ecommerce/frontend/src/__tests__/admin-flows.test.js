import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AdminProducts from '@/views/admin/Products.vue'
import AdminOrders from '@/views/admin/Orders.vue'
import AdminUsers from '@/views/admin/Users.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'

const { adminApi } = vi.hoisted(() => ({
  adminApi: {
    getProducts: vi.fn(), getCategories: vi.fn(), updateProduct: vi.fn(), createProduct: vi.fn(), toggleProductStatus: vi.fn(),
    getOrders: vi.fn(), getOrderDetail: vi.fn(), shipOrder: vi.fn(),
    getUsers: vi.fn(), getUserDetail: vi.fn(), updateUserStatus: vi.fn(),
    getDashboard: vi.fn(),
  },
}))
vi.mock('@/api', () => ({ adminApi }))
vi.mock('vue-router', () => ({ useRoute: () => ({ query: {} }) }))

const product = {
  id: 'product-1', name: '测试显卡', slug: 'test-gpu', category_id: 'gpu', price: 4599, stock: 10,
  is_active: true, price_source_name: '品牌官网', price_source_url: 'https://example.com/gpu',
  price_checked_at: '2026-09-01T09:00:00Z',
}
const order = { id: 'order-1', order_no: 'PC20260901', status: 'paid', items: [] }
const user = { id: 'user-1', username: 'customer', email: 'customer@example.com', is_active: true }

async function mountPage(component) {
  const wrapper = mount(component, { global: { stubs: { DsDialog: true } } })
  await flushPromises()
  return wrapper
}

describe('admin management flows', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    adminApi.getProducts.mockResolvedValue({ items: [{ ...product }], total: 60 })
    adminApi.getCategories.mockResolvedValue([{ id: 'gpu', name: '显卡', slug: 'gpu' }])
    adminApi.getOrders.mockResolvedValue({ items: [{ ...order }], total: 60 })
    adminApi.getUsers.mockResolvedValue({ items: [{ ...user }], total: 60 })
    adminApi.getDashboard.mockResolvedValue({ daily_stats: [{ date: '09-14', orders: 0, revenue: 0 }], order_status_counts: {} })
  })

  it.each([
    ['products', AdminProducts, 'getProducts', 'fetchProducts'],
    ['orders', AdminOrders, 'getOrders', 'fetchOrders'],
    ['users', AdminUsers, 'getUsers', 'fetchUsers'],
  ])('starts a new %s search on the first page and supports form submission', async (_name, component, apiMethod, fetchMethod) => {
    const wrapper = await mountPage(component)
    wrapper.vm.currentPage = 3
    await wrapper.vm[fetchMethod]()
    expect(adminApi[apiMethod]).toHaveBeenLastCalledWith(expect.objectContaining({ page: 3 }))

    await wrapper.get('form input').setValue('new search')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(adminApi[apiMethod]).toHaveBeenLastCalledWith(expect.objectContaining({ page: 1, keyword: 'new search' }))
    expect(wrapper.vm.currentPage).toBe(1)
    wrapper.unmount()
  })

  it.each([
    ['products', AdminProducts, 'getProducts', 'fetchProducts', 'products', product],
    ['orders', AdminOrders, 'getOrders', 'fetchOrders', 'orders', order],
    ['users', AdminUsers, 'getUsers', 'fetchUsers', 'users', user],
  ])('ignores an outdated %s response after a new filter request finishes', async (_name, component, apiMethod, fetchMethod, listKey, item) => {
    const wrapper = await mountPage(component)
    let resolveOld
    adminApi[apiMethod].mockImplementationOnce(() => new Promise(resolve => { resolveOld = resolve }))
    const oldRequest = wrapper.vm[fetchMethod]()
    adminApi[apiMethod].mockResolvedValueOnce({ items: [{ ...item, id: 'new-result' }], total: 1 })
    await wrapper.vm[fetchMethod]()
    resolveOld({ items: [{ ...item, id: 'old-result' }], total: 60 })
    await oldRequest
    expect(wrapper.vm[listKey][0].id).toBe('new-result')
    expect(wrapper.vm.total).toBe(1)
    wrapper.unmount()
  })

  it('preserves the original price check time when only product inventory changes', async () => {
    const wrapper = await mountPage(AdminProducts)
    wrapper.vm.openEdit(product)
    wrapper.vm.form.stock = 20
    await wrapper.vm.handleSubmit()
    expect(adminApi.updateProduct).toHaveBeenCalledWith(product.id, expect.objectContaining({
      stock: 20, price_checked_at: product.price_checked_at,
      price_source_name: product.price_source_name, price_source_url: product.price_source_url,
    }))
    wrapper.unmount()
  })

  it('clears the price check time when a source becomes incomplete', async () => {
    const wrapper = await mountPage(AdminProducts)
    wrapper.vm.openEdit(product)
    wrapper.vm.form.price_source_url = ''
    await wrapper.vm.handleSubmit()
    expect(adminApi.updateProduct).toHaveBeenCalledWith(product.id, expect.objectContaining({ price_checked_at: null }))
    wrapper.unmount()
  })

  it('does not send duplicate product status updates while an update is pending', async () => {
    const wrapper = await mountPage(AdminProducts)
    let resolveUpdate
    adminApi.toggleProductStatus.mockImplementationOnce(() => new Promise(resolve => { resolveUpdate = resolve }))
    const row = wrapper.vm.products[0]
    const firstUpdate = wrapper.vm.toggleStatus(row)
    await wrapper.vm.toggleStatus(row)
    expect(adminApi.toggleProductStatus).toHaveBeenCalledTimes(1)
    resolveUpdate()
    await firstUpdate
    expect(row.is_active).toBe(false)
    wrapper.unmount()
  })

  it('rejects blank shipment tracking and trims valid tracking before sending', async () => {
    const wrapper = await mountPage(AdminOrders)
    wrapper.vm.openShipDialog(order)
    wrapper.vm.shipForm = { shipping_company: '顺丰速运', tracking_number: '   ' }
    await wrapper.vm.confirmShip()
    expect(adminApi.shipOrder).not.toHaveBeenCalled()
    expect(wrapper.vm.shipError).toContain('物流单号')

    wrapper.vm.shipForm.tracking_number = ' SF123456789 '
    await wrapper.vm.confirmShip()
    expect(adminApi.shipOrder).toHaveBeenCalledWith(order.id, { shipping_company: '顺丰速运', tracking_number: 'SF123456789' })
    wrapper.unmount()
  })

  it('renders an empty dashboard with zero-width bars and a readable zero order count', async () => {
    const wrapper = await mountPage(AdminDashboard)
    const bars = wrapper.findAll('[style]')
    expect(bars).toHaveLength(6)
    expect(bars.every(bar => bar.attributes('style') === 'width: 0%;')).toBe(true)
    expect(wrapper.text()).toContain('0 单')
    expect(wrapper.html()).not.toContain('NaN')
    wrapper.unmount()
  })
})
