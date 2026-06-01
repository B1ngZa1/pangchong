Place the production product model at:

```text
public/models/pangchong.glb
```

The configurator attempts to load `/models/pangchong.glb`. If the file is missing
or fails to load, `Product3DViewer.vue` renders an interactive code-generated
placeholder model so the page never shows a blank 3D area.

For production, export a single optimized `.glb` and consider Draco or meshopt
compression for faster loading.
