import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import Product3DViewer from '@/components/Product3DViewer.vue'

const loaderState = vi.hoisted(() => ({ mode: 'error' }))

vi.mock('three', () => {
  class Vector3 {
    constructor(x = 0, y = 0, z = 0) {
      this.x = x
      this.y = y
      this.z = z
    }
    set(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; return this }
    setScalar(value) { return this.set(value, value, value) }
    fromArray(values = []) { return this.set(values[0] || 0, values[1] || 0, values[2] || 0) }
    copy(value) { return this.set(value.x, value.y, value.z) }
    add(value) { this.x += value.x; this.y += value.y; this.z += value.z; return this }
    sub(value) { this.x -= value.x; this.y -= value.y; this.z -= value.z; return this }
    normalize() { return this }
    multiplyScalar(value) { this.x *= value; this.y *= value; this.z *= value; return this }
  }

  class Euler extends Vector3 {}

  class Color {
    constructor(value = '#000000') { this.value = value }
    copy(value) { this.value = value?.value ?? value; return this }
    set(value) { this.value = value; return this }
  }

  class Object3D {
    constructor() {
      this.name = ''
      this.children = []
      this.parent = null
      this.position = new Vector3()
      this.rotation = new Euler()
      this.scale = new Vector3(1, 1, 1)
      this.userData = {}
    }
    add(...children) {
      children.forEach((child) => {
        child.parent = this
        this.children.push(child)
      })
    }
    remove(child) { this.children = this.children.filter(item => item !== child) }
    traverse(callback) {
      callback(this)
      this.children.forEach(child => child.traverse(callback))
    }
    updateMatrixWorld() {}
  }

  class Group extends Object3D {}
  class Scene extends Group {}

  class PerspectiveCamera extends Object3D {
    constructor() {
      super()
      this.near = 0.1
      this.far = 100
      this.aspect = 1
    }
    updateProjectionMatrix() {}
  }

  class MeshStandardMaterial {
    constructor(options = {}) {
      Object.assign(this, options)
      this.name = options.name || ''
      this.color = new Color(options.color)
      this.emissive = options.emissive ? new Color(options.emissive) : undefined
      this.emissiveIntensity = options.emissiveIntensity || 0
      this.opacity = options.opacity ?? 1
      this.transparent = options.transparent ?? false
      this.userData = {}
    }
    clone() { return new MeshStandardMaterial({ ...this, color: this.color.value, emissive: this.emissive?.value }) }
    dispose() {}
  }

  class Geometry { dispose() {} }
  class BoxGeometry extends Geometry {}
  class CircleGeometry extends Geometry {}

  class Mesh extends Object3D {
    constructor(geometry = new Geometry(), material = new MeshStandardMaterial()) {
      super()
      this.geometry = geometry
      this.material = material
      this.isMesh = true
    }
  }

  class Light extends Object3D {}
  class HemisphereLight extends Light {}
  class DirectionalLight extends Light {
    constructor() {
      super()
      this.shadow = { mapSize: { set() {} } }
    }
  }

  class Box3 {
    setFromObject() { return this }
    isEmpty() { return true }
    getCenter(target) { return target }
    getSize(target) { return target.set(1, 1, 1) }
  }

  class WebGLRenderer {
    constructor() {
      this.domElement = document.createElement('canvas')
      this.shadowMap = {}
    }
    setPixelRatio() {}
    setSize() {}
    render() {}
    dispose() {}
  }

  return {
    ACESFilmicToneMapping: 'ACESFilmicToneMapping',
    Box3,
    BoxGeometry,
    CircleGeometry,
    Color,
    DirectionalLight,
    Group,
    HemisphereLight,
    Mesh,
    MeshStandardMaterial,
    PCFShadowMap: 'PCFShadowMap',
    PerspectiveCamera,
    Scene,
    SRGBColorSpace: 'SRGBColorSpace',
    Vector3,
    WebGLRenderer,
  }
})

vi.mock('three/examples/jsm/controls/OrbitControls.js', async () => {
  const { Vector3 } = await import('three')
  return {
    OrbitControls: class OrbitControls {
      constructor() { this.target = new Vector3() }
      update() {}
      dispose() {}
    },
  }
})

vi.mock('three/examples/jsm/loaders/GLTFLoader.js', async () => {
  const THREE = await import('three')
  return {
    GLTFLoader: class GLTFLoader {
      load(_url, onLoad, _onProgress, onError) {
        if (loaderState.mode === 'pending') return
        if (loaderState.mode === 'error') {
          queueMicrotask(() => onError(new Error('model unavailable')))
          return
        }

        const scene = new THREE.Group()
        const caseNode = new THREE.Group()
        caseNode.name = 'diy-case'
        caseNode.add(new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshStandardMaterial()))
        scene.add(caseNode)
        queueMicrotask(() => onLoad({ scene }))
      }
    },
  }
})

const diyParts = ['case', 'motherboard', 'cpu', 'gpu', 'ram', 'ssd', 'cooler', 'psu']
  .map(id => ({ id, selected: true, productName: id }))

function mountViewer(props = {}) {
  return mount(Product3DViewer, {
    props: {
      modelUrl: '/models/case.glb',
      parts: diyParts,
      ...props,
    },
  })
}

describe('Product3DViewer resilience triggers', () => {
  beforeEach(() => {
    loaderState.mode = 'error'
    vi.stubGlobal('requestAnimationFrame', vi.fn(() => 1))
    vi.stubGlobal('cancelAnimationFrame', vi.fn())
    vi.stubGlobal('ResizeObserver', class ResizeObserver { observe() {}; disconnect() {} })
    vi.stubGlobal('WebGL2RenderingContext', class WebGL2RenderingContext {})
    vi.stubGlobal('matchMedia', vi.fn(() => ({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })))
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({})
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  it('emits WebGL unavailable before creating a viewer', async () => {
    vi.stubGlobal('WebGL2RenderingContext', undefined)
    vi.stubGlobal('WebGLRenderingContext', undefined)

    const wrapper = mountViewer()
    await nextTick()

    expect(wrapper.emitted('failure')?.[0]?.[0]).toMatchObject({ reason: 'webgl-unavailable' })
    wrapper.unmount()
  })

  it('emits model loading failure when GLTFLoader rejects the asset', async () => {
    loaderState.mode = 'error'
    const wrapper = mountViewer()
    await flushPromises()

    expect(wrapper.emitted('failure')?.[0]?.[0]).toMatchObject({ reason: 'model-load-failed' })
    expect(cancelAnimationFrame).toHaveBeenCalled()
    wrapper.unmount()
  })

  it('emits missing assembly nodes after validating a loaded model', async () => {
    loaderState.mode = 'missing-nodes'
    const wrapper = mountViewer()
    await flushPromises()

    expect(wrapper.emitted('failure')?.[0]?.[0]).toMatchObject({
      reason: 'missing-assembly-nodes',
      missingNodes: ['motherboard', 'cpu', 'gpu', 'ram', 'ssd', 'cooler', 'psu'],
    })
    wrapper.unmount()
  })

  it('emits a loading timeout and ignores a still-pending model request', async () => {
    vi.useFakeTimers()
    loaderState.mode = 'pending'
    const wrapper = mountViewer({ loadTimeoutMs: 8000 })

    await vi.advanceTimersByTimeAsync(8000)
    await nextTick()

    expect(wrapper.emitted('failure')?.[0]?.[0]).toMatchObject({ reason: 'load-timeout' })
    wrapper.unmount()
  })
})
