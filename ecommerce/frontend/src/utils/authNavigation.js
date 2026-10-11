export function resolveAuthRedirect(value) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || value.includes('\\')) return '/'
  if (/^\/(login|register)(?:[/?#]|$)/.test(value)) return '/'
  return value
}

export function authErrorMessage(error, fallback) {
  if (typeof error?.displayMessage === 'string') return error.displayMessage
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map(item => item.msg).filter(Boolean).join('；') || fallback
  return fallback
}
