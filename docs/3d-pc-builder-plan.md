# 3D PC 装机配置器 — 技术方案

## 一、功能概述

在现有 DIY 装机配置器基础上，引入 **3D 可视化装机体验**。用户选择配件后，可在 3D 场景中实时预览整机装配效果，支持旋转、缩放、透视查看内部结构，实现"所见即所得"的装机体验。

### 核心功能

| 功能 | 描述 |
|------|------|
| 3D 机箱展示 | 透明/半透明机箱，内部配件实时可见 |
| 配件装配渲染 | CPU/GPU/主板/内存/散热/电源/机箱风扇按真实位置渲染 |
| 自由视角控制 | 旋转（Orbit）、缩放（Zoom）、平移（Pan） |
| 视角预设 | 正面/侧面/顶部/内部透视一键切换 |
| 配件热插拔 | 点击/拖拽更换配件，3D 场景即时更新 |
| RGB 光效模拟 | 风扇/水冷/内存条发光效果（可选） |
| 线缆示意 | 电源线与数据线的简略走线展示（可选） |
| 截图/导出 | 生成装机配置海报或分享图 |

---

## 二、技术栈选型

### 2.1 核心 3D 引擎

| 技术 | 用途 | 选型理由 |
|------|------|----------|
| **Three.js** (r160+) | 3D 渲染引擎 | WebGL 生态最成熟，社区资源丰富 |
| **TresJS** (v4+) | Vue 3 的 Three.js 封装 | 与项目 Vue 3 技术栈天然集成，声明式 API，响应式数据绑定 |
| **@tresjs/cientos** | TresJS 扩展包 | 提供 OrbitControls、useFBX/useGLTF、环境贴图等开箱即用功能 |
| **GSAP** (GreenSock) | 动画引擎 | 实现组件切换、相机过渡、装配动画时的流畅补间 |

### 2.2 3D 资源

| 技术 | 用途 | 选型理由 |
|------|------|----------|
| **Blender** 4.x | 3D 建模/编辑 | 开源免费，GLTF 导出完善 |
| **glTF 2.0** (GLB) | 3D 模型格式 | Web 端加载最优，PBR 材质支持，压缩率高 |
| **meshoptimizer** / gltf-transform | 模型压缩 | 减少 GLB 体积，提升加载速度 |
| **Draco** | 网格压缩 | 大幅缩小模型文件，Three.js 原生支持 |

### 2.3 前端框架（已有）

| 技术 | 用途 |
|------|------|
| **Vue 3** (Composition API) | UI 框架 |
| **Pinia** | 状态管理 |
| **Tailwind CSS** 3.x | 样式 |
| **Vite** 5.x | 构建工具 |
| **TypeScript** | 类型安全（建议 3D 模块使用 TS 编写） |

### 2.4 后端（已有）

| 技术 | 用途 |
|------|------|
| **FastAPI** | 提供配件 3D 模型 URL、兼容性数据 |
| **PostgreSQL** | 存储配件元数据、模型路径 |

### 2.5 DevOps

| 技术 | 用途 |
|------|------|
| **CDN** (阿里云 OSS / CloudFront) | 托管 3D 模型静态文件 |
| **Vite** Code Splitting | 3D 模块按需懒加载 |

---

## 三、架构设计

### 3.1 组件树

```
DIY.vue  (改造升级)
├── DIY3DCanvas.vue          ← 新增：3D 画布核心
│   ├── <TresCanvas>         ← TresJS 渲染器
│   │   ├── <PC-Case>        ← 机箱模型（半透明材质）
│   │   ├── <Motherboard>    ← 主板模型
│   │   ├── <CPU>            ← CPU + 散热器模型
│   │   ├── <GPU>            ← 显卡模型
│   │   ├── <RAM>            ← 内存条模型
│   │   ├── <PSU>            ← 电源模型
│   │   ├── <Storage>        ← 硬盘模型
│   │   ├── <CaseFan>        ← 风扇模型
│   │   └── <CableManager>   ← 线缆示意（可选）
│   ├── OrbitControls        ← 旋转/缩放/平移
│   ├── EnvironmentMap       ← 环境光照
│   └── ViewPresets          ← 视角预设快捷键
├── ComponentSelector.vue    ← 配件选择面板（已有基础）
├── CompatibilityChecker.vue ← 兼容性检测（已有基础）
├── BuildSummary.vue         ← 配置清单/价格汇总（已有基础）
└── ScreenshotButton.vue     ← 截图导出
```

