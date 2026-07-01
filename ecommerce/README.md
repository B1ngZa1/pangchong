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

新克隆项目后可以不创建 `.env`。`docker-compose.yml` 使用 `${变量:-默认值}` 写法，已经内置本地开发默认值：

- 数据库：`pangchong_ecommerce`
- 数据库用户：`pangchong`
- 数据库密码：`pangchong_dev_password`
- Redis 密码：`pangchong_dev_redis`
- JWT 密钥：`change-me-local-dev-secret`

只有在需要覆盖这些默认值、CORS 来源或第三方服务配置时，才复制环境变量模板：

```bat
copy .env.example .env
```

macOS/Linux：

```bash
cp .env.example .env
```

Docker Compose 会自动读取当前目录下的 `.env`。这个文件只影响 Docker Compose 启动的服务，手动运行后端时请使用 `backend/.env`，详见 [开发环境搭建指南](docs/setup.md)。

如果已经启动过数据库容器，再修改 `POSTGRES_PASSWORD`、`POSTGRES_USER` 或 `POSTGRES_DB`，旧数据卷仍会保留第一次初始化时的配置。要用新配置重建本地数据，请运行：

```bash
docker compose down -v
docker compose up -d --build
```

## 测试账号

数据库首次初始化时会导入 `database/seed.sql` 中的测试账号。

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| `testuser` | `test123456` | 普通用户 |
| `admin` | `test123456` | 管理员 |

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

如果你不想通过 Docker 跑前后端，可以手动安装 Python、Node.js、PostgreSQL 和 Redis。完整步骤见 [开发环境搭建指南](docs/setup.md)。

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
├── docs/                       # 项目文档
├── docker-compose.yml          # 本地开发 Compose 文件
├── docker-compose.prod.yml     # 生产部署 Compose 文件
├── .env.example                # 可选 Compose 环境变量模板
├── start.bat                   # Windows 一键启动
└── start.sh                    # macOS/Linux 一键启动
```

## 文档

- [开发环境搭建指南](docs/setup.md)
- [架构设计](docs/architecture.md)
- [项目检查清单](docs/checklist.md)

## 许可证

MIT License
