<template>
  <div
    @dragenter.prevent="onDragEnter"
    @dragover.prevent
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
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

    <!-- 素材统计 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
      <div class="bg-dark-900 rounded-xl border border-dark-800 p-4">
        <p class="text-xs text-dark-500">素材总数</p>
        <p class="text-2xl font-bold text-white mt-1">{{ summary.total }}</p>
        <p class="text-xs text-dark-500 mt-1">合计 {{ formatSize(summary.total_size) }}</p>
      </div>
      <div class="bg-dark-900 rounded-xl border border-dark-800 p-4">
        <p class="text-xs text-dark-500">商品图片</p>
        <p class="text-2xl font-bold text-white mt-1">{{ summary.images }}</p>
        <p class="text-xs text-dark-500 mt-1">PNG / JPEG / WebP</p>
      </div>
      <div class="bg-dark-900 rounded-xl border border-dark-800 p-4">
        <p class="text-xs text-dark-500">3D 模型</p>
        <p class="text-2xl font-bold text-white mt-1">{{ summary.models }}</p>
        <p class="text-xs text-dark-500 mt-1">GLB，绑定后用于 DIY</p>
      </div>
      <div class="bg-dark-900 rounded-xl border border-dark-800 p-4">
        <p class="text-xs text-dark-500">未被引用</p>
        <p class="text-2xl font-bold mt-1" :class="summary.unused > 0 ? 'text-yellow-300' : 'text-white'">
          {{ summary.unused }}
        </p>
        <p class="text-xs text-dark-500 mt-1">可在下方清理释放空间</p>
      </div>
    </div>

    <section class="mb-4 rounded-xl border border-primary-500/20 bg-primary-500/[0.035] p-4" aria-labelledby="model-intake-title">
      <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-primary-500">3D 资产接入</p>
          <h2 id="model-intake-title" class="mt-1 text-base font-semibold text-white">先确认公开分发许可，再上传 GLB</h2>
          <p class="mt-1 max-w-3xl text-sm leading-6 text-dark-400">
            商品页截图、厂商官网链接或预览地址都不能替代再分发许可。模型绑定商品时，系统会要求填写来源 URL 与许可说明。
          </p>
        </div>
        <div class="grid gap-2 text-xs leading-5 text-dark-400 sm:grid-cols-3 lg:max-w-xl">
          <p><span class="font-semibold text-dark-200">来源</span><br>自制、书面授权或许可明确的资产</p>
          <p><span class="font-semibold text-dark-200">结构</span><br>GLB 2.0，DIY 机箱需通过八节点校验</p>
          <p><span class="font-semibold text-dark-200">体积</span><br>建议 ≤6 MB，上传硬限制 20 MB</p>
        </div>
      </div>
    </section>

    <!-- 操作栏 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 p-4 mb-4 flex flex-wrap gap-3 items-center">
      <input v-model="keyword" placeholder="搜索文件路径" aria-label="搜索文件路径"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-4 py-2 text-sm focus:border-primary-500 outline-none w-56" />
      <select v-model="kindFilter" aria-label="按类型筛选"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-3 py-2 text-sm focus:border-primary-500 outline-none">
        <option value="">全部类型</option>
        <option value="image">图片</option>
        <option value="model">3D 模型</option>
      </select>
      <select v-model="usageFilter" aria-label="按引用状态筛选"
        class="bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-3 py-2 text-sm focus:border-primary-500 outline-none">
        <option value="">全部引用状态</option>
        <option value="used">已引用</option>
        <option value="unused">未引用</option>
      </select>
      <DsButton variant="secondary" type="button" :loading="loading" @click="fetchAssets">刷新</DsButton>
      <div class="flex-1"></div>
      <p class="text-xs text-dark-500 hidden lg:block">图片 ≤5MB · DIY GLB ≤20MB · 绑定时需填写许可与来源 URL</p>
    </div>

    <!-- 素材网格：首格固定为上传瓦片 -->
    <div class="bg-dark-900 rounded-xl border border-dark-800 p-4">
      <DsAsyncState
        :state="requestState === 'empty' ? 'success' : requestState"
        loading-label="正在加载素材库"
        error-title="素材库加载失败"
        :error-description="requestError"
        @retry="fetchAssets"
      >
        <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          <!-- 上传瓦片 -->
          <button
            type="button"
            class="min-h-[220px] rounded-lg border-2 border-dashed flex flex-col items-center justify-center gap-2 p-4 text-center transition-colors motion-reduce:transition-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
            :class="dragging ? 'border-primary-500 bg-primary-500/10' : 'border-dark-700 bg-dark-950/40 hover:border-primary-500/60'"
            :title="dragging ? '松开鼠标完成上传' : '点击选择文件上传'"
            @click="openFilePicker"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-10 w-10 text-primary-500/80" aria-hidden="true">
              <path d="M12 16V4m0 0-4 4m4-4 4 4" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" stroke-linecap="round" />
            </svg>
            <span class="text-sm font-medium text-dark-200">
              {{ assets.length ? '拖入或点击上传素材' : '素材库还是空的，上传第一个素材' }}
            </span>
            <span class="text-xs text-dark-500">图片 ≤5MB · DIY GLB ≤20MB</span>
          </button>

          <article
            v-for="asset in filteredAssets"
            :key="asset.path"
            class="rounded-lg border border-dark-800 bg-dark-950/60 overflow-hidden flex flex-col transition-colors hover:border-dark-700 motion-reduce:transition-none"
          >
            <button
              type="button"
              class="block w-full aspect-[4/3] bg-dark-900 border-b border-dark-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 group"
              :class="asset.kind === 'model' ? 'glb-preview' : ''"
              :title="`在新窗口打开 ${asset.path}`"
              @click="openPreview(asset)"
            >
              <img
                v-if="asset.kind === 'image' && !previewErrors[asset.path]"
                :src="asset.url"
                :alt="asset.path"
                loading="lazy"
                class="w-full h-full object-contain transition-transform group-hover:scale-[1.03] motion-reduce:transition-none motion-reduce:group-hover:scale-100"
                @error="previewErrors[asset.path] = true"
              />
              <span v-else class="flex h-full w-full flex-col items-center justify-center gap-2 text-dark-500">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" class="h-12 w-12" :class="asset.kind === 'model' ? 'text-primary-500/70' : ''" aria-hidden="true">
                  <path d="M12 2.8 21 7.6v8.8l-9 4.8-9-4.8V7.6l9-4.8z" />
                  <path d="M3.4 7.8 12 12.4l8.6-4.6" />
                  <path d="M12 12.4v8.6" stroke-dasharray="0.1 2.6" stroke-linecap="round" />
                </svg>
                <span class="text-xs">{{ asset.kind === 'model' ? 'GLB 3D 模型' : '预览不可用' }}</span>
              </span>
            </button>

            <div class="p-3 flex flex-col gap-2 flex-1">
              <p class="text-sm font-medium text-dark-200 truncate" :title="asset.path">
                {{ fileName(asset.path) }}
              </p>
              <div class="flex flex-wrap items-center gap-1.5">
                <DsBadge :tone="asset.kind === 'model' ? 'accent' : 'info'">
                  {{ asset.kind === 'model' ? '3D 模型' : '图片' }}
                </DsBadge>
                <DsBadge v-if="asset.used_by.length" tone="success">已引用</DsBadge>
                <DsBadge v-else tone="warning">未引用</DsBadge>
              </div>
              <p class="text-xs text-dark-500">
                {{ formatSize(asset.size) }} · {{ formatDate(asset.updated_at) }}
              </p>
              <p v-if="asset.used_by.length" class="text-xs text-dark-400 truncate">
                引用：<RouterLink
                  v-for="product in asset.used_by"
                  :key="product.id"
                  :to="{ name: 'AdminProducts', query: { keyword: product.slug } }"
                  class="text-primary-400 hover:underline"
                  :title="`在商品管理中打开 ${product.name}`"
                >{{ product.name }}</RouterLink>
              </p>
              <div class="mt-auto pt-2 flex items-center gap-2">
                <DsButton variant="ghost" size="sm" type="button" @click="copyUrl(asset)">复制链接</DsButton>
                <DsButton
                  variant="danger"
                  size="sm"
                  type="button"
                  :disabled="asset.used_by.length > 0"
                  :title="asset.used_by.length ? '素材仍被商品引用，请先在商品管理中解除绑定' : '删除该素材'"
                  @click="askDelete(asset)"
                >
                  删除
                </DsButton>
              </div>
            </div>
          </article>
        </div>
      </DsAsyncState>
    </div>

    <!-- 拖放遮罩 -->
    <div
      v-if="dragging"
      class="fixed inset-0 z-50 bg-dark-950/85 flex items-center justify-center pointer-events-none"
      aria-hidden="true"
    >
      <div class="rounded-2xl border-2 border-dashed border-primary-500 px-12 py-10 text-center bg-dark-900/80">
        <p class="text-xl font-semibold text-white">松开以上传素材</p>
        <p class="mt-1 text-sm text-dark-400">图片 ≤5MB · DIY GLB ≤20MB</p>
      </div>
    </div>

    <input ref="fileInput" type="file" class="hidden" accept=".png,.jpg,.jpeg,.webp,.glb" @change="onUploadChange" />

    <!-- 删除确认 -->
    <DsDialog
      v-model:open="showDelete"
      title="删除素材"
      description="删除后无法恢复，请确认该素材不再被任何页面使用。"
      size="sm"
    >
      <p v-if="deleteTarget" class="text-sm text-dark-300 break-all">
        确定删除 <span class="text-white font-medium">{{ deleteTarget.path }}</span> 吗？
      </p>
      <template #footer>
        <DsButton variant="ghost" type="button" @click="showDelete = false">取消</DsButton>
        <DsButton variant="danger" type="button" :loading="deleting" @click="confirmDelete">删除</DsButton>
      </template>
    </DsDialog>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { adminApi } from '@/api'