### 3.2 数据流

```
┌─────────────┐   用户选择配件   ┌──────────────────┐
│  Pinia Store │ ◄────────────── │ ComponentSelector │
│  (diyStore)  │ ──────────────► │                  │
│              │  响应式更新状态  └──────────────────┘
│  selected:   │
│    cpu       │──► CPU 模型的 position/scale/GLB 路径
│    gpu       │──► GPU 模型的 position/scale/GLB 路径
│    mobo      │──► Motherboard 模型的 position/scale/GLB 路径
│    ...       │
└──────┬───────┘
       │  watch / computed
       ▼
┌──────────────────┐
│  DIY3DCanvas.vue │────► TresJS 响应式更新 3D 场景
│  (TresJS scene)  │
└──────────────────┘
```

### 3.3 Pinia Store 扩展 (`store/diy3d.js`)

```ts
interface ComponentSlot {
  id: string          // 配件 ID
  name: string        // 配件名
  category: string    // 分类 (cpu/gpu/mobo/ram/psu/storage/cooler/case_fan/case)
  modelUrl: string    // GLB 模型 CDN 地址
  position: [number, number, number]  // 在机箱内的相对坐标
  rotation: [number, number, number]  // 旋转角度
  scale: [number, number, number]     // 缩放
  price: number
}

interface DIY3DState {
  selectedComponents: Record<string, ComponentSlot | null>
  caseModel: string              // 机箱模型 URL
  cameraPreset: string           // 当前视角预设名
  showSkeleton: boolean          // 显示骨架/线缆
  rgbColor: string               // RGB 主色调
}
```

---

## 四、分阶段实施计划

### 阶段一：基础 3D 搭建（2-3 周）

**目标**：在页面上渲染一个可旋转的机箱 3D 模型

- [ ] 安装依赖：`tresjs`, `three`, `@tresjs/cientos`
- [ ] 创建 `DIY3DCanvas.vue` 基础组件，引入 TresCanvas
- [ ] 准备 1 个机箱 GLB 模型（Blender 建或购买资产）
- [ ] 配置 HDR 环境贴图（Studio 光照）
- [ ] 实现 OrbitControls 旋转/缩放/平移
- [ ] 实现 4 个视角预设按钮（正面、侧面、45°、顶部）
- [ ] 添加进度条 loading 动画
- [ ] Vite 配置 glTF/glb 静态资源处理（`assetsInclude`）

**交付物**：页面可见 3D 机箱，可用鼠标旋转缩放

### 阶段二：核心配件加载（3-4 周）

**目标**：根据用户选择的配件，在 3D 场景中加载对应模型

- [ ] 在数据库中为每个 SKU 增加 `model_3d_url` 字段
- [ ] 准备 15-20 个通用配件 GLB 模型（每个品类 2-3 个典型型号）
- [ ] 实现配件模型按坐标定位到机箱内
- [ ] 实现配件切换时的过渡动画（GSAP tween）
- [ ] 实现主板→CPU→内存→GPU→散热器的层级装配逻辑
- [ ] 半透明机箱外壳（玻璃/亚克力材质模拟）
- [ ] 兼容性检测在 3D 场景中的视觉提示（红色高亮冲突配件）

**交付物**：选择配件后 3D 场景实时更新，显示完整装配效果

### 阶段三：交互增强（2-3 周）

**目标**：3D 场景支持点击交互、高亮、动画

- [ ] Raycaster 射线检测实现点击选中配件
- [ ] 选中配件高亮边框（Outline Pass / 发光材质）
- [ ] 点击配件弹出 info 卡片（型号、价格、规格）
- [ ] 右键菜单快速更换配件
- [ ] 装配/拆卸动画（translate + rotate 过渡）
- [ ] 视角自动聚焦到选中配件
- [ ] 爆炸视图（Exploded View）—— 一键散开所有配件

**交付物**：3D 场景可交互，点击/右键操作顺畅

### 阶段四：视觉打磨（1-2 周）

