<template>
  <div>
    <DsAlert
      v-if="feedback"
      class="mb-4"
      :title="feedback.title"
      :description="feedback.description"
      :tone="feedback.tone"
      :role="feedback.tone === 'danger' ? 'alert' : 'status'"
      dismissible
      @dismiss="feedback = null"
    />

    <!-- 操作栏 -->
    <form class="bg-dark-900 rounded-xl border border-dark-800 p-4 mb-4 grid gap-3 sm:grid-cols-[minmax(0,1fr)_10rem_auto] lg:grid-cols-[minmax(0,1fr)_12rem_auto_auto] items-end" @submit.prevent="searchProducts">
      <DsField v-model="filters.keyword" label="搜索商品" placeholder="商品名称 / 品牌 / 型号" autocomplete="off" />
      <DsField v-model="filters.is_active" as="select" label="上架状态" placeholder="全部状态"
        :options="[{ value: 'true', label: '已上架' }, { value: 'false', label: '已下架' }]" @change="searchProducts" />
      <DsButton variant="secondary" :loading="loading" type="submit"><i class="fas fa-search mr-1" aria-hidden="true"></i>搜索</DsButton>
      <DsButton type="button" @click="openCreate"><i class="fas fa-plus mr-1"></i>添加商品</DsButton>
    </form>

    <!-- 商品表格 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 overflow-hidden">
      <DsAsyncState
        :state="requestState"
        loading-label="正在加载商品列表"
        empty-title="暂无商品数据"
        empty-description="调整搜索条件，或先创建一条商品记录。"
        error-title="商品列表加载失败"
        :error-description="requestError"
        @retry="fetchProducts"
      >
      <DsDataTable v-if="requestState === 'success'" label="后台商品列表">
      <table>
        <thead>
          <tr class="text-dark-500 border-b border-dark-800 bg-dark-950/50">
            <th class="text-left py-3 px-4">商品</th>
            <th class="text-left py-3 px-4">品牌/型号</th>
            <th class="text-right py-3 px-4">售价</th>
            <th class="text-right py-3 px-4">库存</th>
            <th class="text-right py-3 px-4">销量</th>
            <th class="text-center py-3 px-4">状态</th>
            <th class="text-center py-3 px-4">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id"
            class="border-b border-dark-800 last:border-0 hover:bg-dark-800/50 transition-colors">
            <td class="py-3 px-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-dark-800 rounded-lg flex-shrink-0 overflow-hidden">
                  <img v-if="p.image_url" :src="p.image_url" :alt="p.name" loading="lazy" class="w-full h-full object-cover" @error="onThumbError" />
                  <span v-else class="flex items-center justify-center h-full text-dark-600">📦</span>
                </div>
                <span class="truncate max-w-xs font-medium">{{ p.name }}</span>
                <span v-if="p.model_3d_url" class="rounded bg-primary-500/10 px-1.5 py-0.5 text-[10px] text-primary-400">GLB</span>
              </div>
            </td>
            <td class="py-3 px-4 text-dark-400 text-xs">{{ p.brand }} {{ p.model }}</td>
            <td class="py-3 px-4 text-right font-bold">¥{{ Number(p.price).toLocaleString() }}</td>
            <td class="py-3 px-4 text-right">
              <span :class="p.stock <= 5 ? 'text-red-400' : 'text-dark-300'">{{ p.stock }}</span>
            </td>
            <td class="py-3 px-4 text-right text-dark-400">{{ p.sold_count }}</td>
            <td class="py-3 px-4 text-center">
              <button @click="toggleStatus(p)"
                :disabled="statusUpdating.has(p.id)"
                class="text-xs px-2.5 py-1 rounded-full font-medium transition-colors"
                :class="p.is_active ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' : 'bg-dark-700 text-dark-400 hover:bg-dark-600'">
                {{ p.is_active ? '已上架' : '已下架' }}
              </button>
            </td>
            <td class="py-3 px-4 text-center">
              <button @click="openEdit(p)" class="text-primary-500 hover:underline text-xs">编辑</button>
            </td>
          </tr>
        </tbody>
      </table>
      </DsDataTable>
      </DsAsyncState>

      <!-- 分页 -->
      <div v-if="requestState === 'success' && totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-dark-800">
        <span class="text-dark-500 text-xs">共 {{ total }} 条</span>
        <DsPagination v-model:page="currentPage" :total-pages="totalPages" :disabled="loading" @change="fetchProducts" />
      </div>
    </div>

    <!-- 编辑/创建弹窗 -->
    <DsDialog v-model:open="showForm" :title="editingId ? '编辑商品' : '添加商品'" description="商品信息、资产来源和价格依据会同时保存。" size="lg">
          <DsAlert v-if="formError" class="mb-4" title="商品信息未保存" :description="formError" tone="danger" role="alert" />
          <div class="space-y-4">
            <div>
              <label class="text-sm text-dark-400 block mb-1">商品名称 *</label>
              <input v-model="form.name" class="input w-full" placeholder="商品名称" />
            </div>
            <div>
              <label class="text-sm text-dark-400 block mb-1">商品标识 (slug) *</label>
              <input v-model="form.slug" class="input w-full" placeholder="product-slug" :disabled="!!editingId" />
            </div>
            <div>
              <label class="text-sm text-dark-400 block mb-1">商品分类 *</label>
              <select v-model="form.category_id" class="input w-full">
                <option value="">请选择分类</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm text-dark-400 block mb-1">品牌</label>
                <input v-model="form.brand" class="input w-full" placeholder="品牌" />
              </div>
              <div>
                <label class="text-sm text-dark-400 block mb-1">型号</label>
                <input v-model="form.model" class="input w-full" placeholder="型号" />
              </div>
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="text-sm text-dark-400 block mb-1">售价 *</label>
                <input v-model.number="form.price" type="number" step="0.01" class="input w-full" placeholder="0.00" />
              </div>
              <div>
                <label class="text-sm text-dark-400 block mb-1">原价</label>
                <input v-model.number="form.original_price" type="number" step="0.01" class="input w-full" placeholder="0.00" />
              </div>
              <div>
                <label class="text-sm text-dark-400 block mb-1">库存</label>
                <input v-model.number="form.stock" type="number" class="input w-full" placeholder="0" />
              </div>
            </div>
            <div>
              <label class="text-sm text-dark-400 block mb-1">主图URL</label>
              <input v-model="form.image_url" class="input w-full" placeholder="https://..." />
              <input class="mt-2 block w-full text-xs text-dark-400" type="file" accept=".png,.jpg,.jpeg,.webp" @change="uploadAsset($event, 'image')" />
            </div>
            <div class="rounded-lg border border-dark-700 bg-dark-950/40 p-4">
              <div class="mb-3 flex items-center justify-between gap-3">
                <label class="text-sm text-dark-300">{{ isDiyCaseProduct ? 'DIY 机箱 GLB（八节点合同）' : 'GLB 模型 URL' }}</label>
                <span v-if="form.model_3d_url" class="text-xs text-primary-400">已绑定</span>
              </div>
              <input v-model="form.model_3d_url" class="input w-full" placeholder="https://.../model.glb" />
              <div class="mt-3 grid grid-cols-[1fr_110px] gap-3">
                <input
                  class="block w-full text-xs text-dark-400 disabled:opacity-40"
                  type="file"
                  accept=".glb,model/gltf-binary"
                  :disabled="!editingId || uploading === '3D 模型'"
                  @change="uploadAsset($event, 'model')"
                />
                <input v-model.number="form.model_3d_scale" type="number" min="0.01" max="100" step="0.01" class="input w-full" aria-label="模型缩放" />
              </div>
              <p v-if="!editingId" class="mt-2 text-xs text-dark-500">先保存商品，再上传模型，避免产生未绑定文件。</p>
              <p v-if="uploading" class="mt-1 text-xs text-primary-500">正在上传 {{ uploading }}...</p>
              <p v-if="modelContractStatus" class="mt-2 text-xs" :class="modelContractStatus.valid ? 'text-primary-400' : 'text-yellow-300'">
                {{ modelContractStatus.message }}
              </p>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm text-dark-400 block mb-1">素材许可</label>
                <input v-model="form.asset_license" class="input w-full" placeholder="例如 CC BY 4.0" />
              </div>
              <div>
                <label class="text-sm text-dark-400 block mb-1">素材来源 URL</label>
                <input v-model="form.asset_source_url" class="input w-full" placeholder="https://厂商或素材页" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm text-dark-400 block mb-1">价格来源</label>
                <input v-model="form.price_source_name" class="input w-full" placeholder="京东 / 品牌官网" />
              </div>
              <div>
                <label class="text-sm text-dark-400 block mb-1">来源 URL</label>
                <input v-model="form.price_source_url" class="input w-full" placeholder="https://..." />
              </div>
            </div>
            <div>
              <label class="text-sm text-dark-400 block mb-1">商品描述</label>
              <textarea v-model="form.description" class="input w-full" rows="3" placeholder="商品描述"></textarea>
            </div>
            <div class="flex gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="form.is_active" class="accent-primary-500" />
                <span class="text-sm text-dark-400">上架</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="form.is_featured" class="accent-primary-500" />
                <span class="text-sm text-dark-400">推荐</span>
              </label>
            </div>
          </div>
          <template #footer>
            <DsButton variant="ghost" type="button" @click="showForm = false">取消</DsButton>
            <DsButton :loading="saving" :disabled="Boolean(uploading)" type="button" @click="handleSubmit">保存</DsButton>
          </template>
    </DsDialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { adminApi } from '@/api'
