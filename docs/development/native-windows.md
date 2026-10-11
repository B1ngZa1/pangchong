# Windows 本地运行（不需要 Docker）

项目也可用 Python 3.11+、Node.js 和 PostgreSQL 16+ 的本机程序运行。

在项目根目录执行：

```powershell
.\ecommerce\start-local.ps1
cd ecommerce/frontend
npm install
npm run dev
```

打开 <http://localhost:3000>。API 文档在 <http://localhost:8000/docs>。
普通用户为 `testuser / test123456`，管理员为 `admin / test123456`。

脚本会创建后端 `.venv`、安装依赖、执行 Alembic 迁移，并在空数据库导入 96 件商品和 14 个分类。
再次运行会保留订单、用户和商品数据。若 Python 或 PostgreSQL 未被找到，可显式指定：

```powershell
.\ecommerce\start-local.ps1 -PythonExecutable C:\Python312\python.exe -PostgresBin 'C:\Program Files\PostgreSQL\18\bin'
```

此模式使用 `output/local-runtime/postgres` 中独立的开发数据库，端口为 `127.0.0.1:55432`，不会连接已有系统数据库。
该数据库仅监听本机回环地址，并使用本地 trust 认证；用于开发演示，不作为生产配置。
API 默认监听 `127.0.0.1:8000`，日志保存在 `output/local-runtime/`。
前端和数据库/后端各自运行；停止前端可在启动终端按 Ctrl+C。
停止后端可通过任务管理器结束日志对应的 Python 进程；脚本创建的 PID 记录在 `backend.pid`。
停止独立数据库时执行 `pg_ctl.exe -D <项目绝对路径>\output\local-runtime\postgres stop -m fast`。

在沙箱订单页点击“模拟支付”后，可登录管理员在订单管理中发货，再由购买用户确认收货。
整个流程不会发起真实扣款。配送费用由 API 返回并由服务器重新计算：默认满 299 元包邮，否则 10 元。

运行全部后端测试（包括真实 PostgreSQL 并发和完整订单流程）：

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\createdb.exe' -h 127.0.0.1 -p 55432 -U pangchong pangchong_test
$env:POSTGRES_TEST_DATABASE_URL='postgresql+asyncpg://pangchong@127.0.0.1:55432/pangchong_test'
cd ecommerce/backend
.\.venv\Scripts\python.exe -m pytest
```

`pangchong_test` 必须是专用测试库。省略该变量时仍可运行单元/API 契约测试，PostgreSQL 测试将跳过。
