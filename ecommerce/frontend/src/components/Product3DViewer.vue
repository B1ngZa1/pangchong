<template>
  <section
    class="relative min-h-[360px] overflow-hidden rounded-lg border border-dark-800 bg-dark-950 sm:min-h-[430px] lg:min-h-[520px]"
    aria-label="胖虫产品 3D 展示视口，可拖拽旋转并使用滚轮缩放"
    data-testid="diy-3d-viewer"
    :data-motion-preference="reducedMotion ? 'reduce' : 'no-preference'"
  >
    <div ref="viewportRef" class="absolute inset-0"></div>

    <div class="pointer-events-none absolute inset-x-0 top-0 flex items-center justify-between gap-3 p-4">
      <div class="rounded-lg border border-white/10 bg-black/45 px-3 py-2 backdrop-blur">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-primary-500">交互式 3D 预览</p>
        <p class="mt-0.5 text-xs text-dark-300">拖拽旋转 · 滚轮缩放</p>
      </div>
      <div class="hidden rounded-lg border border-white/10 bg-dark-950/80 px-3 py-2 text-right text-xs text-dark-300 backdrop-blur sm:block">
        <p>{{ modelStatusLabel }} · {{ selectedVariant?.name || '默认外观' }} / {{ selectedMaterial?.name || '默认材质' }}</p>
        <p v-if="assetLicense && !placeholderReason" class="mt-1 text-[10px] text-dark-400">许可：{{ assetLicense }}</p>
      </div>
    </div>

    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/25 p-4">
      <div class="w-full max-w-sm rounded-lg border border-dark-700 bg-dark-900/95 px-4 py-3 text-center shadow-2xl">
        <DsAsyncState state="loading" loading-label="正在加载 3D 模型" />
        <p v-if="modelUrl" class="mt-2 truncate text-xs text-dark-500">{{ modelUrl }}</p>
      </div>
    </div>

    <div v-if="placeholderReason === 'webgl-unavailable'" class="absolute inset-0 flex items-center justify-center bg-dark-950 p-6 text-center">
      <div class="max-w-md rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-4 py-3 text-sm leading-6 text-yellow-100">
        当前环境无法创建 WebGL 视图，请使用配置清单继续选件和购买。
      </div>
    </div>
    <div v-else-if="placeholderReason === 'error'" class="absolute left-4 right-4 top-24 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs leading-5 text-yellow-100 backdrop-blur sm:left-auto sm:max-w-sm">
      已绑定的 GLB 模型未能加载，已切换到交互式示意预览。
    </div>
    <div v-else-if="placeholderReason === 'timeout'" class="absolute left-4 right-4 top-24 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs leading-5 text-yellow-100 backdrop-blur sm:left-auto sm:max-w-sm">
      3D 模型加载超时，已切换到交互式示意预览。
    </div>
    <div v-else-if="placeholderReason === 'missing'" class="absolute left-4 right-4 top-24 rounded-lg border border-white/10 bg-dark-950/80 px-3 py-2 text-xs leading-5 text-dark-300 backdrop-blur sm:left-auto sm:max-w-sm">
      所选机箱尚未绑定 GLB，当前显示交互式示意预览。
    </div>
    <div v-else-if="missingPartNodes.length || emptyPartNodes.length" class="absolute left-4 right-4 top-24 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs leading-5 text-yellow-100 backdrop-blur sm:left-auto sm:max-w-sm">
      <p v-if="missingPartNodes.length">模型缺少装配节点：{{ missingPartNodes.join('、') }}。</p>
      <p v-if="emptyPartNodes.length">节点没有可渲染网格：{{ emptyPartNodes.join('、') }}。</p>
    </div>

    <div v-if="partTags.length" class="pointer-events-none absolute inset-x-0 bottom-0 p-4">
      <div class="rounded-lg border border-white/10 bg-dark-950/80 p-3 backdrop-blur">
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-dark-400">配置状态</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="part in partTags"
            :key="part.id"
            class="max-w-[180px] truncate rounded border px-2 py-1 text-[11px]"
            :class="part.selected
              ? 'border-primary-500/40 bg-primary-500/10 text-primary-300'
              : 'border-white/10 bg-white/[0.04] text-dark-400'"
          >
            {{ part.name }}{{ part.selected ? ` · ${part.productName}` : ' · 待选' }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { collectDiyPartRoots, DIY_MODEL_PART_KEYS, findMissingDiyPartKeys } from '@/utils/modelParts'
import { DsAsyncState } from '@/design-system'
import {
  DIY_VIEWER_LOAD_TIMEOUT_MS,
  getDiyViewerFailure,
  hasWebGLSupport,
} from '@/utils/diyViewerResilience'

const props = defineProps({
  modelUrl: { type: String, default: '' },
  modelScale: { type: [Number, String], default: 1 },
  modelPosition: { type: Array, default: () => [0, 0, 0] },
  modelRotation: { type: Array, default: () => [0, 0, 0] },
  assetLicense: { type: String, default: '' },
  assetSourceUrl: { type: String, default: '' },
  selectedVariant: { type: Object, default: null },
  selectedMaterial: { type: Object, default: null },
  autoRotate: { type: Boolean, default: true },
  cameraPreset: { type: String, default: 'front' },
  resetKey: { type: Number, default: 0 },
  parts: { type: Array, default: () => [] },
  loadTimeoutMs: { type: Number, default: DIY_VIEWER_LOAD_TIMEOUT_MS },
  active: { type: Boolean, default: true },
})

const emit = defineEmits(['failure', 'ready'])

const viewportRef = ref(null)
const loading = ref(true)
const placeholderReason = ref('')
const missingPartNodes = ref([])
const emptyPartNodes = ref([])

let scene
let camera
let renderer
let controls
let resizeObserver
let frameId
let modelRoot
let modelAsset
let floor
let usingPlaceholder = false
let reducedMotionQuery
let reducedMotion = false
let activeLoadId = 0
let loadTimeoutId
let animationRunning = false
let cameraDistance = 5
const modelCenter = new THREE.Vector3(0, 0.35, 0)

const baseMaterialNames = new Set(['body', 'screen-lid', 'keyboard-deck', 'trackpad', 'case-shell', 'side-panel'])
const accentMaterialNames = new Set(['accent', 'logo', 'edge-light'])
const diyPartKeys = new Set(DIY_MODEL_PART_KEYS)
const modelStatusLabel = computed(() => placeholderReason.value ? '交互式示意预览' : '已验证 GLB 模型')

const partTags = computed(() => {
  return (props.parts || [])
    .filter(part => diyPartKeys.has(part.id || part.type))
    .map(part => ({
      id: part.id || part.type,
      name: part.shortName || part.name || part.label || part.id,
      productName: part.productName || part.product_name || part.selectedName || '',
      selected: Boolean(part.selected),
    }))
})

onMounted(() => {
  reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion = reducedMotionQuery.matches
  reducedMotionQuery.addEventListener?.('change', handleMotionPreference)

  if (!hasWebGLSupport()) {
    loading.value = false
    placeholderReason.value = 'webgl-unavailable'
    emitFailure('webgl-unavailable')
    return
  }

  try {
    initScene()
    loadModel()
    startAnimation()
  } catch (error) {
    loading.value = false
    placeholderReason.value = 'webgl-unavailable'
    emitFailure('webgl-unavailable', { error: error instanceof Error ? error.message : String(error) })
  }
})

onBeforeUnmount(() => {
  clearLoadTimeout()
  stopAnimation()
  resizeObserver?.disconnect()
  reducedMotionQuery?.removeEventListener?.('change', handleMotionPreference)
  controls?.dispose()
  disposeObject(modelRoot)
  renderer?.dispose()
  renderer?.domElement?.remove()
})

watch(() => props.selectedVariant, applyMaterials, { deep: true })
watch(() => props.selectedMaterial, applyMaterials, { deep: true })
watch(() => props.autoRotate, updateControls)
watch(() => props.active, (active) => {
  if (active) startAnimation()
  else stopAnimation()
})
watch(() => props.cameraPreset, () => resetCamera())
watch(() => props.resetKey, () => resetCamera())
watch(() => props.modelUrl, () => {
  if (scene) loadModel()
})
watch(
  () => [props.modelScale, props.modelPosition, props.modelRotation],
  () => {
    if (!modelRoot || usingPlaceholder) return
    applyCatalogTransform()
    frameModel()
    resetCamera()
  },
  { deep: true }
)
watch(() => props.parts, () => {
  if (usingPlaceholder && scene) {
    setModelRoot(createPlaceholderModel(), true)
  } else {
    applyPartStates()
  }
}, { deep: true })

function handleMotionPreference(event) {
  reducedMotion = event.matches
  updateControls()
}

function initScene() {
  const container = viewportRef.value
  scene = new THREE.Scene()
  scene.background = new THREE.Color('#090909')

  camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100)
  camera.position.set(4.5, 2.8, 5)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.05
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFShadowMap
  container.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  controls.enablePan = false
  controls.minDistance = 2.4
  controls.maxDistance = 9
  updateControls()

  const hemiLight = new THREE.HemisphereLight('#dce7ff', '#101010', 1.5)
  scene.add(hemiLight)

  const keyLight = new THREE.DirectionalLight('#ffffff', 2.6)
  keyLight.position.set(4, 6, 5)
  keyLight.castShadow = true
  keyLight.shadow.mapSize.set(1024, 1024)
  scene.add(keyLight)

  const rimLight = new THREE.DirectionalLight('#44D62C', 1.1)
  rimLight.position.set(-4, 2.5, -3)
  scene.add(rimLight)

  floor = new THREE.Mesh(
    new THREE.CircleGeometry(4.8, 96),
    new THREE.MeshStandardMaterial({ color: '#0f1115', roughness: 0.9, metalness: 0.1 })
  )
  floor.rotation.x = -Math.PI / 2
  floor.position.y = -0.58
  floor.receiveShadow = true
  scene.add(floor)

  resizeObserver = new ResizeObserver(resizeRenderer)
  resizeObserver.observe(container)
  resizeRenderer()
}

