import { readdir, readFile, writeFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(scriptDir, '..')
const sourceDir = path.join(rootDir, 'src')
const contentDir = path.resolve(rootDir, '../../docs/design-system/content')
const inventoryJsonPath = path.join(contentDir, 'ui-copy.inventory.json')
const inventoryCsvPath = path.join(contentDir, 'ui-copy.inventory.csv')
const overridesPath = path.join(contentDir, 'ui-copy.overrides.json')
const action = process.argv[2] || 'extract'
const writeChanges = process.argv.includes('--write')

const visibleAttributes = ['alt', 'aria-label', 'placeholder', 'title']
const supportedExtensions = new Set(['.vue', '.js', '.ts'])

async function walk(directory) {
  const output = []
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.name === '__tests__' || entry.name.startsWith('.')) continue
    // Administrative region names are reference data, not editable product copy.
    if (entry.name === 'regions.js') continue
    const fullPath = path.join(directory, entry.name)
    if (entry.isDirectory()) output.push(...await walk(fullPath))
    else if (supportedExtensions.has(path.extname(entry.name))) output.push(fullPath)
  }
  return output.sort((a, b) => a.localeCompare(b, 'en'))
}

function lineNumber(source, offset) {
  return source.slice(0, offset).split('\n').length
}

function normalizeText(text) {
  return text.replace(/\s+/g, ' ').trim()
}

function containsHan(text) {
  return /[\u3400-\u9fff]/u.test(text)
}

