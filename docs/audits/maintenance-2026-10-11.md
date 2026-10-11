# 2026-10-11 工程维护与 Git 同步

## 计划和证据

用户要求维护当前项目，并同步聊天中关联的其他 GitHub 项目。通过聊天 cwd、Git origin、工作树和项目检查识别到本仓库。

维护顺序：保留既有改动 → 审计敏感与运行文件 → 运行现有验证 → 应用兼容依赖修复 → 复验 → 提交并正常推送。

## 本轮改动

- 补齐 Git 忽略规则：数据库旁文件、测试缓存、Playwright 元数据/报告、前端输出和根 output。
- PostgreSQL 集群、UV 缓存、截图、QA 会话和本地恢复补丁全部保留在磁盘，不上传。
- 执行 `npm.cmd audit fix --ignore-scripts --no-fund`，仅应用现有版本范围允许的依赖更新。
- 清理五个源码/配置文件末尾多余空行，保留既有 Markdown 硬换行空格。
- 提交已有应用、测试、设计系统、启动工具和文档变更；原 master 已有两个本地提交一并同步。
- 既有 docs/scripts 删除与新增路径属于此前重组，本轮没有执行新的删除、移动或重命名。

## 验证结果

| 检查 | 结果 |
| --- | --- |
| `npm.cmd run check`（ecommerce/frontend） | 类型检查、19 个测试文件/138 项测试、生产构建通过 |
| `.\.venv\Scripts\python.exe -m pytest -m "not postgres"`（ecommerce/backend） | 115 passed、1 skipped；排除 PostgreSQL 并发测试 |
| `python scripts/check_structure.py` | 通过 |
| `git -c core.whitespace=cr-at-eol diff --cached --check -- . ':!*.md'` | 源码通过，既有 Markdown 格式保留 |
| 私钥和常见 GitHub/API/AWS token 模式扫描 | 未发现匹配；不是全面安全认证 |

测试中的支付路径使用本地模拟/沙箱逻辑；未连接真实支付接口。既有路由测试警告、模拟离线错误和 Three.js 大 chunk 提示保留。

## 已有目录重组核对

- diy_parts.py、scraper.py 已对应 tools/catalog/ 下的新文件。
- import_price_verification.py 已对应 ecommerce/backend/app/cli/ 下的新文件。
- 14 个旧根 docs 对应 docs/3d、product、audits、planning、deployment 或 archive。
- 旧 ecommerce 架构和安装说明对应 docs/archive/legacy-ecommerce-architecture.md、docs/development/local-setup.md。
- 旧 ecommerce/docs/checklist.md 没有单文件替代，当前发布/风险验收规则分布于 docs/operations/release-checklist.md 和 docs/project-management/03-risk-and-acceptance.md。旧版本仍可用 `git show 51368d7:ecommerce/docs/checklist.md` 只读检索，不复用旧测试账户信息。

## 未完成项与恢复

- npm audit 从 23 项降至 15 项：2 critical、8 high、5 moderate。Vitest/Tinypool、Tailwind、Vite/esbuild 等需要另行迁移和回归；Vue/server-renderer 仍有可修复告警，需核对依赖解析。本轮不将审计结果表述为无漏洞。
- PostgreSQL 并发集成、完整浏览器验收、部署和真实支付未执行。
- master 的维护前 HEAD 为 51368d7，origin 为 B1ngZa1/pangchong。
- 本地恢复材料在 output/git-maintenance-backups/2026-10-11/，保存原暂存/未暂存补丁和依赖文件备份；可能包含本地配置，按敏感资料保管，不上传。
- 本轮没有 reset、强制推送、清理用户文件、修改业务数据库、执行迁移或操作真实订单。
