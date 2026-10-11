# 胖虫电商 — 技术栈优化与项目全景计划

> 文档版本：1.0 | 更新日期：2026-05-27

> 状态：历史技术栈规划，版本与能力判断保留为 2026-05-27 快照；当前代码边界请以[架构文档](../architecture/README.md)为准。

---

## 一、项目当前技术栈总览

### 1.1 前端 (ecommerce/frontend)

| 分类 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | Vue 3 (Composition API) | ^3.4.15 | UI 框架 |
| 构建 | Vite | ^5.0.11 | 开发/构建 |
| 路由 | vue-router | ^4.2.5 | SPA 路由 |
| 状态 | Pinia | ^2.1.7 | 全局状态管理 |
| HTTP | axios | ^1.6.5 | API 请求 |
| CSS | Tailwind CSS | ^3.4.1 | 原子化样式 |
| 工具 | @vueuse/core | ^10.7.2 | Vue Composables 工具集 |

**语言**：JavaScript (无 TypeScript)

### 1.2 后端 (ecommerce/backend)

| 分类 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | FastAPI | 0.109.0 | Python Web API |
| ASGI | Uvicorn | 0.27.0 | ASGI 服务器 |
| ORM | SQLAlchemy (async) | 2.0.25 | 异步数据库操作 |
| 数据库驱动 | asyncpg | 0.29.0 | PostgreSQL 异步驱动 |
| 迁移 | Alembic | 1.13.1 | 数据库迁移 |
| 缓存 | Redis + hiredis | 5.0.1 | 缓存/会话 |
| 认证 | python-jose | 3.3.0 | JWT 签发/验证 |
| 密码 | passlib + bcrypt | 4.0.1 | 密码哈希 |
| 验证 | Pydantic v2 | 2.5.3 | 数据校验 |
| HTTP客户端 | httpx | 0.26.0 | 外部 API 调用 |
| 邮件 | aiosmtplib | 3.0.1 | 异步邮件发送 |
| 文件上传 | python-multipart | 0.0.6 | multipart 解析 |

**语言**：Python 3.11+ (无 mypy/pyright 类型检查)

### 1.3 数据库

PostgreSQL 16 (含 uuid-ossp 扩展)

| 表名 | 说明 | 关联 |
|------|------|------|
| `users` | 用户 | → addresses, cart_items, orders |
| `user_addresses` | 收货地址 | → users |
| `categories` | 商品分类 (树形) | self.parent_id, → products |
| `products` | 商品 | → categories |
| `cart_items` | 购物车 | → users, products |
| `orders` | 订单 | → users, → order_items |
| `order_items` | 订单商品快照 | → orders, products |
| `price_history` | 价格变动历史 | → products |
| `audit_logs` | 操作审计日志 | → users |

视图：`order_details`、`product_sales_stats`

### 1.4 基础设施

| 分类 | 技术 | 状态 |
|------|------|------|
| 容器化 | Docker + Docker Compose | 已有 |
| 反向代理 | Nginx | 已有 |
| SSL | 自签证书 | 已有 |
| 开发环境 | Vite dev server + Uvicorn --reload | 已有 |
| 生产环境 | docker-compose.prod.yml | 已有 |

---

## 二、当前项目目录结构（2026-08-10）

```text
pangchong/
├── .github/workflows/              # CI 质量门禁
├── docs/                          # 全项目文档中心
│   ├── README.md                  # 唯一文档索引
│   ├── architecture/              # 系统、前端、后端、网络安全、数据
│   ├── development/               # 本地开发与调试
│   ├── deployment/                # 部署与托管服务
│   ├── operations/                # 发布、回滚与运维
│   ├── product/                   # 商品、DIY、服务与演示
│   ├── 3d/                        # 3D 方案与资产流水线
│   ├── planning/                  # 优化规划
│   ├── audits/                    # 审计快照
│   ├── data/                      # 核验数据
│   ├── design-system/             # 设计系统
│   ├── project-management/        # 任务、风险、验收与证据
│   └── archive/                   # 被替代的历史资料
├── ecommerce/                    # 主应用
│   ├── backend/                   # FastAPI、Alembic、pytest
│   ├── frontend/                  # Vue 3、Vite、Vitest、3D
│   ├── database/                  # 本地初始化与 demo seed
│   ├── docker/nginx/              # 反向代理配置
│   ├── scripts/                   # 生产配置/初始化验证
│   ├── docker-compose.yml         # 本地环境
│   └── docker-compose.prod.yml    # 生产形态模板
├── scripts/                       # 全仓结构与质量检查
├── tools/catalog/                 # 离线商品数据工具
├── CONTRIBUTING.md
└── README.md
```

