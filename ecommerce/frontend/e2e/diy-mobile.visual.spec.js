import { expect, test } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'

const EVIDENCE_DIR = path.resolve('output/playwright/diy-resilience-2026-09-13')

const CATEGORY_IDS = {
  cpu: 'd1000000-0000-0000-0000-000000000001',
  gpu: 'd1000000-0000-0000-0000-000000000002',
  motherboard: 'd1000000-0000-0000-0000-000000000003',
  ram: 'd1000000-0000-0000-0000-000000000004',
  ssd: 'd1000000-0000-0000-0000-000000000005',
  cooler: 'd1000000-0000-0000-0000-000000000006',
  psu: 'd1000000-0000-0000-0000-000000000007',
  case: 'd1000000-0000-0000-0000-000000000008',
}

const fixtureProducts = {
  [CATEGORY_IDS.cpu]: [{
    id: 'e2e-cpu-9600x',
    name: 'AMD Ryzen 5 9600X 处理器',
    brand: 'AMD',
    model: 'Ryzen 5 9600X',
    description: '移动视觉回归的稳定目录夹具。',
    price: 1499,
    original_price: 1799,
    image_url: '/assets/pangchong-product-fallback.png',
    stock: 99,
    specs: { socket: 'AM5', tdp: '65W', cores: '6核12线程' },
  }],
  [CATEGORY_IDS.gpu]: [],
  [CATEGORY_IDS.motherboard]: [],
  [CATEGORY_IDS.ram]: [],
  [CATEGORY_IDS.ssd]: [],
  [CATEGORY_IDS.cooler]: [],
  [CATEGORY_IDS.psu]: [],
  [CATEGORY_IDS.case]: [],
}

async function installApiFixtures(page) {
  const unmockedRequests = []

  // Keep this visual suite fully local. Register the catch-all first because
  // Playwright invokes the most recently registered matching route first.
  await page.route('**://*/api/**', route => {
    unmockedRequests.push(`${route.request().method()} ${route.request().url()}`)
    return route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Unexpected API request in DIY visual fixture' }),
    })
  })

  // Router startup probes the HttpOnly refresh cookie before entering /diy.
  // A successful anonymous response prevents that probe from becoming a real
  // 401/500 resource request while preserving the unauthenticated UI state.
  await page.route('**/api/auth/refresh', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ access_token: '', refresh_token: '' }),
  }))

  await page.route('**/api/cart**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ items: [] }),
  }))

  await page.route('**/api/products**', async route => {
    const url = new URL(route.request().url())
    const categoryId = url.searchParams.get('category_id')
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: fixtureProducts[categoryId] || [] }),
    })
  })

  await page.route('**/api/market/price-history/**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ points: [], source: 'unavailable' }),
  }))

  return { unmockedRequests }
}

async function installWebglMode(page, mode) {
  await page.addInitScript(({ initialMode }) => {
    window.__PANGCHONG_E2E_WEBGL__ = initialMode

    if (initialMode !== 'unavailable') return

    document.addEventListener('click', (event) => {
      if (event.target instanceof Element && event.target.closest('[data-testid="diy-viewer-retry"]')) {
        window.__PANGCHONG_E2E_WEBGL__ = 'available'
      }
    }, true)
  }, { initialMode: mode })
}

function monitorPageErrors(page) {
  const errors = []
  page.on('console', message => {
    if (message.type() === 'error') errors.push(`console.error: ${message.text()}`)
  })
  page.on('pageerror', error => errors.push(`pageerror: ${error.message}`))
  return errors
}

async function openDiy(page, { webgl = 'native' } = {}) {
  const apiFixtures = await installApiFixtures(page)
  await installWebglMode(page, webgl)
  await page.goto('/diy', { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle')
  await expect(page.getByRole('heading', { name: 'DIY 装机配置器' })).toBeVisible()
  await waitForDocumentToSettle(page)
  return apiFixtures
}

async function waitForDocumentToSettle(page) {
  // The app uses an out-in route transition. Visibility alone does not prove
  // that the entering page has reached its final opacity or final layout.
  await expect(page.locator('.page-enter-active')).toHaveCount(0)
  await page.evaluate(async () => {
    await document.fonts?.ready
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
  })
}

async function waitForViewerToSettle(page) {
  const viewer = page.getByTestId('diy-3d-viewer')
  const canvas = viewer.locator('canvas')
  await expect(canvas).toBeVisible()
  await expect.poll(() => canvas.evaluate(element => {
    const { width, height } = element.getBoundingClientRect()
    return Math.round(width * height)
  })).toBeGreaterThan(0)
  await page.evaluate(async () => {
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
  })
}

async function captureVisual(page, testInfo, name) {
  await waitForDocumentToSettle(page)
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true })
  const evidencePath = path.join(EVIDENCE_DIR, `${testInfo.project.name}-${name}.png`)
  await page.screenshot({ path: evidencePath, fullPage: false, animations: 'disabled' })
  await expect(page).toHaveScreenshot(`${name}.png`)
}

