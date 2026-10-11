# OPS-102 / OPS-103：生产隔离门禁证据

> 门禁：07-27 production-isolation gate  
> 实施与复验记录日期：2026-08-10  
> 关联风险：R-03  
> 状态：已关闭（配置策略、负向启动测试与全新 Docker 数据卷复验通过）

## 实现边界

- `docker-compose.prod.yml` 固定 `APP_ENV=production`，只挂载 schema 初始化和商品组件数据，不挂载 `database/seed.sql`；`!override` 同时防止本地 Compose 叠加时继承 demo seed；`init.sql` 与 `components.sql` 均不得插入用户、订单或订单项。
- 本地 `docker-compose.yml` 继续挂载 demo seed，并显式使用 `APP_ENV=development`、`RELOAD=true`，保留答辩和本地开发便利。
- 生产 `preflight` 必须成功完成，PostgreSQL 和 Redis 才能启动。默认、缺失、短或低多样性的数据库/Redis 密码与 `SECRET_KEY`，`DEBUG=true`、`RELOAD=true`、不安全 CORS、`ALIPAY_SANDBOX=true`，以及缺失/占位支付凭证都会失败退出；错误输出不回显配置值。
- `python -m app.cli.bootstrap_admin` 只允许创建第一个管理员：使用 PostgreSQL 事务级 advisory lock 防止并发双建，发现任意已有管理员后永久拒绝；密码只从交互提示、stdin 或挂载文件读取，不接受命令行密码参数，也不输出密码。初始管理员密码至少 16 字符、至少 8 个不同字符，且不得包含用户名或邮箱本地部分，也不得使用仓库已知弱密码。
- 这项变更没有 schema migration。删除生产 seed 挂载不会清理历史数据卷；已有环境必须单独检查并处置过去导入的 demo 身份和订单。

## Compose 配置策略检查

在仓库根目录运行：

```powershell
Set-Location ecommerce
python scripts/verify_production_config.py
```

该检查渲染并检查独立生产 Compose、`local + production` 叠加 Compose 和本地 Compose：前两者必须无 seed 且数据库/Redis/后端均依赖成功的预检；本地文件必须保留唯一的 demo seed 并固定为 development。2026-08-10 实际结果：

```text
PASS: production Compose is seed-free and preflight-gated; the demo seed remains local-only.
```

## 自动负向启动测试

在仓库根目录运行：

```powershell
Set-Location ecommerce/backend
python -m pytest tests/test_production_startup.py -q
```

2026-08-10 实际结果：`25 passed`。用例覆盖一个合法生产配置和以下失败配置：

- 后端默认和本地 Compose 默认 `SECRET_KEY`；
- 少于 32 字符或字符多样性不足的弱 `SECRET_KEY`；
- 默认/缺失的 PostgreSQL、Redis 密码，以及缺失 Redis URL 密码；
- `DEBUG=true`；
- `RELOAD=true`；
- 空、通配符、HTTP 或 localhost CORS origin；
- `ALIPAY_SANDBOX=true`；
- 分别缺失 `ALIPAY_APP_ID`、`ALIPAY_PRIVATE_KEY`、`ALIPAY_PUBLIC_KEY`；
- 启动错误和管理员输入错误不回显 secret/password；初始管理员弱密码与身份相关密码被拒绝；
- 生产 Compose 重新挂载 demo seed、Dockerfile 重新加入 `--reload`、生产 init SQL 写入用户/订单时的静态回归保护。

单独人工观察失败输出可运行：

```powershell
$env:APP_ENV = 'production'
$env:SECRET_KEY = 'change-me'
$env:DEBUG = 'false'
$env:RELOAD = 'false'
$env:ALIPAY_SANDBOX = 'false'
$env:ALIPAY_APP_ID = '2026000000000001'
$env:ALIPAY_PRIVATE_KEY = 'configured-private-key'
$env:ALIPAY_PUBLIC_KEY = 'configured-public-key'
python -m app.start --check
if ($LASTEXITCODE -eq 0) { throw 'weak production SECRET_KEY was accepted' }
Remove-Item Env:APP_ENV, Env:SECRET_KEY, Env:DEBUG, Env:RELOAD, Env:ALIPAY_SANDBOX, Env:ALIPAY_APP_ID, Env:ALIPAY_PRIVATE_KEY, Env:ALIPAY_PUBLIC_KEY
```