---

## 三、当前问题诊断

### 3.1 前端（按严重程度排序）

| # | 问题 | 严重度 | 影响 |
|---|------|--------|------|
| 1 | **无 TypeScript** | 🔴 高 | 无类型安全，重构风险大，IDE 提示弱 |
| 2 | **无测试** | 🔴 高 | 无 Vitest/Cypress，回归全靠人工 |
| 3 | **无表单验证库** | 🟡 中 | 手动验证逻辑分散在多个组件中 |
| 4 | **无 i18n** | 🟡 中 | 中文硬编码，无法国际化扩展 |
| 5 | **无 SSR/SSG** | 🟡 中 | SPA 对 SEO 不友好，首屏白屏 |
| 6 | **自动导入缺失** | 🟢 低 | 手动 import Vue API，代码冗余 |
| 7 | **图片无懒加载** | 🟢 低 | 所有图片一次性加载，浪费带宽 |
| 8 | **无 PWA** | 🟢 低 | 无离线缓存，移动端体验差 |
| 9 | **根目录旧文件未清理** | 🟢 低 | index.html/about.html/diy.html 等旧版文件冗余 |
| 10 | **CartSidebar 未使用但未删除** | 🟢 低 | 死代码 |

### 3.2 后端（按严重程度排序）

| # | 问题 | 严重度 | 影响 |
|---|------|--------|------|
| 1 | **无类型检查** | 🔴 高 | 无 mypy/pyright，类型错误运行时才发现 |
| 2 | **无测试用例** | 🔴 高 | tests/ 目录为空 |
| 3 | **Alembic 未初始化** | 🔴 高 | migrations/ 目录为空，生产数据库变更无版本管理 |
| 4 | **无速率限制** | 🟡 中 | API 易被滥用/攻击 |
| 5 | **Redis 配置了但未使用** | 🟡 中 | 缓存/会话应该使用 Redis，目前未集成 |
| 6 | **无后台任务** | 🟡 中 | 邮件发送、订单超时取消等同步执行 |
| 7 | **无结构化日志** | 🟡 中 | 只用 print()，生产环境无法排查 |
| 8 | **无 API 版本管理** | 🟡 中 | 无法平滑升级 API |
| 9 | **docker-compose 密码硬编码** | 🟡 中 | `060120` 出现在多处 |
| 10 | **无 CI/CD pipeline** | 🟡 中 | 手动部署，容易出错 |
| 11 | **无 WebSocket** | 🟢 低 | 订单状态更新需轮询 |
| 12 | **文件上传无安全扫描** | 🟢 低 | 用户上传无类型/病毒检查 |
| 13 | **审计日志表存在但未自动记录** | 🟢 低 | audit_logs 表已建但无触发器/中间件自动写入 |

### 3.3 数据库

| # | 问题 | 严重度 | 影响 |
|---|------|--------|------|
| 1 | 中文全文搜索性能差 | 🟡 中 | GIN `to_tsvector('simple')` 简单分词，需 pg_jieba 或 zhparser |
| 2 | `products.images` JSONB 可能存储大数组 | 🟢 低 | 建议大图移出数据库，仅保存 URL 路径 |
| 3 | price_history 表无自动触发器 | 🟢 低 | 需应用层手动写入 |

---

## 四、技术栈优化方案

### 4.1 前端优化建议

#### 4.1.1 立即执行（P0 - 2 周内）

**A. 引入 TypeScript**

```
vue 3.4+ 原生支持 <script setup lang="ts">
收益：编译时类型检查、自动补全、重构安全
成本：渐进迁移，先改 store/router/api，再改组件
```

迁移路径：
1. `tsconfig.json` 配置（`strict: true`）
2. Store 文件 `.js` → `.ts`（Pinia 支持完整 TS 泛型）
3. API 层 `.js` → `.ts`（axios 请求/响应类型定义）
4. Router 配置 `.js` → `.ts`
5. 组件逐批迁移（`.vue` 文件中 `<script setup lang="ts">`）