import { DsAlert, DsAsyncState, DsButton, DsDataTable, DsDialog, DsField, DsPagination } from '@/design-system'

const route = useRoute()

const products = ref([])
const categories = ref([])
const loading = ref(true)
const requestState = ref('loading')
const requestError = ref('请检查网络后重试。')
const feedback = ref(null)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const filters = ref({ keyword: '', is_active: '' })
let listRequestId = 0
const statusUpdating = ref(new Set())

const totalPages = computed(() => Math.ceil(total.value / pageSize))
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// 表单
const showForm = ref(false)
const editingId = ref(null)
const saving = ref(false)
const uploading = ref('')
const modelContractStatus = ref(null)
const formError = ref('')
const defaultForm = {
  name: '', slug: '', brand: '', model: '', price: null, original_price: null,
  category_id: '', stock: 0, image_url: '', description: '', is_active: true, is_featured: false,
  model_3d_url: '', model_3d_scale: 1, model_3d_position: null, model_3d_rotation: null,
  asset_license: '', asset_source_url: '',
  price_source_name: '', price_source_url: '', price_checked_at: null,
}
const form = ref({ ...defaultForm })
const originalPriceSource = ref('')
const priceSourceKey = value => JSON.stringify([value.price_source_name || '', value.price_source_url || ''])
const activeCategory = computed(() => categories.value.find(category => category.id === form.value.category_id))
const isDiyCaseProduct = computed(() => activeCategory.value?.slug === 'case')

