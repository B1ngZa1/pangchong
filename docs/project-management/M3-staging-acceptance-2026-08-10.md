# M3 staging 验收记录（2026-08-10）

> 验收时区：Asia/Shanghai  
> 验收范围：Supabase 项目恢复、远端迁移与核心表、仓库质量门禁、M3 staging 证据  
> 关联任务：OPS-301、OPS-302、OPS-303、QA-301  
> 关联风险：R-03、R-07、R-08、R-09  
> 总结论：**No-Go；不得接收真实交易。数据库子项修复后通过，但 M3 staging 整体验收不通过。**

## 1. 验收对象

| 字段 | 实际值 |
| --- | --- |
| 仓库基线 | `51368d77e1f1`；分支 `master`；工作区有未提交改动，因此不能作为可追溯 release 制品 |
| Supabase 项目 | `pangchong` / `fprinlepgtrixxnmvqsj` |
| 项目 URL | `https://fprinlepgtrixxnmvqsj.supabase.co` |
| 区域 / 数据库 | 东京 `ap-northeast-1` / PostgreSQL 17.6 |
| 最终项目状态 | `ACTIVE_HEALTHY` |
| 仓库 Alembic head | `a9c3e7d5b102`，单头 |
| 远端 Alembic 版本 | `a9c3e7d5b102` |
| 正式验收人 | 未提供；本记录为技术复核证据，仍需非作者验收并签字 |

## 2. 恢复与最小修复记录

1. 首次读取项目时状态为 `RESTORING`；未重复触发恢复。随后项目转为 `ACTIVE_HEALTHY`，数据库可查询。
2. 恢复后远端 Alembic 为 `f2a8c5d1e904`，缺少仓库字段 `products.asset_source_url`。应用远端迁移 `alembic_schema_b7e1c4a9d203`，新增一个可空 `varchar(500)` 字段并原子更新 Alembic 版本。
3. 验收期间仓库 head 更新为 `a9c3e7d5b102`；待该快照 67 个后端测试全部通过后，应用同名远端迁移，新增订单幂等与 DIY 快照引用所需的四个可空字段及 `uq_orders_user_idempotency_key` 唯一约束。
4. 未修改业务数据、RLS 策略、浏览器角色权限、索引或 Storage 对象；未为满足验收而补造 staging、告警或恢复演练证据。

远端 Supabase migration ledger 最终为：

| 时间版本 | 名称 |
| --- | --- |
| `20260622184819` | `harden_supabase_access_and_storage` |
| `20260622185133` | `alembic_schema_e6f4a1b9c207` |
| `20260622185255` | `fix_supabase_advisors_f2a8c5d1e904` |
| `20260810013833` | `alembic_schema_b7e1c4a9d203` |
| `20260810014452` | `alembic_schema_a9c3e7d5b102` |

Supabase ledger 没有逐条镜像早期 Alembic revision；早期环境曾以初始化 SQL/合并迁移建立。为避免仅凭名称误判，本次以 `public.alembic_version` 和实时 schema 逐表复核为准。

## 3. 迁移与核心表比较

仓库 revision 链为：

`ad260c2f895d -> 8d1a9b4c2f6e -> c4b7e2a9d130 -> e6f4a1b9c207 -> f2a8c5d1e904 -> b7e1c4a9d203 -> a9c3e7d5b102`

最终比较结果：

| 检查项 | 实际结果 | 判定 |
| --- | --- | --- |
| 9 张核心表 | `users`、`user_addresses`、`categories`、`products`、`cart_items`、`orders`、`order_items`、`price_history`、`audit_logs` 均存在 | 通过 |
| 核心表列集合 | 对照当前模型、`database/init.sql` 和 Alembic head 后，缺失列 0、额外列 0 | 通过 |
| 商品素材来源 | `products.asset_source_url varchar(500) null` 已存在 | 通过 |
| 订单幂等 | `orders.idempotency_key`、`request_fingerprint` 及 `UNIQUE (user_id, idempotency_key)` 已存在 | 通过 |
| DIY 快照引用 | `order_items.configuration_id`、`configuration_version` 已存在 | 通过 |
| 数据量 | 14 个分类、96 个商品；用户 0、订单 0 | 数据恢复通过；交易 staging 数据未建立 |
| Compose 专用视图 | `database/init.sql` 定义的 `order_details`、`product_sales_stats` 不在远端，且应用代码未引用 | 非核心差异；本次不补建 |