**B. 引入 Vitest 单元测试**

```bash
npm i -D vitest @vue/test-utils jsdom
```

优先测试：Store (cart/user)、API 拦截器、工具函数

**C. 引入 unplugin-auto-import**

```bash
npm i -D unplugin-auto-import
```

```ts
// vite.config.ts
import AutoImport from 'unplugin-auto-import/vite'
AutoImport({
  imports: ['vue', 'vue-router', 'pinia', '@vueuse/core'],
  dts: 'src/auto-imports.d.ts',
})
```

收益：无需手动 `import { ref, computed } from 'vue'`，减少模板代码

#### 4.1.2 短期执行（P1 - 4 周内）

**D. 引入 unplugin-vue-components**

```bash
npm i -D unplugin-vue-components
```

自动按需导入 `src/components/` 下的组件，无需手动 import

**E. 引入表单验证库 — VeeValidate + Zod**

```bash
npm i vee-validate zod @vee-validate/zod
```

统一 Checkout、Login、Register、Profile、Addresses 中的表单验证逻辑

**F. 图片懒加载**

```bash
npm i @vueuse/integrations
```

使用 `v-lazy` 指令或原生 `loading="lazy"` + IntersectionObserver

**G. 引入 @vitejs/plugin-legacy**

兼容老旧浏览器（主要是移动端 WebView）

#### 4.1.3 中期执行（P2 - 8 周内）

**H. SSR/SSG — Nuxt 3 迁移评估**

| 方案 | 优点 | 缺点 |
|------|------|------|
| 保持 Vite SPA + prerender | 改动小 | SEO 改善有限 |
| 迁移到 Nuxt 3 | SEO 完美、首屏快 | 改动大、需重写路由/插件 |
| Vite + vite-plugin-ssr | 折中方案 | 生态不如 Nuxt |

建议：短期用 `vite-plugin-ssr`，中长期考虑 Nuxt 3。

**I. PWA 支持**

```bash
npm i -D vite-plugin-pwa
```

`vite-plugin-pwa` 自动生成 Service Worker + manifest.json，支持离线缓存。

**J. 国际化 i18n**

```bash
npm i vue-i18n@9
```

#### 4.1.4 建议新增的 npm 依赖

```json
{
  "devDependencies": {
    "typescript": "^5.4.0",
    "vitest": "^1.3.0",
    "@vue/test-utils": "^2.4.0",
    "jsdom": "^24.0.0",
    "unplugin-auto-import": "^0.17.0",
    "unplugin-vue-components": "^0.26.0",
    "@vitejs/plugin-legacy": "^5.3.0",
    "vite-plugin-pwa": "^0.19.0",
    "eslint": "^8.57.0",
    "@typescript-eslint/parser": "^7.0.0",
    "eslint-plugin-vue": "^9.22.0"
  },
  "dependencies": {
    "vee-validate": "^4.12.0",
    "zod": "^3.22.0",
    "@vee-validate/zod": "^4.12.0",
    "vue-i18n": "^9.10.0"
  }
}
```

#### 4.1.5 重构建议

| 文件 | 当前问题 | 建议 |
|------|----------|------|
| `api/index.js` | 140+ 行，API + axios 配置混在一起 | 拆分为 `api/http.ts` + `api/auth.ts` + `api/products.ts` + ... |
| `store/cart.js` | 340+ 行，逻辑过重 | 拆出 `utils/coupon.ts`、`utils/shipping.ts`、`utils/storage.ts` |
| `AppNavbar.vue` | 内联 SVG 过多 | 抽 `components/icons/` 目录 |
| 多个 View | 重复的 loading/empty/error 状态 | 抽 `<DataState>` 通用组件 |
| `Checkout.vue` | 470+ 行，步骤逻辑+表单混在一起 | 拆分为 StepAddress/StepDelivery/StepPayment/StepConfirm 子组件 |

---

### 4.2 后端优化建议

#### 4.2.1 立即执行（P0 - 2 周内）

**A. 初始化 Alembic 迁移**

