# 胖虫 PangChong — DIY 电脑电商平台

> 极致性能，由你定义

胖虫科技官方电商系统，前后端分离架构。覆盖游戏本、轻薄本、台式主机、工作站、迷你主机及 80+ DIY 配件，支持商品浏览、购物车、订单管理、支付集成、管理后台等完整功能。

---

## 快速启动

前置要求：Git · Docker Desktop 或 Docker Engine · Docker Compose v2（推荐；脚本也兼容 `docker-compose`）

```bash
git clone <repository-url> pangchong
cd pangchong/ecommerce

# Windows
.\start.bat

# macOS / Linux
./start.sh

# 或直接使用 Docker Compose
docker compose up -d --build
```

启动后访问：

| 服务 | 地址 |
| ---- | ---- |
| 前端 | `http://localhost:3000` |
| 后端 API | `http://localhost:8000` |
| Swagger 文档 | `http://localhost:8000/docs` |
| ReDoc 文档 | `http://localhost:8000/redoc` |

### 常用命令

```bash
cd ecommerce
docker compose ps           # 查看容器状态
docker compose logs -f      # 查看日志
docker compose down         # 停止服务（保留数据）
docker compose down -v      # 停止并删除数据
```

---

## 测试账号

| 用户名 | 密码 | 角色 |
| ---- | ---- | ---- |
| `testuser` | `test123456` | 普通用户 |
| `admin` | `test123456` | 管理员 |

---

## 环境变量

新克隆项目无需创建 `.env`，`docker-compose.yml` 已提供本地开发默认值。

仅在需修改数据库/Redis 密码、JWT 密钥、CORS 来源或第三方服务配置时，复制 `.env.example` → `.env`：

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

`.env` 已加入 `.gitignore`，不会被提交。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端框架 | Vue 3 (Composition API) · Vite 5 · TypeScript |
| 状态管理 | Pinia 2 |
| 路由 | Vue Router 4 |
| UI | Tailwind CSS 3.4 · Reka UI 无障碍原语 · 深色设计令牌 |
| 3D 渲染 | Three.js · GLTFLoader（按需加载） |
| HTTP 客户端 | Axios (拦截器 + JWT 自动刷新) |
| 后端框架 | FastAPI 0.109 (async) |
| ORM | SQLAlchemy 2.0 (async) |
| 数据验证 | Pydantic v2 |
| 数据库 | PostgreSQL 16 |
| 缓存 | Redis 7 |
| 认证 | JWT HS256 (access + refresh) · bcrypt |
| 测试 | Vitest · pytest · 浏览器主路径冒烟 |
| 部署 | Docker · Docker Compose · Nginx |

---

## 项目结构

```
pangchong/
├── .github/workflows/                  # GitHub Actions 质量门禁
├── docs/                                # 全项目文档中心（按职责物理分类）
│   ├── README.md                        # 文档统一索引
│   ├── architecture/                    # 系统 · 前端 · 后端 · 网络安全 · 数据
│   ├── development/                     # 本地开发与调试
│   ├── deployment/                      # 部署和托管服务
│   ├── operations/                      # 发布、回滚与运维清单
│   ├── product/ · 3d/                   # 产品资料与 3D 资产规范
│   ├── planning/ · audits/              # 优化规划与历史审计
│   ├── data/ · design-system/           # 核验数据与设计系统
│   ├── archive/                         # 已被替代、仅供追溯的历史资料
│   └── project-management/              # 老板策划书与四人任务包
├── scripts/                             # 目录检查与跨平台质量门禁
├── tools/catalog/                       # 离线商品采集与数据生成工具
│
├── ecommerce/                           # 电商全栈应用
│   ├── docker-compose.yml               # 开发环境
│   ├── docker-compose.prod.yml          # 生产环境
│   ├── start.bat / start.sh             # 一键启动脚本
│   ├── .env.example                     # 环境变量模板
│   │
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── alembic.ini                  # 数据库迁移
│   │   ├── requirements.txt
│   │   ├── pyproject.toml               # pytest / mypy 配置
│   │   ├── app/
│   │   │   ├── main.py                  # FastAPI 入口 + 安全中间件
│   │   │   ├── cli/                     # 管理员初始化、价格核验导入等命令
│   │   │   ├── core/                    # config · database · security
│   │   │   ├── api/                     # auth · products · cart · orders · payment · admin · market
│   │   │   ├── models/                  # User · Product · Cart · Order
│   │   │   ├── schemas/                 # Pydantic 请求/响应 Schema
│   │   │   ├── services/                # 物流 · 存储 · 3D 模型服务
│   │   │   └── utils/                   # 邮件
│   │   ├── migrations/                  # Alembic 迁移
│   │   └── tests/                       # pytest API / 迁移 / 启动门禁
│   │
│   ├── frontend/
│   │   ├── Dockerfile
│   │   ├── vite.config.js · tsconfig.json · tailwind.config.js
│   │   ├── public/models/               # 3D 模型 (GLB/GLTF)
│   │   └── src/
│   │       ├── main.js                  # 入口
│   │       ├── api/                     # Axios 封装 + 拦截器
│   │       ├── router/                  # 路由 + 导航守卫
│   │       ├── store/                   # Pinia (user · cart · notify)
│   │       ├── components/              # 通用组件 · 3D 查看器 · 配置面板
│   │       ├── views/                   # 页面 + admin/ + user/
│   │       ├── utils/                   # 支付工具
│   │       └── __tests__/               # Vitest 组件与流程测试
│   │
│   ├── database/
│   │   ├── init.sql                     # 建表 (9 张表)
│   │   ├── seed.sql                     # 96 商品 · 14 分类 · 测试账号
│   │   └── components.sql               # 80+ DIY 配件数据
│   │
│   └── docker/nginx/                    # Nginx 反向代理配置
│
├── CONTRIBUTING.md                      # 协作与完成定义
└── .editorconfig                        # 文本格式约定
```

