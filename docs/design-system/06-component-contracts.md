# PANGCHONG 组件契约 v0.9.11

## Choice Card

`DsChoiceCard` 的必需契约：`modelValue`、`value`、`title`；可选 `description`、`type`（radio/checkbox）、`name`、`disabled`。整卡可点击，内部 input 必须保留原生表单语义和可见焦点。

组件契约同时约束视觉、行为、文案、可访问性和代码 API。任何新组件先写契约，再写 Vue 实现或 Figma 组件。

## v0.9.5 迁移补充

Cart.vue 的不可逆删除使用 DsDialog，删除结果使用 DsToast；DIY.vue 的筛选、语义步骤和主要 CTA 使用 DsField / DsStepIndicator / DsButton，3D 懒加载占位使用 DsAsyncState；AppNavbar.vue 和 ProductConfiguratorPanel.vue 的图标动作使用 DsIconButton；ProductDetail.vue、Login.vue、Register.vue 与 user/Profile.vue 使用 DsAsyncState / DsField / DsAlert / DsButton。这些迁移不改变业务数据契约，只统一焦点、尺寸、反馈和 token 消费。

## v0.9.6 服务中心补充

`DsToggle` 使用原生 `button[role=switch]`，必须提供可见或程序化关联的 `label`，并同步 `aria-checked`、`disabled` 与 `update:modelValue`。`ServicePolicyPanel` 负责协议章节的标题、开合状态、`aria-controls` 和 FAQ 展示；`Services.vue` 保留 hash 导航、路由同步和 Cookie 持久化。`ServiceCookiePreferences` 只负责偏好编辑与保存触发，不直接访问路由或接口。

服务中心的页面级视觉契约由 `Services.vue` 消费 `color.theme.service.*`：`canvas / hero / rail / surface / surface-hover / category-hover / search / contact` 对应画布与表面，`border-* / divider-* / control-*` 对应分隔与控件，`text-*` 对应内容层级，`spark` 对应 Hero 氛围光，`print-*` 对应打印态。透明叠层必须使用生成的 `--pc-color-theme-service-*-rgb` 变量加 alpha。抽取的 `ServicePolicyPanel` 与 `ServiceCookiePreferences` 继续消费 semantic Token，以保持组件可复用；不得通过新增 raw color prop 破坏该边界。

应用壳层必须提供可见的 skip link、稳定的 `main#main-content` 锚点、`tabindex="-1"` 和页面锚点的 `scroll-margin-top`；全局页面过渡与组件动效必须在 `prefers-reduced-motion: reduce` 下停止或降级。

## v0.9.7 交易与 3D 控制补充

`DsCheckbox` 保留原生 checkbox 的键盘、标签和表单语义；`mixed=true` 时同步 DOM `indeterminate` 与 `aria-checked="mixed"`，适用于购物车部分选中。`ProductConfiguratorPanel` 只负责配置选项展示和事件转发，颜色值仍来自业务数据，视觉状态只消费 semantic Token；自动旋转统一使用 `DsToggle`，并遵守减少动态效果设置。

## v0.9.11 Commerce 与 Workbench 模式

`DsMediaCategoryCard` 只保留一个可见的下一步链接，图片错误降级到 fallback，图片不能替代标题和描述；`DsWorkbenchShell` 通过 `nav`、`canvas`、`inspector` 三个 slot 统一信息架构，`compact` 在窄屏按导航、画布、检查器顺序堆叠；`DsPartsInspector` 的每个硬件行是原生 button，必须暴露 `aria-pressed`，价格和状态文字同时可见，空列表必须提供可理解的恢复说明。

`DsCommerceNav` 使用两个原生 `nav` 区域区分全局任务和商品分类，当前链接用 `aria-current="page"`，分类区只在自身容器内横向滚动；`AppNavbar` 的移动菜单必须暴露 `aria-expanded`/`aria-controls`，打开后把焦点送入菜单，Tab 只能在菜单项之间循环，Escape 关闭并把焦点还给触发器；`DsBuildSummary` 用 `dl/dt/dd` 表达价格、兼容性、功耗和性能事实，语义色必须同时配合文字，不得只显示颜色或图标。

`DsMenu` 用 `v-model:open` 和 `trigger`/default slots 承载账号、工具和操作菜单；触发器必须消费组件提供的 `aria-haspopup`、`aria-expanded`、`aria-controls`，菜单项使用 `role="menuitem"`。打开后默认聚焦首项，支持 Arrow/Home/End 导航，Escape 关闭并回焦，Tab 离开前先关闭，点击菜单外自动关闭。

## 1. 状态模型

