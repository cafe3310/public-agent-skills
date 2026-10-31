# Blender Environment & Service Setup

`blender-skills` relies on a live connection between the Agent / CLI scripts and Blender via the Blender MCP socket server, as well as external generative services.

---

## 1. Prerequisites Checklist

| Component | Required For | Recommended Version / Configuration |
| :--- | :--- | :--- |
| **Blender** | All 3D operations and rendering | 4.x or 5.x (Blender 5.x recommended) |
| **blender-mcp addon** | Agent-to-Blender communication | Active TCP socket server listening on `localhost:9876` |
| **Node.js** | PolyHaven & Three.js helper scripts | v18+ LTS |
| **ffmpeg** | Video encoding with transparent alpha | System binary in PATH |

---

## 2. Blender MCP Addon Setup

1. Install the `blender-mcp` addon in Blender:
   - Source: [github.com/ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)
   - In Blender: `Edit > Preferences > Add-ons > Install...`
   - Enable the addon checkbox.
2. In the Blender 3D Viewport:
   - Press `N` to open the sidebar.
   - Navigate to the `BlenderMCP` panel.
   - Click **Connect** (default port `9876`).
3. PolyHaven Integration:
   - In the addon sidebar, ensure the **PolyHaven** feature is toggled on so asset downloads and shader graphs are automatically handled.

---

## 3. Communication Protocol (Socket RPC)

Scripts located under `subskills/*/scripts/` communicate with Blender by opening a raw TCP socket to `localhost:9876` and sending JSON payloads:

```json
{
  "type": "<command_name>",
  "params": { ... }
}
```

Common RPC types:
- `download_polyhaven_asset`: `{ asset_id, type: "hdris"|"textures"|"models", resolution: "1k"|"2k"|"4k" }`
- `apply_polyhaven_hdri`: `{ asset_id, strength, rotation }`
- `apply_polyhaven_texture`: `{ object_name, asset_id, resolution, scale }`
- `import_model`: `{ file_path }`
- `export_glb`: `{ output_path, export_materials: true }`
- `render_still`: `{ output_path, resolution_x, resolution_y, transparent }`

---

## 4. Video Rendering Conventions

Camera animation subskills render animation sequences and compile them using `ffmpeg`:
- **Default Resolution**: 1920x1080 @ 24fps.
- **Default Output Directory**: `~/Desktop/Blender Videos/`.
- **Alpha Transparency**:
  - `mov` (Default): Apple ProRes 4444 with 32-bit depth (RGB + Alpha).
  - `webm`: VP9 codec with alpha channel for web embedding.
- **Background**: Transparent film mode enabled in Blender (`bpy.context.scene.render.film_transparent = True`).