## 4. 安全、Storage 与数据质量

- 9 张核心表全部启用 RLS；`anon`、`authenticated` 对这些表没有表级权限，符合 FastAPI 后端独占数据访问的边界。
- Security Advisor 只有“RLS 已开启但无 policy”的 `INFO`。这是当前后端独占、默认拒绝设计的预期结果，不为消除提示而开放浏览器访问。参考 [Supabase linter 0008](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy)。
- Performance Advisor 仅报告恢复后尚未使用的索引，均为 `INFO`；没有足够运行样本支持删除索引，本次保持不变。
- `catalog-images`（5 MB，PNG/JPEG/WebP）和 `catalog-models`（20 MB，GLB/octet-stream）桶均存在且配置正确，但两个桶对象数均为 0。
- 96 个商品全部 active 且有 `image_url`，但 `price_source_url`、`price_checked_at`、`model_3d_url`、模型授权及素材来源的完整记录均为 0。目录数量恢复不等于首发 SKU 来源验收通过。

## 5. 自动验证结果

| 验证 | 结果 |
| --- | --- |
| 后端编译 | 通过（Python 3.12.6） |
| 后端测试 | 67/67 通过；含服务端计价、库存、重复提交幂等和生产启动保护 |
| Alembic | 单 head：`a9c3e7d5b102` |
| 前端类型检查 | 通过 |
| 前端测试 | 12 个文件、72/72 通过 |
| 前端生产构建 | 通过；`Product3DViewer` 产物约 634 kB，保留为性能跟踪项 |
| 远端 schema 复核 | Alembic 版本、核心列、唯一约束、RLS、权限与 bucket 均通过 |

## 6. M3 验收与 No-Go 阻断项

| M3 项 | 证据 | 结论 |
| --- | --- | --- |
| OPS-301 独立 staging | 未发现可由测试人员访问的应用 staging URL；Nginx 配置仅监听 HTTP；TLS 目录只有占位文件；后端 Dockerfile 未切换非 root 用户；没有 staging 专用凭证证据 | **No-Go blocker** |
| OPS-302 可观测性 | 仓库及已提供材料中没有请求 ID、结构化应用日志、5xx/支付失败/备份失败告警送达记录 | **No-Go blocker（R-08）** |
| OPS-303 备份恢复 | 本次暂停项目原地恢复成功，但不是“从空隔离环境恢复数据库和资产”的演练；无资产对象、RPO、RTO、值班人或恢复耗时记录 | **No-Go blocker（R-07，P0）** |
| QA-301 多端回归 | 只有本地自动化门禁；无部署后关键 API、主流浏览器及 360/390/430 px 真机/浏览器回归证据 | **No-Go blocker** |
| 首发 SKU 与资产 | 96 个商品缺少价格核验时间/来源，Storage 无图片或 GLB 对象，未形成 20–50 个来源、授权和售后信息完整的首发集合 | **No-Go blocker（R-09）** |
| 发布可追溯性 | 工作区有大量未提交改动，当前快照没有不可变版本号或部署制品，也没有非作者签字 | **No-Go blocker** |
| 全局 P0 门槛 | 风险登记仍将 R-01 至 R-05、R-07 标为未关闭；按“没有证据即未通过”原则，不得接收真实款项 | **No-Go blocker** |

## 7. 解除条件与复验

1. 成员 4 提供独立 HTTPS staging 地址、TLS 检查、staging 独立凭证、非 root/非 reload 运行证据，并绑定可追溯提交或制品版本。
2. 成员 4 完成告警故障注入，留存 5xx、支付失败和备份失败的送达记录。
3. 成员 4 与非作者从空隔离环境恢复数据库和 Storage，记录恢复点、RPO、RTO、耗时、数据校验和负责人。
4. 成员 3 选择 20–50 个首发 SKU，补齐并双人复核价格来源、检查时间、库存、图片/模型授权、素材来源和售后责任。
5. 测试人员在已部署 staging 完成关键 API、桌面端与 360/390/430 px 回归，提交缺陷清单。
6. 项目负责人按 `03-risk-and-acceptance.md` 关闭全部 P0，并由非作者复验；项目负责人和测试/运维负责人签字后再安排下一次 M3 复审。

在上述条件完成前，Supabase 数据库可继续用于 staging 整备，但本记录不授权公开上线、真实支付或真实用户数据导入。
