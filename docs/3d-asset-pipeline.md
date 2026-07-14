# DIY 3D 资产流水线

答辩路径固定使用目录商品 `lianli-o11d-evo-rgb` 作为首个机箱模型挂载位。可以从[联力 O11 Dynamic EVO 产品页](https://lian-li.com/product/o11-dynamic-evo/)开始联系厂商或核对素材来源，但产品页本身不等于再分发许可。只有明确允许网页公开分发的自制、购买或授权资产才可上传。

## `diy-case-v1` 节点合同

GLB 2.0 必须包含以下八个命名节点；节点可以是 Mesh，也可以是包含多个 Mesh 的 Group，但每个节点的子树中至少要有一个可渲染 Mesh：

```text
case
motherboard
cpu
gpu
ram
ssd
cooler
psu
```

查看器会把命名 Group 的所有后代 Mesh 作为同一个配件处理。名称不区分大小写，并兼容 `chassis`、`mainboard`、`memory`、`storage`、`aio`、`power` 等导出别名；交付资产仍建议使用上面的标准名称。

## Blender 导出约定

- 单位优先使用米；应用旋转与缩放，原点设在机箱几何中心。
- 将八个配件分别放入对应的命名 Group，避免只给内部单个 Mesh 命名。
- 删除螺纹、不可见内部结构和重复面；贴图使用 WebP，最长边不超过 2048。
- 导出单个 GLB 2.0，建议小于 6 MB，硬限制 20 MB。
- 禁止把品牌 CAD 宣称为热流体或结构仿真模型。

## 管理后台挂载

1. 执行 `alembic upgrade head`，确保商品表包含 `asset_source_url`。
2. 在后台商品页搜索并编辑 `lianli-o11d-evo-rgb`。
3. 确认分类为“机箱”，先填写“素材许可”和“素材来源 URL”。
4. 选择 GLB。后端会校验 GLB 2.0 结构、声明长度和八节点合同；本地模式写入 `backend/uploads/diy/<uuid>.glb`，显式 Supabase 模式写入 `catalog-models/diy/<uuid>.glb`。
5. 页面显示“节点合同通过”后保存商品。上传使用唯一对象路径，避免覆盖同一路径造成 CDN 旧缓存。
6. 打开 DIY，选择该机箱。查看器右上角应显示 `Catalog GLB` 和许可；清空 URL、网络失败或文件损坏时会明确回退到 `Generated fallback`。

直接填写外部 GLB URL 也必须同时保存许可和来源，但不会获得上传接口的节点校验。答辩版本优先走后台上传。

## Storage 安全边界

- 本地答辩默认 `ASSET_STORAGE_BACKEND=local`，不会请求 Supabase。
- 显式 Supabase 模式下，Bucket 公开只代表任何持有 URL 的人可读取；上传仍只经 FastAPI 管理员接口。
- Secret/`service_role` Key 只放在后端环境变量，禁止使用 `VITE_` 前缀。
- 每个文件使用新路径且 `x-upsert: false`，因此不需要给浏览器开放 Storage 的 INSERT、SELECT 或 UPDATE 策略。
- `catalog-models` 限制为 20 MB；应用请求上限为 22 MB，用于容纳 multipart 边界。