async function loadModel() {
  const loadId = ++activeLoadId
  clearLoadTimeout()
  loading.value = true
  placeholderReason.value = ''
  missingPartNodes.value = []
  emptyPartNodes.value = []

  if (!props.modelUrl) {
    showPlaceholder('missing')
    emit('ready', { source: 'generated' })
    return
  }

  const startedAt = performance.now()
  loadTimeoutId = window.setTimeout(() => {
    if (loadId !== activeLoadId) return
    activeLoadId += 1
    showPlaceholder('timeout')
    emitFailure('load-timeout', { elapsedMs: Math.round(performance.now() - startedAt) })
  }, Math.max(Number(props.loadTimeoutMs) || DIY_VIEWER_LOAD_TIMEOUT_MS, 1))

  const loader = new GLTFLoader()
  loader.load(
    props.modelUrl,
    (gltf) => {
      if (loadId !== activeLoadId) return disposeObject(gltf.scene)
      clearLoadTimeout()
      const contract = setModelRoot(gltf.scene)
      usingPlaceholder = false
      loading.value = false
      if (contract.missing.length || contract.empty.length) {
        emitFailure('missing-assembly-nodes', {
          missingNodes: contract.missing,
          emptyNodes: contract.empty,
        })
        return
      }
      emit('ready', {
        source: 'catalog',
        elapsedMs: Math.round(performance.now() - startedAt),
      })
    },
    undefined,
    () => {
      if (loadId !== activeLoadId) return
      clearLoadTimeout()
      showPlaceholder('error')
      emitFailure('model-load-failed')
    }
  )
}

