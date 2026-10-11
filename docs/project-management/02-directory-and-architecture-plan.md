# 目录与架构优化方案

> 原则：先建立边界和质量门禁，再逐模块迁移；不创建没有职责的空目录，不为“看起来整齐”而重写可用代码。

## 1. 本轮已完成的目录优化

2026-08-10 补充：已将被替代的静态网站和五人分工文档移入 `docs/archive/`；价格核验导入器从孤立的 `backend/scripts/` 并入 `app/cli/`；新增 `scripts/check_structure.py` 并接入本地与 CI 质量门禁，阻止旧入口和生成物回流。随后完成文档物理分类，把系统、前端、后端、网络安全、开发、部署、运维、产品、3D、规划与审计分别收口到职责目录。

```text
pangchong/
├── .github/
│   └── workflows/
│       └── quality-gate.yml          # PR/主分支自动质量门禁
├── docs/
│   ├── README.md                     # 全部文档统一索引
│   ├── architecture/                 # 系统、前端、后端、网络安全与数据边界
│   ├── development/                  # 本地环境与调试
│   ├── deployment/                   # 部署与托管服务
│   ├── operations/                   # 发布、回滚与运维清单
│   ├── product/                      # 商品、DIY、服务与演示材料
│   ├── 3d/                           # 3D 方案与资产流水线
│   ├── planning/                     # 项目与技术演进计划
│   ├── audits/                       # 特定时间点的审计快照
│   ├── data/                         # 核验数据与口径
│   ├── design-system/                # 设计系统文档
│   ├── archive/                      # 被替代的历史资料
│   └── project-management/           # 老板、团队、验收与提示词文档包
├── ecommerce/                        # 在线电商应用
│   ├── backend/
│   ├── frontend/
│   ├── database/
│   └── docker/
├── scripts/
│   ├── check_structure.py            # 目录边界与生成物检查
│   ├── quality-check.ps1             # Windows 本地质量门禁
│   └── quality-check.sh              # macOS/Linux 本地质量门禁
├── tools/
│   └── catalog/
│       ├── scraper.py                # 商品采集工具
│       ├── diy_parts.py              # DIY 数据生成工具
│       ├── requirements.txt          # 工具独立依赖
│       └── README.md                 # 使用与合规边界
├── CONTRIBUTING.md                   # 协作和完成定义
├── .editorconfig                     # 基础文本格式约定
└── README.md
```

文档已按职责完成物理迁移，并同步修复仓库内引用。`docs/README.md` 是唯一入口，`ecommerce/docs/` 不再维护第二套架构说明。

## 2. 当前架构的主要问题

| 问题 | 影响 | 优先级 |
| --- | --- | --- |
| 订单、支付、购物车业务逻辑集中在 API 路由 | 难以单测、复用和保证事务边界 | P0/P1 |
| DIY 定价信任客户端快照 | 可造成实际资金损失 | P0 |
| 第三方支付/物流与路由强耦合 | 沙箱、生产、失败降级难统一 | P0/P1 |
| 初始化 SQL、seed 和 Alembic 职责重叠 | 生产可能导入测试数据，schema 演进不可控 | P0 |
| 缺少 repositories/domain/integrations 明确边界 | 数据访问、业务规则和第三方调用混杂 | P1 |
| 文档分散且部分状态过时 | 老板、开发和测试使用不同基线 | P1 |

### 2.1 四名成员的架构解决方案

| 成员 | 负责解决的问题 | 解决方案 | 边界与交接 |
| --- | --- | --- | --- |
| 成员 1：后端/技术负责人 | 路由承载业务、客户端定价、支付耦合、事务不清 | 建立 Money/Pricing domain、order/payment service、repository 和支付 adapter；补状态历史与幂等约束 | 保持 API 兼容；DTO 交成员 2 联调；部署配置交成员 4 复核 |
| 成员 2：前端/体验 | 页面与 API/状态耦合、DTO 漂移、错误恢复分散、3D 包过大 | 先抽取 checkout/payment feature，统一状态模型与错误模式；关键 DTO 类型化；3D 动态加载 | 不复制服务端定价/支付规则；契约由成员 1 批准；商品字段由成员 3 确认 |
| 成员 3：商品/3D/运营 | 数据来源不明、资产不可追溯、seed 混用、物流模拟成功 | 建立 SKU 完成标准、价格/库存来源、资产授权版本和可重复导入；物流失败明确降级 | 商品 schema 交成员 1；后台交互交成员 2；超时/告警交成员 4 |
| 成员 4：QA/DevOps | 环境混用、无托管门禁、无恢复证据、发布风险与代码脱节 | 建立 CI、环境启动保护、staging、结构化日志/告警、备份恢复和 PR 风险门禁 | 不自行改变业务规则；部署/恢复由非作者复验；阻断不合规 PR |

详细路径、周任务和验收证据见[四人任务卡](task-cards/README.md)。架构协作遵循“主责人实现、相邻角色评审、成员 4 验证”的交付链；共享文件先确认主责，避免多人同时重写。

## 3. 后端目标结构

建议按业务模块渐进形成以下结构：

