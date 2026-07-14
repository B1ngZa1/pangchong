import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import PriceProvenance from '@/components/PriceProvenance.vue'
import {
  getPriceProvenance,
  getTraceablePricePoints,
  summarizePriceProvenance,
} from '@/utils/priceProvenance'

const verifiedProduct = {
  price_source_name: '品牌官网',
  price_source_url: 'https://example.com/product',
  price_checked_at: '2026-06-30T08:00:00Z',
}

describe('price provenance presentation', () => {
  it('marks a price verified only when source, link, and check time are complete', () => {
    expect(getPriceProvenance(verifiedProduct)).toMatchObject({
      isVerified: true,
      state: 'verified',
      statusLabel: '价格已核验',
      sourceName: '品牌官网',
    })

    expect(getPriceProvenance({
      ...verifiedProduct,
      price_source_url: '',
    })).toMatchObject({
      isVerified: false,
      state: 'unavailable',
      unavailableMessage: '价格来源信息不完整，暂未完成核验',
    })
  })

  it('renders a linked source for verified prices and explicit unavailable copy otherwise', () => {
    const verified = mount(PriceProvenance, {
      props: { product: verifiedProduct },
    })
    expect(verified.attributes('data-verification-state')).toBe('verified')
    expect(verified.text()).toContain('价格已核验')
    expect(verified.get('a').attributes('href')).toBe('https://example.com/product')

    const unavailable = mount(PriceProvenance, {
      props: { product: {} },
    })
    expect(unavailable.attributes('data-verification-state')).toBe('unavailable')
    expect(unavailable.text()).toContain('暂无可验证的价格来源')
    expect(unavailable.text()).toContain('不会标记为已核验或历史低价')
  })

  it('counts verified DIY parts and removes history points without complete sources', () => {
    expect(summarizePriceProvenance([verifiedProduct, {}, null])).toEqual({
      total: 2,
      verified: 1,
      unavailable: 1,
    })

    expect(getTraceablePricePoints([
      {
        date: '2026-06-29',
        price: 999,
        source_name: '品牌官网',
        source_url: 'https://example.com/product',
      },
      {
        date: '2026-06-30',
        price: 899,
        source_name: '未提供链接的记录',
        source_url: null,
      },
    ])).toHaveLength(1)
  })
})
