# 胖虫 PangChong - DIY电脑官网

> 极致性能，由你定义

胖虫是一家专注DIY电脑的厂商，提供游戏笔记本、轻薄本、台式主机、工作站和迷你主机全线产品。本项目为胖虫官网前端，采用雷蛇风格暗黑主题，集成产品展示、DIY在线装机、购物车等完整功能。

## 项目文件

```
pangchong/
├── index.html          # 首页（产品展示、DIY定制介绍、社区）
├── products.html       # 产品列表页（全部产品筛选浏览）
├── diy.html            # DIY在线装机页（141款配件自由搭配）
├── about.html          # 核心技术页（品牌故事、六大优势）
├── style.css           # 全局样式表（雷蛇风格暗黑主题）
├── script.js           # 交互逻辑 + 产品/配件数据库
├── scraper.py          # 京东 & 抖音商品爬虫
├── diy_parts.py        # DIY八大件数据库构建脚本
├── pangchong.db        # SQLite 本地数据库
├── products.json       # 导出：JSON格式产品数据
├── products_db.js      # 导出：JS格式产品数据
└── README.md           # 本文件
```

## 页面导航

| 页面 | 文件 | 说明 |
| --- | --- | --- |
| 首页 | [index.html](index.html) | 品牌首页，产品展示、DIY定制介绍、社区、用户评价 |
| 产品列表 | [products.html](products.html) | 全部17款产品，支持6分类筛选浏览 |
| DIY装机 | [diy.html](diy.html) | 141款配件自由搭配，5套预设方案，实时价格/功耗计算 |
| 核心技术 | [about.html](about.html) | 品牌故事、六大核心技术、品质流程、合作伙伴 |

## 文档目录

| 文档 | 说明 |
|------|------|
| [网站页面结构](docs/website.md) | 完整页面目录树、交互功能清单、外部链接 |
| [整机产品目录](docs/products.md) | 17款全线产品配置、价格、分类 |
| [DIY八大件配件库](docs/diy-parts.md) | 141款主流配件详细规格、价格、推荐 |

## 快速开始

```bash
# 1. 直接打开网页预览（无需构建工具）
start index.html

# 2. 构建DIY配件数据库
python diy_parts.py

# 3. 运行爬虫更新整机产品数据
python scraper.py
```

## 数据概览

| 类别 | 数量 | 说明 |
| --- | --- | --- |
| 整机产品 | 17款 | 游戏本6 / 轻薄本2 / 台式4 / 工作站2 / 迷你3 |
| DIY配件 | 141款 | CPU30 / GPU22 / 主板18 / 内存14 / SSD16 / 电源13 / 机箱12 / 散热16 |

## 核心功能

- **产品展示** — 6分类筛选、快速预览弹窗、购物车
- **DIY在线装机** — 8大配件自由搭配、5套预设方案、实时价格/功耗计算
- **全局搜索** — 实时匹配产品名、配置、系列
- **响应式布局** — 适配手机/平板/桌面三端
- **粒子动画** — 英雄区背景连线粒子效果

## 购买渠道

| 平台 | 链接 |
|------|------|
| 抖音主页 | https://v.douyin.com/hYq_ldkfZQ4/ |
| 京东旗舰店 | https://mall.jd.com/index-1000651190.html |
| B站 | https://www.bilibili.com |

## 技术栈

- 前端：HTML + CSS + Vanilla JS（零依赖）
- 数据库：SQLite（diy_parts.py / scraper.py）
- 爬虫：requests + BeautifulSoup（京东/抖音，反爬回退本地数据）

## 后续扩展

- [ ] 替换SVG占位图为真实产品图片
- [ ] 对接支付API（京东/支付宝/微信）
- [ ] 添加产品详情页
- [ ] 接入后端数据库管理
- [ ] 用户注册/登录系统
- [ ] SEO优化
- [ ] 部署上线
