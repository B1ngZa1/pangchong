# 价格核验

填写 `price-verification.csv` 时，只有同时具备参考价、来源名称、来源 URL、ISO 8601 核价时间并将 `status` 改为 `verified` 的行会被导入。

```powershell
cd ecommerce/backend
python -m app.cli.import_price_verification ../../docs/data/price-verification.csv
```

导入器只写价格历史和来源元数据，不会擅自修改商城售价；重复的来源 URL 与核价时间会被跳过。