```bash
cd backend
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

必须做：当前 migrations/ 为空，生产环境无法追踪数据库变更。

**B. 引入 mypy 类型检查**

```bash
pip install mypy
```

```ini
# pyproject.toml
[tool.mypy]
strict = true
plugins = ["sqlalchemy.ext.mypy.plugin"]
```

**C. 添加 pytest 测试用例**

优先测试：
- `test_auth.py` — 注册/登录/Token 刷新
- `test_products.py` — CRUD + 搜索 + 排序
- `test_cart.py` — 匿名/登录购物车 + 合并
- `test_orders.py` — 创建订单 + 库存扣减

#### 4.2.2 短期执行（P1 - 4 周内）

**D. 引入速率限制**

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# 对敏感端点：
@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(...): ...
```

**E. 集成 Redis 缓存**

```python
import redis.asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# 缓存热门商品、分类列表
@router.get("/products/featured")
@cache(expire=300)  # 5 分钟
async def get_featured_products(): ...
```

**F. 引入后台任务 — ARQ**

```bash
pip install arq
```

用途：
- 异步发送邮件（注册欢迎、订单确认、发货通知）
- 订单超时自动取消（30 分钟未支付）
- 商品销量统计更新

**G. 结构化日志 — loguru**

```bash
pip install loguru
```

替换所有 `print()` → `logger.info()` / `logger.error()`

#### 4.2.3 中期执行（P2 - 8 周内）

**H. API 版本化**

```
/api/v1/products     →  当前所有 API
/api/v1/auth
```

未来 v2 可独立演进

**I. WebSocket 实时通知**

```python
from fastapi import WebSocket

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    ...
```

用途：订单状态变更推送、管理员新订单提醒

**J. CI/CD Pipeline — GitHub Actions**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest --cov=app ecommerce/backend/tests/
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx vitest run ecommerce/frontend/
```

**K. 文件上传安全**

```bash
pip install python-magic  # MIME 类型检测
```

- 检查 MIME 类型白名单（image/jpeg, image/png, image/webp）
- 限制文件大小
- 生成随机文件名，防止路径遍历

**L. 审计日志自动化**

```python
# middleware/audit.py
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.method in ("POST", "PUT", "DELETE"):
        # 写入 audit_logs 表
        ...
    return response
```

#### 4.2.4 建议新增的 Python 依赖

```txt
# 类型检查
mypy==1.8.0

# 速率限制
slowapi==0.1.9

# 缓存
fastapi-cache2[redis]==0.2.1

# 后台任务
arq==0.26.0

# 结构化日志
loguru==0.7.2

# WebSocket 支持
# (FastAPI 内置)

# 测试增强
httpx==0.26.0
pytest-asyncio==0.23.3
pytest-cov==4.1.0
factory-boy==3.3.0          # 测试数据工厂
faker==22.0.0               # 假数据生成

# 安全
python-magic==0.4.27        # 文件 MIME 检测
```

---

### 4.3 数据库优化

#### 4.3.1 中文全文搜索增强

```sql
-- 方案 A: 使用 zhparser 扩展（需要编译安装）
CREATE EXTENSION zhparser;
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- 重建索引
DROP INDEX idx_products_name_search;
CREATE INDEX idx_products_name_search ON products
  USING GIN (to_tsvector('chinese', name));

-- 方案 B: 使用 pg_bigm 实现模糊搜索（安装更简单）
CREATE EXTENSION pg_bigm;
CREATE INDEX idx_products_name_bigm ON products USING gin (name gin_bigm_ops);
```

#### 4.3.2 新增推荐表

```sql
CREATE TABLE price_history_trigger AS ...
-- 建议为 price_history 添加自动触发器
CREATE OR REPLACE FUNCTION record_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        INSERT INTO price_history (product_id, price)
        VALUES (NEW.id, NEW.price);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_price_change
    AFTER UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION record_price_change();
```

#### 4.3.3 索引优化建议

```sql
-- 复合索引：商品列表常见查询
CREATE INDEX idx_products_cat_active ON products(category_id, is_active)
  WHERE is_active = true;

