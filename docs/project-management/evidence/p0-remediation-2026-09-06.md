# P0 修复证据：支付回调与浏览器会话

日期：2026-09-06

本次只关闭仓库内可直接修复、可自动化验收的 P0 缺口；外部资质、生产备份恢复和非作者上线验收仍保持开放。

## 支付回调信任边界

- `PaymentService.handle_alipay_callback()` 现在要求订单的 `payment_method` **严格等于** `alipay`；未发起支付宝支付的订单即使收到有效 RSA2 通知，也不会进入已支付状态。
- 订单行锁、服务端 Decimal 金额比较、`payment_events` 唯一键和状态单调处理保持不变。
- 回归测试新增“无支付宝 handoff 的订单拒绝回调”，并保留伪造金额、错误 app、错误签名类型、重复/乱序通知测试。

## 浏览器会话边界

- 登录、注册和刷新接口设置 `HttpOnly`、生产强制 `Secure`、`SameSite=Lax`、`Path=/api/auth` 的 refresh cookie。
- 前端不再从 `localStorage` 恢复 access/refresh token；access token 只驻留 Pinia 内存，刷新通过 cookie 完成。旧版本 key 在清理会话时删除。
- 登录/刷新默认响应体不再暴露 refresh token；仅显式携带 `X-Token-Transport: body` 的非浏览器迁移客户端保留旧响应格式。
- 生产配置预检要求 `AUTH_COOKIE_SECURE=true`；非生产本地 HTTP 仍可使用 `false` 以支持开发。
- 保留请求体 refresh token 的短期兼容路径，供非浏览器客户端迁移；浏览器 API 已统一 `withCredentials`。

## 验证结果

本地 `pangchong-frontend` 容器已重启以清理旧 Vite 模块图；重启后 `/products`、`/diy`、`/cart` 和未登录 `/checkout` 均恢复真实路由内容，`DsPriceSummary` 不再触发模块导出错误。

```text
backend: python -m pytest -q
102 passed, 1 skipped

frontend: npm test
18 files, 123 tests passed

frontend: npm run typecheck
passed

frontend: npm run build
passed (仅 Three.js 554.78 kB chunk 仍有 Vite 提示)

frontend: design:tokens:check / design:figma:check / design:lint / copy:check
全部通过；1182 条 UI copy、60 个源文件
```

## 尚不能宣称已关闭的 P0

- R-02 仍需非作者复验和真实支付宝沙箱联调；本地自动化不能替代商户证书、回调网络和对账验收。
- R-05 主体/域名/备案/支付商户材料是外部事项。
- R-07 数据库与商品资产备份恢复尚无隔离环境演练证据。