async function fetchProducts() {
  const requestId = ++listRequestId
  loading.value = true
  requestState.value = 'loading'
  requestError.value = '请检查网络后重试。'
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.is_active !== '') params.is_active = filters.value.is_active
    const data = await adminApi.getProducts(params)
    if (requestId !== listRequestId) return
    products.value = data.items || []
    total.value = data.total || 0
    requestState.value = products.value.length ? 'success' : 'empty'
  } catch (e) {
    if (requestId !== listRequestId) return
    console.warn('后台商品服务不可用', e)
    requestError.value = e.displayMessage || e.message || '请检查网络后重试。'
    requestState.value = 'error'
  } finally {
    if (requestId === listRequestId) loading.value = false
  }
}

function searchProducts() {
  currentPage.value = 1
  return fetchProducts()
}

async function fetchCategories() {
  try {
    categories.value = await adminApi.getCategories()
  } catch (error) {
    console.warn('后台分类服务不可用', error)
    categories.value = []
  }
}

function openCreate() {
  editingId.value = null
  form.value = { ...defaultForm }
  originalPriceSource.value = priceSourceKey(form.value)
  modelContractStatus.value = null
  formError.value = ''
  showForm.value = true
}

function openEdit(p) {
  editingId.value = p.id
  form.value = {
    name: p.name, slug: p.slug, brand: p.brand || '', model: p.model || '',
    price: p.price, original_price: p.original_price, category_id: p.category_id || '', stock: p.stock,
    image_url: p.image_url || '', description: p.description || '',
    model_3d_url: p.model_3d_url || '', model_3d_scale: Number(p.model_3d_scale || 1),
    model_3d_position: p.model_3d_position || null, model_3d_rotation: p.model_3d_rotation || null,
    asset_license: p.asset_license || '', asset_source_url: p.asset_source_url || '',
    price_source_name: p.price_source_name || '',
    price_source_url: p.price_source_url || '', price_checked_at: p.price_checked_at || null,
    is_active: p.is_active, is_featured: p.is_featured,
  }
  originalPriceSource.value = priceSourceKey(form.value)
  modelContractStatus.value = p.model_3d_url
    ? { valid: true, message: '目录中已有模型；重新上传会生成新 URL。' }
    : null
  formError.value = ''
  showForm.value = true
}