-- 订单列表常见查询
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 购物车查询优化
CREATE INDEX idx_cart_user_active ON cart_items(user_id) WHERE quantity > 0;
```

---

## 五、可开发功能清单

### 5.1 短期（1-2 月）

| # | 功能 | 涉及模块 | 优先级 |
|---|------|----------|--------|
| 1 | 商品搜索自动补全 | 前端 + 后端搜索 API | P0 |
| 2 | 商品收藏/心愿单 | 新表 wishlists + API + UI | P1 |
| 3 | 商品评价/评分系统 | 新表 reviews + API + UI | P1 |
| 4 | 优惠券系统（后端） | 新表 coupons + 管理后台 | P1 |
| 5 | 库存预警通知 | 后端定时任务 + 管理员通知 | P1 |
| 6 | 快递物流实时追踪 | 快递鸟 API 对接 | P1 |
| 7 | 移动端适配优化 | Tailwind 响应式微调 | P1 |
| 8 | 用户头像上传 | 后端文件上传 + 裁剪 | P2 |

### 5.2 中期（2-4 月）

| # | 功能 | 涉及模块 | 优先级 |
|---|------|----------|--------|
| 9 | **3D PC 装机配置器** | TresJS + Three.js + 3D 模型 | P0 |
| 10 | 微信/支付宝真实支付 | 支付 API 对接 | P1 |
| 11 | 邮件通知系统 | SMTP + ARQ 异步任务 | P1 |
| 12 | 管理后台数据大屏 | ECharts + Dashboard 改造 | P1 |
| 13 | 商品对比功能 | 前端组件 + API | P2 |
| 14 | 限时秒杀/闪购 | 新表 flash_sales + 定时任务 | P2 |
| 15 | 用户等级/积分系统 | 新表 points + 等级规则引擎 | P2 |
| 16 | 发票管理 | 新表 invoices + API + UI | P2 |
| 17 | 多语言支持 (i18n) | vue-i18n + 翻译文件 | P2 |
| 18 | 数据导出 (Excel/CSV) | openpyxl + 管理后台 | P2 |

### 5.3 长期（4-6 月）

| # | 功能 | 涉及模块 | 优先级 |
|---|------|----------|--------|
| 19 | 社区/论坛 | 新模块 + 帖子/回复/点赞 | P2 |
| 20 | 装机方案分享广场 | 方案模板 + 社交分享 | P2 |
| 21 | AI 装机推荐 | LLM API + 需求分析引擎 | P3 |
| 22 | 二手交易市场 | 新模块 + 认证 + 担保交易 | P3 |
| 23 | 配件租赁服务 | 新业务模块 | P3 |
| 24 | 小程序端 | uni-app / Taro 跨端方案 | P3 |
| 25 | 数据分析 BI | Apache Superset / Metabase 集成 | P3 |

---

## 六、数据库扩展计划

### 6.1 待新增的表

#### 6.1.1 商品收藏 (wishlists)

```sql
CREATE TABLE wishlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);
```

#### 6.1.2 商品评价 (reviews)

```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(id),
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    content TEXT,
    images JSONB,
    is_verified BOOLEAN DEFAULT false,  -- 是否真实购买
    is_anonymous BOOLEAN DEFAULT false,
    like_count INTEGER DEFAULT 0,
    reply TEXT,              -- 商家回复
    replied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_product ON reviews(product_id, is_verified);
CREATE INDEX idx_reviews_user ON reviews(user_id);
```

#### 6.1.3 优惠券 (coupons)

```sql
CREATE TABLE coupons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100),
    type VARCHAR(20) NOT NULL CHECK (type IN ('fixed', 'percent')),
    value DECIMAL(10,2) NOT NULL,   -- 固定金额 或 百分比
    min_amount DECIMAL(10,2),       -- 最低消费门槛
    max_discount DECIMAL(10,2),     -- 百分比券的最大优惠金额
    total_count INTEGER,            -- 发放总量
    used_count INTEGER DEFAULT 0,
    user_limit INTEGER DEFAULT 1,   -- 每人限用次数
    start_at TIMESTAMPTZ,
    end_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_coupons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    coupon_id UUID NOT NULL REFERENCES coupons(id) ON DELETE CASCADE,
    used_at TIMESTAMPTZ,
    order_id UUID REFERENCES orders(id),
    UNIQUE(user_id, coupon_id, order_id)
);
```

#### 6.1.4 积分系统 (points)

```sql
CREATE TABLE point_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,  -- purchase, review, signin, referral
    reference_id UUID,            -- 关联订单/评价 ID
    description VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### 6.1.5 3D 模型关联

