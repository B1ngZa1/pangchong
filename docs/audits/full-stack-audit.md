# 胖虫电商系统全栈审核报告

审核日期：2026-05-29

## 概览

本次审核覆盖 `ecommerce` 前端、后端、数据库脚本与部署配置。当前项目已经具备完整电商雏形：Vue 3 + Vite + Pinia 前端，FastAPI + SQLAlchemy + PostgreSQL 后端，Docker Compose 部署骨架。核心风险集中在路由顺序、匿名购物车权限、生产配置、安全审计、数据库迁移治理、前端体验一致性与测试覆盖。

## P0：必须立即处理

- 已修复：`/products/{product_id}` 路由位于 `/products/slug/{slug}`、`/products/hot/list`、`/products/featured/list` 之前，会导致静态路径被当成 UUID 解析，首页热门商品和商品详情可能返回 422。
  - 处理：已将静态商品路由前置，并新增 `ecommerce/backend/tests/test_routes.py` 回归测试。
- 已修复：匿名购物车更新/删除接口只检查 item 是否有 `session_id`，没有校验请求中的 session 是否匹配，存在越权修改/删除购物车项风险。
  - 处理：后端 `PUT /cart/items/{item_id}` 与 `DELETE /cart/items/{item_id}` 增加 `session_id` 校验，前端 cart API 同步传递 session。
- 已修复：后台用户状态、商品状态、订单发货接口前端发送 JSON body，但后端读取 query 参数，导致管理后台操作失败。
  - 处理：后端改为接收 Pydantic body schema。
- 建议立即处理：生产环境仍存在默认弱密钥、默认数据库密码示例和 `DEBUG` 配置风险。
  - 建议：生产启动时检测 `SECRET_KEY`、数据库密码、Redis 密码、支付密钥，发现默认值直接拒绝启动。

## P1：高优先级

- 已修复：Pydantic v2 `class Config` 弃用警告。
  - 处理：schema 与 settings 已迁移到 `ConfigDict`。
- 已优化：前台首页、导航、页脚、商品列表、商品详情初步改为黑底、电光绿、高性能硬件视觉，并加入本地 hero/商品兜底图。
- 已优化：新增全局通知 store，首页核心购买链路的商品列表与详情页已从 `alert()` 切换为统一 Toast。
- 建议：继续替换 Checkout、DIY、OrderDetail、用户地址、后台页面中的 `alert()`，统一为全局通知组件。
- 建议：订单支付回调、模拟支付、取消订单、发货等状态变更需要引入订单状态历史表，避免后续售后无法追踪。
- 建议：支付回调必须加入幂等保护，使用订单号、第三方交易号、回调事件 ID 建唯一约束。
- 建议：数据库 schema 演进应以 Alembic 为准，生产环境不要依赖 `Base.metadata.create_all()` 自动建表。

## P2：中期优化

- 前端建议：
  - 商品图统一本地或 CDN 托管，避免依赖外链图床。
  - 商品卡、购物车、结算页、DIY 工作台继续统一成高密度暗色电商界面。
  - 商品详情增加图库、规格分组、售后/质保、兼容性说明。
  - 移动端商品筛选建议做底部抽屉，而不是长期固定横向滚动条。
  - 后台页面建议减少紫色状态标签，统一到黑绿主视觉与状态色。
- 后端建议：
  - 将路由中的业务逻辑逐步迁移到 service 层，优先迁移购物车、订单、支付、商品查询。
  - 统一分页响应结构，减少前台/后台接口字段差异。
  - 统一错误响应结构：`code`、`message`、`detail`、`request_id`。
  - 搜索关键词应限制长度，并对 `%`、`_` 等通配语义做明确处理。
- 数据库建议：
  - 商品列表增加 `(is_active, category_id, created_at DESC)`、`(is_active, is_featured, sold_count DESC)`、`(is_active, price)` 组合索引。
  - 订单后台增加 `(status, created_at DESC)` 与 `(user_id, created_at DESC)` 索引。
  - 商品搜索考虑 `pg_trgm` 或中文搜索方案，不只依赖 `to_tsvector('simple', name)`。

## P3：体验与可维护性

- 前端建议：
  - 引入组件测试覆盖导航、商品卡、购物车数量、Toast、商品详情加购。
  - 增加移动端截图回归检查，重点看首页 hero、商品列表、购物车、结算页。
  - 图片增加尺寸策略：hero、商品卡、详情页分别输出不同尺寸。
  - `frontend/src/api/index.js` 可拆分为 `auth/products/cart/orders/payment/admin` 模块。
- 后端建议：
  - 增加 API 集成测试，覆盖商品列表、slug 详情、热门商品、匿名购物车修改、后台状态更新。
  - 增加结构化日志，至少包含 request_id、path、status、duration、user_id。
  - 新增 `/ready` 区分应用进程健康和数据库/Redis 可用状态。
- 部署建议：
  - Docker Compose 区分 dev/prod，生产镜像不挂载源码。
  - Nginx 配置静态资源长期缓存、API 超时、gzip/brotli。

## P4：长期演进

- 引入库存流水、支付流水、订单状态历史、售后/退款表，支撑真实运营。
- Redis 用于热门商品、分类、首页推荐短缓存，但下单库存判断仍以数据库事务为准。
- 后台 dashboard 聚合查询做短缓存或物化统计，避免数据量变大后拖慢后台。
- 逐步建立可观测性：慢查询日志、错误追踪、前端 JS 错误率、支付成功率、下单成功率。
- DIY 装机如果继续扩展，应抽象配件兼容性规则，不要长期把复杂规则塞进 JSONB。

## 当前验证

- 前端构建：`npm run build -- --outDir C:\Users\14012\AppData\Local\Temp\pangchong-vite-check --emptyOutDir`
- 后端测试：`python -m pytest -q`
- 当前结果：前端构建通过，后端测试通过。

