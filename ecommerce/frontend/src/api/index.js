import axios from 'axios'
import { useUserStore } from '@/store/user'
import router from '@/router'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

function redirectToLoginForProtectedRoute() {
  const currentRoute = router.currentRoute.value
  if (currentRoute.meta.requiresAuth || currentRoute.meta.requiresAdmin) {
    router.push({ name: 'Login', query: { redirect: currentRoute.fullPath } })
  }
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    const isRefreshRequest = originalRequest?.url?.includes('/auth/refresh')

    // 刷新请求自身的 401 必须直接返回，否则旧 token 会触发无限刷新循环。
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isRefreshRequest) {
      originalRequest._retry = true

      const userStore = useUserStore()

      // 尝试刷新 token
      if (userStore.refreshToken) {
        try {
          await userStore.refreshAccessToken()
          // 重新发送原请求
          originalRequest.headers.Authorization = `Bearer ${userStore.token}`
          return api(originalRequest)
        } catch (refreshError) {
          // 刷新失败：保留游客购物车，只有受保护页面才跳转登录。
          userStore.clearSession()
          redirectToLoginForProtectedRoute()
          return Promise.reject(refreshError)
        }
      } else {
        // 没有 refresh token：清理会话，但不要打断公开页面。
        userStore.clearSession()
        redirectToLoginForProtectedRoute()
      }
    }

    // 返回错误信息（保留结构化错误数据）
    const detail = error.response?.data?.detail
    const message = Array.isArray(detail)
      ? detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join('; ')
      : (detail || error.message || '请求失败')
    error.displayMessage = message
    return Promise.reject(error)
  }
)

export default api

// ============ 认证 API ============

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  // Refresh uses a bare client so its own 401 can never re-enter this interceptor.
  refreshToken: (data) => axios.post('/api/auth/refresh', data).then(response => response.data),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/me', data),
  changePassword: (data) => api.post('/auth/change-password', data),
  getAddresses: () => api.get('/auth/addresses'),
  createAddress: (data) => api.post('/auth/addresses', data),
  updateAddress: (id, data) => api.put(`/auth/addresses/${id}`, data),
  deleteAddress: (id) => api.delete(`/auth/addresses/${id}`)
}

// ============ 商品 API ============

export const productApi = {
  getProducts: (params) => api.get('/products', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
  getProductBySlug: (slug) => api.get(`/products/slug/${slug}`),
  getCategories: () => api.get('/products/categories'),
  getFeaturedProducts: (limit = 10) => api.get('/products/featured/list', { params: { limit } }),
  getHotProducts: (limit = 10) => api.get('/products/hot/list', { params: { limit } })
}

// ============ 行情 API ============

export const marketApi = {
  getPriceHistory: (productId, days = 30) => api.get(`/market/price-history/${productId}`, { params: { days } })
}

// ============ 购物车 API ============

export const cartApi = {
  getCart: (sessionId) => api.get('/cart', { params: { session_id: sessionId } }),
  addToCart: (data, sessionId) => api.post('/cart/items', data, { params: { session_id: sessionId } }),
  updateCartItem: (id, data, sessionId) => api.put(`/cart/items/${id}`, data, { params: { session_id: sessionId } }),
  removeCartItem: (id, sessionId) => api.delete(`/cart/items/${id}`, { params: { session_id: sessionId } }),
  clearCart: (sessionId) => api.delete('/cart/clear', { params: { session_id: sessionId } }),
  mergeCart: (sessionId) => api.post('/cart/merge', { session_id: sessionId })
}

// ============ 订单 API ============

export const orderApi = {
  createOrder: (data) => api.post('/orders', data),
  getOrders: (params) => api.get('/orders', { params }),
  getOrder: (id) => api.get(`/orders/${id}`),
  cancelOrder: (id, data) => api.post(`/orders/${id}/cancel`, data)
}

// ============ 支付 API ============

export const paymentApi = {
  createPayment: (orderId, data) => api.post(`/payment/create/${orderId}`, data),
  sandboxMockPay: (orderId) => api.post(`/payment/sandbox/mock-pay/${orderId}`),
  getPaymentStatus: (orderNo) => api.get(`/payment/status/${orderNo}`)
}

// ============ 管理员 API ============

export const adminApi = {
  // 仪表盘
  getDashboard: () => api.get('/admin/dashboard'),

  // 用户管理
  getUsers: (params) => api.get('/admin/users', { params }),
  getUserDetail: (id) => api.get(`/admin/users/${id}`),
  updateUserStatus: (id, isActive) => api.put(`/admin/users/${id}/status`, { is_active: isActive }),

  // 订单管理
  getOrders: (params) => api.get('/admin/orders', { params }),
  getOrderDetail: (id) => api.get(`/admin/orders/${id}`),
  shipOrder: (id, data) => api.post(`/admin/orders/${id}/ship`, data),

  // 商品管理
  getProducts: (params) => api.get('/admin/products', { params }),
  toggleProductStatus: (id, isActive) => api.put(`/admin/products/${id}/status`, { is_active: isActive }),
  createProduct: (data) => api.post('/products', data),
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  uploadAsset: (bucket, file, modelContract = '', productId = '') => {
    const data = new FormData()
    if (bucket) data.append('bucket', bucket)
    if (modelContract) data.append('model_contract', modelContract)
    if (productId) data.append('product_id', productId)
    data.append('file', file)
    return api.post('/admin/assets', data, { headers: { 'Content-Type': 'multipart/form-data' } })
  },

  // 分类管理
  getCategories: () => api.get('/admin/categories'),
  createCategory: (data) => api.post('/products/categories', data),
}
