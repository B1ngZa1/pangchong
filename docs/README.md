# 胖虫项目文档中心

本目录是全项目的唯一文档入口。文档按职责物理分类，不再把产品、架构、部署、审计和历史材料平铺在 `docs/` 根目录。

## 新成员推荐阅读

1. [系统总览](architecture/system-overview.md)
2. [本地开发环境](development/local-setup.md)
3. [前端架构](architecture/frontend.md)或[后端架构](architecture/backend.md)
4. [网络与安全](architecture/network-security.md)
5. [协作规范](../CONTRIBUTING.md)

## 分类索引

| 分类 | 内容 | 入口 |
| --- | --- | --- |
| 架构 | 系统、前端、后端、网络安全、数据存储 | [architecture/](architecture/README.md) |
| 开发 | 本地安装、启动与调试 | [development/](development/README.md) |
| 部署 | 生产部署和托管服务边界 | [deployment/](deployment/README.md) |
| 运维 | 发布检查、回滚、监控和日常操作 | [operations/](operations/README.md) |
| 产品 | 商品、DIY、服务协议、演示和门店资料 | [product/](product/README.md) |
| 3D | PC Builder 方案与资产流水线 | [3d/](3d/README.md) |
| 规划 | 项目与技术栈优化方案 | [planning/](planning/README.md) |
| 审计 | 全栈和商业化准备度审计 | [audits/](audits/README.md) |
| 设计系统 | 视觉 token、组件和设计资产 | [design-system/](design-system/README.md) |
| 项目管理 | 老板策划、四人任务、风险和验收证据 | [project-management/](project-management/README.md) |
| 数据 | 价格核验数据和口径 | [data/](data/README.md) |
| 历史归档 | 已被替代但需保留追溯的资料 | [archive/](archive/README.md) |

## 目录约定

- `docs/` 根目录只保留本索引；新文档必须进入职责目录。
- README 负责导航，长篇内容使用独立文件；同一主题只保留一个现行真值来源。
- 架构文档必须区分“已实现、部分实现、目标、阻断项”，不能把计划写成现状。
- 功能变化同步更新对应的产品/架构文档；部署或安全变化同步更新发布清单。
- 过时文档移入 `archive/` 并写明替代文档，不静默删除历史依据。
- 管理和审计文档使用 `YYYY-MM-DD` 日期，注明状态、负责人或适用读者。

工具自身的用法放在相邻 `README.md`，例如[商品数据工具](../tools/catalog/README.md)，不混入业务架构。
