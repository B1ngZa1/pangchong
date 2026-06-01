import { afterEach, describe, expect, it, vi } from 'vitest'
import { resolveHashScroll } from '@/router'

describe('router hash scrolling', () => {
  afterEach(() => {
    document.body.innerHTML = ''
    vi.useRealTimers()
  })

  it('resolves an existing hash target immediately', () => {
    document.body.innerHTML = '<section id="faq"></section>'

    const target = document.getElementById('faq')

    expect(resolveHashScroll('#faq')).toEqual({
      el: target,
      top: 92,
      behavior: 'smooth',
    })
  })

  it('waits for async route content before resolving the hash target', async () => {
    vi.useFakeTimers()

    const scrollPosition = resolveHashScroll('#tech-support', 100)
    await vi.advanceTimersByTimeAsync(1)

    document.body.innerHTML = '<section id="tech-support"></section>'
    const target = document.getElementById('tech-support')
    await vi.advanceTimersByTimeAsync(16)

    await expect(scrollPosition).resolves.toEqual({
      el: target,
      top: 92,
      behavior: 'smooth',
    })
  })

  it('falls back to the page top when a hash target is missing', async () => {
    vi.useFakeTimers()

    const scrollPosition = resolveHashScroll('#missing-section', 20)
    await vi.advanceTimersByTimeAsync(32)

    await expect(scrollPosition).resolves.toEqual({ top: 0 })
  })
})
