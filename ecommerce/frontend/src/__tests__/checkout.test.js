import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import Checkout from '@/views/Checkout.vue'
import { authApi, cartApi, orderApi } from '@/api'
import { useCartStore } from '@/store/cart'

const { routerPush } = vi.hoisted(() => ({
  routerPush: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: routerPush }),
}))

vi.mock('@/utils/payment', () => ({
  redirectToPayment: vi.fn(),
}))

vi.mock('@/api', () => ({
  authApi: {
    register: vi.fn(),
    login: vi.fn(),
    refreshToken: vi.fn(),
    getProfile: vi.fn(),
    updateProfile: vi.fn(),
    changePassword: vi.fn(),
    getAddresses: vi.fn(),
    createAddress: vi.fn(),
    updateAddress: vi.fn(),
    deleteAddress: vi.fn(),
  },
  cartApi: {
    getCart: vi.fn(),
    addToCart: vi.fn(),
    updateCartItem: vi.fn(),
    removeCartItem: vi.fn(),
    clearCart: vi.fn(),
    mergeCart: vi.fn(),
  },
  orderApi: {
    createOrder: vi.fn(),
    getOrders: vi.fn(),
    getOrder: vi.fn(),
    cancelOrder: vi.fn(),
  },
  paymentApi: {
    createPayment: vi.fn(),
  },
}))

const address = {
  id: '11111111-1111-1111-1111-111111111111',
  recipient_name: 'Test Buyer',
  phone: '13800000000',
  province: 'Shanghai',
  city: 'Shanghai',
  district: 'Pudong',
  address: 'No. 1 Test Road',
  postal_code: '200000',
  is_default: true,
  created_at: '2026-06-15T00:00:00Z',
}

function backendCartItem(overrides = {}) {
  return {
    id: '22222222-2222-2222-2222-222222222222',
    product_id: '33333333-3333-3333-3333-333333333333',
    item_type: 'product',
    name: 'Backend GPU',
    brand: 'Pangchong',
    model: 'RTX',
    description: '',
    specs: { chip: 'RTX' },
    price: 4999,
    original_price: null,
    image_url: '/gpu.png',
    stock: 10,
    quantity: 1,
    selected: true,
    is_in_stock: true,
    ...overrides,
  }
}

function diyCustomItem() {
  return {
    id: 'local_diy_cart_row',
    product_id: 'diy-selected-build',
    item_type: 'custom',
    custom_type: 'diy_pc',
    name: 'DIY custom PC',
    brand: 'Pangchong',
    model: 'DIY',
    description: 'Selected DIY build',
    specs: {
      custom_type: 'diy_pc',
      CPU: 'Ryzen 9',
      GPU: 'RTX 5090',
    },
    snapshot: {
      type: 'diy_pc',
      parts: [
        { key: 'cpu', label: '处理器 CPU', product_id: 'cpu-1', brand: 'AMD', name: 'Ryzen 9' },
        { key: 'gpu', label: '显卡 GPU', product_id: 'gpu-1', brand: 'NVIDIA', name: 'RTX 5090' },
      ],
      appearance: {
        variant_name: '虫翼绿',
        material_name: '高亮涂层',
      },
    },
    price: 12999,
    original_price: null,
    image_url: '',
    stock: 1,
    quantity: 1,
    selected: true,
    is_in_stock: true,
  }
}

function localProductItem() {
  return {
    ...backendCartItem({
      id: 'local_guest_gpu',
      product_id: '77777777-7777-7777-7777-777777777777',
      item_type: undefined,
      name: 'Guest GPU',
      quantity: 2,
    }),
  }
}

function backendApiCartItem(item, id = '88888888-8888-8888-8888-888888888888') {
  return {
    id,
    product_id: item.product_id,
    product_name: item.name,
    product_brand: item.brand,
    product_model: item.model,
    product_description: item.description,
    product_specs: item.specs,
    product_price: item.price,
    product_original_price: item.original_price,
    product_image: item.image_url,
    product_stock: item.stock,
    quantity: item.quantity,
    is_in_stock: item.is_in_stock,
  }
}

