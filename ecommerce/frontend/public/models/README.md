Local development may place licensed product models in this directory, for example:

```text
public/models/pangchong-diy.glb
```

The DIY storefront passes its model path into `Product3DViewer.vue`. If the file
is missing, omitted, or fails to load, the viewer renders an interactive
code-generated placeholder model so the page never shows a blank 3D area.

Production models should be uploaded through the admin asset API to the
`catalog-models` Supabase bucket. A DIY model must expose the named nodes
`case`, `motherboard`, `cpu`, `gpu`, `ram`, `ssd`, `cooler`, and `psu`.
See `docs/3d-asset-pipeline.md`; do not commit vendor CAD without a verified
redistribution license.
