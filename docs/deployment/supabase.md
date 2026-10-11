# Supabase 部署边界

Supabase 是可选部署目标，不是本地开发或答辩运行时依赖。启用时，本项目只使用 Supabase 托管 PostgreSQL 和 Storage；认证、业务 API、管理员权限、购物车和订单仍由 FastAPI 处理。

本地 `docker-compose.yml` 会忽略外部 `DATABASE_URL`，固定连接 Compose 内的 PostgreSQL，并固定使用 `ASSET_STORAGE_BACKEND=local`。这样项目暂停、网络断开或旧凭据失效时，答辩流程仍可运行。

## 当前项目

- Project ref：`fprinlepgtrixxnmvqsj`
- Project URL：`https://fprinlepgtrixxnmvqsj.supabase.co`
- 实际区域：东京 `ap-northeast-1`
- 计划区域：新加坡 `ap-southeast-1`
- 当前状态：`ACTIVE_HEALTHY`（2026-08-10 从暂停状态恢复后复核）
- Alembic 版本：`a9c3e7d5b102`
- 目录数据：14 个分类、96 个商品，其中 86 个 DIY 配件

区域创建后不能原地修改。该项目曾处于暂停状态，虽已于 2026-08-10 恢复并完成数据库复核，仍不应作为答辩前置条件；若面向中国南方用户正式部署，应另建新加坡项目后迁移。

`https://<project-ref>.supabase.co/rest/v1/` 是 Data REST API，不是 PostgreSQL 连接串。FastAPI 必须使用控制台 Connect 面板提供的 Session Pooler 连接串。

## 数据库

1. 从 Connect 面板复制 Session Pooler 连接串，将协议改为 `postgresql+asyncpg://`。
2. 对密码做 URL 编码，并启用 SSL；不要把连接串提交到 Git。
3. 在 `ecommerce/backend` 执行 `alembic upgrade head`。
4. 关闭 Data API，或确认 `anon`、`authenticated` 对业务表没有权限。
5. RLS 无策略是本项目刻意的默认拒绝状态，浏览器不得直连业务表。

## Storage

- `catalog-images`：公开读取，5 MB，PNG/JPEG/WebP。
- `catalog-models`：公开读取，20 MB，GLB。
- 上传、覆盖和删除只允许 FastAPI 管理员接口调用。
- 浏览器中禁止出现 Secret Key 或 `service_role` Key。
- 后端请求上限至少设为 22 MB，给 20 MB GLB 的 multipart 封装留出空间。

## 环境变量

只有显式部署到 Supabase 时才设置以下变量，并使用 `docker-compose.prod.yml` 或手动启动后端：

```env
DATABASE_URL=postgresql+asyncpg://postgres.<project-ref>:<encoded-password>@<session-pooler>:5432/postgres?ssl=require
ASSET_STORAGE_BACKEND=supabase
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SECRET_KEY=<backend-only-secret-key>
SUPABASE_IMAGE_BUCKET=catalog-images
SUPABASE_MODEL_BUCKET=catalog-models
MAX_REQUEST_SIZE=23068672
```

`ASSET_STORAGE_BACKEND=local` 是默认值。仅设置 `SUPABASE_URL` 或 Secret Key 不会触发远程请求，避免过期配置意外拖慢本地启动和上传。

参考：[数据库安全](https://supabase.com/docs/guides/database/secure-data)、[Storage 访问控制](https://supabase.com/docs/guides/storage/security/access-control)。
