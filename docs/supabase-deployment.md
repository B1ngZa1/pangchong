# Supabase 部署边界

本项目只使用 Supabase 托管 PostgreSQL 和 Storage。认证、业务 API、管理员权限、购物车和订单仍由 FastAPI 处理。

## 当前项目

- Project ref：`fprinlepgtrixxnmvqsj`
- Project URL：`https://fprinlepgtrixxnmvqsj.supabase.co`
- 实际区域：东京 `ap-northeast-1`
- 计划区域：新加坡 `ap-southeast-1`
- Alembic 版本：`f2a8c5d1e904`
- 目录数据：14 个分类、96 个商品，其中 86 个 DIY 配件

区域创建后不能原地修改。当前东京项目可以继续用于答辩；若面向中国南方用户正式部署，应另建新加坡项目后迁移。

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

## 环境变量

```env
DATABASE_URL=postgresql+asyncpg://postgres.<project-ref>:<encoded-password>@<session-pooler>:5432/postgres?ssl=require
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SECRET_KEY=<backend-only-secret-key>
SUPABASE_IMAGE_BUCKET=catalog-images
SUPABASE_MODEL_BUCKET=catalog-models
```

参考：[数据库安全](https://supabase.com/docs/guides/database/secure-data)、[Storage 访问控制](https://supabase.com/docs/guides/storage/security/access-control)。
