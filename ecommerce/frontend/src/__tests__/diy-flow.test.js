import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, nextTick } from 'vue'
import DIY from '@/views/DIY.vue'
import { useCartStore } from '@/store/cart'

const { apiGet, marketGetPriceHistory, notifyShow, routerPush, routeQuery } = vi.hoisted(() => ({
  apiGet: vi.fn(),
  marketGetPriceHistory: vi.fn(),
  notifyShow: vi.fn(),
  routerPush: vi.fn(),
  routeQuery: {},
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: routeQuery }),
  useRouter: () => ({ push: routerPush }),
}))

vi.mock('@/api', () => ({
  default: { get: apiGet },
  marketApi: { getPriceHistory: marketGetPriceHistory },
  cartApi: {
    getCart: vi.fn(),
    addToCart: vi.fn(),
    updateCartItem: vi.fn(),
    removeCartItem: vi.fn(),
    clearCart: vi.fn(),
    mergeCart: vi.fn(),
  },
}))

vi.mock('@/store/notify', () => ({
  useNotifyStore: () => ({ show: notifyShow }),
}))

function part(id, name, price, specs = {}) {
  return {
    id,
    name,
    brand: `Brand ${id}`,
    model: `Model ${id}`,
    price,
    original_price: price + 100,
    image_url: `/${id}.png`,
    specs,
  }
}

const Product3DViewerStub = defineComponent({
  name: 'Product3DViewer',
  emits: ['failure', 'ready'],
  template: '<div data-testid="product-3d-viewer-stub"></div>',
})

function completeSelection() {
  return {
    0: part('cpu-1', 'Ryzen 9', 4000, { socket: 'AM5', tdp: '120W' }),
    1: part('gpu-1', 'RTX 5090', 12000, { length: '300mm', tdp: '450W' }),
    2: part('motherboard-1', 'X870E', 2500, { socket: 'AM5', memory: 'DDR5', form_factor: 'ATX' }),
    3: part('ram-1', '64GB DDR5', 1200, { type: 'DDR5' }),
    4: part('ssd-1', '4TB NVMe', 1800),
    5: part('cooler-1', '360 AIO', 900, { height: '150mm' }),
    6: part('psu-1', '1200W PSU', 1400, { wattage: '1200W' }),
    7: {
      ...part('case-1', 'Full Tower', 1100, { mb_support: 'ATX', gpu_length: '400mm', cooler_height: '180mm' }),
      model_3d_url: 'https://example.supabase.co/storage/v1/object/public/catalog-models/diy/case.glb',
      model_3d_scale: 0.01,
      model_3d_position: [0, 0.2, 0],
      model_3d_rotation: [0, 1.57, 0],
      asset_license: 'CC BY 4.0',
      asset_source_url: 'https://example.com/licensed-case',
    },
  }
}

async function mountDiy(pinia = createPinia()) {
  setActivePinia(pinia)
  const wrapper = mount(DIY, {
    global: {
      plugins: [pinia],
      stubs: {
        Product3DViewer: Product3DViewerStub,
        ProductConfiguratorPanel: true,
      },
    },
  })
  await flushPromises()
  return wrapper
}

