# PANGCHONG 商业化界面基准与提炼规则

版本：v0.9.11 · 2026-09-06  
范围：电商发现、DIY 工作台、购物车与结算的 Web 界面。

本文件只提炼公开设计系统的可迁移原则，不复制品牌资产、图片、文案或代码。参考对象包括 [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)、[Vercel Geist](https://vercel.com/geist/stack)、[Shopify Polaris](https://polaris.shopify.com/)、[IBM Carbon](https://carbondesignsystem.com/elements/color/overview/) 和项目已有的 BuildCores 交互审计。

### v0.4 官方基准复核（2026-08-14）

- [Apple Layout](https://developer.apple.com/design/human-interface-guidelines/layout)：把主事实放在首屏，使用分组、对齐和渐进披露降低扫描成本，并让布局适配窗口变化；本轮对应 `DsCartLineItem` 的编辑态/只读态与结算摘要层级。
- [Apple Focus and Selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection/)：焦点必须稳定、可见且与列表对象的选择关系清晰；本轮保留 44px 操作区域和 `:focus-visible` 语义环。
- [Geist Button](https://vercel.com/geist/button)：loading 不应通过替换按钮而丢失焦点，图标按钮必须有动作与对象明确的 `aria-label`；本轮作为 `DsButton`、`DsIconButton` 和结算提交态的验收依据。

### v0.7 官方基准复核（2026-08-14）

- [Atlassian Design Components](https://atlassian.design/components/)：把 Empty state、Progress indicator、Dynamic table、Pagination 和 Focus ring 作为独立可组合能力；本轮将 `DsPagination` 从页面按钮中抽离，并把订单列表的错误/空态与分页拆开。
- [Atlassian Empty state](https://atlassian.design/components/empty-state/)：空状态需要说明“没有数据”以及“下一步能做什么”；本轮订单空态提供直接去商品页的恢复动作。
- [IBM Carbon Notification](https://carbondesignsystem.com/components/notification/usage/)：区分 inline、toast、actionable 和 callout，错误消息要短、说明原因并给出用户动作；本轮商品/订单列表的失败状态使用 `DsAsyncState`，不会再伪装成空列表。

### v0.8 官方基准复核（2026-08-14）

- [Atlassian Progress tracker](https://atlassian.design/components/progress-tracker/)：把旅程中的已完成、当前和未开始节点分开表达；本轮将同一规则抽象为订单详情 `DsOrderTimeline`，并为取消/退款提供终止分支。
- [Atlassian Design Components](https://atlassian.design/components/)：Progress tracker 属于独立的状态指示器，和 Pagination、Inline message、Modal dialog 等能力组合使用；本轮订单详情将履约进度、就地错误和不可逆操作确认拆成独立组件契约。

### v0.9 官方基准复核（2026-08-14）

- [Atlassian Dynamic table](https://atlassian.design/components/dynamic-table/)：将分页、排序和行数据视为同一个数据表能力；本轮先抽取 `DsDataTable` 的可聚焦滚动和密度边界，再由后台页面组合 `DsPagination` 与业务查询。
- [Atlassian Design Components](https://atlassian.design/components/)：表格、Modal dialog、Inline message 和 Pagination 是可组合能力；本轮后台订单/商品页把运营反馈拆为 `DsAsyncState`、`DsAlert` 和 `DsDialog`，避免页面自建反馈分叉。

### v0.9.3 官方基准复核（2026-08-14）

- [Atlassian Radio](https://atlassian.design/components/radio/) 与 [IBM Carbon Radio accessibility](https://carbondesignsystem.com/components/radio-button/accessibility/)：选择控件应保留原生键盘、分组名称和选中状态；同一原则扩展到购物车删除确认与 DIY 筛选，所有动作必须有清晰的焦点和恢复路径。
- [IBM Carbon Radio usage](https://carbondesignsystem.com/components/radio-button/usage/)：选项卡片应让标签、说明和选择状态形成一体；`DsChoiceCard` 已用于结算，DIY 的筛选字段则统一进 `DsField`，避免页面自建 select/input 视觉分叉。
- [IBM Carbon Text input accessibility](https://carbondesignsystem.com/components/text-input/accessibility/) 与 [Text input usage](https://carbondesignsystem.com/components/text-input/usage/)：标签必须与控件程序化关联，帮助/错误文字通过 `aria-describedby` 暴露；字段尺寸和状态应按上下文统一。本轮认证、资料和商品搜索入口改为 `DsField` / `DsSearchField`。

### v0.9.7 官方基准复核（2026-08-14）

- [Vercel Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md)：交互控件优先使用语义 HTML，焦点必须可见，动画应尊重 `prefers-reduced-motion`，避免 `transition: all`；本轮 3D 配置器改为 semantic Token、`DsToggle` 和显式属性过渡。
- [IBM Carbon Text input accessibility](https://carbondesignsystem.com/components/text-input/accessibility/)：组件应保留原生键盘操作、标签关联与辅助文本播报；本轮将批量选择抽为 `DsCheckbox`，mixed 状态同步 DOM `indeterminate` 和 `aria-checked="mixed"`。
- [Atlassian Components](https://atlassian.design/components/)：复杂页面由可组合基础组件和业务模式构成；本轮将 3D 配置与购物车批量选择纳入组件契约，页面仅保留业务编排。

### v0.9.11 官方基准复核（2026-09-06）

- [Atlassian Components](https://atlassian.design/components/) 将 Empty state、Inline message、Modal dialog、Progress/Skeleton、Focus ring、Responsive 和 Design tokens 作为可组合能力；本轮继续保持 `DsAsyncState`、`DsAlert`、`DsDialog`、`DsSkeleton` 与 Token 层分离，并把导航当前态补成 `aria-current` 契约。
- [Atlassian Modal dialog](https://atlassian.design/components/modal-dialog) 与其无障碍指南强调模态交互必须让用户完成当前任务并可恢复；本轮 `DsDialog` 保留焦点回归和 Escape 关闭，购物车不可逆删除仍不允许降级成浏览器原生确认框。
- [Material accessibility](https://m1.material.io/usability/accessibility.html) 与 [Material buttons](https://m1.material.io/components/buttons.html) 将触控目标、焦点顺序和可替代操作作为基础约束；PANGCHONG 保留 Web 端 44px touch token（与 Apple Web 习惯一致），并在紧凑密度下只减少视觉留白，不缩小可操作区域。
- [Atlassian content design](https://atlassian.design/get-started/content-design) 强调清晰、统一、可本地化的界面语言；本轮新增/迁移文案必须进入 `copy:extract` 清单，错误、空态、部分成功和恢复动作不能只依赖颜色或图标。
- [WAI-ARIA Menubar Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/) 与 [Material menus](https://m2.material.io/develop/android/components/menu/) 都把打开后的初始焦点、键盘关闭和菜单项导航视为交互契约；本轮将同一原则落到 `AppNavbar`：移动菜单和搜索面板声明展开关系，焦点进入内容，Tab 不逃出菜单，Escape 后回到触发器。

## 1. 观察 → PANGCHONG 决策

| 公开模式 | 可迁移的行为原则 | PANGCHONG 的落地 | 不复制的部分 |
| --- | --- | --- | --- |
| Apple HIG 的层级、对齐、渐进披露 | 先突出当前任务与最重要事实，再展开次级信息；布局随屏幕变化 | 首屏只保留一个主行动；DIY 默认引导模式；配置明细可折叠 | Apple 的 Liquid Glass、图形资产与平台专属控件 |
| Vercel Geist 的高对比色阶与组件 Best Practices | 颜色按背景/边框/文本/状态角色管理；组件拥有明确使用边界和键盘行为 | `color.semantic.*` 作为业务唯一入口；Tabs、Dialog、IconButton 明确 `role`、焦点与键盘契约 | Geist 字体、品牌黑白比例和组件源码 |
| Shopify Polaris 的内容与状态语义 | 组件不仅定义外观，还定义文案、空态、错误态和恢复动作 | `DsAsyncState` 固定 loading/success/empty/error/partial；错误不再伪装成 0 件 | Polaris 的品牌色、后台导航结构和文案风格 |
| IBM Carbon 的 token 分层 | 原始色值与语义角色分离，主题变化只改语义别名 | JSON 单一源 → CSS/Tailwind；新增颜色先定义角色再消费 | Carbon 的组件命名、图标和品牌蓝 |
| BuildCores 配置器的高密度工作台 | 配置、兼容、功耗、价格和预览需要同屏协同，但不能同权重 | 工作台采用导航/画布/检查器三栏；兼容性与价格做摘要，规则按需展开 | 对方布局、商品图片和交互细节 |

## 2. 商业化质量门槛

### 2.1 任务层

- 每个视图只有一个首要动作，主按钮在视觉、DOM 顺序和键盘顺序中一致。
- 交易事实（价格、库存、兼容性、来源、配送）优先于装饰信息。
- 异步请求必须能区分五种状态：`loading`、`success`、`empty`、`error`、`partial`。
- 错误态必须给出恢复动作；不可把网络失败写成“暂无商品”或“0 件”。

### 2.2 视觉层

- 颜色、间距、圆角、阴影和动效只能来自 token；组件样式不得新增十六进制值。
- 交易正文最小 14px，输入控件最小 16px，辅助信息最小 12px。
- 普通文本对比度目标 ≥ 4.5:1；焦点环必须可见且不依赖绿色单一颜色传达状态。
- 触控目标默认 ≥ 44×44px；紧凑密度也只能缩小视觉留白，不能缩小可操作区域。

### 2.3 响应式层

- 390px：单列、筛选抽屉、底部或区块内主行动；不允许横向滚动承载核心交易信息。
- 768px：允许导航展开，但 DIY 仍维持单一主工作区。
- 1024px：商品/配置与摘要并列；摘要不重复完整明细。
- 1280px：内容最大宽度 1280px，工作台可使用导航/画布/检查器三栏。

## 3. 公开基准的证据使用方式

每次竞品或大厂界面观察都记录四列：

1. **观察**：只描述可见的布局、状态、交互和内容层级；
2. **证据**：链接、截图日期和页面状态；
3. **提炼**：可迁移的设计规则；
4. **边界**：不复制的品牌、资产、文案或代码。

AI 巡检只能引用本轮截图和 DOM 证据，不能凭“像 Apple/像 Vercel”给分。设计评审结论必须回写到 token、组件契约或页面验收条件中。

## 4. 当前 v0.9 组件覆盖

| 层级 | 组件 | 关键能力 |
| --- | --- | --- |
| Primitive | `DsButton`、`DsIconButton`、`DsField`、`DsCheckbox`、`DsToggle`、`DsSkeleton` | 统一尺寸、焦点、loading、禁用、选择项、mixed 状态和自动填充 |
| Feedback | `DsBadge`、`DsAlert`、`DsEmptyState`、`DsAsyncState`、`DsToast` | 状态语义、错误恢复、局部降级、结果反馈 |
| Surface | `DsCard`、`DsDialog`、`DsProductCard`、`DsCartLineItem` | 容器层级、焦点回归、Escape、产品事实、库存与数量交互；结算预览复用只读变体 |
| Navigation | `DsTabs` | tablist/tab/tabpanel、箭头键、禁用项与 URL 映射约定 |
| Business trust | `DsPriceProvenance`（兼容入口：`PriceProvenance`） | 价格口径、来源、更新时间与“待验证”降级 |
| Business decision | `DsCompatibilityStatus` | 通过、待核验、风险与阻断原因可见化 |
| Commerce flow | `DsStepIndicator`、`DsOrderSummary` | 当前步骤、不可跳过的未来步骤、已选商品和金额事实保持一致 |
| DIY decision | `DsDiyPartPicker` | 选择态、兼容性建议、规格摘要和价格依据集中在同一张候选卡 |
| Recovery feedback | `DsOrderSuccess` | 创建成功、支付中、支付失败和订单/购物恢复动作不丢失 |
| List navigation | `DsPagination` | 页码窗口、前后页禁用态、当前页语义和移动端触控尺寸统一 |
| Fulfillment status | `DsOrderTimeline` | 提交/支付/发货/完成状态，取消/退款分支，当前节点和时间证据统一 |
| Operations table | `DsDataTable` | 后台表格可聚焦滚动、响应式边界和语义 region 统一 |
| Commerce feedback | `DsDialog`、`DsToast` | 购物车删除确认使用可回焦对话框，库存/结算提示使用可关闭、可读出的 toast |
| Workbench controls | `DsField`、`DsButton`、`DsIconButton`、`DsToggle` | DIY 筛选、步骤导航、3D fallback、自动旋转和全局移动搜索共享输入、按钮与状态契约 |
| Search pattern | `DsSearchField` | 输入标签、提交动作和空查询行为统一；在不同密度下只改变 compact 变体 |
| Selection pattern | `DsCheckbox` | 全选、部分选择、批量删除共享原生 checkbox、mixed 状态和可见焦点 |

下一阶段：将 `DsDiyPartPicker` 的选件动作与筛选、比较、埋点契约进一步拆分，并把用户管理与仪表盘迁移到相同的状态/表格契约。

### v0.9.1 后台运营覆盖

- `admin/Users.vue`：按后台运营的高风险动作补齐确认对话框、成功/失败反馈和可恢复列表状态。
- `admin/Dashboard.vue`：把热销商品表格纳入 `DsDataTable`，让仪表盘与订单、商品、用户列表共享同一密度与移动端承载规范。

### v0.9.2 交易选择控件复核

- [Atlassian Radio](https://atlassian.design/components/radio/)：单选控件只允许一个选项；本轮将地址、配送和支付选择抽取为 `DsChoiceCard`，保留原生 radio 的表单语义。
- [IBM Carbon Radio button accessibility](https://carbondesignsystem.com/components/radio-button/accessibility/)：单选组应有可访问分组名称、键盘操作和状态表达；结算页沿用 fieldset/legend 组合契约。
