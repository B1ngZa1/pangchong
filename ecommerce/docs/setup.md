# 胖虫电商系统 - 本地启动指南

这份指南面向第一次从 GitHub 克隆项目的开发者。推荐使用 Docker Compose 启动完整栈；如果你要调试后端或前端，也可以按后面的手动开发流程运行。

## 你会启动哪些服务

| 服务 | 容器名 | 本地地址 |
| --- | --- | --- |
| 前端 Vite 服务 | `pangchong-frontend` | http://localhost:3000 |
| 后端 FastAPI 服务 | `pangchong-backend` | http://localhost:8000 |
| API 文档 | `pangchong-backend` | http://localhost:8000/docs |
| PostgreSQL | `pangchong-postgres` | localhost:5432 |
| Redis | `pangchong-redis` | localhost:6379 |

PostgreSQL 容器第一次创建数据卷时，会自动导入：

- `database/init.sql`
- `database/seed.sql`
- `database/components.sql`

## 前置要求

Docker 启动方式只需要：

- Git
- Docker Desktop 或可用的 Docker Engine
- Docker Compose v2（`docker compose`）或旧版 `docker-compose`

手动开发方式还需要：

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7（当前代码基本不依赖 Redis，但 Docker 栈会一起启动）

## 推荐方式：Docker Compose

### 1. 克隆并进入项目

```bash
git clone <repository-url> pangchong
cd pangchong/ecommerce
```

如果你已经在仓库根目录：

```bash
cd ecommerce
```

### 2. 直接启动

Windows：

```bat
.\start.bat
```

macOS/Linux：

```bash
./start.sh
```

也可以不使用脚本，直接运行：

```bash
docker compose up -d --build
```

旧版 Compose：

```bash
docker-compose up -d --build
```

### 3. 打开页面

| 内容 | 地址 |
| --- | --- |
| 前端应用 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### 4. 登录测试账号

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| `testuser` | `test123456` | 普通用户 |
| `admin` | `test123456` | 管理员 |

## `.env` 行为说明

新克隆项目后不需要创建 `.env`。`docker-compose.yml` 已经写入本地开发默认值：

| 变量 | 默认值 |
| --- | --- |
| `POSTGRES_DB` | `pangchong_ecommerce` |
| `POSTGRES_USER` | `pangchong` |
| `POSTGRES_PASSWORD` | `pangchong_dev_password` |
| `REDIS_PASSWORD` | `pangchong_dev_redis` |
| `SECRET_KEY` | `change-me-local-dev-secret` |
| `DEBUG` | `true` |
| `ALLOWED_ORIGINS` | `["http://localhost:3000","http://localhost","http://localhost:80"]` |

只有在你要修改默认密码、JWT 密钥、CORS 来源、支付宝或邮件配置时，才复制模板：

```bat
copy .env.example .env
```

macOS/Linux：

```bash
cp .env.example .env
```

注意：

- Docker Compose 会自动读取 `ecommerce/.env`，并用其中的变量覆盖 `docker-compose.yml` 的默认值。
- `.env` 已在 `.gitignore` 中忽略，不要提交。
- `ecommerce/.env` 只服务于 Docker Compose。
- 手动运行后端时，请在 `backend/.env` 中配置 `DATABASE_URL` 等变量。
- 如果已经启动过数据库容器，再修改 `POSTGRES_DB`、`POSTGRES_USER` 或 `POSTGRES_PASSWORD`，旧数据卷仍保留第一次初始化的数据库。需要重建时运行 `docker compose down -v`。

## 常用 Docker 命令

```bash
# 查看容器状态
docker compose ps

# 查看全部日志
docker compose logs -f

# 只看后端日志
docker compose logs -f backend

# 只看前端日志
docker compose logs -f frontend

# 重启所有服务
docker compose restart

# 停止服务，保留数据库和 Redis 数据
docker compose down

# 停止服务并删除本地数据卷
docker compose down -v
```

## 手动开发：后端

手动运行后端时，建议从 `ecommerce/backend` 目录启动。`app/core/config.py` 会从当前工作目录读取 `.env`。

### 1. 创建虚拟环境并安装依赖

```bash
cd ecommerce/backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 准备本地 PostgreSQL

下面的账号和密码与 Docker Compose 默认值保持一致。

```sql
CREATE USER pangchong WITH PASSWORD 'pangchong_dev_password';
CREATE DATABASE pangchong_ecommerce OWNER pangchong;
```

从 `ecommerce` 目录导入表结构和测试数据：

```bash
cd ecommerce

psql -U pangchong -d pangchong_ecommerce -f database/init.sql
psql -U pangchong -d pangchong_ecommerce -f database/seed.sql
psql -U pangchong -d pangchong_ecommerce -f database/components.sql
```

### 3. 创建 `backend/.env`

```env
DATABASE_URL=postgresql+asyncpg://pangchong:pangchong_dev_password@localhost:5432/pangchong_ecommerce
REDIS_URL=redis://:pangchong_dev_redis@localhost:6379/0
SECRET_KEY=change-me-local-dev-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=true
APP_NAME=胖虫电商系统
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost","http://localhost:80"]

ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
ALIPAY_PUBLIC_KEY=
ALIPAY_SANDBOX=true

SMTP_USER=
SMTP_PASSWORD=
```

### 4. 启动后端

```bash
cd ecommerce/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

- http://localhost:8000/docs
- http://localhost:8000/redoc

## 手动开发：前端

```bash
cd ecommerce/frontend
npm install
npm run dev
```

Vite 默认监听 http://localhost:3000，并把 `/api` 请求代理到 `http://localhost:8000`。如需覆盖代理目标：

PowerShell：

```powershell
$env:VITE_API_TARGET="http://localhost:8001"
npm run dev
```

CMD：

```bash
set VITE_API_TARGET=http://localhost:8001
npm run dev
```

macOS/Linux：

```bash
VITE_API_TARGET=http://localhost:8001 npm run dev
```

## API 快速测试

登录：

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456"
  }'
```

商品列表：

```bash
curl "http://localhost:8000/api/products?page=1&page_size=10"
```

添加购物车需要登录后的 Token：

```bash
curl -X POST "http://localhost:8000/api/cart/items" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "product_id": "11111111-1111-1111-1111-111111111111",
    "quantity": 1
  }'
```

## 常见问题

### 端口被占用

检查 3000、8000、5432、6379：

```bat
netstat -ano | findstr :8000
```

macOS/Linux：

```bash
lsof -i :8000
```

### 修改数据库密码后连接失败

PostgreSQL 官方镜像只在首次创建数据卷时初始化数据库。修改 `.env` 后，如果旧数据卷还在，容器内数据库不会自动改密码。开发环境可直接重建：

```bash
docker compose down -v
docker compose up -d --build
```

### 依赖安装慢

后端：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

前端：

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### Docker Compose 命令不一致

新版本使用：

```bash
docker compose ps
```

旧版本使用：

```bash
docker-compose ps
```

`start.bat` 和 `start.sh` 会自动选择可用命令。

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
│   ├── tests/                  # 测试
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
├── .env.example                # 可选 Compose 环境变量模板
├── start.bat                   # Windows 一键启动
└── start.sh                    # macOS/Linux 一键启动
```
