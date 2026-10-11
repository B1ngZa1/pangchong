# 商品数据工具

本目录存放离线商品采集与 DIY 配件数据生成工具，避免一次性数据脚本与在线业务代码混放。

## 环境准备

```bash
python -m venv .venv
python -m pip install -r tools/catalog/requirements.txt
```

## 使用方式

从仓库根目录运行：

```bash
python tools/catalog/scraper.py
python tools/catalog/diy_parts.py
```

两个脚本共用 `tools/catalog/pangchong.db`。爬虫还会在本目录生成 `products.json` 和 `products_db.js`。

## 使用边界

- 仅采集有权使用的数据，并遵守目标网站条款、访问频率和知识产权要求。
- 采集结果必须经过人工核价、授权来源和字段完整性检查后，才能进入正式商品库。
- 生成的 SQLite、JSON 和 JS 数据属于本地中间产物，不应直接作为生产数据库。

