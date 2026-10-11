import { readFile, readdir, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(scriptDir, '..')
const tokenPath = path.join(rootDir, 'src/design-system/tokens/pangchong.tokens.json')
const manifestPath = path.join(rootDir, 'public/design-system.figma-manifest.json')
const checkOnly = process.argv.includes('--check')

const tokens = JSON.parse(await readFile(tokenPath, 'utf8'))

function kebab(value) {
  return value
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/[^a-zA-Z0-9]+/g, '-')
    .toLowerCase()
}

function flatten(node, segments = [], output = []) {
  for (const [key, value] of Object.entries(node)) {
    if (key.startsWith('$')) continue
    const next = [...segments, key]
    if (value && typeof value === 'object' && '$value' in value) {
      output.push({
        path: next,
        pathString: next.join('.'),
        type: value.$type,
        value: value.$value,
        description: value.$description || '',
      })
      continue
    }
    if (value && typeof value === 'object') flatten(value, next, output)
  }
  return output
}

async function collectVueSources(directory, relativeDirectory = 'src/design-system/components') {
  const entries = await readdir(directory, { withFileTypes: true })
  const sources = []
  for (const entry of entries) {
    const absolutePath = path.join(directory, entry.name)
    const relativePath = `${relativeDirectory}/${entry.name}`
    if (entry.isDirectory()) {
      sources.push(...await collectVueSources(absolutePath, relativePath))
    } else if (entry.isFile() && entry.name.endsWith('.vue')) {
      sources.push(relativePath.replaceAll(path.sep, '/'))
    }
  }
  return sources
}

function cssName(token) {
  return `--pc-${token.path.map(kebab).join('-')}`
}

function parsePixels(value) {
  if (typeof value === 'number') return value
  if (typeof value !== 'string') return null
  const match = value.trim().match(/^(-?\d+(?:\.\d+)?)(rem|px)?$/i)
  if (!match) return null
  const number = Number(match[1])
  return match[2]?.toLowerCase() === 'rem' ? number * 16 : number
}

function parseNumber(value) {
  if (typeof value === 'number') return value
  if (typeof value !== 'string') return null
  const number = Number(value.trim())
  return Number.isFinite(number) ? number : null
}

function parseDuration(value) {
  if (typeof value === 'number') return value
  if (typeof value !== 'string') return null
  const match = value.trim().match(/^(-?\d+(?:\.\d+)?)(ms|s)$/i)
  if (!match) return null
  const number = Number(match[1])
  return match[2].toLowerCase() === 's' ? number * 1000 : number
}

function collectionFor(token) {
  const [root, group] = token.path
  if (root === 'color' && group === 'semantic') return 'Color'
  if (root === 'color' && group === 'theme') return 'Theme'
  if (root === 'color') return 'Primitives'
  if (root === 'font') return 'Typography'
  if (root === 'motion') return 'Motion'
  if (root === 'shadow') return 'Effects'
  return 'Layout'
}

function figmaName(token) {
  return figmaNameForPath(token.path)
}

function figmaNameForPath(pathParts) {
  const [root, group, ...rest] = pathParts
  if (root === 'color' && group === 'semantic') return ['Color', ...rest].join('/')
  if (root === 'color' && group === 'theme') return ['Theme', ...rest].join('/')
  if (root === 'color') return ['Primitives', group, ...rest].join('/')
  if (root === 'font') return ['Typography', ...pathParts.slice(1)].join('/')
  if (root === 'shadow') return ['Effects', ...pathParts.slice(1)].join('/')
  if (root === 'motion') return ['Motion', ...pathParts.slice(1)].join('/')
  return [collectionFor({ path: pathParts }), ...pathParts].join('/')
}

function isReference(value) {
  return typeof value === 'string' && /^\{.+\}$/.test(value)
}

function aliasPath(value) {
  return value.match(/^\{(.+)\}$/)?.[1] || null
}

function aliasValue(value) {
  const pathString = aliasPath(value)
  return pathString ? { alias: figmaNameForPath(pathString.split('.')) } : null
}

