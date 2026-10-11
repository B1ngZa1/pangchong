# PANGCHONG Figma Handoff v0.9.11

这份文档把代码设计系统整理成可在 Figma 连接器恢复后执行的同步包。当前不宣称已经写回 Figma：仓库没有目标 `fileKey`，当前 Figma 账号为 Starter 的 View seat，只能完成只读身份确认。

## 当前源与产物

| 层 | 文件 | 规则 |
| --- | --- | --- |
| 唯一源 | `ecommerce/frontend/src/design-system/tokens/pangchong.tokens.json` | 只在这里修改原始值、引用和描述 |
| CSS/Tailwind | `src/design-system/tokens/tokens.css`、`tailwind-theme.js`、`public/design-system.tokens.css` | `npm run design:tokens` 生成，禁止手改 |
| Figma handoff | `public/design-system.figma-manifest.json` | `npm run design:figma` 生成，`design:figma:check` 检查漂移 |
| 组件源码 | `src/design-system/components/` | Vue 组件是运行时行为的事实来源 |
| 规范与契约 | `docs/design-system/02*.md`、`06*.md` | 记录语义、状态、无障碍和迁移边界 |

当前统计：179 个 Token；175 个可映射 Figma 变量；4 个 Effect Style；37 个组件源码文件，其中 35 个已进入 Figma handoff 组件入口（含 `DsEmptyState`、`DsMenu`、`DsPriceSummary` 与 `PriceProvenance` 兼容入口）。`font.size.display` 使用 `clamp()`，在 manifest 中保留为 `unsupported`，不伪装成静态 Figma FLOAT。

## Figma Collection 计划

| Collection | Mode | 变量范围 | 关键约束 |
| --- | --- | --- | --- |
| `Primitives` | `Value` | 原始颜色 | 变量 scope 为空，只被语义层 alias |
| `Color` | `Default` / `High Contrast` | `color.semantic.*` | 背景、文字、边框使用精确 scope；High Contrast 复现代码中的 3 个覆盖值 |
| `Theme` | `Value` | `color.theme.*` | 只用于首页、门店、服务中心等明确主题场景，不能替代语义色 |
| `Layout` | `Value` | space、size、radius、opacity、breakpoint、zIndex | 仅给可绑定的 Figma 属性设置 scope |
| `Typography` | `Value` | font family、size、line-height、weight | `clamp()` 仅保留源码证据，需在 Figma 中人工选择展示档位 |
| `Motion` | `Value` | duration、easing | duration 以毫秒 FLOAT 传递，easing 以 STRING 记录 |
| `Effects` | `Value` | shadow | 作为 Effect Style 来源，不创建 COLOR/FLOAT 变量替代阴影 |

manifest 中每个变量同时记录：DTCG `sourcePath`、Figma `name`、类型、scope、`var(--pc-...)` code syntax、Default/High Contrast mode 值和描述。这样 Dev Mode、代码审查与 AI 巡检使用同一命名事实。

## 组件库分层

Figma 页面按以下顺序建立，组件创建前必须先搜索可复用库组件：

1. `Cover`
2. `Getting Started`
3. `Foundations`
4. `---`
5. `Components/Button`、`IconButton`、`Field`、`SearchField`、`Toggle`、`Checkbox`、`Badge`、`Alert`、`Toast`、`Skeleton`
6. `Patterns/AsyncState`、`Card`、`Dialog`、`Tabs`、`ChoiceCard`、`ProductCard`、`CartLineItem`
7. `Patterns/Commerce`、`Patterns/DIY`、`Patterns/Operations`
8. `---`
9. `Utilities`

组件的 Figma 名称、Vue 源码路径和 Code Connect label 已写入 manifest。Variant 轴遵循组件契约：状态、尺寸、语气是变体；图标和插槽使用 `INSTANCE_SWAP`，不为每个图标制造 variant。

## 大厂基准 → PANGCHONG 决策

| 公开系统 | 可迁移观察 | 本系统落点 |
| --- | --- | --- |
| [Apple Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/) 与 [Focus and Selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection/) | 焦点必须可定位；信息不能只靠颜色传达；控件要适配键盘与辅助技术 | `color.semantic.border.focus`、44px touch token、`DsIconButton` label、`DsDialog` focus return、状态文字与图形并存 |
| [IBM Carbon Color](https://carbondesignsystem.com/elements/color/overview/) | 角色 Token 与层级 Token 取代硬编码值；暗色模式用层级组织空间；焦点有统一角色 | `Color` semantic aliases、`Layout` collection、canvas/surface/elevated 三层、统一 focus token |
| [Vercel Geist Typography](https://vercel.com/geist/typography) 与 [Colors](https://vercel.com/geist/colors) | 类型按用途组合字号/行高/字重；背景、组件背景、边框、文本分工明确 | `font.*` 规模、组件状态映射、页面只消费语义 Token；主题色不泄漏到通用组件 |

这些规则是抽象提炼，不复制品牌颜色、资产、文案或布局。AI 评审只能用本轮页面截图与 DOM 证据验证它们。

## 连接器恢复后的执行顺序

1. 用户提供 `https://figma.com/design/<fileKey>/...` 并确认编辑权限。
2. 只读执行 `get_metadata`，重建页面、变量、样式、组件的 state ledger。
3. 对目标文件先执行 `get_libraries(fileKey)`，再分别搜索 `button`、`field`、`card`、`product card`、`data table`。
4. 对有兼容属性与 Token 模型的组件优先复用；不兼容时本地重建或 wrapper，不直接 detach 远程组件。
5. 先写入 collections/variables/styles，再逐组件创建、`get_metadata`、`get_screenshot`，最后做 Code Connect。
6. 完成 Phase 4 的 accessibility、命名、绑定和页面截图审计后，才把 `syncStatus.targetFileKey` 写入 manifest。

## 当前差距与边界

- 代码 → Figma：已完成可审计 manifest，等待目标文件与编辑权限。
- Figma → 代码：无法在没有 fileKey 的情况下读取现有页面/库，因此没有虚构“冲突已解决”。
- 视觉同步：本轮只能以仓库实际页面与公开系统规则为依据；连接器恢复后补 foundations/component screenshots。
- 任何新的 Token、组件或页面都必须先更新 manifest 生成结果，再进入 Figma 同步。
