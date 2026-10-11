import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartApi } from '@/api'
import { useUserStore } from './user'

const COUPON_KEY = 'pangchong_coupon'
const SESSION_KEY = 'cart_session_id'
const LOCAL_CART_KEY = 'pangchong_local_cart'
const SELECTED_KEY = 'pangchong_cart_selected'

export interface CartItem {
  id: string
  product_id: string
  item_type?: 'product' | 'custom'
  custom_type?: string
  name: string
  brand: string
  model: string
  description: string
  specs: Record<string, unknown>
  snapshot?: Record<string, unknown>
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
  try {
    const raw = JSON.parse(localStorage.getItem(LOCAL_CART_KEY) || '[]')
    return Array.isArray(raw) ? raw.map(normalizeLocalItem) : []
  }
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
    item_type: 'product',
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

function getLocalItemType(item: Partial<CartItem>): CartItem['item_type'] {
  if (item.item_type === 'custom' || item.item_type === 'product') return item.item_type

  const hasCustomType = typeof item.custom_type === 'string' && item.custom_type.length > 0
  const hasSnapshot = item.snapshot !== null && typeof item.snapshot === 'object' && !Array.isArray(item.snapshot)
  return hasCustomType || hasSnapshot ? 'custom' : 'product'
}

function normalizeLocalItem(item: Partial<CartItem>): CartItem {
  const stock = Number(item.stock ?? 99)
  return {
    id: item.id || 'local_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
    product_id: item.product_id || item.id || '',
    item_type: getLocalItemType(item),
    custom_type: item.custom_type,
    name: item.name || '本地定制商品',
    brand: item.brand || '',
    model: item.model || '',
    description: item.description || '',
    specs: item.specs || {},
    snapshot: item.snapshot,
    price: Number(item.price || 0),
    original_price: item.original_price != null ? Number(item.original_price) : null,
    image_url: item.image_url || '',
    stock,
    quantity: Math.max(1, Number(item.quantity || 1)),
    selected: item.selected !== false,
    is_in_stock: item.is_in_stock !== false && stock > 0,
  }
}

function isLocalOrCustomItem(item: Pick<CartItem, 'id' | 'item_type'>): boolean {
  return item.id.startsWith('local_') || item.item_type === 'custom'
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const loading = ref(false)
  const loadError = ref('')
  const coupon = ref<CouponState>({ code: null, discount: 0 })
  const commerceSettings = ref({ shipping_fee: 10, free_shipping_threshold: 299, currency: 'CNY', payment_mode: 'sandbox' })
  const shippingRegion = ref('江浙沪')
  const sessionId = ref(getSessionId())

  const totalItems = computed(() => items.value.reduce((s, i) => s + i.quantity, 0))
  const selectedItems = computed(() => items.value.filter(i => i.selected && i.stock > 0 && i.is_in_stock !== false))
  const selectedCount = computed(() => selectedItems.value.reduce((s, i) => s + i.quantity, 0))
  const allSelected = computed(() => items.value.length > 0 && items.value.every(i => i.selected || i.stock <= 0))
  const subtotal = computed(() => selectedItems.value.reduce((s, i) => s + Number(i.price) * i.quantity, 0))
  const shippingCost = computed(() => selectedCount.value === 0 || subtotal.value >= commerceSettings.value.free_shipping_threshold ? 0 : commerceSettings.value.shipping_fee)
  const discountAmount = computed(() => 0)
  const totalAmount = computed(() => Math.max(0, subtotal.value + shippingCost.value - discountAmount.value))
  const isEmpty = computed(() => items.value.length === 0)

  async function fetchCommerceSettings() {
    // Keep default estimates available during a temporary settings outage.
    if (typeof cartApi.getCommerceSettings !== 'function') return
    try {
      const data = await cartApi.getCommerceSettings()
      if (Number.isFinite(Number(data?.shipping_fee)) && Number.isFinite(Number(data?.free_shipping_threshold))) {
        commerceSettings.value = { ...data, shipping_fee: Number(data.shipping_fee), free_shipping_threshold: Number(data.free_shipping_threshold) }
      }
    } catch { /* The confirmed order always uses the server's final amount. */ }
  }

  async function fetchCart() {
    const userStore = useUserStore()
    loading.value = true
    loadError.value = ''
    try {
      // App mounts before public-route session restoration completes. Wait to
      // choose the authenticated or anonymous cart, without delaying the page.
      await Promise.all([userStore.hydrateSession(), fetchCommerceSettings()])
      const sid = userStore.isLoggedIn ? undefined : sessionId.value
      const data = await cartApi.getCart(sid) as { items?: BackendCartItem[] }
      const backendItems = (data.items || []).map(mapCartItem)
      const localItems = loadLocalCart().filter(li =>
        !backendItems.some(bi => bi.product_id === li.product_id)
      )
      items.value = [...backendItems, ...localItems]
    } catch {
      loadError.value = '购物车同步失败，请检查网络后重试。已保留当前商品。'
      const localItems = loadLocalCart()
      if (items.value.length === 0 && localItems.length > 0) items.value = localItems
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
    if (!Number.isFinite(quantity) || item.stock <= 0) return
    const newQty = Math.max(1, Math.min(99, Math.min(Math.floor(quantity), item.stock)))
    if (newQty === item.quantity) return
    const previousQuantity = item.quantity
    item.quantity = newQty

    if (isLocalOrCustomItem(item)) {
      saveLocalCart(items.value.filter(isLocalOrCustomItem))
      persistSelectedState()
      return
    }

    const userStore = useUserStore()
    const sid = userStore.isLoggedIn ? undefined : sessionId.value
    try {
      await cartApi.updateCartItem(itemId, { quantity: newQty }, sid)
    } catch {
      item.quantity = previousQuantity
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
    if (itemId.startsWith('local_')) {
      items.value = items.value.filter(i => i.id !== itemId)
      saveLocalCart(items.value.filter(i => i.id.startsWith('local_')))
      persistSelectedState()
    } else {
      try {
        await cartApi.removeCartItem(itemId, sid)
        items.value = items.value.filter(i => i.id !== itemId)
        persistSelectedState()
      } catch {
        throw new Error('删除失败')
      }
    }
  }

  async function removeSelected() {
    const userStore = useUserStore()
    const sid = userStore.isLoggedIn ? undefined : sessionId.value
    const toRemove = items.value.filter(i => i.selected)
    const results = await Promise.allSettled(
      toRemove.map(i => {
        if (i.id.startsWith('local_')) return Promise.resolve()
        return cartApi.removeCartItem(i.id, sid)
      })
    )
    const removedIds = new Set(toRemove.filter((_, index) => results[index].status === 'fulfilled').map(item => item.id))
    items.value = items.value.filter(item => !removedIds.has(item.id))
    saveLocalCart(loadLocalCart().filter(item => !removedIds.has(item.id)))
    persistSelectedState()
    if (results.some(result => result.status === 'rejected')) throw new Error('部分商品删除失败，已保留未删除的商品，请重试')
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
    saveLocalCart([])
    persistSelectedState()
    try { await cartApi.clearCart(sid) }
    catch { console.warn('clearCart failed') }
  }

  async function mergeCart() {
    try {
      const data = await cartApi.mergeCart(sessionId.value) as { items?: BackendCartItem[] }
      const backendItems = (data.items || []).map(mapCartItem)
      const localItems = loadLocalCart().filter(li =>
        !backendItems.some(bi => bi.product_id === li.product_id)
      )
      items.value = [...backendItems, ...localItems]
    } catch {
      console.warn('mergeCart failed')
      await fetchCart()
    }
  }

  function applyCoupon(code: string) {
    return { success: false, message: '当前暂无可用优惠码，商品以页面售价结算' }
  }

  function removeCoupon() {
    coupon.value = { code: null, discount: 0 }
  }

  function setShippingRegion(region: string) {
    shippingRegion.value = region
  }

  function getShippingRates() {
    return [{ name: '标准配送', cost: commerceSettings.value.shipping_fee }]
  }

  function isInCart(productId: string) {
    return items.value.some(i => i.product_id === productId)
  }

  function isLocalItem(item: CartItem) {
    return item.id.startsWith('local_')
  }

  function isCustomItem(item: CartItem) {
    return item.item_type === 'custom'
  }

  function addLocalItem(productObj: Record<string, unknown>, quantity = 1) {
    const existing = items.value.find(i => i.product_id === productObj.id)
    if (existing) {
      existing.quantity += quantity
      existing.selected = true
      if (productObj.snapshot && typeof productObj.snapshot === 'object') {
        existing.snapshot = productObj.snapshot as Record<string, unknown>
      }
      if (productObj.specs && typeof productObj.specs === 'object') {
        existing.specs = productObj.specs as Record<string, unknown>
      }
      if (productObj.item_type === 'custom' || productObj.custom_type) {
        existing.item_type = 'custom'
        existing.custom_type = productObj.custom_type as string
      }
    } else {
      const itemType = (productObj.item_type as CartItem['item_type']) || (productObj.custom_type || productObj.snapshot ? 'custom' : 'product')
      const newItem: CartItem = {
        id: 'local_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
        product_id: productObj.id as string,
        item_type: itemType,
        custom_type: (productObj.custom_type as string) || undefined,
        name: productObj.name as string,
        brand: (productObj.brand as string) || '',
        model: (productObj.model as string) || '',
        description: (productObj.description as string) || '',
        specs: (productObj.specs as Record<string, unknown>) || {},
        snapshot: (productObj.snapshot as Record<string, unknown>) || undefined,
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
    persistSelectedState()
  }

  function addCustomItem(productObj: Record<string, unknown>, quantity = 1) {
    addLocalItem({ ...productObj, item_type: 'custom' }, quantity)
  }

  function clearOnLogout() {
    items.value = []
    coupon.value = { code: null, discount: 0 }
    shippingRegion.value = '江浙沪'
    loadError.value = ''
    try {
      localStorage.removeItem(LOCAL_CART_KEY)
      localStorage.removeItem(SELECTED_KEY)
      localStorage.removeItem(COUPON_KEY)
    } catch (e) { console.warn('localStorage clear failed:', e) }
  }

  return {
    items, loading, loadError, commerceSettings, coupon, shippingRegion, sessionId,
    totalItems, selectedItems, selectedCount, allSelected,
    subtotal, shippingCost, discountAmount, totalAmount, isEmpty,
    fetchCart, fetchCommerceSettings, addToCart, addItem, addLocalItem, addCustomItem, updateQuantity,
    toggleSelect, toggleSelectAll,
    removeLocalItems,
    removeItem, removeSelected, clearCart,
    mergeCart, applyCoupon, removeCoupon,
    setShippingRegion, getShippingRates, isInCart, isLocalItem, isCustomItem, clearOnLogout,
  }
})
