<template>
  <div>
    <!-- 操作栏 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 p-4 mb-4 flex flex-wrap gap-3 items-center">
      <input v-model="filters.keyword" placeholder="搜索商品名/品牌/型号" @keyup.enter="fetchProducts"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-4 py-2 text-sm focus:border-primary-500 outline-none w-64" />
      <select v-model="filters.is_active" @change="fetchProducts"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-3 py-2 text-sm focus:border-primary-500 outline-none">
        <option value="">全部状态</option>
        <option value="true">已上架</option>
        <option value="false">已下架</option>
      </select>
      <button @click="fetchProducts" class="px-4 py-2 bg-dark-800 text-dark-300 text-sm rounded-lg hover:bg-dark-700">
        <i class="fas fa-search mr-1"></i>搜索
      </button>
      <div class="flex-1"></div>
      <button @click="openCreate" class="px-4 py-2 bg-primary-500 text-dark-950 text-sm font-semibold rounded-lg hover:bg-primary-400">
        <i class="fas fa-plus mr-1"></i>添加商品
      </button>
    </div>

    <!-- 商品表格 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 overflow-hidden">
      <div v-if="loading" class="flex justify-center py-16">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
      </div>

      <div v-else-if="products.length === 0" class="text-center py-16 text-dark-500">
        暂无商品数据
      </div>

      <table v-else class="w-full text-sm">
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
                  <img v-if="p.image_url" :src="p.image_url" class="w-full h-full object-cover" />
                  <span v-else class="flex items-center justify-center h-full text-dark-600">📦</span>
                </div>
                <span class="truncate max-w-xs font-medium">{{ p.name }}</span>
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

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-dark-800">
        <span class="text-dark-500 text-xs">共 {{ total }} 条</span>
        <div class="flex gap-1">
          <button v-for="pg in visiblePages" :key="pg"
            @click="currentPage = pg; fetchProducts()"
            class="w-8 h-8 rounded text-xs font-medium transition-colors"
            :class="currentPage === pg ? 'bg-primary-500 text-dark-950' : 'bg-dark-800 text-dark-400 hover:text-white'">
            {{ pg }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑/创建弹窗 -->
    <Teleport to="body">
      <div v-if="showForm" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="bg-dark-900 rounded-2xl border border-dark-700 w-[90vw] max-w-lg max-h-[85vh] shadow-2xl flex flex-col">
          <div class="flex items-center justify-between p-6 border-b border-dark-800">
            <h3 class="text-lg font-bold">{{ editingId ? '编辑商品' : '添加商品' }}</h3>
            <button @click="showForm = false" class="text-dark-500 hover:text-white"><i class="fas fa-times"></i></button>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-4">
            <div>
              <label class="text-sm text-dark-400 block mb-1">商品名称 *</label>
              <input v-model="form.name" class="input w-full" placeholder="商品名称" />
            </div>
            <div>
              <label class="text-sm text-dark-400 block mb-1">商品标识 (slug) *</label>
              <input v-model="form.slug" class="input w-full" placeholder="product-slug" :disabled="!!editingId" />
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
          <div class="p-6 border-t border-dark-800 flex gap-3 justify-end">
            <button @click="showForm = false" class="px-5 py-2 rounded-lg text-sm bg-dark-800 text-dark-300 hover:bg-dark-700">取消</button>
            <button @click="handleSubmit" :disabled="saving"
              class="px-5 py-2 rounded-lg text-sm bg-primary-500 text-dark-950 font-semibold hover:bg-primary-400 disabled:opacity-50">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'

const products = ref([])
const loading = ref(true)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const filters = ref({ keyword: '', is_active: '' })

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
const defaultForm = {
  name: '', slug: '', brand: '', model: '', price: null, original_price: null,
  stock: 0, image_url: '', description: '', is_active: true, is_featured: false,
}
const form = ref({ ...defaultForm })

async function fetchProducts() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.is_active !== '') params.is_active = filters.value.is_active
    const data = await adminApi.getProducts(params)
    products.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('获取商品失败:', e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { ...defaultForm }
  showForm.value = true
}

function openEdit(p) {
  editingId.value = p.id
  form.value = {
    name: p.name, slug: p.slug, brand: p.brand || '', model: p.model || '',
    price: p.price, original_price: p.original_price, stock: p.stock,
    image_url: p.image_url || '', description: p.description || '',
    is_active: p.is_active, is_featured: p.is_featured,
  }
  showForm.value = true
}

async function handleSubmit() {
  if (!form.value.name || !form.value.slug || !form.value.price) {
    alert('请填写必填字段：名称、标识、售价')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await adminApi.updateProduct(editingId.value, form.value)
    } else {
      await adminApi.createProduct(form.value)
    }
    showForm.value = false
    fetchProducts()
  } catch (e) {
    alert('保存失败：' + (e.message || '请重试'))
  } finally {
    saving.value = false
  }
}

async function toggleStatus(p) {
  try {
    await adminApi.toggleProductStatus(p.id, !p.is_active)
    p.is_active = !p.is_active
  } catch (e) {
    alert('操作失败')
  }
}

onMounted(fetchProducts)
</script>
