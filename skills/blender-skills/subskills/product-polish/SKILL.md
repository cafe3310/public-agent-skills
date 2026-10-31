---
name: blender-product-polish
description: >
  Import a 3D model (GLB/GLTF) into Blender and apply a sleek, glossy product-shot finish with studio lighting. Trigger when asked to polish a 3D model, make a raw model look shiny, apply product lighting in Blender, or prepare a 3D asset for product shots.
license: MIT
author: https://github.com/kevinbadi/blender-skills
depends_on_skill:
  - blender-skills
depends_on_binary:
  - blender
  - node
---
# Blender Product Polish

Takes a raw 3D model file (e.g. exported from generative 3D tools) and transforms it into a polished, product-shot-ready scene in Blender via the Blender MCP addon.

## Prerequisites

- **Blender** (5.x+) running with the **Blender MCP addon** active on port 9876
- A `.glb` or `.gltf` file to import

## How to Run

```bash
node subskills/product-polish/scripts/blender-product-polish.js --file "/path/to/model.glb"
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file` | Path to the GLB/GLTF file to import | **required** |
| `--port` | Blender MCP port | `9876` |
| `--preset` | Lighting preset: `studio`, `dramatic`, `soft` | `studio` |
| `--roughness` | Surface roughness (0 = mirror, 1 = matte) | `0.02` |
| `--coat` | Clearcoat weight (0-1) | `1.0` |
| `--transmission` | Glass transmission (0-1) | `0.05` |
| `--no-clean` | Keep existing scene objects | `false` |

## What It Does

1. **Clears the scene** (removes default cube, lights, camera)
2. **Imports the GLB/GLTF** model
3. **Strips noisy normal/roughness maps** from raw exports (these cause dotty reflections)
4. **Applies a glass-like material** — ultra-low roughness, full clearcoat, high IOR
5. **Adds 4-point studio lighting** — key, fill, rim, and bounce lights
6. **Switches to EEVEE with ray tracing** for smooth real-time reflections (no pixelation during camera movement)
7. **Frames the viewport** on the imported model

## Lighting Presets

- **studio** (default): Balanced 4-point setup. Key (350W), Fill (250W), Rim (250W), Bounce (100W). Clean product photography look.
- **dramatic**: Strong key + rim, minimal fill. High contrast, moody.
- **soft**: Even lighting from all sides. Minimal shadows, airy feel.

## Notes

- Raw model exports often include noisy normal maps and roughness textures that look pixelated/dotty under strong lighting. This skill disconnects those and uses flat material values instead.
- The skill uses EEVEE (not Cycles) to avoid progressive sampling noise during viewport navigation.
- After running, you can orbit freely in Blender without pixelation.
