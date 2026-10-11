# BE-101 至 BE-103：服务端权威计价证据

> 实施日期：2026-08-10  
> 关联门槛：07-27 P0 gate  
> 关联风险：R-01、R-04、R-11  
> 当前结论：R-01、R-04 已关闭；R-11 联合契约验收继续独立跟踪

## 1. 冻结请求契约

`POST /api/orders` 保留既有地址、备注、购物车选择和 `custom_items` 外层字段。普通商品仍通过服务端购物车行 ID 结算；DIY 行不再接受名称、图片、规格或价格，只接受配置版本和选项/商品引用：

```json
{
  "address_id": "11111111-1111-1111-1111-111111111111",
  "remark": null,
  "cart_item_ids": ["22222222-2222-2222-2222-222222222222"],
  "custom_items": [
    {
      "configuration": {
        "configuration_id": "diy-pc",
        "version": 1,
        "variant_id": "green",
        "material_id": "gloss",
        "parts": [
          {
            "slot_id": "cpu",
            "product_id": "33333333-3333-3333-3333-333333333333",
            "quantity": 1
          }
        ]
      },
      "quantity": 1
    }
  ],
  "idempotency_key": "44444444-4444-4444-4444-444444444444"
}
```

完整 DIY 请求必须对配置版本定义的八个槽位各引用一次。Pydantic DTO 使用 `extra="forbid"`；在订单或 DIY 行加入 `price: "0.01"` 会返回 422，不能进入计价服务。未携带 `idempotency_key` 的旧普通购物车客户端仍可创建订单，但只有升级后的客户端重试同一 key 时才获得重复提交保护。

## 2. 服务端计价、快照与事务边界

- `app/services/money.py` 将数据库 `Decimal` 售价转换为整数分，所有乘法、求和、运费门槛和最终金额均以分计算，写库时再转成两位 `Decimal`。
- `app/services/diy_catalog.py` 固定 `diy-pc` v1 的槽位、分类、外观/材质名称和服务端差价。客户端只能引用这些 ID。
- `app/services/orders.py` 集中处理地址/购物车读取、配置校验、按稳定顺序 `SELECT ... FOR UPDATE` 锁定商品、合并普通与 DIY 库存需求、服务端计价、库存扣减、购物车清理、flush/commit/rollback 和幂等重放。
- 普通行保存成交名称、图片、规格、单价和小计副本；DIY 行由服务端构造 `_snapshot`，保存配置 ID/版本、配件 ID/名称/规格/成交价/数量、外观引用和总价。后续商品名称、规格或价格变化不会回写历史订单。
- 取消订单根据普通行和 DIY `_snapshot.parts` 恢复库存；创建过程任一步异常由 service 回滚。`(user_id, idempotency_key)` 唯一约束处理并发重复请求；同 key 不同请求指纹返回 409。

数据库变更位于 `a9c3e7d5b102_server_owned_order_pricing.py`：增加订单幂等 key/请求指纹以及订单行配置 ID/版本；`ecommerce/database/init.sql` 同步更新全新初始化结构。

## 3. 自动化证据

2026-08-10 本地执行：

```text
cd ecommerce/backend
python -m compileall -q app
python -m pytest -q
# 84 passed；test_order_service.py 与 test_orders_api.py 覆盖：
# - 普通与 DIY 的 0.01 客户端价格字段被拒绝
# - Decimal/整数分精确合计
# - 普通与 DIY 缺货、下架
# - 当前价格重算与历史快照不随目录变化
# - 重复提交只建一单且只扣一次库存

python -m alembic heads
# a9c3e7d5b102 (head)

cd ecommerce/frontend
npm run check
# vue-tsc 通过；12 files / 72 tests passed；vite build 通过
# checkout.test.js 证明即使本地 DIY 展示价改为 0.01，请求也不含 price/name/specs。
```

本节记录的是 2026-08-10 的服务层基线；当时没有把内存 service 测试等同于真实数据库并发验收。R-04 的 PostgreSQL 末件并发与失败回滚验收已在下节完成。

## 4. R-04 PostgreSQL 并发与回滚闭环

2026-08-14 在 Docker Compose PostgreSQL 16 上使用独立数据库 `pangchong_ecommerce_r04` 完成真实数据库验收。测试入口为 [`test_postgres_concurrency.py`](../../../ecommerce/backend/tests/test_postgres_concurrency.py)，通过真实 FastAPI `POST /api/orders`、独立 async SQLAlchemy sessions 和 PostgreSQL 行锁执行；每个测试使用唯一用户/商品数据，数据库在命令开始时重建，应用种子库不参与测试。

可重复命令（从仓库根目录执行；测试 URL 从正在运行的 backend `DATABASE_URL` 派生，不把密码写入命令或证据）：