function semanticScope(token) {
  const [, group] = token.path
  if (token.path[0] === 'color' && group === 'semantic') {
    const role = token.path[2]
    if (role === 'text') return ['TEXT_FILL']
    if (role === 'border') return ['STROKE_COLOR']
    return ['FRAME_FILL', 'SHAPE_FILL']
  }
  if (token.type === 'color') return []
  if (token.path[0] === 'space') return ['GAP']
  if (token.path[0] === 'radius') return ['CORNER_RADIUS']
  if (token.path[0] === 'font' && token.path[1] === 'size') return ['FONT_SIZE']
  if (token.path[0] === 'font' && token.path[1] === 'lineHeight') return ['LINE_HEIGHT']
  if (token.path[0] === 'font' && token.path[1] === 'weight') return ['FONT_WEIGHT']
  if (token.path[0] === 'font' && token.path[1] === 'family') return ['FONT_FAMILY']
  if (token.path[0] === 'size') return ['WIDTH_HEIGHT']
  if (token.path[0] === 'opacity') return ['OPACITY']
  return []
}

function variableType(token) {
  if (token.type === 'color') return 'COLOR'
  if (token.type === 'fontFamily' || token.type === 'cubicBezier') return 'STRING'
  if (token.type === 'shadow') return null
  return 'FLOAT'
}

function normalizedValue(token) {
  if (isReference(token.value)) return aliasValue(token.value)
  if (token.type === 'dimension' || token.type === 'number' || token.type === 'fontWeight' || token.type === 'duration') {
    const number = token.type === 'dimension'
      ? parsePixels(token.value)
      : token.type === 'duration'
        ? parseDuration(token.value)
        : parseNumber(token.value)
    return number === null ? { unsupported: true, sourceValue: token.value } : number
  }
  return token.value
}

function highContrastValue(token) {
  const overrides = {
    'color.semantic.text.secondary': '{color.dark.100}',
    'color.semantic.text.muted': '{color.dark.200}',
    'color.semantic.border.subtle': '{color.dark.600}',
  }
  const override = overrides[token.pathString]
  return override ? normalizedValue({ ...token, value: override }) : normalizedValue(token)
}

const flatTokens = flatten(tokens)
const variables = flatTokens
  .filter((token) => variableType(token))
  .map((token) => ({
    sourcePath: token.pathString,
    name: figmaName(token),
    collection: collectionFor(token),
    type: variableType(token),
    scopes: semanticScope(token),
    codeSyntax: `var(${cssName(token)})`,
    value: normalizedValue(token),
    modes: token.path[0] === 'color' && token.path[1] === 'semantic'
      ? { Default: normalizedValue(token), 'High Contrast': highContrastValue(token) }
      : { Value: normalizedValue(token) },
    description: token.description,
  }))

const effects = flatTokens
  .filter((token) => token.type === 'shadow')
  .map((token) => ({
    sourcePath: token.pathString,
    name: figmaName(token),
    cssValue: token.value,
    description: token.description,
  }))

const componentSources = [
  ['Button', 'src/design-system/components/DsButton.vue'],
  ['IconButton', 'src/design-system/components/DsIconButton.vue'],
  ['Menu', 'src/design-system/components/DsMenu.vue'],
  ['SearchField', 'src/design-system/components/DsSearchField.vue'],
  ['Field', 'src/design-system/components/DsField.vue'],
  ['Toggle', 'src/design-system/components/DsToggle.vue'],
  ['Checkbox', 'src/design-system/components/DsCheckbox.vue'],
  ['Badge', 'src/design-system/components/DsBadge.vue'],
  ['Alert', 'src/design-system/components/DsAlert.vue'],
  ['Toast', 'src/design-system/components/DsToast.vue'],
  ['Skeleton', 'src/design-system/components/DsSkeleton.vue'],
  ['AsyncState', 'src/design-system/components/DsAsyncState.vue'],
  ['EmptyState', 'src/design-system/components/DsEmptyState.vue'],
  ['Card', 'src/design-system/components/DsCard.vue'],
  ['Dialog', 'src/design-system/components/DsDialog.vue'],
  ['Tabs', 'src/design-system/components/DsTabs.vue'],
  ['ChoiceCard', 'src/design-system/components/DsChoiceCard.vue'],
  ['ProductCard', 'src/design-system/components/DsProductCard.vue'],
  ['CartLineItem', 'src/design-system/components/DsCartLineItem.vue'],
  ['OrderSummary', 'src/design-system/components/DsOrderSummary.vue'],
  ['PriceSummary', 'src/design-system/components/DsPriceSummary.vue'],
  ['DiyPartPicker', 'src/design-system/components/DsDiyPartPicker.vue'],
  ['StepIndicator', 'src/design-system/components/DsStepIndicator.vue'],
  ['Pagination', 'src/design-system/components/DsPagination.vue'],
  ['OrderTimeline', 'src/design-system/components/DsOrderTimeline.vue'],
  ['DataTable', 'src/design-system/components/DsDataTable.vue'],
  ['CompatibilityStatus', 'src/design-system/components/DsCompatibilityStatus.vue'],
  ['OrderSuccess', 'src/design-system/components/DsOrderSuccess.vue'],
  ['ContrastToggle', 'src/design-system/components/DsContrastToggle.vue'],
  ['MediaCategoryCard', 'src/design-system/components/commerce/DsMediaCategoryCard.vue'],
  ['CommerceNav', 'src/design-system/components/commerce/DsCommerceNav.vue'],
  ['WorkbenchShell', 'src/design-system/components/workbench/DsWorkbenchShell.vue'],
  ['PartsInspector', 'src/design-system/components/workbench/DsPartsInspector.vue'],
  ['BuildSummary', 'src/design-system/components/workbench/DsBuildSummary.vue'],
  ['PriceProvenance', 'src/components/PriceProvenance.vue'],
]

