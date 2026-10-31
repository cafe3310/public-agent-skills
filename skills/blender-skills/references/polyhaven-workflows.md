# PolyHaven Workflows & Asset Management

The PolyHaven subskills family integrates free, CC0-licensed HDRIs, PBR textures, and 3D prop models directly into Blender scenes via the Blender MCP socket API.

---

## 1. Subskills Capabilities Breakdown

| Subskill | Entry Command | Primary Output | Use Case |
| :--- | :--- | :--- | :--- |
| **`polyhaven-studio-setup`** | `node scripts/polyhaven-studio-setup.js` | HDRI world lighting + ground plane | Fast one-command product photo studio setup |
| **`polyhaven-texture-apply`** | `node scripts/polyhaven-texture-apply.js` | Applied PBR shader network | Assign photorealistic texture to a specific object |
| **`polyhaven-material-swap`** | `node scripts/polyhaven-material-swap.js` | Rendered variant stills | Rapidly compare material options (metals, woods, stones) |
| **`polyhaven-scene-builder`** | `node scripts/polyhaven-scene-builder.js` | Full stage with pedestal & props | Complete showroom / editorial scene composition |
| **`polyhaven-hdri-showcase`** | `node scripts/polyhaven-hdri-showcase.js` | Multi-environment contact sheet | Test and evaluate lighting schemes under varied conditions |

---

## 2. Frequently Used Presets

### Studio HDRIs
- `studio_small_09`: Clean white neutral studio lighting (default)
- `studio_small_08`: Warm, gentle studio ambiance
- `photo_studio_loft_hall`: Loft photography studio with natural window spill
- `studio_small_03`: Soft diffused studio lighting
- `industrial_sunset_02_puresky`: Warm sunset golden hour reflections
- `royal_esplanade`: Rich, architectural interior reflections

### Texture Presets (`polyhaven-material-swap`)
- `metals`: `brushed_metal`, `steel`, `gold`, `copper`
- `woods`: `wood_cabinet_worn_long`, `wood_floor_deck`
- `stones`: `marble_01`, `concrete_wall_003`, `granite`
- `fabrics`: `fabric_pattern_07`, `denim`, `linen`

---

## 3. PBR Texture Shader Configuration

When `polyhaven-texture-apply` is triggered, it downloads the following maps based on selected resolution (`1k`, `2k`, `4k`):
1. **Base Color / Diffuse**: Connected to Principled BSDF `Base Color` (sRGB).
2. **Roughness**: Connected to Principled BSDF `Roughness` (Non-Color).
3. **Normal Map**: Passed through a Normal Map node to `Normal` (Non-Color).
4. **Displacement** (Optional): Connected to Material Output `Displacement`.
5. **Mapping / UV**: Controlled by a single `Value` node linked to Scale for uniform tiling.
