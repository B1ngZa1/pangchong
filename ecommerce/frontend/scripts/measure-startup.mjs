import { chromium } from '@playwright/test'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import fs from 'node:fs'
import path from 'node:path'

// Measure the Vite production build. With no --url, this script starts and stops
// its own preview server. API and font responses are fixed so a backend outage or
// Google Fonts availability cannot skew comparisons.
const args = Object.fromEntries(process.argv.slice(2).map((arg) => {
  const [key, ...value] = arg.replace(/^--/, '').split('=')
  return [key, value.join('=')]
}))
const baseURL = args.url || 'http://127.0.0.1:4173'
const output = args.out || path.resolve('../../output/mobile-startup-2026-09-13/after-normal.json')
const runs = Number(args.runs || 1)
const authDelayMs = Number(args['auth-delay-ms'] || 0)
const fontDelayMs = Number(args['font-delay-ms'] || 0)
const viewports = [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile-360', width: 360, height: 844 },
  { name: 'mobile-390', width: 390, height: 844 },
  { name: 'mobile-430', width: 430, height: 932 },
].filter(viewport => !args.only || viewport.name === args.only)
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

if (!Number.isInteger(runs) || runs < 1 || runs > 10 || authDelayMs < 0 || fontDelayMs < 0) {
  throw new Error('Use --runs=1..10 and nonnegative --auth-delay-ms / --font-delay-ms')
}

async function serverIsReachable(url) {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(400) })
    return response.status < 500
  } catch {
    return false
  }
}

async function startPreviewServer(url) {
  if (await serverIsReachable(url)) return null

  const target = new URL(url)
  if (target.protocol !== 'http:' || !['127.0.0.1', 'localhost'].includes(target.hostname)) {
    throw new Error('Automatic preview only supports a local HTTP URL. Pass --url for another server.')
  }

  const viteBin = path.resolve('node_modules/vite/bin/vite.js')
  const previewProcess = spawn(process.execPath, [viteBin, 'preview', '--host', target.hostname, '--port', target.port || '4173', '--strictPort'], {
    cwd: process.cwd(),
    stdio: ['ignore', 'ignore', 'pipe'],
  })
  let errorOutput = ''
  previewProcess.stderr.on('data', chunk => { errorOutput += String(chunk) })

  for (let attempt = 0; attempt < 50; attempt += 1) {
    if (previewProcess.exitCode !== null) {
      throw new Error(`Vite preview exited before it was ready. ${errorOutput.trim()}`)
    }
    if (await serverIsReachable(url)) return previewProcess
    await delay(100)
  }

  previewProcess.kill()
  throw new Error(`Vite preview did not become ready within 5 seconds. ${errorOutput.trim()}`)
}

async function stopPreviewServer(previewProcess) {
  if (!previewProcess || previewProcess.exitCode !== null) return
  previewProcess.kill()
  await Promise.race([once(previewProcess, 'exit'), delay(3000)])
}

const rows = []
let previewProcess
let browser
try {
  previewProcess = args.url ? null : await startPreviewServer(baseURL)
  browser = await chromium.launch({ headless: true })
  for (const viewport of viewports) {
    for (let run = 1; run <= runs; run += 1) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        deviceScaleFactor: 1,
        locale: 'zh-CN',
        colorScheme: 'dark',
      })
      const page = await context.newPage()
      const errors = []
      page.on('pageerror', error => errors.push(error.message))
      await page.route('https://fonts.googleapis.com/**', async route => {
        await delay(fontDelayMs)
        await route.fulfill({ status: 200, contentType: 'text/css', body: '' })
      })
      await page.route(url => url.pathname.startsWith('/api/'), async route => {
        const url = new URL(route.request().url())
        if (url.pathname === '/api/auth/refresh') await delay(authDelayMs)
        const body = url.pathname === '/api/cart' ? { items: [] }
          : url.pathname === '/api/auth/refresh' ? { access_token: '' }
          : []
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
      })
      const response = await page.goto(baseURL, { waitUntil: 'domcontentloaded', timeout: 30000 })
      await page.waitForFunction(() => performance.getEntriesByType('paint').some(entry => entry.name === 'first-contentful-paint'), null, { timeout: 30000 })
      await page.locator('[data-qa="home-hero"]').waitFor({ timeout: 30000 })
      const heroVisibleMs = await page.evaluate(() => Math.round(performance.now()))
      // Wait for the delayed fixture to finish so resource counts use the same cutoff.
      await page.waitForLoadState('networkidle', { timeout: 30000 })
      const metrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0]
        const resources = performance.getEntriesByType('resource')
        return {
          responseStart: Math.round(navigation.responseStart),
          domContentLoaded: Math.round(navigation.domContentLoadedEventEnd),
          load: Math.round(navigation.loadEventEnd),
          firstContentfulPaint: Math.round(performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint').startTime),
          resourceCount: resources.length,
          transferBytes: resources.reduce((total, item) => total + item.transferSize, 0),
          resources: resources.map(item => ({
            url: item.name.replace(location.origin, ''),
            startMs: Math.round(item.startTime),
            durationMs: Math.round(item.duration),
            transferBytes: item.transferSize,
          })),
        }
      })
      rows.push({ viewport: viewport.name, width: viewport.width, run, status: response.status(), heroVisibleMs, ...metrics, errors })
      console.log(`${viewport.name} #${run}: FCP ${metrics.firstContentfulPaint} ms, hero ${heroVisibleMs} ms, ${metrics.resourceCount} resources`)
      await context.close()
    }
  }
} finally {
  await browser?.close()
  await stopPreviewServer(previewProcess)
}

fs.mkdirSync(path.dirname(output), { recursive: true })
fs.writeFileSync(output, `${JSON.stringify({
  generatedAt: new Date().toISOString(),
  environment: { baseURL, route: '/', browser: 'Playwright Chromium', build: 'Vite production preview', cache: 'new browser context per run', api: 'deterministic local fixtures', font: 'deterministic empty CSS', authDelayMs, fontDelayMs, runs },
  rows,
}, null, 2)}\n`)