预期：退出码 `2`，stderr 包含 `Production startup preflight failed` 和 `SECRET_KEY`，不会出现 Uvicorn 启动日志。

## 全新生产初始化复验

Docker Desktop/Engine 可用时，在仓库根目录运行：

```powershell
Set-Location ecommerce
python scripts/verify_production_init.py
```

脚本会创建随机 Compose project、临时环境文件和全新 volume，然后依次断言：

1. init 完成后 `users|orders|order_items = 0|0|0`；
2. 一次性命令创建管理员后 `users|admins|orders|known_demo_identities = 1|1|0|0`；
3. 第二次管理员 bootstrap 返回非零并包含 `one-time bootstrap is disabled`；
4. `finally` 清理该随机 project 的容器、volume、network、临时环境文件和临时 backend image。

2026-08-10 实际结果：

```text
PASS: fresh production contains no demo users/orders and bootstrap is one-time.
```

该脚本中的 `down --volumes` 只作用于随机命名的 disposable project。禁止把该参数复制到真实生产 project。

## 生产部署与首次管理员

1. 使用 Docker Compose 2.24.4 或更新版本。从模板创建未跟踪的生产环境文件并替换全部 `replace-me`；支付密钥使用部署平台 secret 注入，不能提交到 Git：

   ```powershell
   Set-Location ecommerce
   Copy-Item .env.production.example .env.production
   python -c "import secrets; print(secrets.token_hex(32))"
   python scripts/verify_production_config.py
   docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build --wait
   ```

2. 只在数据库为空且没有管理员时，由授权运维人员在交互终端运行一次。密码由隐藏提示读取，不进入 shell history：

   ```powershell
   docker compose --env-file .env.production -f docker-compose.prod.yml run --rm --no-deps backend python -m app.cli.bootstrap_admin --username production-admin --email admin@example.com
   ```

3. 记录命令输出中的管理员 username/email 和变更单号，不记录密码；登录后按组织密码轮换流程保存到密码管理器。

4. 对升级前已经存在的数据卷，先只读检查。发现以下已知 demo 数据时保持 No-Go，由数据负责人备份并审批清理/隔离，不能假设移除 seed mount 会自动删除它们：

   ```powershell
   docker compose --env-file .env.production -f docker-compose.prod.yml exec -T postgres psql -U pangchong -d pangchong_ecommerce -c "SELECT id, username, email, is_admin FROM users WHERE id IN ('a0000000-0000-0000-0000-000000000001','a0000000-0000-0000-0000-000000000002') OR username IN ('testuser','admin') OR email IN ('test@pangchong.com','admin@pangchong.com');"
   docker compose --env-file .env.production -f docker-compose.prod.yml exec -T postgres psql -U pangchong -d pangchong_ecommerce -c "SELECT id, order_no, user_id, status FROM orders WHERE id IN ('c0000000-0000-0000-0000-000000000001','c0000000-0000-0000-0000-000000000002') OR order_no IN ('PC202401150001','PCDEMO20260002');"
   ```

如自定义了 `POSTGRES_USER`/`POSTGRES_DB`，上面两个只读命令同步替换 `-U`/`-d` 参数。

## 回滚与止损

- 配置预检失败：不要放宽校验。执行 `docker compose --env-file .env.production -f docker-compose.prod.yml stop nginx backend` 停止接流量，修复 secret/debug/reload/sandbox 配置后重新运行 `python -m app.start --check` 或测试套件，再部署。
- 应用版本回滚：保留当前生产 Compose 的“无 seed 挂载”、`APP_ENV=production` 和启动校验，保留 PostgreSQL/Redis volumes；只回滚应用镜像/代码到上一个也能通过本门禁的版本。真实生产禁止执行 `docker compose down -v`。
- 初始化 SQL 无 migration，因此应用回滚不需要数据库 downgrade。不要为回滚重新挂载 `seed.sql`。
- 管理员建错：先记录审计证据，再用受审批的数据变更将该账号 `is_active=false` 并轮换凭据；不要删除订单关联账号，也不要尝试重复 bootstrap。该命令有意在存在停用管理员时也保持锁闭。
- 如果没有任何历史版本能通过本门禁，回滚目标是停止真实交易并保持 No-Go，而不是恢复带 demo seed、弱密钥、sandbox、debug 或 reload 的旧生产配置。