function clearLoadTimeout() {
  if (loadTimeoutId) {
    window.clearTimeout(loadTimeoutId)
    loadTimeoutId = undefined
  }
}

function emitFailure(reason, details = {}) {
  stopAnimation()
  emit('failure', getDiyViewerFailure(reason, details))
}

function showPlaceholder(reason) {
  usingPlaceholder = true
  placeholderReason.value = reason
  loading.value = false
  setModelRoot(createPlaceholderModel(), true)
}

function setModelRoot(nextRoot, placeholder = false) {
  if (modelRoot) {
    scene.remove(modelRoot)
    disposeObject(modelRoot)
  }

  usingPlaceholder = placeholder
  modelAsset = nextRoot
  modelAsset.traverse((node) => {
    if (!node.isMesh) return
    node.castShadow = true
    node.receiveShadow = true
    if (Array.isArray(node.material)) {
      node.material = node.material.map(material => material.clone())
    } else if (node.material) {
      node.material = node.material.clone()
    }
  })

  centerAsset(modelAsset)
  modelRoot = new THREE.Group()
  modelRoot.name = placeholder ? 'generated-model-root' : 'catalog-model-root'
  modelRoot.add(modelAsset)
  scene.add(modelRoot)
  applyCatalogTransform()
  frameModel()
  applyMaterials()
  applyPartStates()
  if (placeholder) {
    missingPartNodes.value = []
    emptyPartNodes.value = []
  } else if (isDiyConfiguration()) {
    const partRoots = collectDiyPartRoots(modelAsset)
    missingPartNodes.value = findMissingDiyPartKeys(collectNodeNames(modelAsset))
    emptyPartNodes.value = DIY_MODEL_PART_KEYS.filter((key) => {
      const roots = partRoots.get(key) || []
      return roots.length > 0 && !roots.some(hasRenderableMesh)
    })
  }
  resetCamera()
  return {
    missing: [...missingPartNodes.value],
    empty: [...emptyPartNodes.value],
  }
}

