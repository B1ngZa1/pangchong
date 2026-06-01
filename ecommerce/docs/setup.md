# 胖虫电商系统 - 开发环境搭建指南

## 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+ (可选，用于缓存)
- Git

## 快速开始

### 1. 克隆项目

```bash
cd c:/University/Code_total/pangchong
git clone <repository-url> ecommerce
cd ecommerce
```

### 2. 后端设置

#### 2.1 创建 Python 虚拟环境

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2.2 配置环境变量

For local non-Docker backend runs, create `backend/.env`. Docker Compose uses `ecommerce/.env` as an optional override and otherwise falls back to the local defaults in `docker-compose.yml`.

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://pangchong:060120@localhost:5432/pangchong_ecommerce

# Redis 配置（可选）
REDIS_URL=redis://localhost:6379/0

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 应用配置
DEBUG=true
APP_NAME=胖虫电商系统

# CORS 配置
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# 支付宝配置（沙箱）
ALIPAY_APP_ID=your_app_id
ALIPAY_PRIVATE_KEY=your_private_key
ALIPAY_PUBLIC_KEY=your_public_key
ALIPAY_SANDBOX=true

# 邮件配置（可选）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=noreply@pangchong.com
SMTP_FROM_NAME=胖虫科技

# 快递鸟配置（可选）
KDNIAO_APP_KEY=your_app_key
KDNIAO_APP_SECRET=your_app_secret
```

#### 2.3 初始化数据库

```bash
# 创建数据库
psql -U postgres
CREATE DATABASE pangchong_ecommerce;
CREATE USER pangchong WITH PASSWORD '060120';
GRANT ALL PRIVILEGES ON DATABASE pangchong_ecommerce TO pangchong;
\q

# 导入数据库结构
psql -U pangchong -d pangchong_ecommerce -f ../database/init.sql

# 导入测试数据（可选）
psql -U pangchong -d pangchong_ecommerce -f ../database/seed.sql
```

#### 2.4 启动后端服务

```bash
# 开发模式启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 3. 前端设置

#### 3.1 安装依赖

```bash
cd frontend

# 安装依赖
npm install
```

#### 3.2 启动前端服务

```bash
# 开发模式启动
npm run dev

# 访问前端应用
# http://localhost:3000
```

### 4. 使用 Docker Compose（推荐）

```bash
# 在项目根目录
cd ecommerce

# Optional: create ecommerce/.env to override the built-in Docker defaults.
# Windows: copy .env.example .env
# macOS/Linux: cp .env.example .env

# Start all services from a fresh checkout
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

## 测试账号

测试数据中的用户账号：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| testuser | test123456 | 普通用户 |
| admin | test123456 | 管理员 |

## API 测试

### 使用 curl 测试

#### 用户注册

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "password": "password123"
  }'
```

#### 用户登录

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456"
  }'
```

#### 获取商品列表

```bash
curl "http://localhost:8000/api/products?page=1&page_size=10"
```

#### 添加购物车（需要 Token）

```bash
curl -X POST "http://localhost:8000/api/cart/items" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "product_id": "11111111-1111-1111-1111-111111111111",
    "quantity": 1
  }'
```

### 使用 Swagger UI

1. 访问 http://localhost:8000/docs
2. 点击 "Authorize" 按钮
3. 输入 Token（格式：`Bearer <token>`）
4. 测试各个 API 接口

## 常见问题

### 1. 数据库连接失败

检查 PostgreSQL 服务是否启动，以及 `.env` 文件中的数据库配置是否正确。

```bash
# Windows
net start postgresql-x64-14

# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql
```

### 2. 端口被占用

```bash
# 查看端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# 修改端口
uvicorn app.main:app --port 8001
```

### 3. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 项目结构

```
ecommerce/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic 模式
│   │   ├── services/          # 业务逻辑
│   │   ├── utils/             # 工具函数
│   │   └── main.py            # 应用入口
│   ├── migrations/            # 数据库迁移
│   ├── tests/                 # 测试
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── views/             # 页面
│   │   ├── store/             # Pinia 状态
│   │   ├── api/               # API 调用
│   │   ├── router/            # 路由
│   │   └── assets/            # 静态资源
│   ├── package.json
│   └── Dockerfile
├── database/                  # 数据库脚本
│   ├── init.sql
│   └── seed.sql
├── docker/                    # Docker 配置
├── docker-compose.yml
└── docs/                      # 文档
```

## 下一步

1. 查看 [架构文档](architecture.md) 了解系统设计
2. 查看 API 文档了解接口详情
3. 开始开发你的功能！
