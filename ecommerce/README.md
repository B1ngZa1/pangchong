# 胖虫电商系统

> 完整可上线的电商系统，涵盖前端展示、后端逻辑、数据存储、支付安全、三方集成

## 项目概述

本项目是为胖虫科技打造的完整电商系统，采用前后端分离架构，支持商品展示、购物车、订单管理、支付集成等核心功能。

## 技术栈

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Pinia** - Vue 状态管理
- **Vue Router** - 路由管理
- **TailwindCSS** - 原子化 CSS 框架
- **Axios** - HTTP 客户端

### 后端
- **Python 3.11+** - 编程语言
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy** - ORM 框架
- **PostgreSQL** - 关系型数据库
- **Redis** - 缓存（可选）

### 部署
- **Docker** - 容器化
- **Docker Compose** - 多容器编排
- **Nginx** - 反向代理

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
cd ecommerce
docker-compose up -d
```

访问：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 方式二：本地开发

详见 [开发环境搭建指南](docs/setup.md)

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
│   │   └── utils/             # 工具函数
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── views/             # 页面
│   │   ├── store/             # 状态管理
│   │   ├── api/               # API 调用
│   │   └── router/            # 路由
│   ├── package.json
│   └── Dockerfile
├── database/                  # 数据库脚本
│   ├── init.sql              # 初始化脚本
│   └── seed.sql              # 测试数据
├── docker/                   # Docker 配置
├── docker-compose.yml
└── docs/                     # 文档
```

## 核心功能

### 1. 用户系统
- 注册/登录（JWT 认证）
- 个人信息管理
- 收货地址管理

### 2. 商品系统
- 商品分类
- 商品列表（分页、筛选、搜索）
- 商品详情

### 3. 购物车
- 添加/删除/修改数量
- 未登录购物车（Session）
- 登录后购物车合并

### 4. 订单系统
- 从购物车创建订单
- 库存扣减
- 订单状态管理
- 运费计算

### 5. 支付系统
- 支付宝沙箱集成
- 支付回调处理
- 防重复支付

### 6. 三方集成
- 物流查询（快递鸟 API）
- 邮件通知（订单确认、欢迎邮件）
- 客服系统（Tawk.to）

## 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| testuser | test123456 | 普通用户 |
| admin | test123456 | 管理员 |

## 文档

- [架构设计](docs/architecture.md)
- [开发环境搭建](docs/setup.md)
- [项目检查清单](docs/checklist.md)

## API 文档

启动后端服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 安全特性

- JWT Token 认证
- bcrypt 密码加密
- SQL 注入防护（ORM 参数化查询）
- XSS 防护（模板自动转义）
- CSRF 防护（SameSite Cookie）
- HTTPS 支持（Nginx 配置）

## 性能优化

- 数据库索引优化
- Redis 缓存（可选）
- Gzip 压缩
- 静态资源缓存
- 代码分割（路由懒加载）

## 部署

### 生产环境配置

1. 修改 `.env` 文件中的配置
2. 配置 SSL 证书
3. 使用 Docker Compose 部署

```bash
# 构建并启动
docker-compose -f docker-compose.yml up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 许可证

MIT License
