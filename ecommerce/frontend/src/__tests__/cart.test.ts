import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCartStore } from '@/store/cart'

describe('Cart Store', () => {
  beforeEach(() => {
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

  it('applies valid coupon', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 4000 }, 1)
    const result = cart.applyCoupon('PANGGU888')
    expect(result.success).toBe(true)
    expect(cart.coupon.discount).toBe(200)
  })

  it('rejects invalid coupon', () => {
    const cart = useCartStore()
    const result = cart.applyCoupon('INVALID')
    expect(result.success).toBe(false)
  })

  it('rejects coupon below minimum amount', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 500 }, 1)
    const result = cart.applyCoupon('PANGGU888')
    expect(result.success).toBe(false)
  })

  it('calculates shipping cost by region', () => {
    const cart = useCartStore()
    expect(cart.shippingCost).toBe(0) // 江浙沪 default
    cart.setShippingRegion('其他地区')
    expect(cart.shippingCost).toBe(20)
    cart.setShippingRegion('西藏新疆')
    expect(cart.shippingCost).toBe(50)
  })

  it('calculates total amount with discount and shipping', () => {
    const cart = useCartStore()
    cart.addLocalItem({ id: 't1', name: 'A', price: 4000 }, 1)
    cart.setShippingRegion('其他地区')
    cart.applyCoupon('PANGGU888')
    expect(cart.totalAmount).toBe(4000 + 20 - 200)
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
