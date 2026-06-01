# 胖虫电商系统 - 项目检查清单

## 1. 前端展示层

- [ ] 首页（商品列表/轮播图）
- [ ] 商品详情页
- [ ] 购物车页
- [ ] 订单结算页
- [ ] 用户个人中心（订单历史、地址管理）
- [ ] 响应式设计（PC、手机、平板）
- [ ] 现代UI（简洁、美观）
- [ ] 交互动效（按钮悬停、加载状态、购物车数量更新）
- [ ] Vue 3 + Pinia 状态管理
- [ ] TailwindCSS 样式方案
- [ ] 与后端 API 交互

## 2. 后端逻辑层

- [ ] 用户注册/登录（JWT 认证）
- [ ] 商品管理（CRUD）
- [ ] 购物车（添加/删除/修改数量，持久化）
- [ ] 购物车合并（未登录与登录后）
- [ ] 订单生成（从购物车创建）
- [ ] 库存扣减
- [ ] 订单号生成
- [ ] 订单状态管理（待支付/已支付/已发货/已完成）
- [ ] 运费计算（满XX元包邮，否则固定运费10元）
- [ ] RESTful API 设计
- [ ] FastAPI 框架
- [ ] SQLAlchemy ORM

## 3. 数据存储层

- [ ] 用户表（users）
- [ ] 用户地址表（user_addresses）
- [ ] 商品分类表（categories）
- [ ] 商品表（products）
- [ ] 购物车表（cart_items）
- [ ] 订单表（orders）
- [ ] 订单商品表（order_items）
- [ ] 价格历史表（price_history）
- [ ] 操作日志表（audit_logs）
- [ ] 数据库索引优化
- [ ] 外键约束
- [ ] 触发器（自动更新时间戳）
- [ ] 视图（订单详情、销售统计）
- [ ] 测试数据（10个商品、2个用户、1个订单）

## 4. 支付与安全

- [ ] 支付宝集成（沙箱环境）
- [ ] 支付回调处理
- [ ] 防止重复支付
- [ ] 金额校验
- [ ] bcrypt 密码加密
- [ ] SQL 注入防护（参数化查询）
- [ ] XSS 防护（模板自动转义）
- [ ] CSRF 防护（SameSite Cookie）
- [ ] JWT Token 过期与刷新机制
- [ ] HTTPS 配置（Nginx + Let's Encrypt）

## 5. 三方集成

- [ ] 物流查询（快递鸟 API 模拟）
- [ ] 邮件发送（订单确认、欢迎邮件）
- [ ] 客服系统（Tawk.to 嵌入代码）
- [ ] 运费估算

## 6. 部署与运维

- [ ] Docker Compose 配置
- [ ] Nginx 反向代理
- [ ] PostgreSQL 数据库
- [ ] Redis 缓存
- [ ] 环境变量配置
- [ ] 健康检查接口
- [ ] 日志配置

## 7. 开发体验

- [ ] API 文档（Swagger UI / ReDoc）
- [ ] 开发环境搭建指南
- [ ] 测试数据脚本
- [ ] 热重载（前端 + 后端）
- [ ] 错误处理与提示

## 8. 代码质量

- [ ] 代码注释（关键逻辑）
- [ ] 类型提示（Python Type Hints）
- [ ] 组件化设计（Vue 组件）
- [ ] 状态管理（Pinia Store）
- [ ] API 封装（Axios 拦截器）
- [ ] 路由守卫（权限控制）

## 9. 性能优化

- [ ] 数据库索引
- [ ] 查询分页
- [ ] 静态资源缓存
- [ ] Gzip 压缩
- [ ] 图片懒加载
- [ ] 代码分割（路由懒加载）

## 10. 用户体验

- [ ] 加载状态提示
- [ ] 错误提示
- [ ] 表单验证
- [ ] 确认对话框
- [ ] Toast 通知
- [ ] 空状态展示

---

## 快速验证命令

```bash
# 1. 启动后端
cd backend
uvicorn app.main:app --reload

# 2. 访问 API 文档
open http://localhost:8000/docs

# 3. 启动前端
cd frontend
npm run dev

# 4. 访问前端
open http://localhost:3000

# 5. 测试 API
curl http://localhost:8000/health
curl http://localhost:8000/api/products
```

## 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| testuser | test123456 | 普通用户 |
| admin | test123456 | 管理员 |
