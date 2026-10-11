# 部署文档

- [Supabase 部署边界](supabase.md)：托管 PostgreSQL 与 Storage 的使用范围、配置和安全边界。
- [本地开发环境](../development/local-setup.md)：本地 Compose 与手动启动。
- [系统总览](../architecture/system-overview.md)：部署拓扑和环境差异。
- [网络与安全](../architecture/network-security.md)：域名、TLS、端口、安全组和生产门禁。

当前 `docker-compose.prod.yml` 是生产形态的基础模板，不等于已经完成域名、HTTPS、监控、备份、正式支付和云安全组配置。