function collectNodeNames(object) {
  const names = []
  object.traverse(node => names.push(node.name || ''))
  return names
}

function hasRenderableMesh(root) {
  let found = false
  root.traverse((node) => {
    if (node.isMesh) found = true
  })
  return found
}

function createPlaceholderModel() {
  return isDiyConfiguration() ? createDiyPlaceholderModel() : createLaptopPlaceholderModel()
}

function createLaptopPlaceholderModel() {
  const group = new THREE.Group()
  group.name = 'pangchong-placeholder'

  const variant = props.selectedVariant || {}
  const material = buildBodyMaterial(variant.hex || '#111827')
  material.name = 'body'

  const accentMaterial = new THREE.MeshStandardMaterial({
    name: 'accent',
    color: variant.accent || '#44D62C',
    emissive: variant.accent || '#44D62C',
    emissiveIntensity: 0.24,
    roughness: 0.42,
    metalness: 0.45,
  })

  const screenMaterial = new THREE.MeshStandardMaterial({
    color: '#070A0F',
    roughness: 0.2,
    metalness: 0.2,
  })

  const base = makeBox('keyboard-deck', [3.2, 0.18, 2.05], [0, 0, 0], material)
  const lid = makeBox('screen-lid', [3.15, 1.85, 0.12], [0, 1.02, -0.9], material)
  lid.rotation.x = -0.18

  const screen = makeBox('screen', [2.72, 1.46, 0.035], [0, 1.06, -0.965], screenMaterial)
  screen.rotation.x = -0.18

  const keyboard = makeBox('keyboard', [2.18, 0.035, 0.72], [0, 0.12, 0.12], new THREE.MeshStandardMaterial({ color: '#050505', roughness: 0.78, metalness: 0.1 }))
  const trackpad = makeBox('trackpad', [0.86, 0.032, 0.46], [0, 0.13, 0.72], new THREE.MeshStandardMaterial({ name: 'trackpad', color: '#1f2937', roughness: 0.52, metalness: 0.38 }))
  const lightBar = makeBox('edge-light', [2.85, 0.035, 0.045], [0, 0.13, -0.9], accentMaterial)
  const logo = makeBox('logo', [0.36, 0.035, 0.36], [0, 1.32, -1.04], accentMaterial)
  logo.rotation.x = -0.18
  logo.rotation.z = Math.PI / 4

  group.add(base, lid, screen, keyboard, trackpad, lightBar, logo)

  const keyMaterial = new THREE.MeshStandardMaterial({ color: '#111111', roughness: 0.7, metalness: 0.12 })
  for (let row = 0; row < 4; row += 1) {
    for (let col = 0; col < 11; col += 1) {
      const key = makeBox('key', [0.14, 0.025, 0.1], [-1.02 + col * 0.205, 0.16, -0.18 + row * 0.16], keyMaterial)
      group.add(key)
    }
  }

  return group
}

