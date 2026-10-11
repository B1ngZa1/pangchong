import { describe, expect, it, vi } from 'vitest'
import {
  DIY_VIEWER_LOAD_TIMEOUT_MS,
  getDiyViewerFailure,
  hasWebGLSupport,
} from '@/utils/diyViewerResilience'

describe('DIY viewer resilience contract', () => {
  it('uses an eight-second model loading performance budget', () => {
    expect(DIY_VIEWER_LOAD_TIMEOUT_MS).toBe(8000)
  })

  it('detects an unavailable WebGL environment without throwing', () => {
    const browserWindow = {}
    const documentRef = { createElement: vi.fn() }

    expect(hasWebGLSupport(browserWindow, documentRef)).toBe(false)
    expect(documentRef.createElement).not.toHaveBeenCalled()
  })

  it('accepts a hardware-capable WebGL context', () => {
    const context = {}
    const getContext = vi.fn(type => type === 'webgl2' ? context : null)
    const browserWindow = { WebGL2RenderingContext: class WebGL2RenderingContext {} }
    const documentRef = { createElement: () => ({ getContext }) }

    expect(hasWebGLSupport(browserWindow, documentRef)).toBe(true)
    expect(getContext).toHaveBeenCalledWith('webgl2', { failIfMajorPerformanceCaveat: true })
  })

  it.each([
    ['webgl-unavailable', '当前设备无法使用 3D'],
    ['model-load-failed', '3D 模型加载失败'],
    ['missing-assembly-nodes', '3D 模型不完整'],
    ['load-timeout', '3D 加载时间过长'],
  ])('provides clear list-mode copy for %s', (reason, title) => {
    expect(getDiyViewerFailure(reason)).toMatchObject({ reason, title })
  })
})
