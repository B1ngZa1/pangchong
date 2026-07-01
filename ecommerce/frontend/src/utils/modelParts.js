export const DIY_MODEL_PART_KEYS = ['case', 'motherboard', 'cpu', 'gpu', 'ram', 'ssd', 'cooler', 'psu']

const aliases = {
  mobo: 'motherboard',
  mainboard: 'motherboard',
  memory: 'ram',
  storage: 'ssd',
  nvme: 'ssd',
  heatsink: 'cooler',
  aio: 'cooler',
  power: 'psu',
  chassis: 'case',
}

export function normalizeDiyPartKey(name) {
  const normalized = String(name || '').trim().toLowerCase().replace(/^diy[-_]/, '')
  const tokens = normalized.split(/[^a-z0-9]+/).filter(Boolean)
  for (const token of tokens) {
    const candidate = aliases[token] || token
    if (DIY_MODEL_PART_KEYS.includes(candidate)) return candidate
  }
  return null
}

export function findMissingDiyPartKeys(nodeNames) {
  const found = new Set((nodeNames || []).map(normalizeDiyPartKey).filter(Boolean))
  return DIY_MODEL_PART_KEYS.filter(key => !found.has(key))
}
