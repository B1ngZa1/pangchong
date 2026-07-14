# 五分钟答辩演示

## 答辩前准备

从新克隆的仓库进入 `ecommerce`，不要创建 `.env`：

```powershell
.\start.bat
```

macOS/Linux 使用 `./start.sh`。脚本只有在 PostgreSQL、FastAPI 和前端都通过健康检查后才会显示 `Started successfully`。

- 前端：http://localhost:3000
- 健康检查：http://localhost:8000/health
- 普通用户：`testuser / test123456`
- 管理员：`admin / test123456`

本地 Compose 固定使用随项目启动的 PostgreSQL 和 `backend/uploads`。即使系统环境或旧 `.env` 中还留有已暂停的 Supabase URL、数据库连接串或密钥，也不会访问 Supabase。

## 主路径

1. 在首页展示本地种子目录；进入商品或 DIY 页面说明售价、核价来源和“暂无可靠历史价格”是不同状态，不伪造价格曲线。
2. 进入 DIY，依次选择 CPU、显卡、主板、内存、SSD、散热、电源、机箱。
3. 展示六项兼容性检查、功耗、电源冗余和显卡空间；说明 3DMark 是对比估算而非实测。
4. Fresh clone 默认展示程序生成的交互式 3D 模型；如果部署环境已配置有授权的 GLB，再展示八大件节点显隐和高亮。
5. 加入购物车，登录 `testuser`，选择种子地址并提交订单。点击“去支付”会进入站内 `/sandbox/orders/<订单 ID>`，点击“模拟支付成功”完成支付，不会跳转第三方网关。
6. 退出后登录 `admin`，打开“订单管理”，查看刚才的 DIY 快照、支付状态和种子订单。

## 备用路径

- 主流程订单尚未创建：登录 `testuser` 后打开 `/sandbox/orders/c0000000-0000-0000-0000-000000000002`，使用预置待支付订单演示沙箱支付。
- Supabase 不可用：无需切换；本地 PostgreSQL 和本地上传目录是答辩默认值。
- 商品图片不可用：种子数据和页面错误处理都会回退到 `/assets/pangchong-product-fallback.png`。
- GLB 缺失或加载失败：查看器显示程序模型，配置、兼容性检查和订单快照仍然可用。
- 外部行情不可用：页面显示“暂无可靠历史价格”，不影响 DIY、下单和支付。

预置沙箱订单支付一次后会变为“已支付”。需要恢复全新演示数据时执行：

```bash
docker compose down -v
docker compose up -d --build
```

`down -v` 会删除本机该项目的数据库和 Redis 演示数据，只应在确认不需要保留本地数据时使用。

## 技术亮点

- Vue 3 + FastAPI + PostgreSQL 完整业务闭环。
- 本地优先的数据库、资产存储、沙箱支付和确定性种子数据。
- Supabase 仅是可选的托管 PostgreSQL/Storage 部署目标，Secret Key 不进入浏览器。
- GLB 节点合同、程序模型降级和可审计的 DIY 订单快照。