**目标**：提升视觉效果和用户体验

- [ ] PBR 材质调优（金属、塑料、玻璃质感）
- [ ] RGB 风扇/水冷头发光效果（Emissive Map + PointLight）
- [ ] 机箱环境阴影（Contact Shadows / AO）
- [ ] 后处理效果（Bloom 泛光、色调映射）
- [ ] 截图/导出功能（`preserveDrawingBuffer` + canvas.toDataURL / toBlob）
- [ ] 移动端触控适配（Touch Orbit Controls）
- [ ] 暗色/亮色主题适配

**交付物**：视觉效果达到商业产品级别

### 阶段五：性能优化与上线（1-2 周）

**目标**：确保流畅运行，完成上线

- [ ] 模型 LOD（不同距离使用不同精度模型）
- [ ] 模型压缩（Draco + meshoptimizer）
- [ ] CDN 部署 3D 资源，配置 CORS + Cache-Control
- [ ] `Suspense` 异步加载 3D 画布，不阻塞首屏
- [ ] 性能监控（FPS 面板、`stats.js` 或 TresJS `useStats`）
- [ ] 降级方案：WebGL 不可用时回退到静态图片 + 2D 配置器
- [ ] 浏览器兼容测试（Chrome/Firefox/Edge/Safari）

**交付物**：生产环境可用 3D 装机配置器

---

## 五、3D 模型清单

### 5.1 必须准备的模型（MVP）

| 品类 | 数量 | 说明 |
|------|------|------|
| 机箱 (Case) | 3 个 | 全塔 / 中塔 / ITX，内外部都要建模 |
| CPU + 散热器 | 4 套 | 风冷×2（单塔/双塔），一体水冷×2（240/360） |
| GPU | 5 个 | 分别对应 RTX 4060/4070/4080/4090 和 AMD 高端卡外观 |
| 主板 (ATX) | 3 块 | 不同档次（入门/中端/旗舰） |
| RAM | 2 套 | 无灯条 / RGB 灯条 |
| 电源 PSU | 3 个 | SFX / ATX / 模组电源 |
| M.2 SSD | 1 个 | 通用外形 |
| 机箱风扇 | 2 个 | 120mm 无光 / RGB |

**总计约 23 个模型**，可通过缩放/换贴图变体覆盖更多 SKU。

### 5.2 模型制作建议

- **机箱**：仅建外壳 + 内部骨架，不需要精确到螺丝孔
- **通用配件**：使用标准尺寸（ATX 规范），不同品牌通过贴图/颜色区分
- **精度**：每个模型控制在 5K-50K 三角面，Draco 压缩后 500KB-2MB
- **材质**：统一使用 PBR metallic/roughness 工作流
- **来源**：Blender 自制 / Sketchfab 购买 / TurboSquid 资产

---

## 六、关键技术要点

### 6.1 TresJS 基础示例

```vue
<script setup lang="ts">
import { TresCanvas } from '@tresjs/core'
import { OrbitControls, useGLTF, Environment } from '@tresjs/cientos'
import { ref } from 'vue'

const caseRef = ref()
const { scene: caseModel } = await useGLTF('/models/pc-case.glb')
</script>

<template>
  <TresCanvas shadows>
    <TresPerspectiveCamera :position="[3, 2, 5]" :fov="45" />
    <OrbitControls :target="[0, 0, 0]" :max-distance="10" :min-distance="1.5" />
    <Environment :files="['/hdr/studio.hdr']" />

    <primitive :object="caseModel" ref="caseRef" />
  </TresCanvas>
</template>
```

### 6.2 配件坐标定位

每个配件在机箱内的坐标由后端返回或在配置表中定义：

```ts
const SLOT_POSITIONS = {
  motherboard: { position: [0, 0, 0], rotation: [0, 0, 0], scale: [1, 1, 1] },
  cpu:         { position: [0, 0.15, 0.02], rotation: [0, 0, 0], scale: [1, 1, 1] },
  gpu:         { position: [0, -0.18, 0.05], rotation: [0, 0, 0], scale: [1, 1, 1] },
  ram_1:       { position: [0.04, 0.05, 0.03], rotation: [0, 0, 0], scale: [1, 1, 1] },
  ram_2:       { position: [0.06, 0.05, 0.03], rotation: [0, 0, 0], scale: [1, 1, 1] },
  // ...
}
```

