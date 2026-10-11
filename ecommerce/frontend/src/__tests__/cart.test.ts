import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCartStore } from '@/store/cart'
import { useUserStore } from '@/store/user'
import { authApi, cartApi } from '@/api'

describe('Cart Store', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('initializes with empty cart', () => {
    const cart = useCartStore()
    expect(cart.isEmpty).toBe(true)
    expect(cart.totalItems).toBe(0)
    expect(cart.subtotal).toBe(0)
  })

  it('adds local item correctly', () => {
    const cart = useCartStore()
    cart.addLocalItem({
      id: 'test-1',
      name: '测试CPU',
      price: 2999,
      stock: 10,
    })
    expect(cart.totalItems).toBe(1)
    expect(cart.isEmpty).toBe(false)
    expect(cart.subtotal).toBe(2999)
    const item = cart.items[0]
    expect(item.name).toBe('测试CPU')
    expect(item.price).toBe(2999)
    expect(item.selected).toBe(true)
    expect(item.item_type).toBe('product')
    expect(cart.isLocalItem(item)).toBe(true)
    expect(cart.isCustomItem(item)).toBe(false)
  })

  it('stores custom local item snapshots', () => {
    const cart = useCartStore()
    cart.addCustomItem({
      id: 'diy-test',
      name: '胖虫 DIY 整机配置',
      price: 12999,
      custom_type: 'diy_pc',
      specs: {
        '配置类型': 'DIY 装机整机',
        '处理器 CPU': 'Ryzen 9',
      },
      snapshot: {
        type: 'diy_pc',
        parts: [{ key: 'cpu', product_id: 'cpu-1' }],
      },
    })

    expect(cart.totalItems).toBe(1)
    expect(cart.items[0].item_type).toBe('custom')
    expect(cart.items[0].custom_type).toBe('diy_pc')
    expect(cart.items[0].snapshot?.type).toBe('diy_pc')
    expect(cart.isCustomItem(cart.items[0])).toBe(true)
  })

  it('hydrates legacy guest products separately from DIY snapshots', async () => {
    const localProduct = {
      id: 'local_guest_product',
      product_id: 'product-1',
      name: 'Guest GPU',
      price: 4999,
      stock: 5,
      quantity: 1,
      selected: true,
    }
    const diySnapshot = {
      id: 'local_diy_snapshot',
      product_id: 'diy-1',
      name: 'DIY PC',
      price: 12999,
      stock: 1,
      quantity: 1,
      selected: true,
      custom_type: 'diy_pc',
      snapshot: { type: 'diy_pc', parts: [] },
    }
    localStorage.setItem('pangchong_local_cart', JSON.stringify([localProduct, diySnapshot]))
    vi.spyOn(cartApi, 'getCart').mockResolvedValue({ items: [] })

    const cart = useCartStore()
    await cart.fetchCart()

    expect(cart.items).toHaveLength(2)
    expect(cart.items[0].item_type).toBe('product')
    expect(cart.isCustomItem(cart.items[0])).toBe(false)
    expect(cart.items[1].item_type).toBe('custom')
    expect(cart.isCustomItem(cart.items[1])).toBe(true)
  })

  it('waits for session restoration before choosing the cart identity', async () => {
    let finishRefresh!: (value: { access_token: string }) => void
    vi.spyOn(authApi, 'refreshToken').mockReturnValue(new Promise(resolve => {
      finishRefresh = resolve
    }))
    vi.spyOn(authApi, 'getProfile').mockResolvedValue({ id: 'buyer-1', username: 'buyer' })
    const getCart = vi.spyOn(cartApi, 'getCart').mockResolvedValue({ items: [] })

    const cart = useCartStore()
    const fetch = cart.fetchCart()
    expect(getCart).not.toHaveBeenCalled()

    finishRefresh({ access_token: 'restored-access' })
    await fetch

    expect(useUserStore().isLoggedIn).toBe(true)
    expect(getCart).toHaveBeenCalledWith(undefined)
  })

  it('updates local custom item quantity without calling the backend', async () => {
    const cart = useCartStore()
    cart.addCustomItem({
      id: 'diy-qty',
      name: 'Custom PC',
      price: 12999,
      stock: 4,
      custom_type: 'diy_pc',
      snapshot: {
        type: 'diy_pc',
        parts: [{ key: 'cpu', product_id: 'cpu-1' }],
      },
    })
    const item = cart.items[0]
    cart.toggleSelect(item.id)
    const updateSpy = vi.spyOn(cartApi, 'updateCartItem').mockResolvedValue({})

    await cart.updateQuantity(item.id, 3)

    expect(updateSpy).not.toHaveBeenCalled()
    expect(item.quantity).toBe(3)
    expect(item.selected).toBe(false)
    expect(cart.selectedCount).toBe(0)

    const storedItems = JSON.parse(localStorage.getItem('pangchong_local_cart') || '[]')
    expect(storedItems).toHaveLength(1)
    expect(storedItems[0]).toMatchObject({
      id: item.id,
      product_id: 'diy-qty',
      item_type: 'custom',
      custom_type: 'diy_pc',
      quantity: 3,
      selected: false,
    })

    const selectedState = JSON.parse(localStorage.getItem('pangchong_cart_selected') || '{}')
    expect(selectedState[item.id]).toBe(false)
  })

  it('toggles item selection', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 'test-1', name: 'Test', price: 100 })
    expect(cart.items[0].selected).toBe(true)
    cart.toggleSelect(cart.items[0].id)
    expect(cart.items[0].selected).toBe(false)
    expect(cart.selectedCount).toBe(0)
  })

  it('toggles select all', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 100 })
    cart.addLocalItem({ id: 't2', name: 'B', price: 200 })
    cart.toggleSelectAll()
    expect(cart.allSelected).toBe(false)
    cart.toggleSelectAll()
    expect(cart.allSelected).toBe(true)
  })

  it('calculates subtotal correctly', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 1000 }, 2)
    cart.addLocalItem({ id: 't2', name: 'B', price: 500 }, 1)
    expect(cart.subtotal).toBe(2500)
  })

  it('does not invent a discount for an unverified coupon', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 4000 }, 1)
    const result = cart.applyCoupon('PANGGU888')
    expect(result.success).toBe(false)
    expect(result.message).toContain('暂无可用优惠码')
    expect(cart.coupon.discount).toBe(0)
  })

  it('rejects invalid coupon', () => {
    const cart = useCartStore()
    const result = cart.applyCoupon('INVALID')
    expect(result.success).toBe(false)
  })

  it('uses the server-configured shipping rule instead of guessing from a region', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 200 }, 1)
    expect(cart.shippingCost).toBe(10)
    cart.setShippingRegion('其他地区')
    expect(cart.shippingCost).toBe(10)
    cart.setShippingRegion('西藏新疆')
    expect(cart.shippingCost).toBe(10)
    cart.commerceSettings.free_shipping_threshold = 200
    expect(cart.shippingCost).toBe(0)
  })

  it('calculates total amount from the displayed price and shipping configuration', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 200 }, 1)
    cart.setShippingRegion('其他地区')
    cart.applyCoupon('PANGGU888')
    expect(cart.totalAmount).toBe(200 + 10)
  })

  it('removes item from cart', async () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 100 })
    expect(cart.isEmpty).toBe(false)
    await cart.removeItem(cart.items[0].id)
    expect(cart.isEmpty).toBe(true)
  })

  it('removes only purchased local items', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 100 })
    cart.addLocalItem({ id: 't2', name: 'B', price: 200 })
    const [firstItem] = cart.items

    cart.removeLocalItems([firstItem.id])

    expect(cart.totalItems).toBe(1)
    expect(cart.items[0].name).toBe('B')
  })
})