async function handleSubmit() {
  if (saving.value || uploading.value) return
  formError.value = ''
  if (!form.value.name || !form.value.slug || !form.value.price || !form.value.category_id) {
    formError.value = '请填写必填字段：名称、标识、分类、售价。'
    return
  }
  if (form.value.model_3d_url && (!form.value.asset_license.trim() || !form.value.asset_source_url.trim())) {
    formError.value = '绑定 3D 模型前，请填写素材许可和素材来源 URL。'
    return
  }
  saving.value = true
  try {
    const payload = { ...form.value }
    if (priceSourceKey(payload) !== originalPriceSource.value) {
      payload.price_checked_at = payload.price_source_name && payload.price_source_url ? new Date().toISOString() : null
    }
    if (editingId.value) {
      await adminApi.updateProduct(editingId.value, payload)
    } else {
      await adminApi.createProduct(payload)
    }
    showForm.value = false
    await fetchProducts()
    feedback.value = { title: editingId.value ? '商品已更新' : '商品已创建', description: '列表数据已刷新。', tone: 'success' }
  } catch (e) {
    formError.value = e.displayMessage || e.message || '保存失败，请重试。'
  } finally {
    saving.value = false
  }
}

async function uploadAsset(event, kind) {
  const input = event.target
  const file = input.files?.[0]
  if (!file) return
  if (kind === 'model' && file.size > 20 * 1024 * 1024) {
    formError.value = 'GLB 文件不能超过 20 MB。'
    input.value = ''
    return
  }
  if (kind === 'model' && (!form.value.asset_license.trim() || !form.value.asset_source_url.trim())) {
    formError.value = '请先填写素材许可和素材来源 URL，再上传 GLB。'
    input.value = ''
    return
  }
  uploading.value = kind === 'model' ? '3D 模型' : '商品图片'
  try {
    const contract = kind === 'model' && isDiyCaseProduct.value ? 'diy-case-v1' : ''
    const asset = await adminApi.uploadAsset('', file, contract, editingId.value)
    if (kind === 'model') {
      form.value.model_3d_url = asset.url
      const report = asset.node_contract
      modelContractStatus.value = report
        ? {
            valid: report.valid,
            message: report.valid
              ? `节点合同通过：${report.found.join('、')}`
              : [
                  report.missing?.length ? `缺少节点：${report.missing.join('、')}` : '',
                  report.empty?.length ? `空节点：${report.empty.join('、')}` : '',
                ].filter(Boolean).join('；'),
          }
        : { valid: true, message: '模型已上传。' }
    }
    else form.value.image_url = asset.url
  } catch (e) {
    formError.value = e.displayMessage || e.message || '上传失败，请检查资产存储配置。'
  } finally {
    uploading.value = ''
    input.value = ''
  }
}

function onThumbError(event) {
  const img = event.target
  if (img.dataset.fallbackApplied) return
  img.dataset.fallbackApplied = 'true'
  img.src = '/assets/pangchong-product-fallback.png'
}

async function toggleStatus(p) {
  if (statusUpdating.value.has(p.id)) return
  statusUpdating.value.add(p.id)
  const nextStatus = !p.is_active
  try {
    await adminApi.toggleProductStatus(p.id, nextStatus)
    p.is_active = nextStatus
    feedback.value = { title: '商品状态已更新', description: `${p.name} 已${p.is_active ? '上架' : '下架'}。`, tone: 'success' }
    if (filters.value.is_active !== '') await searchProducts()
  } catch (e) {
    feedback.value = { title: '商品状态更新失败', description: e.displayMessage || e.message || '请重试。', tone: 'danger' }
  } finally {
    statusUpdating.value.delete(p.id)
  }
}

onMounted(async () => {
  // 素材库的引用商品链接会带上 keyword，让列表直接落到目标商品。
  const queryKeyword = typeof route?.query?.keyword === 'string' ? route.query.keyword : ''
  if (queryKeyword) filters.value.keyword = queryKeyword
  await Promise.all([
    fetchProducts(),
    fetchCategories(),
  ])
})
</script>
