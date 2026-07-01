import { describe, expect, it } from 'vitest'
import { findMissingDiyPartKeys, normalizeDiyPartKey } from '@/utils/modelParts'

describe('DIY model node contract', () => {
  it('normalizes exporter-friendly node aliases', () => {
    expect(normalizeDiyPartKey('DIY-GPU')).toBe('gpu')
    expect(normalizeDiyPartKey('mainboard_mesh')).toBe('motherboard')
    expect(normalizeDiyPartKey('chassis-shell')).toBe('case')
  })

  it('reports missing required nodes', () => {
    const names = ['case-shell', 'motherboard', 'cpu', 'gpu', 'ram', 'ssd', 'cooler']
    expect(findMissingDiyPartKeys(names)).toEqual(['psu'])
  })
})
