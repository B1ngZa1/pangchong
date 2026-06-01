import type { AxiosInstance } from 'axios'

type ApiMethod = (...args: any[]) => Promise<any>
type ApiGroup = Record<string, ApiMethod>

declare const api: AxiosInstance

export default api
export const authApi: ApiGroup
export const productApi: ApiGroup
export const marketApi: ApiGroup
export const cartApi: ApiGroup
export const orderApi: ApiGroup
export const paymentApi: ApiGroup
export const adminApi: ApiGroup
