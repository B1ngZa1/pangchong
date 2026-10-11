# PANGCHONG Design System v0.9.11

## 1. 设计原则

- **性能可信**：优先展示真实规格、来源、稳定性与兼容性证据。
- **主任务唯一**：同一区域只允许一个最高强调级别的行动。
- **绿色有职责**：虫翼绿用于主行动、当前选择和品牌强调；成功状态必须同时有文字或图形。
- **暗色有层次**：画布、表面、悬浮层逐级变亮，不靠随机灰色堆叠。
- **降级仍可成交**：图片、3D、行情或推荐失败时，基础购买链路仍成立。

## 2. Token 架构

Token 唯一源文件为 `pangchong.tokens.json`。执行 `npm run design:tokens` 生成 CSS 变量与 Tailwind 映射，CI 使用 `npm run design:tokens:check` 防止漂移。Figma 同步读取 `npm run design:figma` 生成的 `public/design-system.figma-manifest.json`，其中固化 collection、mode、scope、alias、WEB code syntax 与组件源码路径。

### 2.1 颜色

| 角色 | Token | 当前值 | 用法 |
| --- | --- | --- | --- |
| 画布 | `color.semantic.background.canvas` | `#020617` | 页面背景 |
| 表面 | `color.semantic.background.surface` | `#0f172a` | 卡片、区域 |
| 抬升表面 | `color.semantic.background.elevated` | `#1e293b` | 输入、菜单、嵌套卡片 |
| 主文本 | `color.semantic.text.primary` | `#f8fafc` | 标题、金额、关键结论 |
| 次文本 | `color.semantic.text.secondary` | `#cbd5e1` | 正文 |
| 弱文本 | `color.semantic.text.muted` | `#94a3b8` | 辅助说明；不得承载唯一关键事实 |
| 主行动 | `color.semantic.action.primary` | `#44d62c` | 每区唯一主按钮 |
| 焦点 | `color.semantic.border.focus` | `#86efac` | 键盘焦点，不得移除 |

禁止在新业务代码中直接写 `#44d62c`、`#020617` 或随意 `rgba(...)`。需要新颜色时，先定义角色，再定义值。

页面主题 Token 只用于保留明确的品牌场景，不得替代语义 Token：

| 主题 | Token | 使用页面 |
| --- | --- | --- |
| 首页氛围 | `color.theme.home.deep / stage / cyan` | `Home.vue` 的深色渐变、商品媒体和冷色氛围光 |
| 门店浅色 | `color.theme.store.canvas / text / muted / surface / border / action / link` | `Store.vue` 的线下门店浅色主题 |
| 服务中心 | `color.theme.service.*` | `Services.vue` 的双层深色协议中心、透明叠层和打印态 |

主题 Token 的源值仍只在 `pangchong.tokens.json` 出现；页面 CSS 通过生成的 `--pc-color-theme-*` 变量消费。

### 2.2 字体

- 字体栈：Noto Sans SC → 系统字体。
- 展示标题：`font.size.display`，只用于首页/专题首屏。
- 页面标题：30–36px；区块标题：20–24px；正文：16px；紧凑交易正文：14px；辅助标签：12px。
- 金额、兼容性结论和错误信息不能使用 10px 文本。
- 中文正文行高 1.5–1.75；三行以上禁止紧行高。

### 2.3 间距、圆角、阴影

- 4px 基础网格：`space.1` 到 `space.24`。
- 页面区块间距默认 48–64px；卡片内边距默认 24px；紧凑列表 16px。
- 默认圆角 8px，主要卡片 12px，促销胶囊或标签才使用 full。
- 阴影只表达层级，不装饰普通列表。暗色模式优先边框 + 小阴影。

### 2.4 动效

- 高频反馈 120ms，微交互 160ms，常规状态变化 200ms，区块进入 320ms，重点媒体 450ms，氛围层 700ms；装饰性 spinner 800ms。
- 位移动画一般不超过 8px。
- `prefers-reduced-motion` 下所有 Token 时长降为 1ms；3D 自动旋转关闭。

### 2.5 透明度

透明度同样属于 Token，不允许在组件中散落 `0.42`、`0.64` 或 `0.74` 等状态值。主题渐变如确需不同层级，必须基于 `rgb(var(--pc-color-*-rgb) / alpha)`，并在页面契约中说明用途：

| Token | 用途 |
| --- | --- |
| `opacity.status` | Badge/Alert 的状态背景 |
| `opacity.disabled` | 禁用控件与不可用内容 |
| `opacity.muted` | 图标按钮等弱化控件 |
| `opacity.overlay` | Dialog 等遮罩层 |
| `size.control.touch` | 关闭、删除等图标动作的最小 44×44px 触控目标 |

### 2.6 响应式

| 断点 | 设计动作 |
| --- | --- |
| 390–639 | 单列；筛选抽屉；底部或区块内主行动；输入 16px |
| 640–767 | 两列卡片；服务承诺可横滑 |
| 768–1023 | 导航展开；DIY 仍以单主工作区为主 |
| 1024–1279 | 商品侧栏与结果并列；购物车双栏 |
| ≥1280 | 最大内容宽 1280px；禁止无限拉宽正文 |