```text
ecommerce/backend/app/
├── api/                    # HTTP 解析、认证依赖、响应映射；不承载核心业务规则
├── core/                   # 配置、数据库、日志、安全、生命周期
├── domain/                 # 纯业务规则：Money、Pricing、OrderState、InventoryPolicy
├── services/               # 用例编排：CreateOrder、HandlePaymentCallback、RefundOrder
├── repositories/           # SQLAlchemy 查询与持久化边界
├── integrations/           # Alipay、物流、邮件、Storage 等适配器
├── models/                 # ORM 模型
├── schemas/                # API 请求/响应模型
└── main.py
```

### 依赖方向

```text
API → Services → Domain
        ↓
   Repositories / Integrations
        ↓
  Database / Third-party APIs
```

- `domain` 不导入 FastAPI、SQLAlchemy 或第三方 SDK。
- `services` 管理事务和用例，不直接拼 HTTP 响应。
- `repositories` 只负责查询和持久化，不决定业务价格或状态。
- `integrations` 对外部 API 做签名、超时、重试、错误映射和观测。
- `api` 只验证输入、调用 service、映射结果。

## 4. 推荐的渐进迁移顺序

### 阶段 A：交易安全边界

1. 新建 `domain/money.py` 和 `domain/pricing.py`，统一 Decimal/分单位与服务端定价。
2. 新建 `services/order_service.py`，迁移创建订单、库存锁定和订单快照。
3. API 保持原路径和响应结构，降低前端联调成本。
4. 每迁移一个行为，先补现有行为测试，再切换调用。

### 阶段 B：支付边界

1. 新建 `integrations/payments/base.py` 定义创建、验签、查询、退款接口。
2. 将支付宝实现放入单独适配器；沙箱和生产只通过配置切换。
3. 新建 `services/payment_service.py` 处理状态机、幂等、对账和退款。
4. 将第三方原始回调摘要存入 payment event，不把敏感原文写入普通日志。

### 阶段 C：数据访问和运营依赖

1. 抽取 order/product/payment repositories，显式处理 `FOR UPDATE` 和事务。
2. 将物流、邮件和 Storage 移入 `integrations`，禁止生产失败时返回模拟成功。
3. 增加 inventory ledger、order status history 和 audit log 的统一写入点。

## 5. 数据库与初始化边界

- Alembic 是生产 schema 演进的唯一来源。
- `database/seed.sql` 只用于本地演示，生产 Compose 不挂载。
- 商品基础数据应通过可重复导入命令或后台导入，不依赖数据库首次启动副作用。
- 管理员通过一次性、可审计的 bootstrap 命令创建，首次登录强制改密。
- migration 必须支持空库升级和已有数据升级，并在 CI 中验证单一 head。

## 6. 前端结构优化方向

当前前端无需大规模换框架，重点是业务边界与类型一致性：

```text
ecommerce/frontend/src/
├── api/                    # HTTP 客户端与按领域拆分的 API
├── components/             # 可复用展示组件
├── features/               # checkout、payment、catalog、account 等业务模块
├── router/
├── stores/                 # 新代码统一 stores；旧 store 逐步迁移
├── types/                  # API DTO 与领域类型
├── utils/                  # 无状态通用工具
└── views/                  # 路由页面，只做页面编排
```

迁移时先拆 `checkout` 和 `payment`，不要一次性移动全部页面。API schema 应通过 OpenAPI 生成或共享契约验证，减少 JS/TS 混用造成的漂移。

## 7. 文档结构治理

现阶段采用“统一入口、物理分类、单一真值来源”策略：

- `docs/architecture/`：当前系统、前端、后端、网络安全和数据边界。
- `docs/development/`、`deployment/`、`operations/`：分别承载开发、部署和发布运维。
- `docs/product/`、`3d/`、`planning/`、`audits/`：分别承载产品、3D、规划和审计。
- `docs/project-management/`：立项、任务、风险、验收和证据。
- `docs/archive/`：被当前实现替代、只供追溯的资料。
- `tools/*/README.md`：工具自身用法和输入输出，不放业务策划。

新文档必须包含用途、状态、负责人或适用读者。被替代的文档在文首标注替代关系，不直接删除历史依据。

## 8. 工程质量门禁

已新增统一门禁：

- 前端：`npm run typecheck`、`npm test`、`npm run build`。
- 后端：`compileall`、`pytest`、`alembic heads`。
- 本地：`scripts/quality-check.ps1` 或 `scripts/quality-check.sh`。
- CI：`.github/workflows/quality-gate.yml`。

后续一个月内应追加：API 集成测试、依赖审计、镜像扫描、migration 空库/升级测试和最小 E2E。

## 9. 架构变更规则

- 单个 PR 只迁移一个用例或一个集成边界。
- 先保持 API 兼容，再讨论版本化；不得在无迁移计划时删除字段。
- 业务状态变化必须有数据库约束、历史记录和幂等策略。
- 第三方调用必须定义超时、重试边界、失败降级和告警。
- 新目录只有在至少承载一个真实模块时创建，禁止空目录式“架构优化”。
- 每项架构变更都要回答：解决什么风险、如何验证、如何回滚。

## 10. 一个月后的目标结构成熟度

本月不要求全部代码迁移到目标结构。验收目标是：订单创建和支付回调两个最高风险用例完成分层，其他模块仍可保持现状；质量门禁、文档入口和责任边界已经稳定，后续成员可以按同一模式继续迁移。