function createDiyPlaceholderModel() {
  const group = new THREE.Group()
  group.name = 'pangchong-diy-placeholder'

  const variant = props.selectedVariant || {}
  const bodyMaterial = buildBodyMaterial(variant.hex || '#111827')
  bodyMaterial.name = 'case-shell'
  const glassMaterial = new THREE.MeshStandardMaterial({
    name: 'side-panel',
    color: '#0b1220',
    roughness: 0.2,
    metalness: 0.25,
    transparent: true,
    opacity: 0.34,
  })

  const frameParts = [
    makeBox('case-shell', [2.45, 0.08, 1.55], [0, -0.42, 0], bodyMaterial),
    makeBox('case-shell', [2.45, 0.08, 1.55], [0, 1.95, 0], bodyMaterial),
    makeBox('case-shell', [0.08, 2.35, 1.55], [-1.18, 0.76, 0], bodyMaterial),
    makeBox('case-shell', [0.08, 2.35, 1.55], [1.18, 0.76, 0], bodyMaterial),
    makeBox('side-panel', [2.25, 2.18, 0.035], [0, 0.76, 0.78], glassMaterial),
  ]
  frameParts.forEach(part => group.add(part))

  const board = makePartBox('motherboard', [0.08, 1.45, 0.95], [-0.62, 0.8, -0.18], '#14532d')
  const cpu = makePartBox('cpu', [0.12, 0.34, 0.34], [-0.55, 1.02, -0.2], '#d1d5db')
  const cooler = makePartBox('cooler', [0.32, 0.52, 0.52], [-0.36, 1.02, -0.2], '#64748b')
  const gpu = makePartBox('gpu', [1.08, 0.25, 0.42], [0.1, 0.52, 0.18], '#1f2937')
  const ramA = makePartBox('ram', [0.08, 0.55, 0.08], [-0.47, 1.02, 0.26], '#16a34a')
  const ramB = makePartBox('ram', [0.08, 0.55, 0.08], [-0.47, 1.02, 0.4], '#16a34a')
  const ssd = makePartBox('ssd', [0.08, 0.46, 0.12], [-0.5, 0.52, -0.42], '#38bdf8')
  const psu = makePartBox('psu', [0.76, 0.42, 0.58], [0.55, -0.12, -0.3], '#334155')

  group.add(board, cpu, cooler, gpu, ramA, ramB, ssd, psu)

  const accentMaterial = new THREE.MeshStandardMaterial({
    name: 'accent',
    color: variant.accent || '#44D62C',
    emissive: variant.accent || '#44D62C',
    emissiveIntensity: 0.28,
    roughness: 0.36,
    metalness: 0.2,
  })
  group.add(makeBox('edge-light', [2.0, 0.035, 0.04], [0, 1.78, 0.81], accentMaterial))

  return group
}

function makeBox(name, size, position, material) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), material)
  mesh.name = name
  mesh.position.set(...position)
  return mesh
}

function makePartBox(partId, size, position, color) {
  const selected = isPartSelected(partId)
  const material = new THREE.MeshStandardMaterial({
    name: `diy-${partId}`,
    color,
    roughness: selected ? 0.46 : 0.78,
    metalness: selected ? 0.34 : 0.12,
    transparent: !selected,
    opacity: selected ? 1 : 0.22,
  })
  material.userData.keepColor = true

  const mesh = makeBox(`diy-${partId}`, size, position, material)
  mesh.userData.keepMaterialColor = true
  return mesh
}

function isDiyConfiguration() {
  return (props.parts || []).some(part => diyPartKeys.has(part.id || part.type))
}

function isPartSelected(partId) {
  return Boolean((props.parts || []).find(part => (part.id || part.type) === partId)?.selected)
}

function buildBodyMaterial(color) {
  const selectedMaterial = props.selectedMaterial || {}
  return new THREE.MeshStandardMaterial({
    color,
    roughness: selectedMaterial.roughness ?? 0.7,
    metalness: selectedMaterial.metalness ?? 0.55,
  })
}

function applyMaterials() {
  if (!modelRoot) return

  const variant = props.selectedVariant || {}
  const materialSettings = props.selectedMaterial || {}
  const color = new THREE.Color(variant.hex || '#111827')
  const accent = new THREE.Color(variant.accent || '#44D62C')

  modelRoot.traverse((node) => {
    if (!node.isMesh || !node.material || node.userData.keepMaterialColor) return
    const materials = Array.isArray(node.material) ? node.material : [node.material]
    materials.forEach((material) => {
      if (material.userData?.keepColor) return
      const materialName = String(material.name || node.name || '').toLowerCase()
      const shouldAccent = [...accentMaterialNames].some((name) => materialName.includes(name))
      const shouldBody = [...baseMaterialNames].some((name) => materialName.includes(name))

      if (shouldAccent) {
        material.color?.copy(accent)
        if (material.emissive) {
          material.emissive.copy(accent)
          material.emissiveIntensity = 0.18
        }
      } else if (shouldBody) {
        material.color?.copy(color)
      }

      if ('roughness' in material) material.roughness = materialSettings.roughness ?? material.roughness
      if ('metalness' in material) material.metalness = materialSettings.metalness ?? material.metalness
      material.needsUpdate = true
    })
  })
}

