<template>
  <section
    class="relative min-h-[360px] overflow-hidden rounded-lg border border-[#2A2A2A] bg-[#090909] sm:min-h-[430px] lg:min-h-[520px]"
    aria-label="胖虫产品 3D 展示视口，可拖拽旋转并使用滚轮缩放"
  >
    <div ref="viewportRef" class="absolute inset-0"></div>

    <div class="pointer-events-none absolute inset-x-0 top-0 flex items-center justify-between gap-3 p-4">
      <div class="rounded-lg border border-white/10 bg-black/45 px-3 py-2 backdrop-blur">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-primary-500">Interactive 3D</p>
        <p class="mt-0.5 text-xs text-[#B0B0B0]">拖拽旋转 · 滚轮缩放</p>
      </div>
      <div class="hidden rounded-lg border border-white/10 bg-black/45 px-3 py-2 text-xs text-[#B0B0B0] backdrop-blur sm:block">
        {{ selectedVariant?.name || '默认外观' }} / {{ selectedMaterial?.name || '默认材质' }}
      </div>
    </div>

    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/25">
      <div class="rounded-lg border border-[#2A2A2A] bg-[#111]/95 px-4 py-3 text-center shadow-2xl">
        <div class="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-[#2A2A2A] border-t-primary-500"></div>
        <p class="text-sm font-medium text-white">正在加载 3D 模型</p>
        <p class="mt-1 text-xs text-[#888]">{{ modelUrl }}</p>
      </div>
    </div>

    <div v-if="loadFailed" class="absolute bottom-4 left-4 right-4 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs leading-5 text-yellow-100 backdrop-blur sm:left-auto sm:max-w-sm">
      模型文件暂未就绪，当前显示代码生成的可交互占位模型。
    </div>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const props = defineProps({
  modelUrl: { type: String, default: '/models/pangchong.glb' },
  selectedVariant: { type: Object, default: null },
  selectedMaterial: { type: Object, default: null },
  autoRotate: { type: Boolean, default: true },
  cameraPreset: { type: String, default: 'front' },
  resetKey: { type: Number, default: 0 },
  parts: { type: Array, default: () => [] },
})

const viewportRef = ref(null)
const loading = ref(true)
const loadFailed = ref(false)

let scene
let camera
let renderer
let controls
let resizeObserver
let frameId
let modelRoot
let reducedMotionQuery
let reducedMotion = false

const baseMaterialNames = new Set(['body', 'screen-lid', 'keyboard-deck', 'trackpad'])
const accentMaterialNames = new Set(['accent', 'logo', 'edge-light'])

onMounted(() => {
  reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion = reducedMotionQuery.matches
  reducedMotionQuery.addEventListener?.('change', handleMotionPreference)

  initScene()
  loadModel()
  animate()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId)
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
watch(() => props.cameraPreset, () => resetCamera())
watch(() => props.resetKey, () => resetCamera())

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

  const floor = new THREE.Mesh(
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
  loading.value = true
  loadFailed.value = false

  try {
    const response = await fetch(props.modelUrl, { method: 'HEAD' })
    if (!response.ok) throw new Error(`Model not found: ${response.status}`)

    const loader = new GLTFLoader()
    loader.load(
      props.modelUrl,
      (gltf) => {
        setModelRoot(gltf.scene)
        loading.value = false
      },
      undefined,
      () => showPlaceholder()
    )
  } catch {
    showPlaceholder()
  }
}

function showPlaceholder() {
  loadFailed.value = true
  loading.value = false
  setModelRoot(createPlaceholderModel())
}

function setModelRoot(nextRoot) {
  if (modelRoot) {
    scene.remove(modelRoot)
    disposeObject(modelRoot)
  }

  modelRoot = nextRoot
  modelRoot.traverse((node) => {
    if (!node.isMesh) return
    node.castShadow = true
    node.receiveShadow = true
    if (node.material) node.material = node.material.clone()
  })

  scene.add(modelRoot)
  centerAndFrame(modelRoot)
  applyMaterials()
  resetCamera()
}

function createPlaceholderModel() {
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

function makeBox(name, size, position, material) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), material)
  mesh.name = name
  mesh.position.set(...position)
  return mesh
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
    if (!node.isMesh || !node.material) return
    const materialName = String(node.material.name || node.name || '').toLowerCase()
    const shouldAccent = [...accentMaterialNames].some((name) => materialName.includes(name))
    const shouldBody = [...baseMaterialNames].some((name) => materialName.includes(name)) || !shouldAccent

    if (shouldAccent) {
      node.material.color?.copy(accent)
      if (node.material.emissive) {
        node.material.emissive.copy(accent)
        node.material.emissiveIntensity = 0.18
      }
    } else if (shouldBody) {
      node.material.color?.copy(color)
    }

    if ('roughness' in node.material) node.material.roughness = materialSettings.roughness ?? node.material.roughness
    if ('metalness' in node.material) node.material.metalness = materialSettings.metalness ?? node.material.metalness
    node.material.needsUpdate = true
  })
}

function centerAndFrame(object) {
  const box = new THREE.Box3().setFromObject(object)
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  object.position.sub(center)

  const maxSize = Math.max(size.x, size.y, size.z, 1)
  const distance = maxSize * 1.55
  controls.minDistance = Math.max(1.8, distance * 0.55)
  controls.maxDistance = distance * 2.5
  camera.near = Math.max(0.01, distance / 100)
  camera.far = distance * 12
  camera.updateProjectionMatrix()
}

function resetCamera() {
  if (!camera || !controls) return
  const preset = props.cameraPreset
  const positions = {
    front: [4.5, 2.65, 5],
    side: [5.8, 2.1, 0.3],
    top: [0.2, 6.2, 1.1],
  }
  const position = positions[preset] || positions.front
  camera.position.set(...position)
  controls.target.set(0, 0.35, 0)
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

function animate() {
  frameId = requestAnimationFrame(animate)
  controls?.update()
  renderer?.render(scene, camera)
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
