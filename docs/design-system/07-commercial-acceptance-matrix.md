# 商业化验收矩阵

版本：v0.9.11 · 2026-09-06

这份矩阵把“大厂界面观察”转成可重复的工程验收。每次 AI 体验巡检必须同时提供截图、DOM/键盘证据和构建检查；仅凭视觉相似度不能通过。

| 区域 | 核心任务 | 成功态 | 失败/空态 | 390px 验收 | 关键证据 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 全局导航 | 找到商品、DIY、购物车并搜索 | 一级导航、购物车数量和搜索入口可见 | 搜索空关键词不跳转；菜单可关闭 | 品牌不被挤压；移动搜索字段可见 | AppNavbar.vue + DsIconButton / DsField | 已实现 |
| 商品发现 | 筛选、排序、打开商品 | 卡片显示价格、库存、来源和唯一主行动 | DsAsyncState 区分 error 与 empty，并可重试 | 筛选不承载核心横向滚动 | Products.vue、copy:check | 已实现 |
| DIY 工作台 | 选件、查看兼容性并加入购物车 | 候选卡可选择；价格、功耗和兼容性同步 | 商品接口失败仍可重试；3D 失败不阻断清单 | 3D、清单和 CTA 按顺序堆叠 | DIY.vue + DsAsyncState / DsField / DsDiyPartPicker | 已实现 |
| 购物车 | 选择、删除、核对金额并结算 | 行项目、库存、数量、摘要和结算 CTA 一致 | 删除有 DsDialog；库存不足用可读 toast | 摘要不遮挡主行动；弹窗可回焦 | Cart.vue + DsCartLineItem / DsDialog / DsToast | 已实现 |
| 结算 | 地址、配送、支付、下单 | fieldset/legend + choice card；金额和订单状态一致 | 保存/提交错误使用 inline alert；支付失败可恢复 | 选择卡单列且可键盘操作 | Checkout.vue + DsChoiceCard / DsAlert | 已实现 |
| 用户地址 | 新增、编辑、删除地址 | 表单字段有 autocomplete、错误和成功反馈 | 列表失败不伪装为空；删除可取消 | 表单与操作按钮触控尺寸达标 | user/Addresses.vue + DsAsyncState / DsDialog | 已实现 |
| 服务中心 | 搜索支持、展开协议、保存 Cookie 偏好 | 搜索结果定位到章节；面板有 `aria-expanded/controls`；开关同步保存态 | 无结果可重置；保存失败不宣称成功 | 章节摘要可读；开关和保存按钮可触达 | Services.vue + ServicePolicyPanel / ServiceCookiePreferences / DsToggle | 已实现 |
| DIY 3D 配置 | 选择颜色、材质、视角与自动旋转 | 选择态明确；重置可操作；自动旋转有 switch 名称和状态 | WebGL 失败不阻断清单；减少动态效果时不持续旋转 | 控件单列/双列适配，触控目标不小于 44px | ProductConfiguratorPanel.vue + DsIconButton / DsToggle | 已实现 |
| 购物车批量选择 | 全选、部分选择、删除所选 | 原生 checkbox 支持 checked/mixed/unchecked；批量删除需确认 | 空购物车有明确回到商品入口 | 全选控件与删除动作保持可见 | Cart.vue + DsCheckbox / DsDialog | 已实现 |
| 应用壳层 | 键盘跳过导航、进入主内容、移动端滚动定位 | 首次 Tab 出现“跳转到主要内容”；主内容可聚焦；hash 标题不被导航遮挡 | reduced motion 不产生页面过渡闪烁 | 390px 仍可触达 skip link 和主内容 | App.vue + main.css / index.html | 已实现 |

## 自动化门槛

1. npm run typecheck
2. npm run test -- --run
3. npm run design:lint
4. npm run copy:extract
5. npm run copy:check
6. npm run design:tokens:check
7. npm run design:figma:check
8. npm run build
9. Playwright：桌面 1280px、移动 390px；至少覆盖 /design-system.html、/cart、/checkout、/diy。DIY 韧性视觉回归另覆盖 360/390/430px 的正常滚动、WebGL 配置清单回退、重试回 3D 与 `prefers-reduced-motion`。

## AI 维护规则

- 每周从上述页面采集同一尺寸截图与 DOM snapshot，比较布局、状态和文案漂移。
- AI 只输出“证据、影响、建议改动、对应 Token/组件、验收方式”，不直接凭审美改色。
- P0：交易阻断、接口错误伪装成空态、焦点丢失、移动端主行动不可达。
- P1：重复组件样式、关键事实低对比度、状态缺少恢复动作、文案含糊。
- P2：装饰层级、间距、动效和非关键文案。
- Figma 未连接时，设计侧只登记映射与待同步项，不宣称已写回 Figma；连接后按 03-code-design-mapping.md 的命名同步。
