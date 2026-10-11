import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { authApi } from '@/api'
import { useUserStore } from '@/store/user'

vi.mock('@/api', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    refreshToken: vi.fn(),
    logout: vi.fn(),
    getProfile: vi.fn(),
    getAddresses: vi.fn(),
    updateProfile: vi.fn(),
    changePassword: vi.fn(),
    createAddress: vi.fn(),
    updateAddress: vi.fn(),
    deleteAddress: vi.fn(),
  },
}))

describe('browser session boundary', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    setActivePinia(createPinia())
    authApi.getProfile.mockResolvedValue({ id: 'user-1', username: 'buyer' })
  })

  it('keeps refresh credentials out of localStorage and JS memory', async () => {
    authApi.login.mockResolvedValue({ access_token: 'access-1', refresh_token: 'refresh-1' })
    const store = useUserStore()

    await store.login({ username: 'buyer', password: 'TestPass1' })

    expect(store.token).toBe('access-1')
    expect(store.refreshToken).toBe('')
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('refreshToken')).toBeNull()
  })

  it('refreshes through the cookie-only request', async () => {
    authApi.refreshToken.mockResolvedValue({ access_token: 'access-2', refresh_token: 'refresh-2' })
    const store = useUserStore()

    await store.refreshAccessToken()

    expect(authApi.refreshToken).toHaveBeenCalledWith()
    expect(store.token).toBe('access-2')
    expect(store.refreshToken).toBe('')
  })
})
