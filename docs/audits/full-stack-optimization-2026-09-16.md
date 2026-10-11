# 全栈优化验收（2026-09-16）

> 状态：本地候选版本已验证；不构成真实交易上线批准。
> 范围：界面文案、无障碍弹层、DIY 3D 预览与降级、素材治理、启动性能、后端生命周期和生产数据库迁移顺序。

## 已交付

| 范围 | 结果 | 可复核入口 |
| --- | --- | --- |
| 界面与文案 | 商品、购物车、订单、DIY、门店和管理素材页采用一致的中文任务文案；关键操作、空态与 3D 降级说明可读 | [文案规范](../design-system/content/ui-copy.style.md)；`npm run copy:check` |
| 可访问性 | 基础对话框改用 Reka UI 的 Dialog 原语，包含标题/描述关联、焦点管理、Esc 和遮罩关闭 | `frontend/src/design-system/components/DsDialog.vue`；对话框组件测试 |
| 3D 体验 | Three.js 仅在 DIY 路由加载；WebGL、模型或节点合同失败时自动回到可继续核价和结算的清单模式 | [3D 资产流水线](../3d/asset-pipeline.md)；[素材选型](../3d/asset-sourcing.md) |
| 性能 | 本地启动测量覆盖桌面与 360/390/430px 视口；3D 代码块独立于常规商城首屏 | `frontend/scripts/measure-startup.mjs`；`npm run perf:startup` |
| 后端运行时 | FastAPI 使用 lifespan 管理连接生命周期；JWT 使用时区感知的过期时间；素材上传保留 HTTP 字段兼容性并消除 Pydantic 命名空间告警 | `backend/app/main.py`、`backend/app/core/security.py`、`backend/app/api/admin.py` |
| 生产数据库 | Compose 先做安全预检，再启动 PostgreSQL/Redis，随后运行一次 `alembic upgrade head`；API 等待迁移成功，生产不再挂载 schema 初始化 SQL 或 demo 数据 | `ecommerce/docker-compose.prod.yml`；`python scripts/verify_production_config.py` |

## 本地验证记录

- 浏览器主路径：DIY 配置页的 3D 说明与清单回退、门店页文案、管理员素材许可说明，以及购物车删除确认对话框均已在本地运行环境检查；DIY 与门店页的浏览器控制台没有 error。
- API 主路径：本地 PostgreSQL 迁移并导入开发目录后，`/health` 返回 `healthy`，商品目录返回 96 条演示商品，管理员登录可获得 bearer token。
- 生产配置：`python ecommerce/scripts/verify_production_config.py` 已通过。该检查只渲染 Compose 配置，不会启动或修改生产容器。
- 质量门禁：2026-09-16 从仓库根目录运行 `scripts/quality-check.ps1` 通过：前端类型检查、19 个 Vitest 文件共 138 项测试与生产构建均通过；后端 113 项测试通过、1 项 PostgreSQL 并发测试按环境跳过，Alembic 为单一 `d9b4e6a2c301` head。
- 构建边界：`three` 保持独立的 DIY 异步块（554.78 kB 原始体积 / 141.00 kB gzip），不会进入常规商城首屏；Vite 仍对此块给出 500 kB 提示，后续模型上线时应继续控制网格与贴图体积。

## 发布边界与回滚

这个候选版本可用于本地演示和受控功能验收。真实交易仍缺少正式 HTTPS、CSP/Host 校验、限流、备份恢复演练、告警、真实支付商户联调以及非作者验收；这些条件由[风险登记与上线验收门槛](../project-management/03-risk-and-acceptance.md)管理，当前结论为 No-Go。

若需要回滚应用代码，发布时应保留上一个可用镜像或提交并使用 `git revert` 创建可审计回滚。数据库迁移采用前滚策略：发生异常时停止 API，评估受影响 revision，再执行经过复核的修复迁移；不要对已有生产库盲目降级或删除数据卷。