describe('Checkout', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.unstubAllGlobals()
    vi.stubGlobal('alert', vi.fn())
    document.body.innerHTML = ''
    localStorage.clear()
    localStorage.setItem('token', 'test-access-token')
    setActivePinia(createPinia())

    authApi.getProfile.mockResolvedValue({ id: 'user-1', username: 'buyer' })
    authApi.getAddresses.mockResolvedValue([address])
    cartApi.getCart.mockResolvedValue({ items: [] })
    orderApi.createOrder.mockResolvedValue({
      id: '44444444-4444-4444-4444-444444444444',
      order_no: 'PC202606150001',
    })
  })

  it('submits selected backend cart item ids with DIY custom items and only removes the local custom row', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const cart = useCartStore()
    const selectedBackendItem = backendCartItem()
    const unselectedBackendItem = backendCartItem({
      id: '55555555-5555-5555-5555-555555555555',
      product_id: '66666666-6666-6666-6666-666666666666',
      name: 'Backend PSU',
      selected: false,
    })
    const selectedDiyItem = diyCustomItem()

    cart.items = [selectedBackendItem, unselectedBackendItem, selectedDiyItem]
    localStorage.setItem('pangchong_local_cart', JSON.stringify([selectedDiyItem]))

    const removeLocalItemsSpy = vi.spyOn(cart, 'removeLocalItems')
    const fetchCartSpy = vi.spyOn(cart, 'fetchCart').mockResolvedValue(undefined)

    const wrapper = mount(Checkout, {
      global: {
        plugins: [pinia],
        stubs: {
          AddressForm: true,
          RouterLink: true,
          Teleport: true,
        },
      },
    })
    await flushPromises()

    wrapper.vm.currentStep = 3
    await nextTick()

    expect(wrapper.text()).toContain('虫翼绿 / 高亮涂层')
    expect(wrapper.text()).toContain('AMD Ryzen 9')
    expect(wrapper.text()).toContain('NVIDIA RTX 5090')

    await wrapper.vm.submitOrder()
    await flushPromises()

    expect(orderApi.createOrder).toHaveBeenCalledWith({
      address_id: address.id,
      remark: null,
      cart_item_ids: [selectedBackendItem.id],
      custom_items: [
        {
          product_name: selectedDiyItem.name,
          product_image: null,
          product_specs: {
            ...selectedDiyItem.specs,
            _snapshot: selectedDiyItem.snapshot,
          },
          price: selectedDiyItem.price,
          quantity: selectedDiyItem.quantity,
        },
      ],
    })
    expect(removeLocalItemsSpy).toHaveBeenCalledWith([selectedDiyItem.id])
    expect(fetchCartSpy).toHaveBeenCalledTimes(1)
    expect(cart.items.map(item => item.id)).toEqual([
      selectedBackendItem.id,
      unselectedBackendItem.id,
    ])
    expect(JSON.parse(localStorage.getItem('pangchong_local_cart') || '[]')).toEqual([])
  })

  it('promotes a selected local product and submits it through the stock-backed cart path', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const cart = useCartStore()
    const localProduct = localProductItem()
    const backendProduct = backendApiCartItem(localProduct)
    cart.items = [localProduct]
    localStorage.setItem('pangchong_local_cart', JSON.stringify([localProduct]))
    cartApi.addToCart.mockResolvedValue(backendProduct)
    cartApi.getCart
      .mockResolvedValueOnce({ items: [backendProduct] })
      .mockResolvedValueOnce({ items: [] })

    const wrapper = mount(Checkout, {
      global: {
        plugins: [pinia],
        stubs: {
          AddressForm: true,
          RouterLink: true,
          Teleport: true,
        },
      },
    })
    await flushPromises()

    wrapper.vm.currentStep = 3
    await nextTick()
    await wrapper.vm.submitOrder()
    await flushPromises()

    expect(cartApi.addToCart).toHaveBeenCalledWith({
      product_id: localProduct.product_id,
      quantity: localProduct.quantity,
    }, undefined)
    expect(orderApi.createOrder).toHaveBeenCalledWith({
      address_id: address.id,
      remark: null,
      cart_item_ids: null,
      custom_items: [],
    })
    expect(JSON.parse(localStorage.getItem('pangchong_local_cart') || '[]')).toEqual([])
  })
})
