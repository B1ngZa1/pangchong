# 项目 UI 文案清单与后期修改

当前清单从 `ecommerce/frontend/src` 中提取可见模板文本、可见属性和包含中文的脚本文本。行政区划 `src/data/regions.js` 属于参考数据，刻意不纳入可编辑文案。

## 文件

- `ui-copy.inventory.csv`：给产品、运营和文案人员审校；Excel 可直接打开。
- `ui-copy.inventory.json`：机器校验与精确定位。
- `ui-copy.overrides.json`：批准后的修改项，避免直接编辑生成清单。

清单字段：

| 字段 | 含义 |
| --- | --- |
| `id` | 按源码文件、文本类型与序号生成的定位 ID |
| `file / line` | 当前源码位置 |
| `kind` | `template-text / attribute / script-string` |
| `owner` | `brand / product / commerce / service / operations` |
| `sourceText` | 当前源码文案 |
| `replacement` | CSV 审校建议列，不直接写回 |
| `status / notes` | 审校状态与备注 |

## 提取与校验

在 `ecommerce/frontend` 中执行：

```powershell
npm run copy:extract
npm run copy:check
```

`copy:check` 用于 CI。源码有新文案但清单未更新时会失败。

## 批量修改

先在 `ui-copy.overrides.json` 添加：

```json
{
  "replacements": {
    "views.home.template-text.001": {
      "from": "PANGCHONG PERFORMANCE LAB",
      "to": "PANGCHONG PERFORMANCE STUDIO"
    }
  }
}
```

然后执行：

```powershell
npm run copy:apply
npm run copy:apply -- --write
npm run copy:extract
npm run check
```

第一条只 dry-run；只有显式增加 `--write` 才会修改源码。`from` 与当前文案不一致时脚本会停止，避免把修改应用到错误位置。

## 文案规范

- 按钮用动作 + 结果：`保存地址`、`重新加载商品`；避免泛化的“确定”。
- 错误说明事实并给下一步：`商品加载失败，请重试`；不要写成“暂无商品”。
- 兼容性分为 `兼容 / 不兼容 / 未验证 / 待补全`，不能只有绿/黄两态。
- 价格必须区分 `起售价 / 当前配置价 / 核验价 / 历史价`。
- 促销、质保、授权、用户量和好评率等承诺必须可追溯来源与有效期。
- 关键结论先说结果，再给规格和证据；同一概念全站只保留一个名称。

## 审校流程

1. owner 完成语义与事实检查；
2. 产品确认动作和状态；
3. 法务/业务确认价格、促销、授权和服务承诺；
4. 开发通过 overrides 写回并跑测试；
5. AI 在桌面和移动截图上检查截断、换行和语气一致性；
6. 合并后重新提取并归档清单。