function isVisibleText(text, kind) {
  const withoutBindings = normalizeText(text.replace(/\{\{[\s\S]*?\}\}/g, ''))
  if (!withoutBindings) return false
  if (containsHan(withoutBindings)) return true
  if (kind === 'script-string') return false
  if (/^(true|false|null|undefined)$/i.test(withoutBindings)) return false
  if (/^(https?:|\/|#|\.|@)/.test(withoutBindings)) return false
  return /[a-zA-Z]{2,}/.test(withoutBindings)
}

function fileKey(relativePath) {
  return relativePath
    .replace(/^src\//, '')
    .replace(/\.(vue|js|ts)$/i, '')
    .replace(/\/index$/i, '')
    .replace(/[^a-zA-Z0-9]+/g, '.')
    .replace(/^\.|\.$/g, '')
    .toLowerCase()
}

function ownerFor(relativePath) {
  if (/views\/admin\//.test(relativePath)) return 'operations'
  if (/Home|AppNavbar|AppFooter/.test(relativePath)) return 'brand'
  if (/DIY|Product3DViewer|Configurator/.test(relativePath)) return 'product'
  if (/Cart|Checkout|Order|Address/.test(relativePath)) return 'commerce'
  if (/Services|Store/.test(relativePath)) return 'service'
  return 'product'
}

function addEntry(entries, counters, source, relativePath, kind, start, end, rawText, quote = '') {
  const text = normalizeText(rawText)
  if (!isVisibleText(text, kind)) return
  counters[kind] = (counters[kind] || 0) + 1
  const id = `${fileKey(relativePath)}.${kind}.${String(counters[kind]).padStart(3, '0')}`
  entries.push({
    id,
    file: relativePath,
    line: lineNumber(source, start),
    kind,
    owner: ownerFor(relativePath),
    sourceText: text,
    replacement: '',
    status: 'needs-review',
    notes: '',
    _start: start,
    _end: end,
    _quote: quote,
  })
}

function collectTemplateText(template, templateOffset, source, relativePath, entries, counters) {
  let inTag = false
  let quote = ''
  let textStart = 0

  const flushText = (end) => {
    if (end <= textStart) return
    const raw = template.slice(textStart, end)
    const leading = raw.search(/\S/)
    if (leading < 0) return
    const trailing = raw.length - raw.trimEnd().length
    const start = templateOffset + textStart + leading
    const finish = templateOffset + textStart + raw.length - trailing
    addEntry(entries, counters, source, relativePath, 'template-text', start, finish, raw.slice(leading, raw.length - trailing))
  }

  for (let index = 0; index < template.length; index += 1) {
    const character = template[index]
    if (!inTag) {
      if (character === '<') {
        flushText(index)
        inTag = true
        quote = ''
        textStart = index + 1
      }
      continue
    }

    if (quote) {
      if (character === quote && template[index - 1] !== '\\') quote = ''
      continue
    }
    if (character === '"' || character === "'") {
      quote = character
      continue
    }
    if (character === '>') {
      inTag = false
      textStart = index + 1
    }
  }

  if (!inTag) flushText(template.length)
}

function collectVue(source, relativePath) {
  const entries = []
  const counters = {}
  const templateMatch = /<template(?:\s[^>]*)?>([\s\S]*?)<\/template>/i.exec(source)

  if (templateMatch) {
    const template = templateMatch[1]
    const templateOffset = templateMatch.index + templateMatch[0].indexOf(template)
    collectTemplateText(template, templateOffset, source, relativePath, entries, counters)

    const attributePattern = new RegExp(`(?<![:@\\w-])(${visibleAttributes.join('|')})\\s*=\\s*(["'])([\\s\\S]*?)\\2`, 'gi')
    let match
    while ((match = attributePattern.exec(template))) {
      const value = match[3]
      const valueOffset = match[0].indexOf(value)
      const start = templateOffset + match.index + valueOffset
      addEntry(entries, counters, source, relativePath, 'attribute', start, start + value.length, value, match[2])
    }
  }

  const scriptPattern = /<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi
  let scriptMatch
  while ((scriptMatch = scriptPattern.exec(source))) {
    const script = scriptMatch[1]
    const scriptOffset = scriptMatch.index + scriptMatch[0].indexOf(script)
    collectScriptStrings(source, script, scriptOffset, relativePath, entries, counters)
  }

  return entries
}

function collectScriptStrings(fullSource, script, offset, relativePath, entries = [], counters = {}) {
  const stringPattern = /(['"`])((?:\\.|(?!\1)[^\\\r\n])*)\1/g
  let match
  while ((match = stringPattern.exec(script))) {
    if (!containsHan(match[2])) continue
    const start = offset + match.index + 1
    addEntry(entries, counters, fullSource, relativePath, 'script-string', start, start + match[2].length, match[2], match[1])
  }
  return entries
}

async function collectInventory() {
  const entries = []
  for (const filePath of await walk(sourceDir)) {
    const source = await readFile(filePath, 'utf8')
    const relativePath = path.relative(rootDir, filePath).replaceAll('\\', '/')
    const fileEntries = path.extname(filePath) === '.vue'
      ? collectVue(source, relativePath)
      : collectScriptStrings(source, source, 0, relativePath)
    entries.push(...fileEntries)
  }
  return entries
}

function publicEntry(entry) {
  const { _start, _end, _quote, ...output } = entry
  return output
}

function csvCell(value) {
  return `"${String(value ?? '').replaceAll('"', '""')}"`
}

function toCsv(entries) {
  const columns = ['id', 'file', 'line', 'kind', 'owner', 'sourceText', 'replacement', 'status', 'notes']
  return `\uFEFF${columns.join(',')}\n${entries.map(entry => columns.map(column => csvCell(entry[column])).join(',')).join('\n')}\n`
}

function inventoryDocument(entries) {
  return {
    schemaVersion: 1,
    generatedBy: 'ecommerce/frontend/scripts/ui-copy.mjs',
    entryCount: entries.length,
    entries: entries.map(publicEntry),
  }
}

async function extract() {
  const entries = await collectInventory()
  await writeFile(inventoryJsonPath, `${JSON.stringify(inventoryDocument(entries), null, 2)}\n`, 'utf8')
  await writeFile(inventoryCsvPath, toCsv(entries), 'utf8')
  if (!existsSync(overridesPath)) {
    await writeFile(overridesPath, `${JSON.stringify({
      schemaVersion: 1,
      instructions: '把需要修改的条目写入 replacements；from 必须等于清单中的 sourceText，to 为新文案。',
      replacements: {},
    }, null, 2)}\n`, 'utf8')
  }
  const fileCount = new Set(entries.map(entry => entry.file)).size
  console.log(`Extracted ${entries.length} UI copy entries from ${fileCount} source files.`)
}

async function check() {
  const current = inventoryDocument(await collectInventory())
  const saved = JSON.parse(await readFile(inventoryJsonPath, 'utf8'))
  if (JSON.stringify(saved) !== JSON.stringify(current)) {
    console.error('UI copy inventory is stale. Run npm run copy:extract.')
    process.exitCode = 1
    return
  }
  console.log(`UI copy inventory is current (${current.entryCount} entries).`)
}

function escapedReplacement(entry, value) {
  if (entry.kind === 'attribute') {
    return entry._quote === '"' ? value.replaceAll('"', '&quot;') : value.replaceAll("'", '&#39;')
  }
  if (entry.kind === 'script-string') {
    let result = value.replaceAll('\\', '\\\\').replaceAll('\r', '\\r').replaceAll('\n', '\\n')
    if (entry._quote === '`') result = result.replaceAll('`', '\\`').replaceAll('${', '\\${')
    else result = result.replaceAll(entry._quote, `\\${entry._quote}`)
    return result
  }
  return value
}

async function applyOverrides() {
  const overrides = JSON.parse(await readFile(overridesPath, 'utf8'))
  const replacements = overrides.replacements || {}
  const inventory = await collectInventory()
  const byId = new Map(inventory.map(entry => [entry.id, entry]))
  const changesByFile = new Map()

  for (const [id, replacement] of Object.entries(replacements)) {
    const entry = byId.get(id)
    if (!entry) throw new Error(`Unknown copy id: ${id}. Re-extract the inventory and update the override.`)
    if (!replacement || typeof replacement !== 'object') throw new Error(`Invalid replacement for ${id}.`)
    if (replacement.from !== entry.sourceText) {
      throw new Error(`Source text changed for ${id}. Expected "${replacement.from}", found "${entry.sourceText}".`)
    }
    if (typeof replacement.to !== 'string' || replacement.to === replacement.from) continue
    const changes = changesByFile.get(entry.file) || []
    changes.push({ ...entry, to: escapedReplacement(entry, replacement.to) })
    changesByFile.set(entry.file, changes)
  }

  const changeCount = [...changesByFile.values()].reduce((sum, changes) => sum + changes.length, 0)
  if (!changeCount) {
    console.log('No UI copy overrides to apply.')
    return
  }

  for (const [relativePath, changes] of changesByFile) {
    const filePath = path.join(rootDir, relativePath)
    let source = await readFile(filePath, 'utf8')
    for (const change of changes.sort((a, b) => b._start - a._start)) {
      source = `${source.slice(0, change._start)}${change.to}${source.slice(change._end)}`
    }
    if (writeChanges) await writeFile(filePath, source, 'utf8')
  }

  console.log(`${writeChanges ? 'Applied' : 'Dry run:'} ${changeCount} copy changes in ${changesByFile.size} files.`)
  if (!writeChanges) console.log('Run npm run copy:apply -- --write to update source files.')
}

if (!['extract', 'check', 'apply'].includes(action)) {
  throw new Error(`Unknown action "${action}". Use extract, check, or apply.`)
}

if (action === 'extract') await extract()
if (action === 'check') await check()
if (action === 'apply') await applyOverrides()
