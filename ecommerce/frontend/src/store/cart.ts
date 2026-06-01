import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartApi } from '@/api'
import { useUserStore } from './user'

const COUPON_KEY = 'pangchong_coupon'
const SESSION_KEY = 'cart_session_id'
const LOCAL_CART_KEY = 'pangchong_local_cart'
const SELECTED_KEY = 'pangchong_cart_selected'

interface CouponInfo {
  minAmount: number
  discount: number
  desc: string
}

const COUPONS: Record<string, CouponInfo> = {
  'PANGGU888': { minAmount: 3000, discount: 200, desc: '满3000减200' },
  'DIY2026': { minAmount: 5000, discount: 500, desc: '满5000减500' },
}

const SHIPPING_RATES: Record<string, number> = {
  '江浙沪': 0,
  '其他地区': 20,
  '西藏新疆': 50,
}

export interface CartItem {
  id: string
  product_id: string
  name: string
  brand: string
  model: string
  description: string
  specs: Record<string, unknown>
  price: number
  original_price: number | null
  image_url: string
  stock: number
  quantity: number
  selected: boolean
  is_in_stock: boolean
}

interface CouponState {
  code: string | null
  discount: number
}

interface BackendCartItem {
  id: string
  product_id: string
  product_name: string
  product_brand?: string
  product_model?: string
  product_description?: string
  product_specs?: Record<string, unknown>
  product_price: string | number
  product_original_price?: string | number | null
  product_image?: string
  product_stock?: number
  quantity: number
  is_in_stock: boolean
}

function getSessionId(): string {
  let id = localStorage.getItem(SESSION_KEY)
  if (!id) {
    id = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem(SESSION_KEY, id)
  }
  return id
}

function loadCoupon(): CouponState {
  try {
    return JSON.parse(localStorage.getItem(COUPON_KEY) || 'null') || { code: null, discount: 0 }
  } catch { return { code: null, discount: 0 } }
}

function saveCoupon(coupon: CouponState) {
  try { localStorage.setItem(COUPON_KEY, JSON.stringify(coupon)) }
  catch (e) { console.warn('localStorage write failed:', e) }
}

function loadSelectedState(): Record<string, boolean> {
  try { return JSON.parse(localStorage.getItem(SELECTED_KEY) || '{}') }
  catch { return {} }
}

function saveSelectedState(state: Record<string, boolean>) {
  try { localStorage.setItem(SELECTED_KEY, JSON.stringify(state)) }
  catch (e) { console.warn('localStorage write failed:', e) }
}

function loadLocalCart(): CartItem[] {
  try { return JSON.parse(localStorage.getItem(LOCAL_CART_KEY) || '[]') }
  catch { return [] }
}

function saveLocalCart(items: CartItem[]) {
  try { localStorage.setItem(LOCAL_CART_KEY, JSON.stringify(items)) }
  catch (e) { console.warn('localStorage write failed:', e) }
}

