import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import DIY from '@/views/DIY.vue'
import { useCartStore } from '@/store/cart'

const { apiGet, notifyShow, routerPush } = vi.hoisted(() => ({
  apiGet: vi.fn(),
  notifyShow: vi.fn(),
  routerPush: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: {} }),
  useRouter: () => ({ push: routerPush }),
}))

vi.mock('@/api', () => ({
  default: { get: apiGet },
  marketApi: { getPriceHistory: vi.fn() },
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

describe('DIY custom-item flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    apiGet.mockResolvedValue({ items: [] })
    setActivePinia(createPinia())
  })

  it('saves the selected appearance and all part details in the cart snapshot', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const wrapper = mount(DIY, {
      global: {
        plugins: [pinia],
        stubs: {
          Product3DViewer: true,
          ProductConfiguratorPanel: true,
        },
      },
    })
    await flushPromises()

    wrapper.vm.selected = {
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
})
