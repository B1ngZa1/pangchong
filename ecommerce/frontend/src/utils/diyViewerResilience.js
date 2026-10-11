export const DIY_VIEWER_LOAD_TIMEOUT_MS = 8000

export const DIY_VIEWER_FAILURES = {
  'webgl-unavailable': {
    title: '当前设备无法使用 3D',
    message: '浏览器或显卡环境未提供可用的 WebGL。已切换到配置清单，选件与下单功能不受影响。',
  },
  'model-load-failed': {
    title: '3D 模型加载失败',
    message: '模型资源暂时无法读取。已切换到配置清单，你仍可继续核价并完成购买。',
  },
  'missing-assembly-nodes': {
    title: '3D 模型不完整',
    message: '模型缺少必需的装配节点。已切换到配置清单，避免用不完整画面误导选件。',
  },
  'load-timeout': {
    title: '3D 加载时间过长',
    message: '3D 模型未在性能预算内准备完成。已切换到更轻量的配置清单。',
  },
}

export function getDiyViewerFailure(reason, details = {}) {
  const normalizedReason = Object.hasOwn(DIY_VIEWER_FAILURES, reason)
    ? reason
    : 'model-load-failed'

  return {
    ...DIY_VIEWER_FAILURES[normalizedReason],
    ...details,
    reason: normalizedReason,
  }
}

export function hasWebGLSupport(browserWindow = window, documentRef = document) {
  try {
    // Browser visual coverage can force the external capability boundary without
    // changing the production renderer or relying on the host GPU.
    if (browserWindow?.__PANGCHONG_E2E_WEBGL__ === 'unavailable') {
      return false
    }

    if (!browserWindow?.WebGLRenderingContext && !browserWindow?.WebGL2RenderingContext) {
      return false
    }

    const canvas = documentRef.createElement('canvas')
    return Boolean(
      canvas.getContext('webgl2', { failIfMajorPerformanceCaveat: true })
      || canvas.getContext('webgl', { failIfMajorPerformanceCaveat: true })
      || canvas.getContext('experimental-webgl', { failIfMajorPerformanceCaveat: true })
    )
  } catch {
    return false
  }
}