function mapCartItem(backendItem: BackendCartItem): CartItem {
  const selectedState = loadSelectedState()
  return {
    id: backendItem.id,
    product_id: backendItem.product_id,
    name: backendItem.product_name,
    brand: backendItem.product_brand || '',
    model: backendItem.product_model || '',
    description: backendItem.product_description || '',
    specs: backendItem.product_specs || {},
    price: Number(backendItem.product_price),
    original_price: backendItem.product_original_price ? Number(backendItem.product_original_price) : null,
    image_url: backendItem.product_image || '',
    stock: backendItem.product_stock ?? 99,
    quantity: backendItem.quantity,
    selected: selectedState[backendItem.id] !== undefined ? selectedState[backendItem.id] : true,
    is_in_stock: backendItem.is_in_stock,
  }
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const loading = ref(false)
  const coupon = ref<CouponState>(loadCoupon())
  const shippingRegion = ref('江浙沪')
  const sessionId = ref(getSessionId())

  const totalItems = computed(() => items.value.reduce((s, i) => s + i.quantity, 0))
  const selectedItems = computed(() => items.value.filter(i => i.selected && i.stock > 0))
  const selectedCount = computed(() => selectedItems.value.reduce((s, i) => s + i.quantity, 0))
  const allSelected = computed(() => items.value.length > 0 && items.value.every(i => i.selected || i.stock <= 0))
  const subtotal = computed(() => selectedItems.value.reduce((s, i) => s + Number(i.price) * i.quantity, 0))
  const shippingCost = computed(() => SHIPPING_RATES[shippingRegion.value] ?? 20)
  const discountAmount = computed(() => {
    const c = coupon.value
    if (!c.code || !c.discount) return 0
    if (subtotal.value >= (COUPONS[c.code]?.minAmount || 0)) return c.discount
    return 0
  })
  const totalAmount = computed(() => Math.max(0, subtotal.value + shippingCost.value - discountAmount.value))
  const isEmpty = computed(() => items.value.length === 0)

  async function fetchCart() {
    const userStore = useUserStore()
    loading.value = true
    try {
      const sid = userStore.isLoggedIn ? undefined : sessionId.value
      const data = await cartApi.getCart(sid) as { items?: BackendCartItem[] }
      const backendItems = (data.items || []).map(mapCartItem)
      const localItems = loadLocalCart().filter(li =>
        !backendItems.some(bi => bi.product_id === li.product_id)
      )
      items.value = [...backendItems, ...localItems]
    } catch {
      console.warn('fetchCart failed')
      const localItems = loadLocalCart()
      if (localItems.length > 0) items.value = localItems
    } finally {
      loading.value = false
    }
  }

  async function addToCart(productId: string, quantity = 1) {
    const userStore = useUserStore()
    const sid = userStore.isLoggedIn ? undefined : sessionId.value
    try {
      await cartApi.addToCart({ product_id: productId, quantity }, sid)
      await fetchCart()
    } catch (e) {
      console.error('addToCart failed:', e)
      throw e
    }
  }

  async function addItem(product: { id: string }, quantity = 1) {
    await addToCart(product.id, quantity)
  }

  async function updateQuantity(itemId: string, quantity: number) {
    const item = items.value.find(i => i.id === itemId)
    if (!item) return
    const userStore = useUserStore()
    const sid = userStore.isLoggedIn ? undefined : sessionId.value
    const newQty = Math.max(1, Math.min(99, Math.min(quantity, item.stock)))
    if (newQty === item.quantity) return
    item.quantity = newQty
    try {
      await cartApi.updateCartItem(itemId, { quantity: newQty }, sid)
    } catch {
      await fetchCart()
      throw new Error('更新数量失败')
    }
  }

  function toggleSelect(itemId: string) {
    const item = items.value.find(i => i.id === itemId)
    if (item && item.stock > 0) {
      item.selected = !item.selected
      persistSelectedState()
    }
  }

  function toggleSelectAll() {
    const newVal = !allSelected.value
    items.value.forEach(i => { if (i.stock > 0) i.selected = newVal })
    persistSelectedState()
  }

  function persistSelectedState() {
    const state: Record<string, boolean> = {}
    items.value.forEach(i => { state[i.id] = i.selected })
    saveSelectedState(state)
  }

  async function removeItem(itemId: string) {
    const userStore = useUserStore()
    const sid = userStore.isLoggedIn ? undefined : sessionId.value
    items.value = items.value.filter(i => i.id !== itemId)
    if (!itemId.startsWith('local_')) {
      try {
        await cartApi.removeCartItem(itemId, sid)
      } catch {
        await fetchCart()
        throw new Error('删除失败')
      }
    }
  }

  async function removeSelected() {
    const userStore = useUserStore()
    const sid = userStore.isLoggedIn ? undefined : sessionId.value
    const toRemove = items.value.filter(i => i.selected)
    items.value = items.value.filter(i => !i.selected)
    persistSelectedState()
    const results = await Promise.allSettled(
      toRemove.map(i => {
        if (i.id.startsWith('local_')) return Promise.resolve()
        return cartApi.removeCartItem(i.id, sid)
      })
    )
    const hasFailure = results.some(r => r.status === 'rejected')
    if (hasFailure) {
      await fetchCart()
    } else {
      const localItems = loadLocalCart().filter(li =>
        !toRemove.some(r => r.product_id === li.product_id)
      )
      saveLocalCart(localItems)
    }
  }

  function removeLocalItems(itemIds: string[]) {
    if (itemIds.length === 0) return
    const ids = new Set(itemIds)
    items.value = items.value.filter(i => !ids.has(i.id))
    const localItems = loadLocalCart().filter(i => !ids.has(i.id))
    saveLocalCart(localItems)
    persistSelectedState()
  }

  async function clearCart() {
    const userStore = useUserStore()
    const sid = userStore.isLoggedIn ? undefined : sessionId.value
    items.value = []
    coupon.value = { code: null, discount: 0 }
    try { await cartApi.clearCart(sid) }
    catch { console.warn('clearCart failed') }
  }

  async function mergeCart() {
    try {
      const data = await cartApi.mergeCart(sessionId.value) as { items?: BackendCartItem[] }
      items.value = (data.items || []).map(mapCartItem)
    } catch {
      console.warn('mergeCart failed')
      await fetchCart()
    }
  }

  function applyCoupon(code: string) {
    const upper = code.trim().toUpperCase()
    const c = COUPONS[upper]
    if (!c) return { success: false, message: '优惠码无效或已过期' }
    if (subtotal.value < c.minAmount) {
      return { success: false, message: `订单金额需满¥${c.minAmount}才可使用此优惠码` }
    }
    coupon.value = { code: upper, discount: c.discount }
    return { success: true, message: `已应用优惠：${c.desc}` }
  }

  function removeCoupon() {
    coupon.value = { code: null, discount: 0 }
  }

  function setShippingRegion(region: string) {
    shippingRegion.value = region
  }

  function getShippingRates() {
    return Object.entries(SHIPPING_RATES).map(([name, cost]) => ({ name, cost }))
  }

  function isInCart(productId: string) {
    return items.value.some(i => i.product_id === productId)
  }

  function addLocalItem(productObj: Record<string, unknown>, quantity = 1) {
    const existing = items.value.find(i => i.product_id === productObj.id)
    if (existing) {
      existing.quantity += quantity
    } else {
      const newItem: CartItem = {
        id: 'local_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
        product_id: productObj.id as string,
        name: productObj.name as string,
        brand: (productObj.brand as string) || '',
        model: (productObj.model as string) || '',
        description: (productObj.description as string) || '',
        specs: (productObj.specs as Record<string, unknown>) || {},
        price: Number(productObj.price),
        original_price: productObj.original_price != null ? Number(productObj.original_price) : null,
        image_url: (productObj.image_url as string) || '',
        stock: (productObj.stock as number) ?? 99,
        quantity,
        selected: true,
        is_in_stock: true,
      }
      items.value.push(newItem)
    }
    const localItems = items.value.filter(i => i.id.startsWith('local_'))
    saveLocalCart(localItems)
  }

  function clearOnLogout() {
    items.value = []
    coupon.value = { code: null, discount: 0 }
    shippingRegion.value = '江浙沪'
    try {
      localStorage.removeItem(LOCAL_CART_KEY)
      localStorage.removeItem(SELECTED_KEY)
      localStorage.removeItem(COUPON_KEY)
    } catch (e) { console.warn('localStorage clear failed:', e) }
  }

  return {
    items, loading, coupon, shippingRegion, sessionId,
    totalItems, selectedItems, selectedCount, allSelected,
    subtotal, shippingCost, discountAmount, totalAmount, isEmpty,
    fetchCart, addToCart, addItem, addLocalItem, updateQuantity,
    toggleSelect, toggleSelectAll,
    removeLocalItems,
    removeItem, removeSelected, clearCart,
    mergeCart, applyCoupon, removeCoupon,
    setShippingRegion, getShippingRates, isInCart, clearOnLogout,
  }
})
