import { describe, expect, it } from 'vitest'
import * as THREE from 'three'
import { collectDiyPartRoots, findMissingDiyPartKeys, normalizeDiyPartKey } from '@/utils/modelParts'

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

  it('treats a named group as the part root for all descendant meshes', () => {
    const scene = new THREE.Group()
    const gpu = new THREE.Group()
    gpu.name = 'gpu'
    const unnamedMesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1))
    gpu.add(unnamedMesh)
    scene.add(gpu)

    const roots = collectDiyPartRoots(scene)
    expect(roots.get('gpu')).toEqual([gpu])
    expect(roots.get('gpu')[0].children).toContain(unnamedMesh)
  })
})
