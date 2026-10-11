# 胖虫电商系统

胖虫电商系统是一个前后端分离的本地开发栈，包含 Vue 3 前端、FastAPI 后端、PostgreSQL 数据库和 Redis。仓库已提供 Docker Compose 默认配置，新克隆后可以直接启动，不需要先猜测或手动创建 `.env`。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vue Router、Pinia、TailwindCSS、Axios、Vite |
| 后端 | Python 3.11、FastAPI、SQLAlchemy、Pydantic |
| 数据 | PostgreSQL 16、Redis 7 |
| 容器 | Docker、Docker Compose |

## 快速开始

前置要求：

- Docker Desktop 或可用的 Docker Engine
- Docker Compose v2（`docker compose`）或旧版 `docker-compose`

从新克隆的仓库进入应用目录：

```bash
git clone <repository-url> pangchong
cd pangchong/ecommerce
```

### Windows 一键启动

```bat
.\start.bat
```

### macOS/Linux 一键启动

```bash
./start.sh
```

### 直接使用 Docker Compose

```bash
docker compose up -d --build
```

如果你的环境只支持旧版命令，也可以使用：

```bash
docker-compose up -d --build
```

启动后访问：

| 服务 | 地址 |
| --- | --- |
| 前端应用 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| Swagger 文档 | http://localhost:8000/docs |
| ReDoc 文档 | http://localhost:8000/redoc |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## `.env` 怎么用

新克隆项目后可以不创建 `.env`。`docker-compose.yml` 已经内置本地开发默认值：

- 数据库：`pangchong_ecommerce`
- 数据库用户：`pangchong`
- 数据库密码：`pangchong_dev_password`
- Redis 密码：`pangchong_dev_redis`
- JWT 密钥：`change-me-local-dev-secret`
- 资产存储：本地 `backend/uploads`

只有在需要覆盖这些默认值、CORS 来源或第三方服务配置时，才复制环境变量模板：

```bat
copy .env.example .env
```

macOS/Linux：

```bash
cp .env.example .env
```

Docker Compose 会自动读取当前目录下的 `.env`。为保证离线答辩可用，本地 Compose 不接受外部 `DATABASE_URL`，并固定使用本地资产存储；Supabase 只通过 `docker-compose.prod.yml` 或手动后端配置启用。手动运行后端时请使用 `backend/.env`，详见 [开发环境搭建指南](../docs/development/local-setup.md)。

如果已经启动过数据库容器，再修改 `POSTGRES_PASSWORD`、`POSTGRES_USER` 或 `POSTGRES_DB`，旧数据卷仍会保留第一次初始化时的配置。要用新配置重建本地数据，请运行：

```bash
docker compose down -v
docker compose up -d --build
```

## 测试账号

`docker-compose.yml` 是显式的本地 demo seed 入口。只有它会在全新的本地数据库卷上导入 `database/seed.sql`；`docker-compose.prod.yml` 不包含该挂载。以下公开账号和本地弱凭证只能用于开发/答辩，生产预检会拒绝它们。

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| `testuser` | `test123456` | 普通用户 |
| `admin` | `test123456` | 管理员 |

生产首次管理员必须使用一次性命令创建，且任何管理员存在后该命令都会拒绝再次执行。生产配置、初始化复验、管理员命令与回滚步骤见 [OPS-102/OPS-103 证据](../docs/project-management/evidence/ops-102-103-production-isolation.md)。

## 生产安全启动

> 注意：生产 Compose 只提供容器拓扑和配置预检，不代表系统已经可承载真实交易。支付宝 RSA2 适配器、金额校验和支付事件幂等已落地；HTTPS/443、refresh token 安全 Cookie、CSRF、统一限流、监控和真实商户联调仍需按[网络与安全基线](../docs/architecture/network-security.md)完成。

生产部署要求 Docker Compose 2.24.4 或更新版本。生产文件使用 `!override` 保护数据库初始化挂载，因此误把本地 Compose 放在生产文件之前叠加时，demo seed 仍会被移除。

从专用模板创建未跟踪的生产配置，替换全部占位值，然后先运行轻量策略检查：

```bash
cp .env.production.example .env.production
python scripts/verify_production_config.py
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build --wait
```

生产栈先执行一次 `preflight`。数据库和 Redis 密码、JWT 密钥、正式支付凭证、HTTPS CORS、非调试/非热重载模式全部通过后，PostgreSQL 和 Redis 才能启动。随后一次性的 `migrate` 服务会执行 `alembic upgrade head`；只有迁移成功，API 才会启动。生产数据库不再挂载 `init.sql`、`components.sql` 或任何 demo seed。失败信息只包含字段和规则，不回显凭证值。

全新生产数据库不会自动创建账号。数据库就绪后，通过隐藏的交互提示创建唯一的首个管理员；不要把密码放在命令参数中：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm backend \
  python -m app.cli.bootstrap_admin \
  --username <initial-admin> \
  --email <admin@example.com>
```

初始管理员密码至少 16 个字符、至少 8 种不同字符，并且不能包含用户名或邮箱本地部分。完整的一次性 Docker 验证入口为 `python scripts/verify_production_init.py`。

## 常用命令

```bash
# 查看容器状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 只看后端日志
docker compose logs -f backend

# 重启服务
docker compose restart

# 停止服务，保留数据库和 Redis 数据
docker compose down

# 停止服务并清空本地数据卷
docker compose down -v
```

## 本地手动开发

如果你不想通过 Docker 跑前后端，可以手动安装 Python、Node.js、PostgreSQL 和 Redis。完整步骤见 [开发环境搭建指南](../docs/development/local-setup.md)。

简要流程：

```bash
# 后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd ../frontend
npm install
npm run dev
```

## 项目结构

```
ecommerce/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # API 路由
│   │   ├── core/               # 配置、数据库、安全工具
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic Schema
│   │   ├── services/           # 业务服务
│   │   └── utils/              # 工具函数
│   ├── migrations/             # Alembic 迁移
│   ├── tests/                  # 后端测试
│   └── Dockerfile
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 客户端
│   │   ├── components/         # 通用组件
│   │   ├── router/             # 路由
│   │   ├── store/              # Pinia 状态
│   │   └── views/              # 页面
│   └── Dockerfile
├── database/                   # 数据库初始化脚本
│   ├── init.sql
│   ├── seed.sql
│   └── components.sql
├── docker/                     # Nginx 等容器配置
├── docker-compose.yml          # 本地开发 Compose 文件
├── docker-compose.prod.yml     # 生产部署 Compose 文件
├── .env.example                # 可选 Compose 环境变量模板
├── start.bat                   # Windows 一键启动
└── start.sh                    # macOS/Linux 一键启动
```

## 文档

- [开发环境搭建指南](../docs/development/local-setup.md)
- [系统与前后端架构](../docs/architecture/README.md)
- [网络与安全基线](../docs/architecture/network-security.md)
- [发布检查清单](../docs/operations/release-checklist.md)

## 许可证

MIT License
