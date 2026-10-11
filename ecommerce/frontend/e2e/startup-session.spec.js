import { expect, test } from '@playwright/test'

test('public home renders during refresh, then restores an admin and their cart identity', async ({ page }) => {
  let releaseRefresh
  const refreshGate = new Promise(resolve => { releaseRefresh = resolve })
  const cartRequests = []

  await page.route('https://fonts.googleapis.com/**', route => route.fulfill({
    status: 200, contentType: 'text/css', body: '',
  }))
  await page.route(url => url.pathname.startsWith('/api/'), async route => {
    const request = route.request()
    const url = new URL(request.url())
    if (url.pathname === '/api/auth/refresh') {
      await refreshGate
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ access_token: 'restored-admin' }) })
    }
    if (url.pathname === '/api/auth/me') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ id: 'admin-1', username: 'admin', is_admin: true }) })
    }
    if (url.pathname === '/api/cart') {
      cartRequests.push({ url: request.url(), authorization: request.headers().authorization })
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ items: [] }) })
    }
    return route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })

  try {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10_000 })
    await expect(page.locator('[data-qa="home-hero"]')).toBeVisible({ timeout: 5_000 })
    expect(cartRequests).toEqual([])
  } finally {
    releaseRefresh()
  }

  await expect(page).toHaveURL(/\/admin\/dashboard$/, { timeout: 10_000 })
  await expect.poll(() => cartRequests.length).toBe(1)
  expect(new URL(cartRequests[0].url).searchParams.has('session_id')).toBe(false)
  expect(cartRequests[0].authorization).toBe('Bearer restored-admin')
})
