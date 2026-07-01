const PART_LABELS = {
  cpu: '处理器 CPU',
  gpu: '显卡 GPU',
  motherboard: '主板',
  ram: '内存 RAM',
  ssd: '固态硬盘 SSD',
  cooler: '散热器',
  psu: '电源 PSU',
  case: '机箱',
}

const SNAPSHOT_TYPE_LABELS = {
  diy_pc: 'DIY 装机快照',
}

const SNAPSHOT_SKIP_KEYS = new Set([
  'type',
  'custom_type',
  'version',
  'created_at',
  'createdAt',
  'parts',
  'selected_parts',
  'selectedParts',
  'components',
  'items',
  'selections',
  'selected_options',
  'selectedOptions',
  'options',
  'appearance',
  'appearance_choice',
  'appearanceChoice',
  'metrics',
  'pricing',
  'compatibility',
])

const SPEC_LABELS = {
  socket: '插槽',
  cores: '核心',
  threads: '线程',
  tdp: 'TDP',
  vram: '显存',
  length: '长度',
  form_factor: '板型',
  memory: '内存支持',
  capacity: '容量',
  type: '类型',
  interface: '接口',
  height: '高度',
  wattage: '功率',
  efficiency: '认证',
  mb_support: '主板支持',
  gpu_length: '显卡限长',
}

const GENERIC_LABELS = {
  config_name: '配置名称',
  configuration_name: '配置名称',
  title: '名称',
  name: '名称',
  theme: '主题',
  color: '颜色',
  material: '材质',
  finish: '表面',
  size: '尺寸',
  budget: '预算',
  note: '备注',
  notes: '备注',
  remark: '备注',
  engraving: '刻字',
  delivery: '交付',
  service: '服务',
}

const PART_SPEC_KEYS = {
  cpu: ['socket', 'cores', 'threads', 'tdp'],
  gpu: ['vram', 'length', 'tdp'],
  motherboard: ['socket', 'form_factor', 'memory'],
  ram: ['capacity', 'type'],
  ssd: ['capacity', 'interface'],
  cooler: ['type', 'height', 'tdp_support'],
  psu: ['wattage', 'efficiency'],
  case: ['type', 'mb_support', 'gpu_length'],
}

const METRIC_FIELDS = [
  { key: 'power', label: '估算功耗', keys: ['total_power_w', 'estimated_power_w', 'power_w', 'power', '估算功耗'], suffix: 'W' },
  { key: 'psu-headroom', label: '电源冗余', keys: ['psu_headroom_w', 'psu_headroom', '电源冗余'], suffix: 'W' },
  { key: 'gpu-space', label: '显卡空间', keys: ['gpu_space_headroom_mm', 'gpu_space_headroom', 'gpu_space', '显卡空间'], suffix: 'mm' },
  { key: '3dmark', label: '3DMark', keys: ['estimated_3dmark', '3dmark', '3DMark'] },
  { key: 'score', label: '评分', keys: ['score', 'rating'] },
]

const PRICING_FIELDS = [
  { key: 'parts-total', label: '配件合计', keys: ['parts_total'] },
  { key: 'appearance-diff', label: '外观差价', keys: ['appearance_price_diff', 'appearance_diff', 'price_diff'] },
  { key: 'saved', label: '优惠', keys: ['saved_amount', 'discount_amount'] },
  { key: 'total', label: '配置总价', keys: ['total', 'total_price', 'final_price'] },
]

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function formatSpecValue(value, options = {}) {
  const allowObjects = options.allowObjects !== false
  if (Array.isArray(value)) {
    return value
      .map((item) => (isPlainObject(item) ? (allowObjects ? JSON.stringify(item) : '') : formatCompactValue(item)))
      .filter(Boolean)
      .join(', ')
  }
  if (isPlainObject(value)) return allowObjects ? JSON.stringify(value) : ''
  return String(value)
}

function formatCompactValue(value) {
  if (value === null || value === undefined || value === '') return ''
  if (Array.isArray(value)) return value.filter(Boolean).join('、')
  if (isPlainObject(value)) return ''
  return String(value)
}