---

## 核心功能

### 用户端

- **商品浏览** — 14 分类 / 96 商品，分页、关键词搜索、分类筛选、价格排序
- **商品详情** — slug 语义化 URL (`/products/intel-i7-14700k`)，规格参数，库存显示
- **购物车** — 登录/未登录双模式，登录后自动合并，退出时清空残留
- **订单** — 下单 → 支付 → 发货 → 完成，库存自动扣减，运费计算
- **用户中心** — 个人资料、收货地址管理、订单历史
- **3D 查看器** — Three.js 实时模型展示 (GLB/GLTF)
- **产品定制** — 颜色、键盘布局、延保、配件搭配选购
- **服务与门店** — 服务协议、线下门店信息

### 管理端

- **数据概览** — 销售额、订单量、用户数仪表盘 + 7 天趋势
- **商品管理** — 上下架、价格/库存编辑、新建商品
- **订单管理** — 发货操作、订单状态流转
- **用户管理** — 用户列表、启用/禁用

### 安全

- **当前已有**：JWT 双 Token、bcrypt 密码哈希、CORS 白名单、请求体大小限制、基础安全响应头、ORM 参数化查询和生产弱配置预检。
- **生产阻断项**：可用的 HTTPS/443 配置、CSRF、统一限流、CSP 和 Host 校验；浏览器 refresh token 已改为 HttpOnly Cookie，但撤销/设备会话、真实商户沙箱/生产验收仍需完成。
- 完整现状、端口矩阵和上线门禁见[网络与安全基线](docs/architecture/network-security.md)。

### 架构文档

- [系统总览](docs/architecture/system-overview.md)
- [前端架构](docs/architecture/frontend.md)
- [后端架构](docs/architecture/backend.md)
- [数据与存储](docs/architecture/data-and-storage.md)
- [发布检查清单](docs/operations/release-checklist.md)

---

## 数据库

| 表 | 说明 |
|----|------|
| `users` | 用户账户 + 角色 (admin/user) |
| `user_addresses` | 收货地址 |
| `products` | 96 款商品 (含 slug · specs · images) |
| `categories` | 14 个分类 (层级结构) |
| `cart_items` | 购物车 (user_id 或 session_id) |
| `orders` | 订单 (含状态 · 运费 · 支付方式) |
| `order_items` | 订单明细 (快照价格) |
| `payments` | 支付记录 (支付宝) |
| `service_agreements` | 服务协议 |

---

## 测试

```bash
# Windows：在项目根目录执行全部质量门禁
.\scripts\quality-check.ps1

# 也可显式指定已安装后端依赖的 Python 3.11+ 环境
.\scripts\quality-check.ps1 -PythonExecutable C:\path\to\python.exe

# macOS / Linux
bash scripts/quality-check.sh

# 或指定已准备好的 Python 3.11+ 环境
PYTHON_BIN=/path/to/python bash scripts/quality-check.sh

# 前端单独执行：类型检查、测试与生产构建
cd ecommerce/frontend
npm run check

# 后端单独执行：API、迁移与生产启动门禁测试
cd ../backend
python -m pytest
```

---

## 购买渠道

| 平台 | 链接 |
| ---- | ---- |
| 抖音 | [v.douyin.com/hYq_ldkfZQ4](https://v.douyin.com/hYq_ldkfZQ4/) |
| 京东旗舰店 | [mall.jd.com/1000651190](https://mall.jd.com/index-1000651190.html) |
| Bilibili | [bilibili.com](https://www.bilibili.com) |

---

## 本地演示已包含

- 交互式 DIY 装机页：3D 预览按路由加载；不支持或加载失败时保留可结算的清单模式。
- 支付宝 RSA2 适配、回调验签与支付事件幂等；真实商户联调仍需在受控环境完成。
- 前端类型检查、单元测试、生产构建，以及后端测试和 Alembic 单头检查。

## 生产上线前仍需完成

- 对接已签约的物流和邮件服务。
- 配置真实 HTTPS 证书、CSP、Host 校验、限流、备份恢复和告警。
- 完成真实商户、经营主体与合规材料的验收。完整 Go / No-Go 条件见[风险登记与上线验收门槛](docs/project-management/03-risk-and-acceptance.md)。