function applyPartStates() {
  if (!modelRoot || usingPlaceholder) return
  const selectedByPart = new Map((props.parts || []).map(part => [part.id || part.type, Boolean(part.selected)]))
  const partRoots = collectDiyPartRoots(modelAsset)

  partRoots.forEach((roots, partKey) => {
    if (partKey === 'case') return
    const selected = selectedByPart.get(partKey) === true
    roots.forEach((root) => {
      root.traverse((node) => {
        if (!node.isMesh || !node.material) return
        const materials = Array.isArray(node.material) ? node.material : [node.material]
        materials.forEach((material) => {
          if (!material.userData.diyOriginal) {
            material.userData.diyOriginal = {
              opacity: material.opacity,
              transparent: material.transparent,
              emissiveIntensity: material.emissiveIntensity || 0,
            }
          }
          const original = material.userData.diyOriginal
          material.transparent = selected ? original.transparent : true
          material.opacity = selected ? original.opacity : 0.12
          if (material.emissive) {
            material.emissive.set(selected ? '#163d12' : '#000000')
            material.emissiveIntensity = selected ? Math.max(original.emissiveIntensity, 0.16) : 0
          }
          material.needsUpdate = true
        })
      })
    })
  })
}

function centerAsset(object) {
  const box = new THREE.Box3().setFromObject(object)
  if (box.isEmpty()) return
  const center = box.getCenter(new THREE.Vector3())
  object.position.sub(center)
}

function applyCatalogTransform() {
  if (!modelRoot) return
  const scale = Number(props.modelScale)
  modelRoot.scale.setScalar(!usingPlaceholder && Number.isFinite(scale) && scale > 0 ? scale : 1)
  modelRoot.position.fromArray(vectorValues(usingPlaceholder ? null : props.modelPosition))
  modelRoot.rotation.fromArray(vectorValues(usingPlaceholder ? null : props.modelRotation))
}

function vectorValues(values) {
  return [0, 1, 2].map(index => {
    const value = Number(values?.[index])
    return Number.isFinite(value) ? value : 0
  })
}

function frameModel() {
  if (!modelRoot) return
  modelRoot.updateMatrixWorld(true)
  const box = new THREE.Box3().setFromObject(modelRoot)
  if (box.isEmpty()) return
  const size = box.getSize(new THREE.Vector3())
  box.getCenter(modelCenter)

  const maxSize = Math.max(size.x, size.y, size.z, 1)
  cameraDistance = Math.max(maxSize * 1.7, 2.8)
  controls.minDistance = Math.max(maxSize * 0.65, 1.2)
  controls.maxDistance = cameraDistance * 3
  camera.near = Math.max(0.01, cameraDistance / 100)
  camera.far = cameraDistance * 12
  camera.updateProjectionMatrix()
  if (floor) floor.position.y = box.min.y - Math.max(size.y * 0.02, 0.03)
}

function resetCamera() {
  if (!camera || !controls) return
  const preset = props.cameraPreset
  const directions = {
    front: [0.86, 0.5, 1],
    side: [1, 0.38, 0.05],
    top: [0.04, 1, 0.18],
  }
  const direction = new THREE.Vector3(...(directions[preset] || directions.front))
    .normalize()
    .multiplyScalar(cameraDistance)
  camera.position.copy(modelCenter).add(direction)
  controls.target.copy(modelCenter)
  controls.update()
}

function updateControls() {
  if (!controls) return
  controls.autoRotate = Boolean(props.autoRotate && !reducedMotion)
  controls.autoRotateSpeed = 0.7
}

function resizeRenderer() {
  const container = viewportRef.value
  if (!container || !renderer || !camera) return

  const width = Math.max(container.clientWidth, 1)
  const height = Math.max(container.clientHeight, 1)
  renderer.setSize(width, height, false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

function startAnimation() {
  if (animationRunning || !renderer || !props.active) return
  animationRunning = true
  animate()
}

function stopAnimation() {
  animationRunning = false
  if (frameId) cancelAnimationFrame(frameId)
  frameId = undefined
}

function animate() {
  if (!animationRunning || !props.active) return
  controls?.update()
  renderer?.render(scene, camera)
  frameId = requestAnimationFrame(animate)
}

function disposeObject(object) {
  if (!object) return
  object.traverse?.((node) => {
    node.geometry?.dispose?.()
    if (Array.isArray(node.material)) {
      node.material.forEach((material) => material.dispose?.())
    } else {
      node.material?.dispose?.()
    }
  })
}
</script>
