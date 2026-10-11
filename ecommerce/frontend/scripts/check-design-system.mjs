import { readFile, readdir } from 'node:fs/promises'
import { resolve, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const rootDir = fileURLToPath(new URL('..', import.meta.url))
const componentDir = resolve(rootDir, 'src/design-system/components')
const sourceDir = resolve(rootDir, 'src')

async function collectSourceFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true })
  const files = []
  for (const entry of entries) {
    const file = resolve(directory, entry.name)
    if (entry.isDirectory()) {
      files.push(...await collectSourceFiles(file))
    } else if (entry.isFile() && /\.(vue|js|ts|css)$/.test(entry.name)) {
      files.push(file)
    }
  }
  return files
}

const componentFiles = (await collectSourceFiles(componentDir))
  .filter(file => file.endsWith('.vue'))
  .concat([
  resolve(rootDir, 'src/components/ProductConfiguratorPanel.vue'),
  resolve(rootDir, 'src/components/ServiceCookiePreferences.vue'),
  resolve(rootDir, 'src/components/ServicePolicyPanel.vue'),
  ])
const themeFiles = [
  resolve(rootDir, 'src/views/Home.vue'),
  resolve(rootDir, 'src/views/Store.vue'),
  resolve(rootDir, 'src/views/Services.vue'),
]
const sourceFiles = await collectSourceFiles(sourceDir)
const motionSourceFiles = sourceFiles.filter(file => !file.includes(`${resolve(rootDir, 'src/design-system/tokens')}`))

const violations = []
for (const file of componentFiles) {
  const source = await readFile(file, 'utf8')
  const patterns = [
    { expression: /#[0-9a-f]{3,8}\b|rgba?\(\s*(?!var\()/gi, message: '组件层禁止直接写颜色字面量；请使用 semantic Token' },
    { expression: /\btransition\s*:\s*all\b|\btransition-all\b/gi, message: '禁止 transition-all；请明确列出可动画属性' },
    { expression: /\b(?:animation|transition)\s*:[^;]*(?:\d+(?:\.\d+)?(?:ms|s))\b/gi, message: '组件动效时长必须来自 motion Token' },
  ]
  for (const { expression, message } of patterns) {
    for (const match of source.matchAll(expression)) {
      const line = source.slice(0, match.index).split('\n').length
      violations.push(`${relative(rootDir, file)}:${line} - ${message}`)
    }
  }
}

for (const file of sourceFiles) {
  const source = await readFile(file, 'utf8')
  const expression = /\btransition\s*:\s*all\b|\btransition-all\b/gi
  for (const match of source.matchAll(expression)) {
    const line = source.slice(0, match.index).split('\n').length
    violations.push(`${relative(rootDir, file)}:${line} - 禁止 transition-all；请明确列出可动画属性`)
  }
}

for (const file of motionSourceFiles) {
  const source = await readFile(file, 'utf8')
  const expressions = [
    /\b(?:animation|transition)(?:-duration)?\s*:[^;]*(?:\d+(?:\.\d+)?(?:ms|s))\b/gi,
    /\bduration-(?:75|100|150|200|300|500|700|1000)\b/gi,
  ]
  for (const expression of expressions) {
    for (const match of source.matchAll(expression)) {
      if (match[0].includes('0.01ms')) continue
      const line = source.slice(0, match.index).split('\n').length
      violations.push(`${relative(rootDir, file)}:${line} - 页面动效时长必须来自 motion Token`)
    }
  }
}

for (const file of themeFiles) {
  const source = await readFile(file, 'utf8')
  const expression = /#[0-9a-f]{3,8}\b|rgba?\(\s*(?!var\()/gi
  for (const match of source.matchAll(expression)) {
    const line = source.slice(0, match.index).split('\n').length
    violations.push(`${relative(rootDir, file)}:${line} - 页面主题必须消费 color.theme 或 semantic Token`)
  }
}

if (violations.length) {
  console.error('Design-system lint failed:')
  console.error(violations.join('\n'))
  process.exitCode = 1
} else {
    console.log(`Design-system lint passed (${componentFiles.length} component files; motion/transition scan ${motionSourceFiles.length} source files; theme scan ${themeFiles.length} pages).`)
}
