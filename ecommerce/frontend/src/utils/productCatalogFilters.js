const CATEGORY_QUERY_ALIASES = {
  'gaming-laptop': 'laptop-gaming',
  'thin-laptop': 'laptop-thin'
}

const SCENE_KEYWORDS = {
  gaming: '游戏',
  creator: '创作',
  office: '办公'
}

const SYSTEM_BRAND = '胖虫'

const TAG_LABELS = {
  hot: '热门整机'
}

const SCENE_LABELS = {
  gaming: '电竞游戏',
  creator: '设计渲染',
  office: '学习办公'
}

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export function firstQueryValue(value) {
  if (Array.isArray(value)) return value[0] || ''
  return value || ''
}

function trimmedQueryValue(value) {
  return String(firstQueryValue(value)).trim()
}

export function resolveCategoryId(categoryQuery, categories) {
  const rawCategory = trimmedQueryValue(categoryQuery)
  if (!rawCategory) return null

  const normalizedCategory = CATEGORY_QUERY_ALIASES[rawCategory] || rawCategory
  const category = categories.find((cat) => (
    cat.id === normalizedCategory || cat.slug === normalizedCategory
  ))

  if (category) return category.id
  return UUID_PATTERN.test(normalizedCategory) ? normalizedCategory : null
}

export function buildProductListParams({ page, pageSize = 20, currentCatId, query }) {
  const params = { page, page_size: pageSize }

  if (currentCatId) {
    params.category_id = currentCatId
  }

  const tag = trimmedQueryValue(query.tag)
  if (tag === 'hot') {
    params.is_featured = true
    params.sort_by = 'sold_count'
    params.sort_order = 'desc'
  }

  const keyword = trimmedQueryValue(query.keyword)
  const scene = trimmedQueryValue(query.scene)
  const sceneKeyword = SCENE_KEYWORDS[scene]
  if (keyword) {
    params.keyword = keyword
  } else {
    if (sceneKeyword) {
      params.keyword = sceneKeyword
    }

    if (sceneKeyword || tag === 'hot') {
      params.brand = SYSTEM_BRAND
    }
  }

  return params
}

export function getCatalogQueryLabel(query) {
  const keyword = trimmedQueryValue(query.keyword)
  if (keyword) return `搜索：${keyword}`

  const tagLabel = TAG_LABELS[trimmedQueryValue(query.tag)]
  if (tagLabel) return tagLabel

  return SCENE_LABELS[trimmedQueryValue(query.scene)] || ''
}