## 3. 基础组件库

当前代码位于 `src/design-system/components/`，通过 `@/design-system` 引用。

### `DsButton`

变体：`primary / secondary / ghost / danger`；尺寸：`sm / md / lg`；支持 `loading / disabled / block`。

```vue
<DsButton size="lg" :loading="saving">保存配置</DsButton>
<DsButton variant="secondary">返回</DsButton>
```

规则：每个视觉区域最多一个 `primary`；危险动作不得只靠红色，按钮文案必须描述结果。

### `DsCard`

支持 `padding="none|sm|md|lg"` 和 `interactive`。普通信息容器不要使用 interactive；可点击卡片必须保证整卡可聚焦或内部有明确链接。

### `DsBadge`

语气：`neutral / accent / success / warning / danger / info`。状态必须有文字，不能只显示色点。

### `DsField`

统一 label、hint、error、required、disabled 与 `v-model`。错误就地出现并用 `role=alert`；不要使用 placeholder 代替 label。

### `DsEmptyState`

用于业务空状态与可恢复失败态的容器。系统失败标题必须说“加载失败”，不能写成“暂无商品”。视觉插槽只能使用真实图标或资产。

### `DsMenu`

用于账号、工具和上下文操作菜单。通过 `v-model:open` 控制状态，`trigger` slot 接收带有 `aria-haspopup`、`aria-expanded` 和 `aria-controls` 的触发器属性；默认 slot 的菜单项必须使用 `role="menuitem"`。打开后聚焦首项，支持 Arrow/Home/End 导航，Escape 和点击外部关闭并恢复触发器焦点。

## 4. 业务组件推进

v0.9.2 新增 `DsChoiceCard`：用于结算地址、配送方式和支付方式选择。每组由原生 radio 语义、可点击整卡、选中/禁用/焦点状态和描述文本组成；分组必须提供 fieldset/legend 或等价的可访问名称。

已落地：`DsIconButton`、`DsMenu`、`DsToast`、`DsDialog`、`DsProductCard`、`DsPriceProvenance`、`DsCompatibilityStatus`、`DsCartLineItem`、`DsAsyncState`、`DsStepIndicator`、`DsOrderSummary`、`DsPriceSummary`、`DsDiyPartPicker`、`DsOrderSuccess`、`DsPagination`、`DsOrderTimeline`、`DsDataTable`；`DsField` 同时覆盖输入框、选择框和多行文本框，其中 `DsCartLineItem` 支持购物车编辑态与结算只读紧凑态，订单摘要复用相同的交易事实。

结算地址使用 `DsField` 的统一错误、禁用、自动填充和选择项契约；订单成功反馈使用 `DsOrderSuccess`，支付创建失败保留在对话框内并提供重试路径。

列表分页使用 `DsPagination`，页码、上一页/下一页、省略号和 `aria-current="page"` 由组件统一管理；切换筛选条件时必须重置到第一页，接口错误不能伪装成空列表。

订单详情使用 `DsOrderTimeline` 展示提交、支付、发货、完成/取消/退款的履约事实；当前节点使用 `aria-current="step"`，未知时间不虚构日期。支付和取消失败使用 `DsAlert` 就地反馈，取消等不可逆动作使用 `DsDialog` 确认，不使用浏览器 `alert/confirm`。

后台订单和商品列表使用 `DsDataTable` 提供可聚焦的横向滚动区域，结合 `DsAsyncState`、`DsPagination` 和 `DsDialog` 管理运营任务；390px 下隐藏固定侧栏，改用可横滑的后台导航，不让主内容被压缩到不可读宽度。

业务组件必须先列出：变体、数据状态、键盘行为、文案插槽、移动端规则和埋点事件，再进入实现。

## 5. 状态规范

每个异步区域必须声明：

1. loading：使用 skeleton，保留布局尺寸；
2. success：数据与操作完整；
3. empty：请求成功但业务数据为空；
4. error：请求失败，包含原因级别、重试和替代路径；
5. partial：部分数据成功，例如价格不可用但商品仍可购买。

错误、警告、未验证、兼容和不兼容必须是不同状态，不能都映射为黄/绿二元结果。

## 6. 无障碍底线

- 所有交互可用键盘完成，焦点清晰可见。
- 图标按钮必须有可访问名称；图片替代文本说明目的而不是文件名。
- Modal 打开后焦点进入、背景 inert、Esc 关闭、关闭后焦点回到触发器。
- 动态结果、购物车总价、DIY 兼容摘要使用合适的 live region，避免重复播报。
- 颜色不是状态的唯一载体；普通文本对比度达到 4.5:1。

### v0.9.1 后台运营补充

用户管理和仪表盘也纳入同一套契约：用户筛选、详情、状态变更沿用 `DsAsyncState`、`DsDataTable`、`DsPagination`、`DsDialog` 与 `DsAlert`；仪表盘趋势、状态和热销商品在请求失败时保留明确的重试入口。
