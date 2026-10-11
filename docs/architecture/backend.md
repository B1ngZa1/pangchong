# 后端架构

> 状态：当前结构说明与目标依赖方向  
> 代码根目录：`ecommerce/backend/`

## 当前目录职责

| 路径 | 职责 |
| --- | --- |
| `app/api/` | HTTP 路由、依赖注入、输入解析和响应映射 |
| `app/services/` | 订单、金额、DIY 目录、物流、存储等用例或集成逻辑 |
| `app/core/` | 配置、数据库、安全与应用基础设施 |
| `app/models/` | SQLAlchemy ORM 模型 |
| `app/schemas/` | Pydantic 请求和响应契约 |
| `app/cli/` | 管理员初始化、数据导入等一次性命令 |
| `migrations/` | Alembic 生产 schema 演进 |
| `tests/` | 路由、服务、安全、配置和迁移测试 |

当前公开 API 位于 `/api`，包括 auth、products、cart、orders、payment、admin 和 market。健康检查位于 `/health`。

生产 Compose 以一次性的 `migrate` 服务执行 `alembic upgrade head`；它成功后才会启动 API。应用 lifespan 只在 development/test 的直接运行场景调用 `create_all`，生产实例不再自行推断或修改 schema。

## 请求生命周期

1. Nginx 将 `/api` 请求转发到 FastAPI。
2. CORS、请求大小和安全响应头中间件处理通用边界。
3. Pydantic 校验输入，认证依赖解析 JWT 并加载当前用户。
4. API 调用 service 或执行尚未迁移的用例逻辑。
5. SQLAlchemy async session 在成功时提交，异常时回滚。
6. 响应只返回契约字段；生产异常不返回内部异常文本。

## 依赖方向

```text
API -> Services -> Domain rules
          |          |
          +------> Repositories / Integrations
                         |
                         +-> PostgreSQL / external APIs / storage
```

当前仓库已开始把订单、金额、DIY 和存储逻辑抽到 services，但尚未形成完整的 domain/repositories/integrations 分层。后续迁移应以单个真实用例为单位，保持现有 API 契约，不创建空目录。

## 关键约束

- 订单：服务端读取商品和配置版本、重新计算金额并在事务内写入订单快照；客户端价格只能作为显示。
- 权限：普通用户只能访问自己的购物车、订单和地址；管理员操作必须依赖后端角色校验。
- 支付：创建支付、回调验签、订单状态、金额校验和幂等属于同一业务边界；适配器位于 `app/integrations/payments/`，状态与事件事务位于 `app/services/payment.py`。
- 文件：上传同时限制请求体、单文件大小、扩展名、MIME/文件签名和目标路径；Supabase Secret Key 只在 storage service 中使用。
- 第三方调用：必须设置超时、可控重试、错误映射、日志脱敏和告警；不能在生产失败时伪造成功。
- 数据库：Alembic 是生产 schema 的唯一来源。生产 Compose 禁止挂载初始化 SQL，并在 API 启动前完成 `alembic upgrade head`；`create_all` 只保留给开发和测试中的直接运行。

## 目标模块边界

优先把高风险交易链路逐步收敛为：

- `domain/`：Money、Pricing、OrderState、InventoryPolicy 等纯规则。
- `repositories/`：SQLAlchemy 查询、锁和持久化。
- `integrations/`：支付宝、物流、邮件、价格服务和 Storage 适配器。
- `services/`：CreateOrder、HandlePaymentCallback、RefundOrder 等用例与事务。
- `api/`：只做 HTTP 输入输出与依赖注入。

## 验证

在 `ecommerce/backend/` 执行：

```bash
python -m compileall app
python -m pytest
python -m alembic heads
```

生产变更还要验证：空库迁移、已有数据升级、并发下单、重复回调、事务回滚、权限越界、第三方超时和日志脱敏。