function toReadableLabel(key) {
  const text = String(key || '').trim()
  if (!text) return ''
  return SPEC_LABELS[text] || GENERIC_LABELS[text] || text
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatMoney(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function formatMetricNumber(value) {
  if (value === null || value === undefined || value === '') return ''
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric.toLocaleString('zh-CN') : String(value)
}

function resolveSpecs(input) {
  if (!input) return null
  if (isPlainObject(input.product_specs)) return input.product_specs
  if (isPlainObject(input.specs)) return input.specs
  return isPlainObject(input) ? input : null
}

export function formatSpecs(specs, limit, options = {}) {
  if (!isPlainObject(specs)) return []
  const entries = Object.entries(specs)
    .filter(([key, value]) => !String(key).startsWith('_') && value !== null && value !== undefined && value !== '')

  return (Number.isFinite(limit) ? entries.slice(0, limit) : entries)
    .map(([label, value]) => ({
      label,
      value: formatSpecValue(value, options),
    }))
    .filter((spec) => spec.value)
}

export function formatCustomSpecs(specs, limit) {
  return formatSpecs(specs, limit, { allowObjects: false })
}

export function isCustomOrderItem(item) {
  if (!item || typeof item !== 'object') return false
  const specs = resolveSpecs(item)
  const snapshot = isPlainObject(item.snapshot) ? item.snapshot : specs?._snapshot
  if (item.item_type === 'product' && !item.custom_type && !specs?.custom_type) return false
  return item.item_type === 'custom'
    || Boolean(item.custom_type)
    || Boolean(specs?.custom_type)
    || isPlainObject(snapshot)
}

export function getCustomSnapshot(input) {
  const specs = resolveSpecs(input)
  const snapshot = isPlainObject(input?.snapshot) ? input.snapshot : specs?._snapshot
  if (!isPlainObject(snapshot) || !isCustomOrderItem(input)) return null
  return snapshot
}

function getCustomType(input, specs = resolveSpecs(input), snapshot = getCustomSnapshot(input)) {
  return input?.custom_type
    || specs?.custom_type
    || snapshot?.custom_type
    || snapshot?.type
    || 'custom'
}

export function getDiySnapshot(input) {
  const specs = resolveSpecs(input)
  const snapshot = getCustomSnapshot(input)
  const declaredType = getCustomType(input, specs, snapshot)
  if (declaredType !== 'diy_pc' || !isPlainObject(snapshot)) return null
  return snapshot
}

export function isDiyPcOrderItem(item) {
  return Boolean(getDiySnapshot(item))
}

function formatPartName(part) {
  if (!isPlainObject(part)) return formatCompactValue(part)
  const brand = formatCompactValue(part?.brand)
  const name = formatCompactValue(part?.name)
    || formatCompactValue(part?.model)
    || formatCompactValue(part?.title)
    || formatCompactValue(part?.value)
  if (!brand) return name
  if (!name) return brand
  return name.toLowerCase().includes(brand.toLowerCase()) ? name : `${brand} ${name}`
}

function formatObjectMeta(source, limit = 3) {
  if (!isPlainObject(source)) return ''
  return Object.entries(source)
    .map(([key, value]) => {
      const formatted = formatCompactValue(value)
      return formatted ? `${SPEC_LABELS[key] || toReadableLabel(key)} ${formatted}` : ''
    })
    .filter(Boolean)
    .slice(0, limit)
    .join(' · ')
}

function formatPartMeta(part) {
  const specs = isPlainObject(part?.specs) ? part.specs : {}
  const keys = PART_SPEC_KEYS[part?.key] || []
  const preferred = keys
    .map((key) => {
      const value = formatCompactValue(specs[key])
      return value ? `${SPEC_LABELS[key] || key} ${value}` : ''
    })
    .filter(Boolean)
    .slice(0, 3)
    .join(' · ')
  return preferred || formatObjectMeta(part?.specs || part?.attributes || part?.options)
}

function normalizePartsSource(snapshot) {
  if (Array.isArray(snapshot.parts)) return snapshot.parts
  const source = snapshot.selected_parts || snapshot.selectedParts || snapshot.components || snapshot.items
  if (Array.isArray(source)) return source
  if (isPlainObject(source)) {
    return Object.entries(source).map(([key, value]) => (
      isPlainObject(value) ? { key, label: toReadableLabel(key), ...value } : { key, label: toReadableLabel(key), value }
    ))
  }
  return []
}

function buildParts(snapshot) {
  return normalizePartsSource(snapshot)
    .map((part, index) => ({
      key: part?.key || part?.id || `part-${index}`,
      label: part?.label || PART_LABELS[part?.key] || toReadableLabel(part?.key) || '配件',
      name: formatPartName(part),
      meta: formatPartMeta(part),
      price: Number(part?.price || part?.price_diff || 0) > 0 ? `¥${formatMoney(part.price || part.price_diff)}` : '',
    }))
    .filter((part) => part.name)
}

function formatAppearance(snapshot, specs, customType = 'custom') {
  const rawAppearance = snapshot.appearance || snapshot.appearance_choice || snapshot.appearanceChoice
  const appearance = isPlainObject(rawAppearance) ? rawAppearance : {}
  const variant = formatCompactValue(
    appearance.variant_name || appearance.color_name || appearance.variant || appearance.color,
  )
  const material = formatCompactValue(
    appearance.material_name || appearance.material || appearance.finish,
  )
  const choice = [variant, material].filter(Boolean).join(' / ')
    || formatCompactValue(rawAppearance)
    || formatCompactValue(specs?.['3D 外观'])
    || formatCompactValue(specs?.['外观'])

  const details = []
  if (appearance.camera_preset) details.push(`视角 ${appearance.camera_preset}`)
  if (typeof appearance.auto_rotate === 'boolean') details.push(appearance.auto_rotate ? '自动旋转' : '固定视角')
  if (Number(appearance.price_diff || 0) > 0) details.push(`外观差价 ¥${formatMoney(appearance.price_diff)}`)

  return choice ? { label: customType === 'diy_pc' ? '3D 外观' : '外观', value: choice, details } : null
}

function metricItem(key, label, value, suffix = '') {
  const formatted = formatMetricNumber(value)
  const needsSuffix = suffix && Number.isFinite(Number(value)) && !String(value).toLowerCase().includes(suffix.toLowerCase())
  return formatted ? { key, label, value: `${formatted}${needsSuffix ? suffix : ''}` } : null
}

function firstDefined(sources, keys) {
  for (const source of sources) {
    if (!isPlainObject(source)) continue
    for (const key of keys) {
      if (source[key] !== null && source[key] !== undefined && source[key] !== '') return source[key]
    }
  }
  return undefined
}

function buildMetrics(snapshot, specs) {
  const metrics = isPlainObject(snapshot.metrics) ? snapshot.metrics : {}
  const rows = METRIC_FIELDS.map((field) => (
    metricItem(field.key, field.label, firstDefined([metrics, snapshot, specs], field.keys), field.suffix)
  ))
  return rows.filter(Boolean)
}

function buildPricing(snapshot) {
  const pricing = isPlainObject(snapshot.pricing) ? snapshot.pricing : {}
  const rows = PRICING_FIELDS.map((field) => {
    const value = firstDefined([pricing, snapshot], field.keys)
    return Number(value || 0) > 0 ? { key: field.key, label: field.label, value: `¥${formatMoney(value)}` } : null
  })
  return rows.filter(Boolean)
}

function summarizeCompatibility(snapshot) {
  const checks = Array.isArray(snapshot.metrics?.compatibility) ? snapshot.metrics.compatibility : []
  if (checks.length === 0) return null

  const warnings = checks.filter((check) => check?.level === 'warn')
  const pending = checks.filter((check) => check?.level === 'pending')
  const issues = (warnings.length ? warnings : pending)
    .slice(0, 2)
    .map((check) => ({
      key: check.key || check.title,
      title: check.title || '兼容检查',
      message: check.message || '',
    }))

  if (warnings.length > 0) {
    return { tone: 'warn', label: `${warnings.length} 项需复核`, issues }
  }
  if (pending.length > 0) {
    return { tone: 'pending', label: `${pending.length} 项待确认`, issues }
  }
  return { tone: 'ok', label: '兼容检查通过', issues: [] }
}

function buildHighlights(snapshot, specs) {
  const optionSource = snapshot.selections || snapshot.selected_options || snapshot.selectedOptions || snapshot.options
  const optionRows = isPlainObject(optionSource)
    ? Object.entries(optionSource).map(([key, value]) => ({
      key: `option-${key}`,
      label: toReadableLabel(key),
      value: formatCompactValue(isPlainObject(value) ? value.name || value.label || value.value : value),
    }))
    : []

  const topRows = Object.entries(snapshot)
    .filter(([key, value]) => !SNAPSHOT_SKIP_KEYS.has(key) && !String(key).startsWith('_') && !isPlainObject(value))
    .map(([key, value]) => ({
      key: `field-${key}`,
      label: toReadableLabel(key),
      value: formatCompactValue(value),
    }))

  const specRows = Object.entries(specs || {})
    .filter(([key, value]) => !String(key).startsWith('_') && value !== null && value !== undefined && value !== '' && !isPlainObject(value))
    .map(([key, value]) => ({
      key: `spec-${key}`,
      label: key,
      value: formatCompactValue(value),
    }))

  const seen = new Set()
  return [...optionRows, ...topRows, ...specRows]
    .filter((row) => row.label && row.value)
    .filter((row) => {
      const fingerprint = `${row.label}:${row.value}`
      if (seen.has(fingerprint)) return false
      seen.add(fingerprint)
      return true
    })
    .slice(0, 6)
}

function formatSnapshotDate(value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleString('zh-CN')
}

export function buildCustomSnapshotDisplay(input) {
  const specs = resolveSpecs(input)
  const snapshot = getCustomSnapshot(input)
  if (!snapshot) return null
  const customType = getCustomType(input, specs, snapshot)
  const display = {
    customType,
    title: SNAPSHOT_TYPE_LABELS[customType] || '定制快照',
    createdAt: formatSnapshotDate(snapshot.created_at || snapshot.createdAt),
    parts: buildParts(snapshot),
    appearance: formatAppearance(snapshot, specs, customType),
    metrics: buildMetrics(snapshot, specs),
    pricing: buildPricing(snapshot),
    highlights: buildHighlights(snapshot, specs),
    compatibility: summarizeCompatibility(snapshot),
  }

  const hasContent = display.parts.length
    || display.appearance
    || display.metrics.length
    || display.pricing.length
    || display.highlights.length
    || display.compatibility
  return hasContent ? display : null
}

export function buildDiySnapshotDisplay(input) {
  const display = buildCustomSnapshotDisplay(input)
  if (display?.customType !== 'diy_pc') return null

  return display
}

export function hasCustomSnapshotDisplay(item) {
  return Boolean(buildCustomSnapshotDisplay(item))
}

function summarizeDisplay(item, display) {
  const cpu = display.parts.find((part) => part.key === 'cpu')
  const gpu = display.parts.find((part) => part.key === 'gpu')
  const fallbackParts = display.parts.slice(0, 2).map((part) => part.name)
  const fallbackHighlights = display.highlights.slice(0, 2).map((row) => `${row.label}: ${row.value}`)
  if (display.customType === 'diy_pc') {
    return [cpu?.name, gpu?.name].filter(Boolean).join(' / ')
      || fallbackParts.join(' / ')
      || item.product_name
  }
  return fallbackParts.join(' / ')
    || display.appearance?.value
    || fallbackHighlights.join(' · ')
    || item.product_name
}

export function buildOrderCustomPreview(order) {
  const item = (order?.items || []).find(hasCustomSnapshotDisplay)
  if (!item) return null

  const display = buildCustomSnapshotDisplay(item)
  if (!display) return null

  const badges = [
    display.appearance ? { key: 'appearance', label: '外观', value: display.appearance.value } : null,
    display.metrics.find((metric) => metric.key === 'power'),
    display.metrics.find((metric) => metric.key === '3dmark'),
  ]

  if (display.customType !== 'diy_pc') {
    badges.push(
      display.metrics.find((metric) => !['power', '3dmark'].includes(metric.key)),
      display.highlights[0],
    )
  }

  return {
    title: display.title,
    summary: summarizeDisplay(item, display),
    badges: badges.filter(Boolean),
  }
}

export function buildDiyOrderPreview(order) {
  const diyItems = (order?.items || []).filter(isDiyPcOrderItem)
  return buildOrderCustomPreview({ ...order, items: diyItems })
}