```text
cd ecommerce
docker compose up -d --build backend
docker compose exec -T postgres dropdb --if-exists -U pangchong pangchong_ecommerce_r04
docker compose exec -T postgres createdb -U pangchong pangchong_ecommerce_r04
docker compose exec -T backend sh -lc 'DATABASE_URL="${DATABASE_URL%/pangchong_ecommerce}/pangchong_ecommerce_r04" python -m alembic upgrade heads'
docker compose exec -T backend sh -lc 'POSTGRES_TEST_DATABASE_URL="${DATABASE_URL%/pangchong_ecommerce}/pangchong_ecommerce_r04" python -m pytest tests/test_postgres_concurrency.py -q'
docker compose exec -T backend python -m pytest tests/test_orders_api.py tests/test_order_service.py::test_duplicate_submit_returns_the_original_order_and_decrements_stock_once -q
docker compose exec -T postgres dropdb --if-exists -U pangchong pangchong_ecommerce_r04
```

实测结果：

```text
python -m alembic upgrade heads
# exit 0；完整迁移图应用到 a9c3e7d5b102 与 c7b3e8f1a204 两个 head

tests/test_postgres_concurrency.py
# 3 passed, 2 warnings in 1.55s

tests/test_orders_api.py + duplicate-submit service regression
# 4 passed, 2 warnings in 1.19s

dropdb cleanup
# exit 0
```

三项 PostgreSQL 断言覆盖：

1. 相同 `(user_id, idempotency_key)` 并发提交：两个 HTTP 请求均返回 `201`，返回同一个订单；随后再次 replay 仍返回同一订单；数据库为 `orders=1`、`order_items=1`、商品 `stock=0`、`sold_count=initial+1`、购物车行 `0`。
2. 不同幂等 key 并发争抢末件：两个请求中恰好一个返回 `201`，另一个返回 `400 out of stock`；数据库仍只有一单，商品只扣一个库存单位并只增加一次 `sold_count`，购物车行已删除。
3. 在真实 flush 完成后注入 commit 失败：service 回滚后数据库为 `orders=0`、`order_items=0`、商品 `stock=1`、`sold_count=initial`、购物车行 `1`，证明订单、库存、销量和购物车删除位于同一事务。

实现补强位于 [`orders.py`](../../../ecommerce/backend/app/services/orders.py)：首次幂等查询之后、购物车读取后和商品行锁取得后再次检查幂等订单。这样第二个相同 key 请求在等待首个事务释放商品行锁后会 replay 已提交订单，不会因末件库存已为 0 被误报为缺货；不同 key 仍经过同一行锁并由服务端库存校验拒绝。

## 5. R-01 独立复验与 Supabase 证据

2026-08-10 使用 Python 3.11 和仓库锁定依赖完成全量复验：

```text
uv run --no-project --isolated --python 3.11 --with-requirements requirements.txt pytest -q
# 84 passed；包含 3 项 HTTP API 测试

python -m compileall -q app
# exit 0

npm run check
# vue-tsc 通过；12 个测试文件、72 项测试通过；Vite production build 通过

python -m alembic heads
# a9c3e7d5b102 (head)
```

[`test_orders_api.py`](../../../ecommerce/backend/tests/test_orders_api.py) 通过真实 FastAPI 路由和生产 `OrderService` 验证：

1. DIY 行附加 `price: "0.01"` 返回 HTTP 422，且没有创建订单；
2. 配置版本高于服务端 `diy-pc` v1 返回 HTTP 409，且事务回滚；
3. 不带任何价格的引用请求按服务端八件商品当前价创建订单；随后修改目录对象的名称、价格和规格，再次读取订单时成交行和 `_snapshot` 保持完全一致。

连接的 Supabase `pangchong` 项目只读复验结果：

- migration 列表包含 `20260810014452 / alembic_schema_a9c3e7d5b102`；
- `information_schema.columns` 确认 `orders.idempotency_key`、`orders.request_fingerprint`、`order_items.configuration_id` 和 `order_items.configuration_version` 已存在；
- `pg_constraint` 确认 `uq_orders_user_idempotency_key` 为 `UNIQUE (user_id, idempotency_key)`；
- migration 后 Supabase Security/Performance Advisors 没有新增 WARN/ERROR。仅返回既有 INFO：RLS 已启用且没有 Data API policy（本应用订单写入走受信 FastAPI/直连数据库，因此公开角色默认无访问）及低流量环境中的 unused-index 提示。

这些证据关闭 R-01 的价格/快照信任边界；R-04 的独立 PostgreSQL 验收见第 4 节；这些证据不自动关闭 R-11。

## 6. 回滚与止损

1. 先关闭或网关阻断 `POST /api/orders`，等待在途创建请求结束；订单查询和已创建订单支付可保持只读/既有流程。
2. 记录部署边界内的订单 ID、幂等 key、订单行快照及商品库存/sold_count，完成一次订单—库存对账。发现差异时保持下单关闭并人工修正，不用代码回滚掩盖差异。
3. 前端 Checkout 与后端订单服务必须作为同一兼容单元回滚。旧后端会重新信任客户端 DIY 价格，因此回滚期间不得恢复真实订单写入；优先以前滚修复替代长期回退。
4. 应用已回退且确认不再读取新字段后，执行 `python -m alembic downgrade b7e1c4a9d203`。该降级只删除幂等/配置引用列和唯一约束，不修改订单金额、订单行价格快照或库存。
5. 若只回滚迁移而仍运行新应用，创建订单会失败；若只回滚前端，旧 DIY payload 会被新后端以 422 拒绝。两种半回滚都应由健康检查阻止放量。
