# 胖虫项目协作规范

## 开始之前

1. 从最新 `master` 创建短生命周期分支。
2. 一个分支只解决一个可验收目标，避免把重构、功能和格式化混在一起。
3. 修改支付、权限、迁移或生产部署时，至少需要另一名成员复核。
4. 编码前先给出问题、根因、解决方案、修改范围、风险、验证和回滚；详细规则见[开发、Git 与风险更新指南](docs/project-management/05-development-and-git-guide.md)。

推荐分支名：

- `feature/<任务ID>-<简短说明>`
- `fix/<任务ID>-<简短说明>`
- `docs/<任务ID>-<简短说明>`

## 本地质量门禁

Windows：

```powershell
.\scripts\quality-check.ps1
```

macOS/Linux：

```bash
bash scripts/quality-check.sh
```

提交前必须保证前端类型检查、测试和生产构建通过，后端编译、测试和 Alembic migration head 检查通过。

## 提交与评审

- 提交信息使用 `<type>(<scope>): <TASK-ID> [<R-ID>|R-none] <purpose>`，例如 `fix(order): BE-102 [R-01] use server pricing`。
- PR 必须使用仓库模板，包含问题根因、解决方案、修改范围、验证命令、风险和回滚方式。
- 关联风险时必须在同一 PR 更新 `docs/project-management/03-risk-and-acceptance.md`；新风险在发现当日登记。
- 开发者只能把风险改为 `待验收`，P0/P1 必须由非作者验证后关闭。
- 不提交 `.env`、密钥、证书、用户数据、数据库文件、构建产物或本地缓存。
- 行为变化必须同步测试；架构决策必须同步到 `docs/architecture/`。
- 新文档按 `docs/README.md` 的职责目录归类，`docs/` 根目录只保留索引；被替代的资料移入 `docs/archive/` 并注明替代关系。
- 前端、后端、网络、数据或部署边界变化时，同时更新对应架构文档和 `docs/operations/release-checklist.md`。

## 完成定义

任务只有同时满足以下条件才算完成：

- 验收标准逐项通过；
- 自动化质量门禁通过；
- 相关文档和配置同步更新；
- 生产风险与回滚方式已说明；
- 实时风险登记和个人任务卡状态已同步；
- 非作者成员完成评审。