import { DsAlert, DsAsyncState, DsBadge, DsButton, DsDialog } from '@/design-system'

const assets = ref([])
const summary = ref({ total: 0, images: 0, models: 0, unused: 0, total_size: 0 })
const loading = ref(false)
const requestState = ref('loading')
const requestError = ref('请检查网络后重试。')
const feedback = ref(null)
const previewErrors = ref({})

const keyword = ref('')
const kindFilter = ref('')
const usageFilter = ref('')

const fileInput = ref(null)
const uploading = ref(false)

const showDelete = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)

const dragging = ref(false)
let dragDepth = 0

const filteredAssets = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  return assets.value.filter(asset => {
    if (kindFilter.value && asset.kind !== kindFilter.value) return false
    const used = asset.used_by.length > 0
    if (usageFilter.value === 'used' && !used) return false
    if (usageFilter.value === 'unused' && used) return false
    if (text && !asset.path.toLowerCase().includes(text)) return false
    return true
  })
})

async function fetchAssets() {
  loading.value = true
  requestState.value = 'loading'
  requestError.value = '请检查网络后重试。'
  try {
    const data = await adminApi.listAssets()
    assets.value = data.items || []
    summary.value = data.summary || summary.value
    requestState.value = assets.value.length ? 'success' : 'empty'
  } catch (e) {
    console.warn('素材库服务不可用', e)
    requestError.value = e.displayMessage || e.message || '请检查网络后重试。'
    requestState.value = 'error'
  } finally {
    loading.value = false
  }
}