| 状态 | 用户看到的事实 | 必须提供 | 禁止行为 |
| --- | --- | --- | --- |
| `loading` | 请求仍在进行 | 保留布局骨架、可感知的加载说明 | 只显示空白或转圈而不保留尺寸 |
| `success` | 数据可用 | 完整内容和下一步 | 用成功色隐藏关键警告 |
| `empty` | 请求成功但没有业务数据 | 解释原因、筛选/返回/创建动作 | 显示系统错误、虚构数量 |
| `error` | 请求或系统失败 | 错误原因级别、重试、替代路径 | 把失败数组清空后渲染空态 |
| `partial` | 部分事实可用 | 可用内容、不可用范围、局部重试 | 阻断整页交易或掩盖缺失字段 |

`DsAsyncState` 是上述状态的统一实现；页面可以用业务文案覆盖默认标题，但不能改变状态语义。根节点在 `loading` 时必须暴露 `aria-busy="true"`，进入 `success`、`empty`、`error` 或 `partial` 后移除该属性，避免把已稳定内容持续宣布为忙碌；`error` 使用 `role="alert"` 与 `aria-live="assertive"`，其余状态使用 `aria-live="polite"`。

## 2. 通用 API 约束

- 所有按钮必须显式 `type`，默认 `button`；表单提交按钮必须由页面传入 `submit`。
- 图标按钮必须有 `label`，并暴露 `aria-label`；不可只依赖 tooltip 或图形。
- 可切换控件使用 `aria-pressed`；Tabs 使用 `aria-selected`、`aria-controls` 和 `role=tabpanel`。
- 所有异步进行中的控件使用 `aria-busy=true`；提交中仍保留可理解的按钮名称。
- 关闭、删除、增加、减少等图标动作必须有 44×44px 的可操作区域；数量步进器的当前值使用 `output[aria-live=polite][aria-atomic=true]`，让增减结果对辅助技术可感知。
- Dialog 打开时焦点进入，Escape 关闭，关闭后焦点回到触发器；背景内容不可继续滚动。
- Toast 只反馈已发生的结果；错误、空态和恢复动作放在内容区域，不依赖自动消失 Toast。
- 时间线的当前节点必须有 `aria-current="step"`；已完成、当前、未开始和终止节点必须同时有文字语义，不能只用颜色或图标区分。
- 不可逆操作必须使用 `DsDialog`，确认和取消按钮都必须有明确结果文案；禁止 `alert()` / `confirm()` 作为业务反馈。

## 3. 组件 → Figma → Vue 映射