### 6.3 组件切换动画 (GSAP)

```ts
import gsap from 'gsap'

function animateComponentSwap(mesh, newPosition) {
  gsap.to(mesh.position, { x: newPosition[0], y: newPosition[1], z: newPosition[2], duration: 0.6, ease: 'power2.out' })
  gsap.from(mesh.scale, { x: 0, y: 0, z: 0, duration: 0.4, ease: 'back.out(1.7)' })
}
```

### 6.4 爆炸视图

```ts
function toggleExplodedView() {
  Object.entries(SLOT_POSITIONS).forEach(([key, slot], i) => {
    const mesh = refs[key]
    if (!mesh) return
    const offset = exploded.value ? 0 : 0.3 + i * 0.15
    gsap.to(mesh.position, { z: slot.position[2] + offset, duration: 0.8, ease: 'power2.inOut' })
  })
  exploded.value = !exploded.value
}
```

### 6.5 Raycaster 点击检测

```ts
import { useRaycaster } from '@tresjs/cientos'

const { intersects } = useRaycaster(caseRef)

watch(intersects, (hits) => {
  if (hits.length > 0) {
    const clicked = hits[0].object
    highlightMesh(clicked)
  } else {
    clearHighlight()
  }
})
```

---

## 七、性能目标

| 指标 | 目标值 |
|------|--------|
| 首屏加载 (含 3D) | < 5s (CDN + 模型压缩后) |
| 3D 画布冷启动 | < 2s |
| 配件切换响应 | < 200ms |
| 渲染帧率 | ≥ 30 FPS (移动端) / ≥ 60 FPS (桌面端) |
| 模型总大小 (MVP) | < 15MB (Draco 压缩后) |
| JS Bundle 增加 | 3D 模块懒加载，首屏不增加 > 50KB |

---

## 八、降级策略

| 场景 | 降级方案 |
|------|----------|
| WebGL 不可用 | 检测 `WEBGL.isWebGLAvailable()`，回退到 3D 图片轮播 + 2D 配置器 |
| 移动端低性能 | 降低像素比 (`renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`)，关闭阴影/后处理 |
| 模型加载失败 | 显示占位方块 + "模型加载中" / "模型暂不可用" |
| 首屏慢 | 3D 画布 `v-if` + `Suspense`，先展示 2D 配置面板 |

---

## 九、依赖清单

```json
{
  "dependencies": {
    "@tresjs/core": "^4.2.0",
    "@tresjs/cientos": "^4.2.0",
    "three": "^0.168.0",
    "gsap": "^3.12.0"
  },
  "devDependencies": {
    "@types/three": "^0.168.0"
  }
}
```

Vite 配置补充：

```ts
// vite.config.ts
export default defineConfig({
  assetsInclude: ['**/*.glb', '**/*.gltf', '**/*.hdr'],
  // 3D 模型建议大文件单独部署 CDN，不走 Vite 打包
})
```

---

## 十、预估工期与资源

| 阶段 | 工期 | 人员 |
|------|------|------|
| 阶段一：基础 3D 搭建 | 2-3 周 | 1 前端 + 1 3D 建模 |
| 阶段二：核心配件加载 | 3-4 周 | 1 前端 + 1 3D 建模 + 1 后端 |
| 阶段三：交互增强 | 2-3 周 | 1 前端 |
| 阶段四：视觉打磨 | 1-2 周 | 1 前端 + 1 3D 建模 |
| 阶段五：性能优化与上线 | 1-2 周 | 1 前端 |
| **总计** | **9-14 周** | |

---

## 十一、风险与应对

| 风险 | 概率 | 应对 |
|------|------|------|
| 3D 模型制作周期长 | 高 | 购买现成资产库 / 简化模型精度 |
| 移动端性能不足 | 中 | 自动降级策略，限制三角面数 |
| WebGL 兼容性问题 | 低 | 降级方案 + 浏览器检测 |
| TresJS API 不稳定 | 低 | 锁定版本，核心逻辑用原生 Three.js 兜底 |
| 模型文件过大 | 中 | Draco 压缩 + CDN + LOD |
