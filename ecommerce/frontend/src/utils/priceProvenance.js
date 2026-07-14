const CHECKED_AT_FORMATTER = new Intl.DateTimeFormat('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  timeZone: 'Asia/Shanghai',
})

function cleanText(value) {
  return typeof value === 'string' ? value.trim() : ''
}

export function isHttpUrl(value) {
  const raw = cleanText(value)
  if (!raw) return false

  try {
    const url = new URL(raw)
    return url.protocol === 'https:' || url.protocol === 'http:'
  } catch {
    return false
  }
}

export function formatCheckedAt(value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : CHECKED_AT_FORMATTER.format(date)
}

export function getPriceProvenance(product = {}) {
  const sourceName = cleanText(product.price_source_name)
  const rawSourceUrl = cleanText(product.price_source_url)
  const sourceUrl = isHttpUrl(rawSourceUrl) ? rawSourceUrl : ''
  const checkedAtLabel = formatCheckedAt(product.price_checked_at)
  const isVerified = Boolean(sourceName && sourceUrl && checkedAtLabel)

  let unavailableMessage = '暂无可验证的价格来源'
  if (sourceName || rawSourceUrl || product.price_checked_at) {
    unavailableMessage = '价格来源信息不完整，暂未完成核验'
  }

  return {
    isVerified,
    state: isVerified ? 'verified' : 'unavailable',
    statusLabel: isVerified ? '价格已核验' : '价格待核验',
    sourceName,
    sourceUrl,
    checkedAtLabel,
    unavailableMessage,
  }
}

export function summarizePriceProvenance(products = []) {
  const items = products.filter(Boolean)
  const verified = items.filter(product => getPriceProvenance(product).isVerified).length
  return {
    total: items.length,
    verified,
    unavailable: items.length - verified,
  }
}

export function isTraceablePricePoint(point = {}) {
  const sourceName = cleanText(point.source_name)
  const sourceUrl = cleanText(point.source_url)
  const price = Number(point.price)
  return Boolean(
    sourceName
    && isHttpUrl(sourceUrl)
    && formatCheckedAt(point.date)
    && Number.isFinite(price)
    && price >= 0
  )
}

export function getTraceablePricePoints(points = []) {
  return Array.isArray(points) ? points.filter(isTraceablePricePoint) : []
}
