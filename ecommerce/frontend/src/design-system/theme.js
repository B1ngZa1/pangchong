const THEME_KEY = 'pangchong-design-theme'

export const DESIGN_THEMES = ['default', 'high-contrast']

export function getStoredDesignTheme() {
  if (typeof window === 'undefined') return 'default'
  const stored = window.localStorage.getItem(THEME_KEY)
  return DESIGN_THEMES.includes(stored) ? stored : 'default'
}

export function applyDesignTheme(theme = 'default') {
  const nextTheme = DESIGN_THEMES.includes(theme) ? theme : 'default'
  if (typeof document !== 'undefined') {
    if (nextTheme === 'default') document.documentElement.removeAttribute('data-theme')
    else document.documentElement.setAttribute('data-theme', nextTheme)
  }
  if (typeof window !== 'undefined') window.localStorage.setItem(THEME_KEY, nextTheme)
  return nextTheme
}

export function toggleDesignTheme(currentTheme = 'default') {
  return applyDesignTheme(currentTheme === 'high-contrast' ? 'default' : 'high-contrast')
}
