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
  const token = ref<string>(localStorage.getItem('token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refreshToken') || '')
  const user = ref<UserProfile | null>(null)
  const addresses = ref<Address[]>([])

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)

  function setTokens(accessToken: string, refresh: string) {
    token.value = accessToken
    refreshToken.value = refresh
    localStorage.setItem('token', accessToken)
    localStorage.setItem('refreshToken', refresh)
  }

  function clearTokens() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    addresses.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  function clearSession() {
    clearTokens()
  }

  async function login(credentials: { username: string; password: string }) {
    const data = await authApi.login(credentials)
    setTokens(data.access_token, data.refresh_token)
    await fetchProfile()
    return data
  }

  async function register(userData: Record<string, unknown>) {
    const data = await authApi.register(userData)
    setTokens(data.access_token, data.refresh_token)
    await fetchProfile()
    return data
  }

  function logout() {
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
    } catch {
      clearTokens()
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) throw new Error('没有 refresh token')
    try {
      const data = await authApi.refreshToken({ refresh_token: refreshToken.value })
      setTokens(data.access_token, data.refresh_token)
      return data
    } catch (error) {
      clearTokens()
      throw error
    }
  }

  async function updateProfile(userData: Record<string, unknown>) {
    const data = await authApi.updateProfile(userData)
    user.value = data as UserProfile
    return data
  }

  async function fetchAddresses() {
    const data = await authApi.getAddresses()
    addresses.value = data as Address[]
    return data
  }

  async function createAddress(addressData: Record<string, unknown>) {
    const data = await authApi.createAddress(addressData)
    addresses.value.push(data as Address)
    return data
  }

  async function updateAddress(id: string, addressData: Record<string, unknown>) {
    const data = await authApi.updateAddress(id, addressData)
    const index = addresses.value.findIndex(a => a.id === id)
    if (index !== -1) addresses.value[index] = data as Address
    return data
  }

  async function deleteAddress(id: string) {
    await authApi.deleteAddress(id)
    addresses.value = addresses.value.filter(a => a.id !== id)
  }

  if (token.value) {
    fetchProfile()
  }

  return {
    token, refreshToken, user, addresses,
    isLoggedIn, isAdmin,
    login, register, logout, clearSession, fetchProfile, refreshAccessToken,
    updateProfile, fetchAddresses, createAddress, updateAddress, deleteAddress,
  }
})
