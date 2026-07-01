export const productVariants = [
  {
    id: 'black',
    name: '胖虫黑',
    hex: '#111827',
    accent: '#44D62C',
    priceDiff: 0,
  },
  {
    id: 'silver',
    name: '星空银',
    hex: '#b8c0cc',
    accent: '#44D62C',
    priceDiff: 0,
  },
  {
    id: 'green',
    name: '虫翼绿',
    hex: '#44D62C',
    accent: '#0f172a',
    priceDiff: 500,
  },
]

export const materialOptions = [
  {
    id: 'matte',
    name: '哑光金属',
    roughness: 0.72,
    metalness: 0.58,
    description: '低反光，适合长时间使用',
  },
  {
    id: 'satin',
    name: '细砂阳极',
    roughness: 0.44,
    metalness: 0.68,
    description: '细腻反射，边缘更有层次',
  },
  {
    id: 'gloss',
    name: '高亮涂层',
    roughness: 0.22,
    metalness: 0.48,
    description: '更强光泽，突出展示效果',
  },
]

export const cameraPresets = [
  { id: 'front', name: '正面' },
  { id: 'side', name: '侧面' },
  { id: 'top', name: '俯视' },
]