function openFilePicker() {
  fileInput.value?.click()
}

async function uploadFile(file) {
  const isModel = file.name.toLowerCase().endsWith('.glb')
  const maxSize = isModel ? 20 * 1024 * 1024 : 5 * 1024 * 1024
  if (file.size > maxSize) {
    feedback.value = {
      title: '文件超过大小限制',
      description: isModel ? 'GLB 模型不能超过 20 MB。' : '图片不能超过 5 MB。',
      tone: 'danger',
    }
    return
  }
  uploading.value = true
  try {
    await adminApi.uploadAsset('', file)
    await fetchAssets()
    feedback.value = { title: '素材已上传', description: `${file.name} 已进入素材库，可在商品管理中绑定使用。`, tone: 'success' }
  } catch (e) {
    feedback.value = {
      title: '上传失败',
      description: e.displayMessage || e.message || '请检查资产存储配置后重试。',
      tone: 'danger',
    }
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function onUploadChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  await uploadFile(file)
}

function onDragEnter(event) {
  if (!event.dataTransfer?.types?.includes('Files')) return
  dragDepth += 1
  dragging.value = true
}

function onDragLeave() {
  dragDepth = Math.max(0, dragDepth - 1)
  if (dragDepth === 0) dragging.value = false
}

function onDrop(event) {
  dragDepth = 0
  dragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) void uploadFile(file)
}

function openPreview(asset) {
  window.open(asset.url, '_blank', 'noopener')
}

async function copyUrl(asset) {
  try {
    await navigator.clipboard.writeText(asset.url)
    feedback.value = { title: '链接已复制', description: asset.url, tone: 'success' }
  } catch {
    feedback.value = {
      title: '复制失败',
      description: '浏览器拒绝了剪贴板访问，请在新窗口打开后手动复制地址。',
      tone: 'danger',
    }
  }
}

function askDelete(asset) {
  deleteTarget.value = asset
  showDelete.value = true
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await adminApi.deleteAsset(deleteTarget.value.path)
    showDelete.value = false
    await fetchAssets()
    feedback.value = { title: '素材已删除', description: `${deleteTarget.value.path} 已从素材库移除。`, tone: 'success' }
  } catch (e) {
    feedback.value = {
      title: '删除失败',
      description: e.displayMessage || e.message || '请稍后重试。',
      tone: 'danger',
    }
    showDelete.value = false
  } finally {
    deleting.value = false
    deleteTarget.value = null
  }
}

function fileName(path) {
  return path.split('/').pop() || path
}

function formatSize(bytes) {
  const size = Number(bytes) || 0
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(2)} MB`
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(fetchAssets)
onUnmounted(() => {
  dragDepth = 0
  dragging.value = false
})
</script>

<style scoped>
/* GLB 没有浏览器原生预览；用淡淡的等距网格提示这是三维资产（色值 = 虫翼绿 #44d62c）。 */
.glb-preview {
  background-image:
    linear-gradient(rgba(68, 214, 44, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(68, 214, 44, 0.06) 1px, transparent 1px);
  background-size: 24px 24px;
}
@media (prefers-reduced-motion: reduce) {
  .glb-preview {
    background-image: none;
  }
}
</style>
