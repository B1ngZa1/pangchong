import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import { useCartStore } from './cart'

export interface UserProfile {
  id: string
  username: string
  email: string
  phone?: string
  nickname?: string
  avatar_url?: string
  is_active: boolean
  is_admin: boolean
  created_at: string
}

export interface Address {
  id: string
  recipient_name: string
  phone: string
  province: string
  city: string
  district: string
  address: string
  postal_code?: string
  is_default: boolean
  created_at: string
}

export const useUserStore = defineStore('user', () => {
  // Access tokens are intentionally memory-only.  The long-lived refresh
  // token is issued as an HttpOnly cookie by the API and is never readable by
  // application JavaScript or persisted in localStorage.
  const token = ref<string>('')
  const refreshToken = ref<string>('')
  const user = ref<UserProfile | null>(null)
  const addresses = ref<Address[]>([])
  const sessionReady = ref(false)
  let hydrationPromise: Promise<void> | null = null

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)

  function setTokens(accessToken: string, _refresh?: string) {
    token.value = accessToken
    // Never copy the refresh credential into JavaScript memory.  The backend
    // rotates it through the HttpOnly cookie; this ref remains empty for API
    // shape compatibility with older callers.
    refreshToken.value = ''
  }

  function clearTokens() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    addresses.value = []
    if (typeof window !== 'undefined') {
      // Remove credentials written by versions before the cookie migration.
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    }
  }

  function clearSession() {
    clearTokens()
  }

  async function login(credentials: { username: string; password: string }) {
    const data = await authApi.login(credentials)
    setTokens(data.access_token, data.refresh_token)
    sessionReady.value = true
    await fetchProfile()
    return data
  }

  async function register(userData: Record<string, unknown>) {
    const data = await authApi.register(userData)
    setTokens(data.access_token, data.refresh_token)
    sessionReady.value = true
    await fetchProfile()
    return data
  }

  function logout() {
    void authApi.logout().catch(() => { /* local logout still succeeds */ })
    clearTokens()
    try {
      const cartStore = useCartStore()
      cartStore.clearOnLogout()
    } catch { /* cart store not initialized yet */ }
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      const data = await authApi.getProfile()
      user.value = data as UserProfile
    } catch (error) {
      clearTokens()
      throw error
    }
  }

  async function refreshAccessToken() {
    try {
      const data = await authApi.refreshToken()
      setTokens(data.access_token, data.refresh_token)
      return data
    } catch (error) {
      clearTokens()
      throw error
    }
  }

  async function hydrateSession() {
    if (sessionReady.value) return
    if (hydrationPromise) return hydrationPromise

    hydrationPromise = (async () => {
      try {
        if (!token.value) {
          await refreshAccessToken()
        }
        await fetchProfile()
      } catch {
        clearTokens()
      } finally {
        sessionReady.value = true
      }
    })()

    try {
      await hydrationPromise
    } finally {
      hydrationPromise = null
    }
  }

  async function updateProfile(userData: Record<string, unknown>) {
    const data = await authApi.updateProfile(userData)
    user.value = data as UserProfile
    return data
  }

  async function fetchAddresses() {
    const data = await authApi.getAddresses()
    // Never let an unexpected empty response corrupt the reactive collection;
    // retaining the last known list keeps checkout renderable while the API
    // contract is being diagnosed.
    if (Array.isArray(data)) addresses.value = data.filter(Boolean) as Address[]
    return data
  }

  async function createAddress(addressData: Record<string, unknown>) {
    const data = await authApi.createAddress(addressData)
    if (data.is_default) addresses.value.forEach(address => { address.is_default = false })
    addresses.value.push(data as Address)
    return data
  }

  async function updateAddress(id: string, addressData: Record<string, unknown>) {
    const data = await authApi.updateAddress(id, addressData)
    if (data.is_default) addresses.value.forEach(address => { address.is_default = false })
    const index = addresses.value.findIndex(a => a.id === id)
    if (index !== -1) addresses.value[index] = data as Address
    return data
  }

  async function deleteAddress(id: string) {
    await authApi.deleteAddress(id)
    addresses.value = addresses.value.filter(a => a.id !== id)
  }

  return {
    token, refreshToken, user, addresses,
    isLoggedIn, isAdmin,
    login, register, logout, clearSession, fetchProfile, refreshAccessToken, hydrateSession,
    updateProfile, fetchAddresses, createAddress, updateAddress, deleteAddress,
  }
})
