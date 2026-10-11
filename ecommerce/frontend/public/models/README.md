本地开发可将已确认可公开分发的商品模型放入此目录，例如：

```text
public/models/pangchong-diy.glb
```

DIY 页面会将模型路径传给 `Product3DViewer.vue`。文件缺失、未配置或加载失败时，
查看器会显示可交互的示意模型，页面不会留下空白的 3D 区域。

模型应通过后台商品表单上传。本地答辩模式会储存在 `backend/uploads`；显式 Supabase
部署会储存在 `catalog-models` Bucket。表单会记录再分发许可与来源 URL，并请求
`diy-case-v1` 校验报告。DIY 模型必须包含 `case`、`motherboard`、`cpu`、`gpu`、
`ram`、`ssd`、`cooler`、`psu` 八个命名节点。

详见 `docs/3d/asset-pipeline.md` 与 `docs/3d/asset-sourcing.md`。未确认再分发许可时，
不得提交厂商 CAD 或从商品页提取的模型。