const mappedDesignSystemSources = new Set(componentSources
  .filter(([, source]) => source.startsWith('src/design-system/components/'))
  .map(([, source]) => source))
const designSystemSources = await collectVueSources(path.join(rootDir, 'src/design-system/components'))
const missingDesignSystemSources = designSystemSources.filter((source) => !mappedDesignSystemSources.has(source))
if (missingDesignSystemSources.length) {
  throw new Error(`Figma handoff is missing component mappings: ${missingDesignSystemSources.join(', ')}`)
}

const componentEntries = componentSources.map(([name, source]) => ({
  name,
  figmaName: `Components/${name}`,
  source,
  framework: 'Vue',
  codeConnect: { label: 'Vue', source },
}))

const manifest = {
  schemaVersion: '0.1.0',
  designSystemVersion: '0.9.11',
  generatedBy: 'scripts/build-figma-handoff.mjs',
  source: 'src/design-system/tokens/pangchong.tokens.json',
  syncStatus: {
    targetFileKey: null,
    editAccess: false,
    note: '等待用户提供目标 Figma design URL 与编辑权限；此 manifest 不宣称已写回 Figma。',
  },
  collections: [
    { name: 'Primitives', modes: ['Value'], purpose: 'raw color values; scopes stay empty' },
    { name: 'Color', modes: ['Default', 'High Contrast'], purpose: 'semantic color aliases and accessible overrides' },
    { name: 'Theme', modes: ['Value'], purpose: 'page-specific brand atmosphere only' },
    { name: 'Layout', modes: ['Value'], purpose: 'spacing, sizing, radius, opacity, breakpoints and layering' },
    { name: 'Typography', modes: ['Value'], purpose: 'font family, size, line height and weight' },
    { name: 'Motion', modes: ['Value'], purpose: 'duration and easing strings' },
    { name: 'Effects', modes: ['Value'], purpose: 'effect-style source tokens; not variables' },
  ],
  variables,
  effects,
  components: componentEntries,
  qa: {
    requiredBeforeSync: [
      'get_libraries(fileKey) before search_design_system',
      'search_design_system for Button, Card, Field and ProductCard before creating components',
      'validate scopes and WEB code syntax on every variable',
      'get_metadata and get_screenshot after every Figma component',
      'add_code_connect_map or send_code_connect_mappings after component validation',
    ],
  },
}

const expected = `${JSON.stringify(manifest, null, 2)}\n`
if (checkOnly) {
  const current = await readFile(manifestPath, 'utf8').catch(() => '')
  if (current !== expected) {
    console.error(`Figma handoff manifest is stale: ${path.relative(rootDir, manifestPath)}`)
    process.exitCode = 1
  } else {
    console.log('Figma handoff manifest is current.')
  }
} else {
  await writeFile(manifestPath, expected, 'utf8')
  console.log(`Generated Figma handoff manifest (${variables.length} variables, ${effects.length} effect styles, ${componentEntries.length} components).`)
}