| Figma 名称 | Vue 入口 | Props/变量 | 典型业务 |
| --- | --- | --- | --- |
| `Components/Button` | `DsButton` | `variant`, `size`, `loading`, `disabled`, `block` | 加入购物车、保存配置、进入结算 |
| `Components/IconButton` | `DsIconButton` | `label`, `variant`, `size`, `pressed`, `loading` | 搜索、筛选、关闭、收藏、导航 |
| `Components/Menu` | `DsMenu` | `open`, `label`, `align`, `closeOnSelect`, trigger/default slots | 用户菜单、工具菜单、上下文操作 |
| `Components/SearchField` | `DsSearchField` | `modelValue`, `label`, `placeholder`, `submitLabel`, `compact` | 全局导航、服务支持、商品目录搜索 |
| `Components/Toggle` | `DsToggle` | `modelValue`, `label`, `disabled` | Cookie 偏好与布尔设置 |
| `Components/Checkbox` | `DsCheckbox` | `modelValue`, `label`, `description`, `disabled`, `mixed` | 购物车全选与批量选择 |
| `Components/Field` | `DsField` | `as`, `label`, `hint`, `error`, `required`, `disabled`, `options`, `autocomplete`, `modelValue` | 地址、优惠码、账号信息、选择框 |
| `Components/Skeleton` | `DsSkeleton` | `variant`, `width`, `height` | 商品、价格、DIY 候选加载 |
| `Components/Alert` | `DsAlert` | `tone`, `title`, `description`, `dismissible` | 兼容性、价格来源、系统提示 |
| `Components/Toast` | `DsToast` | `visible`, `message`, `tone`, `dismissible` | 已加入购物车、保存结果、轻量操作反馈 |
| `Components/ContrastToggle` | `DsContrastToggle` | persisted theme, `aria-pressed` | 全局高对比度偏好 |
| `Patterns/AsyncState` | `DsAsyncState` | `state`, `retry`, `emptyTitle`, `errorTitle` | 商品列表、热门商品、订单详情 |
| `Components/Tabs` | `DsTabs` | `tabs`, `modelValue`, `orientation` | 3D/清单、概览/规格/支持 |
| `Components/Dialog` | `DsDialog` | `open`, `title`, `description`, `size` | 删除确认、筛选、配置详情 |
| `Patterns/ProductCard` | `DsProductCard` | `product`, `categoryLabel`, `fallbackImage`, `interactive` | 商品发现、推荐、搜索结果 |
| `Patterns/CartLineItem` | `DsCartLineItem` | `item`, `selected`, `disabled`, `interactive`, `compact`, `fallbackImage` | 购物车编辑、结算只读预览、库存恢复 |
| `Patterns/StepIndicator` | `DsStepIndicator` | `steps`, `modelValue`, `allowNavigation` | 结算步骤；未来步骤 disabled，当前步骤 `aria-current=step` |
| `Patterns/OrderSummary` | `DsOrderSummary` | `items`, `subtotal`, `shipping`, `discount`, `total`, `fallbackImage` | 结算侧栏与订单确认金额事实 |
| `Patterns/PriceSummary` | `DsPriceSummary` | `subtotal`, `shipping`, `discount`, `total`, `itemCount`, `showTotal` | 购物车与结算共享的价格、配送、优惠和应付金额事实 |
| `Patterns/DiyPartPicker` | `DsDiyPartPicker` | `product`, `selected`, `specs`, `selectionAdvice`, `fallbackImage` | DIY 配件候选、键盘选择、价格依据 |
| `Patterns/OrderSuccess` | `DsOrderSuccess` | `open`, `orderNo`, `paying`, `paymentError` | 订单创建成功、支付重试与恢复路径 |
| `Patterns/Pagination` | `DsPagination` | `page`, `totalPages`, `maxVisible`, `pageLabel`, `pageSuffix`, `disabled` | 列表分页、页码省略、当前页和前后页操作 |
| `Patterns/OrderTimeline` | `DsOrderTimeline` | `events`, `title`, `eyebrow`, `currentLabel` | 订单详情履约节点、当前状态和取消/退款终止分支 |
| `Patterns/DataTable` | `DsDataTable` | `label`, default table slot | 后台密集数据、键盘滚动、移动端表格承载 |
| `Status/Compatibility` | `DsCompatibilityStatus` | `status`, `compact` | DIY、订单快照、结算前风险提示 |
| `Surface/Card` | `DsCard` | `padding`, `interactive`, `as` | 产品卡、摘要、服务承诺 |
| `Status/Badge` | `DsBadge` | `tone` | 推荐、库存、特惠、待验证 |
| `Business/PriceProvenance` | `DsPriceProvenance`（兼容入口：`PriceProvenance`） | `product`, `compact` | 商品卡、详情页、结算前价格信任 |
| `Patterns/Service/PolicyPanel` | `ServicePolicyPanel` | `section`, `open`, `faqs`, `toggle` | 服务协议、FAQ、隐私政策章节 |
| `Patterns/Privacy/CookiePreferences` | `ServiceCookiePreferences` | `options`, `modelValue`, `saved`, `save` | Cookie 偏好设置与保存反馈 |
| `Patterns/3D/ConfiguratorPanel` | `ProductConfiguratorPanel` | `variants`, `materials`, `cameraPresets`, selected values | DIY 3D 外观、材质、视角和自动旋转 |
| `Patterns/Commerce/MediaCategoryCard` | `DsMediaCategoryCard` | `image`, `title`, `description`, `href`, `linkLabel` | 首页/分类入口的图片主导卡片 |
| `Patterns/Commerce/Navigation` | `DsCommerceNav` | `primaryItems`, `categoryItems`, `searchHref`, `density` | 商城一级任务与二级分类导航 |
| `Patterns/DIY/WorkbenchShell` | `DsWorkbenchShell` | `nav`, `canvas`, `inspector` slots, `density` | DIY 三栏工作台与移动端顺序 |
| `Patterns/DIY/PartsInspector` | `DsPartsInspector` | `parts`, `activeId`, `showPriceHistory` | 已选硬件、价格历史和当前检查项 |
| `Patterns/DIY/BuildSummary` | `DsBuildSummary` | `price`, `compatibility`, `power`, `performance` | 配置过程关键事实摘要 |

## 4. Token 消费规则

组件只消费语义 token：`color.semantic.*`、`space.*`、`radius.*`、`shadow.*`、`opacity.*`、`motion.*`、`zIndex.*`。只有 token 源文件可以保存原始 hex、尺寸、透明度或时间值。

代码侧 CSS 变量和 Figma 变量使用同一 kebab/slash 语义：

```text
color.semantic.action.primary
  → --pc-color-semantic-action-primary
  → Figma: Color/action/primary
  → Vue: DsButton[data-variant="primary"]
```

## 5. 变更检查单

提交新组件或破坏性修改时，必须同时更新：

1. `pangchong.tokens.json`（如涉及新视觉语义）；
2. Vue 组件与 `src/design-system/index.js`；
3. 组件契约测试；
4. [03-code-design-mapping.md](03-code-design-mapping.md) 的映射表；
5. [04-ai-ui-maintenance.md](04-ai-ui-maintenance.md) 的巡检证据或验收条件；
6. Figma 组件描述与 Code Connect（连接器可用时）。

弃用组件至少保留一个版本周期，并在调用处提供替代组件和迁移示例。