test.describe('DIY mobile resilience visual regression', () => {
  test('keeps normal page scrolling usable at the mobile breakpoint', async ({ page }, testInfo) => {
    const errors = monitorPageErrors(page)
    const apiFixtures = await openDiy(page)
    await waitForViewerToSettle(page)

    const autoRotate = page.getByRole('switch', { name: '切换 3D 自动旋转' })
    await expect(autoRotate).toBeVisible()
    await autoRotate.click()
    await expect(autoRotate).not.toBeChecked()

    await page.mouse.wheel(0, 720)
    await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(0)
    const scrollMetrics = await page.evaluate(() => ({
      scrollY: window.scrollY,
      scrollHeight: document.documentElement.scrollHeight,
      viewportHeight: window.innerHeight,
    }))
    expect(scrollMetrics.scrollY).toBeGreaterThan(0)
    expect(scrollMetrics.scrollHeight).toBeGreaterThan(scrollMetrics.viewportHeight)

    await captureVisual(page, testInfo, 'normal-scroll')
    expect(apiFixtures.unmockedRequests).toEqual([])
    expect(errors).toEqual([])
  })

  test('falls back to the configuration list when WebGL is unavailable', async ({ page }, testInfo) => {
    const errors = monitorPageErrors(page)
    const apiFixtures = await openDiy(page, { webgl: 'unavailable' })

    await expect(page.getByTestId('diy-list-mode')).toBeVisible()
    await expect(page.getByTestId('diy-viewer-fallback')).toContainText('当前设备无法使用 3D')
    await expect(page.getByTestId('diy-list-compatibility')).toContainText('待验证')
    await expect(page.getByTestId('diy-list-total')).toHaveText('¥0')
    await expect(page.getByTestId('diy-list-add-cart')).toBeDisabled()
    await expect(page.getByTestId('diy-list-checkout')).toBeDisabled()

    await captureVisual(page, testInfo, 'webgl-unavailable-list')
    expect(apiFixtures.unmockedRequests).toEqual([])
    expect(errors).toEqual([])
  })

  test('retries from the list fallback back into the 3D workbench', async ({ page }, testInfo) => {
    const errors = monitorPageErrors(page)
    const apiFixtures = await openDiy(page, { webgl: 'unavailable' })

    await page.getByTestId('diy-viewer-retry').click()
    const viewer = page.getByTestId('diy-3d-viewer')
    await expect(viewer).toBeVisible()
    await expect(viewer).toHaveAttribute('data-motion-preference', 'no-preference')

    const autoRotate = page.getByRole('switch', { name: '切换 3D 自动旋转' })
    await expect(autoRotate).toBeVisible()
    await autoRotate.click()
    await expect(autoRotate).not.toBeChecked()
    await waitForViewerToSettle(page)
    await expect(page.getByTestId('diy-list-mode')).toBeHidden()
    await viewer.scrollIntoViewIfNeeded()

    await captureVisual(page, testInfo, 'retry-back-to-3d')
    expect(apiFixtures.unmockedRequests).toEqual([])
    expect(errors).toEqual([])
  })

  test('honors prefers-reduced-motion in the 3D workbench', async ({ page }, testInfo) => {
    const errors = monitorPageErrors(page)
    await page.emulateMedia({ reducedMotion: 'reduce' })
    const apiFixtures = await openDiy(page)

    const viewer = page.getByTestId('diy-3d-viewer')
    await expect(viewer).toBeVisible()
    await expect(viewer).toHaveAttribute('data-motion-preference', 'reduce')
    await expect(page.getByText('系统减少动态效果时会自动停用。')).toBeVisible()
    await waitForViewerToSettle(page)

    await captureVisual(page, testInfo, 'prefers-reduced-motion')
    expect(apiFixtures.unmockedRequests).toEqual([])
    expect(errors).toEqual([])
  })
})
