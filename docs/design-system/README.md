# PANGCHONG 前端设计系统与体验治理

当前版本：**v0.9.12**。v0.1 的 token 单一源、基础组件、文本提取和 AI 巡检机制已保留；v0.9.11 新增可审计的 Figma handoff manifest、High Contrast mode 映射和大厂基准到代码契约的同步记录，v0.9.12 补齐 DIY 移动端韧性视觉回归的确定性夹具和验收证据。

这套资料把现有黑色硬件风格保留下来，并把它从“页面内零散样式”升级为可维护的产品设计语言。它覆盖品牌、商品发现、DIY 装机、购物车与结算，不直接复制任何参考网站的视觉资产或代码。

## 交付物

| 内容 | 入口 | 用途 |
| --- | --- | --- |
| 现状审计与前端优化路线 | [01-ui-audit-and-optimization.md](01-ui-audit-and-optimization.md) | 按页面、优先级和验收指标推进 |
| Design Token 与组件规范 | [02-design-system-spec.md](02-design-system-spec.md) | 设计与开发共同使用的视觉语义 |
| 代码—设计系统映射 | [03-code-design-mapping.md](03-code-design-mapping.md) | 说明 Token、Tailwind、Vue 组件与业务页面的关系 |
| AI 定期体验维护 | [04-ai-ui-maintenance.md](04-ai-ui-maintenance.md) | 固定证据、评分、问题分级与闭环方式 |
| 商业化界面基准 | [05-commercial-benchmark.md](05-commercial-benchmark.md) | 从 Apple、Geist、Polaris、Carbon 等公开系统提炼可迁移规则 |
| 组件契约 v0.9.11 | [06-component-contracts.md](06-component-contracts.md) | 状态、可访问性、代码/Figma 映射与变更检查单 |
| 文案清单与修改流程 | [content/README.md](content/README.md) | 提取、审校、批量写回、漂移检查 |
| 商业化验收矩阵 | [07-commercial-acceptance-matrix.md](07-commercial-acceptance-matrix.md) | 页面、状态、响应式、可访问性与外部条件的证据化门槛 |
| 当前验收记录 v0.9.10 | [08-v0.9.10-verification.md](08-v0.9.10-verification.md) | 运行时、构建、视觉证据与下一轮风险 |
| Figma handoff 与权限边界 | [09-figma-handoff.md](09-figma-handoff.md) | Collection、变量、组件、Code Connect 与连接器恢复流程 |
| 当前验收记录 v0.9.11 | [10-v0.9.11-verification.md](10-v0.9.11-verification.md) | Token 漂移修复、manifest 与 Figma 证据边界 |
| 当前验收记录 v0.9.12 | [11-v0.9.12-diy-mobile-resilience-verification.md](11-v0.9.12-diy-mobile-resilience-verification.md) | DIY 360 / 390 / 430px 韧性视觉回归、API 隔离和截图证据 |
| 当前界面证据 | [audit-assets](audit-assets) | 2026-08-10 桌面与移动端截图 |

## 代码入口

- Token 源文件：`ecommerce/frontend/src/design-system/tokens/pangchong.tokens.json`
- Token 生成器：`ecommerce/frontend/scripts/build-design-tokens.mjs`
- 独立展示页 Token 输出：`ecommerce/frontend/public/design-system.tokens.css`（由同一生成器维护）
- Vue 基础组件：`ecommerce/frontend/src/design-system/components/`
- 统一导出：`ecommerce/frontend/src/design-system/index.js`
- 文案工具：`ecommerce/frontend/scripts/ui-copy.mjs`
- Figma handoff 生成器：`ecommerce/frontend/scripts/build-figma-handoff.mjs`

## 设计方向

1. **可信的性能实验室**：保留黑色画布、虫翼绿和硬件影像，但减少不承载任务的装饰。
2. **交易信息优先**：价格、库存、兼容性、来源、售后和主行动始终比氛围更重要。
3. **3D 是增强层**：3D 加载失败不能阻断选件、核价、购物车和结算。
4. **渐进呈现**：新手先看到结论与下一步，参数和证据按需展开。
5. **语义驱动**：代码使用 `background / text / border / action / status` 等角色，不直接依赖某个十六进制颜色。
6. **可调节体验**：高对比度偏好可由用户主动切换并持久化，兼容迁移中的 Tailwind 页面与新 DS 组件。

## 参考来源与抽象结果

| 参考 | 观察到的模式 | PANGCHONG 采用 | 明确不复制 |
| --- | --- | --- | --- |
| [Apple Mac](https://www.apple.com.cn/mac/) / [Apple 选购 Mac](https://www.apple.com.cn/shop/buy-mac) | 先给价值结论，再分层展示比较、帮助和购买 | 首页首屏只保留一个主目标；商品页先给“如何选” | 版式、图像、文案语气和品牌视觉 |
| [Razer 商品列表](https://www.razer.com/shop/pc/gaming-laptops) | 筛选、排序、比较、规格和购买动作处于同一任务链 | 商品卡固定展示 3–5 个关键规格并支持比较 | 雷蛇视觉资产与卡片外观 |
| [Dell Alienware 台式机](https://www.dell.com/zh-cn/shop/scc/scr/desktops/appref%3Dalienware-product-line) | 起始价含义、配置差异和可定制入口明确 | 区分“起售价 / 当前配置价 / 核验价”，并解释价格口径 | 促销结构、销售话术与页面布局 |
| [BuildCores](../project-management/06-buildcores-interaction-audit.md) | 选件会同步影响成本、兼容性、功耗与 3D | DIY 使用单一状态源和实时摘要 | 高密度筛选、广告和未成熟桌面搭建 |
| [IBM Carbon](https://carbondesignsystem.com/elements/color/overview/) | 角色 Token、暗色分层和完整交互状态 | `semantic` Token + 表面层级 + focus/disabled 状态 | IBM 的品牌蓝和组件实现 |
| [Ant Design](https://ant.design/docs/spec/introduce/) | 抽象稳定、重复的组件与页面模式 | 先沉淀基础组件，再迁移业务组件 | 企业后台视觉风格 |

## 变更原则

- 新页面必须先使用语义 Token 和设计系统基础组件。
- 旧页面按用户影响逐步迁移，不做一次性全量重写。
- 所有设计改动必须有页面截图、状态清单和验收条件。
- 文案、价格、兼容性和错误状态都属于设计系统范围，不只处理颜色和圆角。