```sql
ALTER TABLE products ADD COLUMN model_3d_url VARCHAR(500);
ALTER TABLE products ADD COLUMN model_3d_scale DECIMAL(3,2) DEFAULT 1.0;
ALTER TABLE products ADD COLUMN model_3d_position JSONB;  -- [x, y, z] 在机箱中的坐标
ALTER TABLE products ADD COLUMN model_3d_rotation JSONB;  -- [x, y, z]
```

#### 6.1.6 通知系统 (notifications)

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(30) NOT NULL,  -- order_status, promotion, system
    title VARCHAR(200) NOT NULL,
    content TEXT,
    is_read BOOLEAN DEFAULT false,
    reference_type VARCHAR(50),
    reference_id UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
```

#### 6.1.7 秒杀/闪购

```sql
CREATE TABLE flash_sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    flash_price DECIMAL(10,2) NOT NULL,
    stock INTEGER NOT NULL,
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---

## 七、优化路线图

```
Week 1-2   │ P0 立即执行
           │ • TypeScript 迁移（前端）
           │ • Alembic 初始化（后端）
           │ • mypy 类型检查（后端）
           │ • Vitest + pytest 框架搭建
           │ • 根目录旧文件清理
           │
Week 3-4   │ P1 短期
           │ • unplugin-auto-import + components
           │ • VeeValidate + Zod 表单重构
           │ • slowapi 速率限制
           │ • Redis 缓存集成
           │ • loguru 结构化日志
           │ • 审计日志中间件
           │
Week 5-8   │ P1 短期（续）
           │ • ARQ 后台任务（邮件/订单超时）
           │ • 商品搜索自动补全
           │ • 商品收藏/心愿单
           │ • 库存预警通知
           │ • API 拆分（api/index.js → 模块化）
           │
Week 9-12  │ P2 中期
           │ • 3D PC 装机配置器（阶段一、二）
           │ • CI/CD Pipeline
           │ • 商品评价系统
           │ • 优惠券系统
           │ • 移动端适配优化
           │
Week 13-16│ P2 中期（续）
           │ • 支付宝/微信真实支付
           │ • 邮件通知系统
           │ • 3D 装机配置器（阶段三、四）
           │ • 快递物流追踪
           │ • 管理后台数据大屏
           │
Week 17-20│ P3 长期
           │ • Nuxt 3 SSR 迁移评估
           │ • PWA 支持
           │ • i18n 多语言
           │ • 3D 装机配置器（阶段五）
           │ • 小程序端评估
```

---

## 八、清理清单

### 立即删除的根目录文件

| 文件 | 原因 |
|------|------|
| `index.html` | 旧版静态官网，功能已被 Vue SPA 替代 |
| `about.html` | 旧版关于页 |
| `diy.html` | 旧版 DIY 页 |
| `products.html` | 旧版商品页 |
| `products.json` | 旧版商品数据，已被 PostgreSQL 替代 |
| `products_db.js` | 旧版数据库脚本 |
| `script.js` | 旧版 JS |
| `style.css` | 旧版 CSS |
| `pangchong.db` | 旧版 SQLite 数据库，已迁移到 PostgreSQL |

### 前端死代码

| 文件 | 原因 |
|------|------|
| `CartSidebar.vue` | 已被 Cart.vue 全页替代，无引用 |

---

## 九、安全加固清单

| # | 项目 | 当前状态 | 建议 |
|---|------|----------|------|
| 1 | SECRET_KEY | 默认值 `CHANGE_THIS_TO_...` | 改为 `os.urandom(32).hex()` 生成，通过环境变量注入 |
| 2 | DB 密码 | docker-compose 明文 `060120` | 使用 Docker secrets 或 `.env` 文件 |
| 3 | Redis 密码 | docker-compose 明文 `060120` | 同上 |
| 4 | HTTPS | 自签证书 | 生产环境使用 Let's Encrypt + certbot |
| 5 | CORS | `allow_origins` 已限制 | 生产关闭 DEBUG 时的宽松策略 |
| 6 | 请求大小 | 无限制 | FastAPI 添加 `MAX_REQUEST_SIZE` 中间件 |
| 7 | SQL 注入 | SQLAlchemy ORM 防护 | 安全（已使用参数化查询） |
| 8 | XSS | Vue 默认转义 | 安全 |
| 9 | CSRF | 无保护 | 添加 SameSite Cookie + CSRF Token |
| 10 | 密码策略 | 无复杂度要求 | 添加最小长度 + 复杂度校验 |