describe('DIY custom-item flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    delete routeQuery.part
    localStorage.clear()
    apiGet.mockResolvedValue({ items: [] })
    marketGetPriceHistory.mockResolvedValue({ points: [], source: 'unavailable' })
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('saves the selected appearance and all part details in the cart snapshot', async () => {
    const pinia = createPinia()
    const wrapper = await mountDiy(pinia)

    wrapper.vm.selected = completeSelection()
    wrapper.vm.selectedVariant = 'green'
    wrapper.vm.selectedMaterial = 'gloss'
    await nextTick()

    expect(wrapper.vm.activeModelUrl).toContain('/catalog-models/diy/case.glb')
    expect(wrapper.vm.activeCaseModel).toMatchObject({
      scale: 0.01,
      position: [0, 0.2, 0],
      rotation: [0, 1.57, 0],
      license: 'CC BY 4.0',
    })

    await wrapper.vm.addToCart()

    const cart = useCartStore()
    expect(cart.items).toHaveLength(1)
    expect(cart.items[0]).toMatchObject({
      item_type: 'custom',
      custom_type: 'diy_pc',
      specs: { '3D 外观': '虫翼绿 / 高亮涂层' },
      snapshot: {
        type: 'diy_pc',
        appearance: {
          variant_id: 'green',
          variant_name: '虫翼绿',
          material_id: 'gloss',
          material_name: '高亮涂层',
          price_diff: 500,
        },
      },
    })
    expect(cart.items[0].snapshot.parts).toHaveLength(8)
    expect(cart.items[0].snapshot.parts[0]).toMatchObject({
      key: 'cpu',
      product_id: 'cpu-1',
      name: 'Ryzen 9',
      brand: 'Brand cpu-1',
    })
    expect(cart.items[0].snapshot.parts[7]).toMatchObject({
      key: 'case',
      model_3d_url: 'https://example.supabase.co/storage/v1/object/public/catalog-models/diy/case.glb',
      asset_license: 'CC BY 4.0',
      asset_source_url: 'https://example.com/licensed-case',
    })
    expect(JSON.parse(localStorage.getItem('pangchong_local_cart'))[0].snapshot).toEqual(cart.items[0].snapshot)
    expect(notifyShow).toHaveBeenCalledWith('DIY 整机配置已作为一件定制商品加入购物车', 'success')
    expect(routerPush).toHaveBeenCalledWith('/cart')

    wrapper.unmount()
  })

  it('unmounts the heavy 3D viewer while the configuration list is active', async () => {
    const wrapper = await mountDiy()

    expect(wrapper.findComponent(Product3DViewerStub).exists()).toBe(true)
    await wrapper.get('[data-testid="diy-list-mode-button"]').trigger('click')
    await nextTick()
    expect(wrapper.findComponent(Product3DViewerStub).exists()).toBe(false)

    await wrapper.get('[data-testid="diy-3d-mode-button"]').trigger('click')
    await flushPromises()
    expect(wrapper.findComponent(Product3DViewerStub).exists()).toBe(true)

    wrapper.unmount()
  })

  it('uses the shared semantic step indicator for DIY progress', async () => {
    const wrapper = await mountDiy()
    const indicator = wrapper.get('.pc-step-indicator')

    expect(indicator.attributes('aria-label')).toBe('DIY 装机步骤')
    expect(indicator.findAll('[aria-current="step"]')).toHaveLength(1)
    expect(indicator.get('[aria-current="step"]').attributes('aria-label')).toBe('第1步：处理器 CPU')
    expect(indicator.get('.pc-step-indicator__status').text()).toContain('第1步，共8步')
    expect(indicator.findAll('button')[1].attributes('disabled')).toBeDefined()

    wrapper.vm.currentStep = 2
    await nextTick()
    expect(indicator.get('[aria-current="step"]').attributes('aria-label')).toBe('第3步：主板')

    wrapper.unmount()
  })

  it.each([
    ['WebGL unavailable', 'webgl-unavailable', '当前设备无法使用 3D', {}],
    ['model loading failure', 'model-load-failed', '3D 模型加载失败', {}],
    ['missing required assembly nodes', 'missing-assembly-nodes', '3D 模型不完整', { missingNodes: ['gpu', 'psu'] }],
    ['model loading timeout', 'load-timeout', '3D 加载时间过长', { elapsedMs: 8000 }],
  ])('automatically enters list mode for %s', async (_label, reason, expectedTitle, details) => {
    const wrapper = await mountDiy()
    const viewer = wrapper.findComponent(Product3DViewerStub)

    viewer.vm.$emit('failure', { reason, ...details })
    await nextTick()

    expect(wrapper.get('[data-testid="diy-list-mode"]').isVisible()).toBe(true)
    expect(wrapper.get('[data-testid="diy-viewer-fallback"]').text()).toContain(expectedTitle)
    expect(wrapper.get('[data-testid="diy-list-add-cart"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="diy-list-checkout"]').exists()).toBe(true)
    if (details.missingNodes) {
      expect(wrapper.get('[data-testid="diy-viewer-fallback"]').text()).toContain('gpu、psu')
    }

    wrapper.unmount()
  })

  it('falls back when the 3D viewer shell never becomes ready', async () => {
    vi.useFakeTimers()
    const wrapper = await mountDiy()

    await vi.advanceTimersByTimeAsync(8000)
    await nextTick()

    expect(wrapper.get('[data-testid="diy-list-mode"]').isVisible()).toBe(true)
    expect(wrapper.get('[data-testid="diy-viewer-fallback"]').text()).toContain('3D 加载时间过长')

    wrapper.unmount()
  })

  it('keeps selection, compatibility, current pricing, cart, checkout, and list access available during retry', async () => {
    const pinia = createPinia()
    const wrapper = await mountDiy(pinia)
    wrapper.vm.selected = completeSelection()
    await nextTick()

    wrapper.findComponent(Product3DViewerStub).vm.$emit('failure', { reason: 'model-load-failed' })
    await nextTick()

    expect(wrapper.get('[data-testid="diy-list-part-cpu"]').text()).toContain('Ryzen 9')
    expect(wrapper.get('[data-testid="diy-list-part-case"]').text()).toContain('Full Tower')
    expect(wrapper.get('[data-testid="diy-list-compatibility"]').text()).toBe('已选配置通过当前检查')
    expect(wrapper.get('[data-testid="diy-list-total"]').text()).toBe('¥24,900')
    expect(wrapper.get('[data-testid="diy-list-price-status"]').text()).toContain('总价仍按当前售价计算')

    await wrapper.get('[data-testid="diy-list-part-case"]').trigger('click')
    expect(wrapper.vm.currentStep).toBe(7)

    await wrapper.get('[data-testid="diy-list-add-cart"]').trigger('click')
    await nextTick()
    expect(useCartStore().items).toHaveLength(1)
    expect(routerPush).toHaveBeenCalledWith('/cart')

    await wrapper.get('[data-testid="diy-viewer-retry"]').trigger('click')
    await nextTick()
    expect(wrapper.get('[data-testid="diy-list-mode"]').isVisible()).toBe(true)
    expect(wrapper.get('[data-testid="diy-viewer-retry"]').text()).toContain('后台重试中')

    wrapper.findComponent(Product3DViewerStub).vm.$emit('failure', { reason: 'load-timeout', elapsedMs: 8000 })
    await nextTick()
    expect(wrapper.get('[data-testid="diy-list-mode"]').isVisible()).toBe(true)
    expect(wrapper.get('[data-testid="diy-viewer-fallback"]').text()).toContain('加载时间过长')

    await wrapper.get('[data-testid="diy-list-checkout"]').trigger('click')
    await nextTick()
    expect(useCartStore().items).toHaveLength(1)
    expect(routerPush).toHaveBeenCalledWith('/checkout')

    wrapper.unmount()
  })

  it('keeps a failed parts request distinct from an empty filter result and exposes retry', async () => {
    apiGet.mockRejectedValueOnce(new Error('catalog offline'))
    const wrapper = await mountDiy()

    expect(wrapper.vm.categoryState).toBe('error')
    expect(wrapper.text()).toContain('配件加载失败')
    expect(wrapper.text()).not.toContain('没有匹配的配件')

    await wrapper.get('.pc-async-state__message button').trigger('click')
    await flushPromises()
    expect(wrapper.vm.categoryState).toBe('empty')
    expect(wrapper.text()).toContain('没有匹配的配件')
    wrapper.unmount()
  })

  it('loads the requested category when entering through a part deep link', async () => {
    routeQuery.part = 'gpu'
    apiGet.mockResolvedValue({ items: [part('gpu-1', 'RTX 5070', 4599)] })
    const wrapper = await mountDiy()

    expect(wrapper.vm.currentStep).toBe(1)
    expect(apiGet).toHaveBeenCalledWith('/products', expect.objectContaining({
      params: expect.objectContaining({ category_id: 'd1000000-0000-0000-0000-000000000002' }),
    }))
    expect(wrapper.text()).toContain('RTX 5070')
    wrapper.unmount()
  })

  it('keeps the active category loading while an earlier category finishes', async () => {
    let resolveCpu
    let resolveGpu
    apiGet
      .mockImplementationOnce(() => new Promise(resolve => { resolveCpu = resolve }))
      .mockImplementationOnce(() => new Promise(resolve => { resolveGpu = resolve }))
    const wrapper = await mountDiy()

    wrapper.vm.currentStep = 1
    await nextTick()
    resolveCpu({ items: [part('cpu-1', 'Ryzen 9', 4000)] })
    await flushPromises()
    expect(wrapper.vm.categoryState).toBe('loading')
    expect(wrapper.text()).not.toContain('没有匹配的配件')

    resolveGpu({ items: [part('gpu-1', 'RTX 5070', 4599)] })
    await flushPromises()
    expect(wrapper.vm.categoryState).toBe('success')
    expect(wrapper.text()).toContain('RTX 5070')
    wrapper.unmount()
  })

  it('restores a loaded category after another category request fails', async () => {
    apiGet
      .mockResolvedValueOnce({ items: [part('cpu-1', 'Ryzen 9', 4000)] })
      .mockRejectedValueOnce(new Error('GPU catalog offline'))
    const wrapper = await mountDiy()
    wrapper.vm.currentStep = 1
    await flushPromises()
    expect(wrapper.vm.categoryState).toBe('error')

    wrapper.vm.currentStep = 0
    await flushPromises()
    expect(wrapper.vm.categoryState).toBe('success')
    expect(wrapper.text()).toContain('Ryzen 9')
    wrapper.unmount()
  })

  it('discards in-flight price history when its selected part is removed', async () => {
    let resolveHistory
    marketGetPriceHistory.mockImplementationOnce(() => new Promise(resolve => { resolveHistory = resolve }))
    const wrapper = await mountDiy()
    wrapper.vm.selectItem(part('cpu-1', 'Ryzen 9', 4000))
    await nextTick()
    expect(wrapper.vm.priceHistoryLoading).toBe(true)

    wrapper.vm.removeCurrent()
    await nextTick()
    expect(wrapper.vm.priceHistoryLoading).toBe(false)
    resolveHistory({ source: 'database', points: [{ date: '2026-09-01', price: 3900, source_name: '品牌官网', source_url: 'https://example.com/cpu' }] })
    await flushPromises()
    expect(wrapper.vm.priceHistory).toEqual([])
    expect(wrapper.vm.priceHistorySource).toBe('unavailable')
    wrapper.unmount()
  })
})
