import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import {
  DsBuildSummary,
  DsCommerceNav,
  DsMediaCategoryCard,
  DsPartsInspector,
  DsWorkbenchShell,
} from '@/design-system'

describe('PANGCHONG commerce and workbench patterns', () => {
  it('keeps commerce navigation links semantic and categories horizontally portable', () => {
    const wrapper = mount(DsCommerceNav, {
      props: {
        primaryItems: [{ id: 'shop', label: '电脑', href: '/products', active: true }, { id: 'diy', label: '装机', href: '/diy' }],
        categoryItems: [{ id: 'gpu', label: '显卡', href: '/products?category=gpu' }],
        searchHref: '/products',
      },
      slots: { actions: '<button type="button">账户</button>' },
    })

    expect(wrapper.get('nav[aria-label="商城主导航"]')).toBeTruthy()
    expect(wrapper.get('a[aria-current="page"]').text()).toBe('电脑')
    expect(wrapper.get('nav[aria-label="商品分类导航"] a').attributes('href')).toContain('category=gpu')
    expect(wrapper.findAll('a')).toHaveLength(4)
    expect(wrapper.get('button').text()).toBe('账户')
  })

  it('announces build facts as a labelled definition list', () => {
    const wrapper = mount(DsBuildSummary, {
      props: { price: 12999, compatibility: '全部兼容', power: 548, performance: 27560 },
    })

    expect(wrapper.get('section').attributes('aria-labelledby')).toMatch(/^pc-build-summary-/)
    expect(wrapper.get('dl').text()).toContain('¥12,999')
    expect(wrapper.get('dl').text()).toContain('548 W')
    expect(wrapper.findAll('dt')).toHaveLength(4)
    expect(wrapper.find('[data-tone="info"] dd').text()).toBe('全部兼容')
  })

  it('keeps media category cards focused on one accessible next step', async () => {
    const wrapper = mount(DsMediaCategoryCard, {
      props: {
        image: '/missing-category.png',
        fallbackImage: '/fallback-category.png',
        eyebrow: '探索',
        title: 'DIY 装机',
        description: '逐项选择硬件，持续查看兼容性。',
        href: '/diy',
        linkLabel: '开始配置',
      },
    })

    expect(wrapper.get('img').attributes('alt')).toBe('DIY 装机')
    expect(wrapper.findAll('a')).toHaveLength(1)
    expect(wrapper.get('a').attributes('href')).toBe('/diy')
    expect(wrapper.text()).toContain('持续查看兼容性')

    await wrapper.get('img').trigger('error')
    expect(wrapper.get('img').attributes('src')).toBe('/fallback-category.png')
  })

  it('keeps the workbench shell regions named and density-tokenized', () => {
    const wrapper = mount(DsWorkbenchShell, {
      props: { density: 'compact', ariaLabel: 'DIY 配置工作台' },
      slots: {
        nav: '<nav>目录</nav>',
        canvas: '<div>3D 画布</div>',
        inspector: '<aside>检查器</aside>',
      },
    })

    expect(wrapper.attributes('aria-label')).toBe('DIY 配置工作台')
    expect(wrapper.attributes('data-density')).toBe('compact')
    expect(wrapper.get('.pc-workbench-shell__nav').text()).toContain('目录')
    expect(wrapper.get('.pc-workbench-shell__canvas').text()).toContain('3D 画布')
    expect(wrapper.get('.pc-workbench-shell__inspector').text()).toContain('检查器')
    expect(wrapper.get('.pc-workbench-shell__nav').attributes('aria-label')).toBe('工作台导航')
    expect(wrapper.get('.pc-workbench-shell__inspector').attributes('aria-label')).toBe('配置检查器')
  })

  it('keeps parts inspector rows actionable and preserves empty recovery copy', async () => {
    const wrapper = mount(DsPartsInspector, {
      props: {
        parts: [
          { id: 'gpu', category: '显卡', name: 'GeForce RTX 5070 Ti 16GB', status: '兼容', price: 6499 },
          { id: 'ram', category: '内存', name: 'DDR5 6000 32GB', status: '双通道', price: 899 },
        ],
        activeId: 'gpu',
        showPriceHistory: true,
      },
    })

    expect(wrapper.get('section').attributes('aria-labelledby')).toMatch(/^pc-parts-inspector-/)
    expect(wrapper.findAll('[role="listitem"]')).toHaveLength(2)
    expect(wrapper.findAll('button[aria-pressed="true"]')).toHaveLength(1)
    expect(wrapper.text()).toContain('¥6,499')

    await wrapper.findAll('[role="listitem"] button')[1].trigger('click')
    expect(wrapper.emitted('select')?.[0]?.[0].id).toBe('ram')
    await wrapper.get('.pc-parts-inspector__history').trigger('click')
    expect(wrapper.emitted('toggle-history')).toHaveLength(1)

    await wrapper.setProps({ parts: [] })
    expect(wrapper.get('[role="status"]').text()).toContain('还没有选择硬件')
  })
})
