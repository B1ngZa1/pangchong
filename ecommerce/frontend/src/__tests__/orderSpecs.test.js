import { describe, expect, it } from 'vitest'
import {
  buildCustomSnapshotDisplay,
  buildDiyOrderPreview,
  buildDiySnapshotDisplay,
  buildOrderCustomPreview,
  formatCustomSpecs,
  formatSpecs,
  hasCustomSnapshotDisplay,
  isDiyPcOrderItem,
} from '@/utils/orderSpecs'

const diyItem = {
  item_type: 'custom',
  product_name: '胖虫 DIY 整机配置',
  product_specs: {
    配置类型: 'DIY 装机整机',
    '3D 外观': '星曜白 / 金属拉丝',
    估算功耗: '620W',
    _snapshot: {
      type: 'diy_pc',
      version: 1,
      created_at: '2026-06-01T08:00:00.000Z',
      parts: [
        {
          key: 'cpu',
          label: '处理器 CPU',
          brand: 'AMD',
          name: 'Ryzen 9 9950X3D',
          price: 4999,
          specs: { socket: 'AM5', cores: '16C', threads: '32T', tdp: '170W' },
        },
        {
          key: 'gpu',
          label: '显卡 GPU',
          brand: 'NVIDIA',
          name: 'RTX 5080',
          price: 8999,
          specs: { vram: '16GB', length: '320mm', tdp: '360W' },
        },
        {
          key: 'psu',
          label: '电源 PSU',
          brand: 'Seasonic',
          name: 'Focus GX 850',
          price: 899,
          specs: { wattage: '850W', efficiency: '80Plus Gold' },
        },
      ],
      appearance: {
        variant_name: '星曜白',
        material_name: '金属拉丝',
        camera_preset: 'front',
        auto_rotate: true,
        price_diff: 300,
      },
      metrics: {
        total_power_w: 620,
        psu_headroom_w: 230,
        gpu_space_headroom_mm: 45,
        estimated_3dmark: 28500,
        compatibility: [
          { key: 'cpu-mobo', title: 'CPU / 主板插槽', level: 'ok', message: 'CPU AM5，主板 AM5' },
        ],
      },
      pricing: {
        parts_total: 16888,
        appearance_price_diff: 300,
        saved_amount: 500,
        total: 16688,
      },
    },
  },
}

const genericCustomItem = {
  item_type: 'custom',
  product_name: '定制键帽套装',
  product_specs: {
    定制类型: '键帽刻字',
    颜色: '青瓷蓝',
    嵌套对象: { raw: true },
    _snapshot: {
      type: 'keycap_engraving',
      created_at: '2026-06-02T08:00:00.000Z',
      selected_options: {
        color: '青瓷蓝',
        layout: '75%',
        engraving: { value: 'HELLO' },
      },
      metrics: {
        score: 92,
      },
      pricing: {
        total: 399,
      },
    },
  },
}

describe('orderSpecs helpers', () => {
  it('keeps private snapshot data out of flat spec tags', () => {
    const specs = formatSpecs(diyItem.product_specs)

    expect(specs.map((spec) => spec.label)).toEqual(['配置类型', '3D 外观', '估算功耗'])
    expect(specs.some((spec) => spec.value.includes('_snapshot'))).toBe(false)
  })

  it('detects persisted DIY PC snapshots from product_specs', () => {
    expect(isDiyPcOrderItem(diyItem)).toBe(true)
    expect(isDiyPcOrderItem({ item_type: 'product', product_specs: { 颜色: '黑色' } })).toBe(false)
    expect(isDiyPcOrderItem({
      item_type: 'product',
      product_specs: { _snapshot: diyItem.product_specs._snapshot },
    })).toBe(false)
  })

  it('builds the same DIY display from a live cart snapshot and a persisted order snapshot', () => {
    const snapshot = {
      ...diyItem.product_specs._snapshot,
      appearance: {
        ...diyItem.product_specs._snapshot.appearance,
        variant: 'duplicate-variant-id',
        material: 'duplicate-material-id',
      },
    }
    const cartItem = {
      item_type: 'custom',
      custom_type: 'diy_pc',
      specs: diyItem.product_specs,
      snapshot,
    }
    const persistedItem = {
      ...diyItem,
      product_specs: { ...diyItem.product_specs, _snapshot: snapshot },
    }

    const liveDisplay = buildDiySnapshotDisplay(cartItem)
    const persistedDisplay = buildDiySnapshotDisplay(persistedItem)

    expect(liveDisplay).toEqual(persistedDisplay)
    expect(liveDisplay.appearance.value).toBe('星曜白 / 金属拉丝')
    expect(liveDisplay.parts.map(part => part.name)).toEqual([
      'AMD Ryzen 9 9950X3D',
      'NVIDIA RTX 5080',
      'Seasonic Focus GX 850',
    ])
  })

  it('builds a compact DIY display model from the saved snapshot', () => {
    const display = buildDiySnapshotDisplay(diyItem)

    expect(display.parts).toHaveLength(3)
    expect(display.parts[0]).toMatchObject({
      label: '处理器 CPU',
      name: 'AMD Ryzen 9 9950X3D',
    })
    expect(display.appearance.value).toBe('星曜白 / 金属拉丝')
    expect(display.metrics.map((metric) => `${metric.label}:${metric.value}`)).toContain('估算功耗:620W')
    expect(display.metrics.map((metric) => `${metric.label}:${metric.value}`)).toContain('3DMark:28,500')
    expect(display.compatibility.label).toBe('兼容检查通过')
    expect(display.pricing.map((price) => price.label)).toContain('配置总价')
  })

  it('summarizes DIY orders for the order list', () => {
    const preview = buildDiyOrderPreview({ items: [diyItem] })

    expect(preview.summary).toBe('AMD Ryzen 9 9950X3D / NVIDIA RTX 5080')
    expect(preview.badges.map((badge) => badge.label)).toEqual(['外观', '估算功耗', '3DMark'])
  })

  it('renders readable summaries for non-DIY custom snapshots', () => {
    const display = buildCustomSnapshotDisplay(genericCustomItem)
    const preview = buildOrderCustomPreview({ items: [genericCustomItem] })

    expect(display.title).toBe('定制快照')
    expect(display.highlights.map((item) => `${item.label}:${item.value}`)).toEqual(
      expect.arrayContaining(['颜色:青瓷蓝', 'Layout:75%', '刻字:HELLO']),
    )
    expect(display.metrics.map((metric) => `${metric.label}:${metric.value}`)).toContain('评分:92')
    expect(display.pricing.map((price) => `${price.label}:${price.value}`)).toContain('配置总价:¥399')
    expect(preview.summary).toContain('颜色: 青瓷蓝')
    expect(preview.badges.map((badge) => badge.label)).toContain('评分')
  })

  it('uses compact no-JSON spec tags for custom fallback data only', () => {
    expect(hasCustomSnapshotDisplay(genericCustomItem)).toBe(true)
    expect(formatCustomSpecs(genericCustomItem.product_specs).map((spec) => spec.label)).toEqual(['定制类型', '颜色'])
    expect(formatSpecs({ 规格: { color: 'black' } })[0].value).toBe('{"color":"black"}')
  })
})
