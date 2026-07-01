# DIY 3D 资产流水线

答辩主模型建议从[联力 O11 Dynamic EVO 官方页面](https://lian-li.com/product/o11-dynamic-evo/)取得 CAD。下载和再分发前必须核对厂商许可；仓库不直接提交来源或许可不明确的 CAD。

## Blender 导出约定

- 单位为米，应用全部旋转与缩放，原点设在机箱几何中心。
- 必须存在八个顶层命名节点：`case`、`motherboard`、`cpu`、`gpu`、`ram`、`ssd`、`cooler`、`psu`。
- 删除螺纹、不可见内部结构和重复面；贴图使用 WebP，最长边不超过 2048。
- 导出单个 GLB，目标小于 5 MB；禁止把品牌 CAD 宣称为热流体或结构仿真模型。
- 上传到 `catalog-models` 后，将公开 URL、缩放、位置、旋转和许可写入商品字段。

查看器会验证节点合同。缺失节点会在页面显示警告，GLB 损坏或网络失败时回退到程序生成模型。
