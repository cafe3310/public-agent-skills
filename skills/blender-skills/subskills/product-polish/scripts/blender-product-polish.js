#!/usr/bin/env node

/**
 * Blender Product Polish
 *
 * Imports a GLB/GLTF into Blender and applies a sleek glossy product-shot
 * finish with studio lighting via the Blender MCP addon socket.
 */

const net = require('net');
const path = require('path');

// --- CLI args ---
const args = process.argv.slice(2);
function getArg(name, def) {
  const i = args.indexOf(`--${name}`);
  if (i === -1) return def;
  return args[i + 1] || def;
}
const hasFlag = (name) => args.includes(`--${name}`);

const filePath = getArg('file', null);
const port = parseInt(getArg('port', '9876'), 10);
const preset = getArg('preset', 'studio');
const roughness = parseFloat(getArg('roughness', '0.02'));
const coatWeight = parseFloat(getArg('coat', '1.0'));
const transmission = parseFloat(getArg('transmission', '0.05'));
const noClean = hasFlag('no-clean');

if (!filePath) {
  console.error('Usage: node blender-product-polish.js --file <path-to-glb>');
  console.error('Options: --port 9876 --preset studio|dramatic|soft --roughness 0.02 --coat 1.0 --transmission 0.05 --no-clean');
  process.exit(1);
}

const absPath = path.resolve(filePath);

// --- Blender MCP socket helper ---
function sendToBlender(code) {
  return new Promise((resolve, reject) => {
    const sock = new net.Socket();
    sock.setTimeout(120000);
    sock.connect(port, 'localhost', () => {
      const cmd = JSON.stringify({ type: 'execute_code', params: { code } });
      sock.write(cmd);
    });
    let data = '';
    sock.on('data', (chunk) => {
      data += chunk.toString();
      try {
        const parsed = JSON.parse(data);
        sock.destroy();
        resolve(parsed);
      } catch (_) { /* keep reading */ }
    });
    sock.on('timeout', () => { sock.destroy(); reject(new Error('Blender socket timeout')); });
    sock.on('error', (err) => reject(err));
    sock.on('close', () => {
      if (data) {
        try { resolve(JSON.parse(data)); } catch (_) { reject(new Error(`Bad response: ${data}`)); }
      }
    });
  });
}

async function run() {
  console.log(`Blender Product Polish`);
  console.log(`  File: ${absPath}`);
  console.log(`  Preset: ${preset}`);
  console.log(`  Roughness: ${roughness} | Coat: ${coatWeight} | Transmission: ${transmission}`);
  console.log(`  Port: ${port}`);
  console.log();

  // --- Lighting presets ---
  const presets = {
    studio: { key: 350, fill: 250, rim: 250, bounce: 100 },
    dramatic: { key: 500, fill: 80, rim: 400, bounce: 50 },
    soft: { key: 200, fill: 200, rim: 150, bounce: 150 },
  };
  const lights = presets[preset] || presets.studio;

  // Safely serialize path for Python string literal
  const pyPath = JSON.stringify(absPath);

  // Step 1: Clean scene and import
  console.log('1. Importing model...');
  const importCode = `
import bpy
import math

${noClean ? '# Skipping scene clean' : `
# Clear scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
`}

# Import GLB/GLTF
bpy.ops.import_scene.gltf(filepath=${pyPath})

obj_count = len([o for o in bpy.data.objects if o.type == "MESH"])
print(f"Imported {obj_count} mesh object(s)")
`;
  let res = await sendToBlender(importCode);
  if (res.status === 'error') throw new Error(`Import failed: ${res.message}`);
  console.log(`   ${res.result?.result?.trim() || 'done'}`);

  // Step 2: Apply glossy material
  console.log('2. Applying glossy material...');
  const materialCode = `
import bpy

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Remove normal map / roughness texture links (cause dotty reflections from raw AI exports)
    links_to_remove = []
    for link in links:
        if link.to_socket.name in ["Normal", "Roughness", "Metallic"]:
            links_to_remove.append(link)
    for link in links_to_remove:
        links.remove(link)

    # Remove orphaned nodes
    for n in [n for n in nodes if n.type in ["SEPARATE_COLOR", "NORMAL_MAP"]]:
        nodes.remove(n)
    for n in [n for n in nodes if n.type == "TEX_IMAGE"]:
        if not any(link for out in n.outputs for link in out.links):
            nodes.remove(n)

    # Apply glass-like BSDF settings
    for node in nodes:
        if node.type == "BSDF_PRINCIPLED":
            node.inputs["Roughness"].default_value = ${roughness}
            node.inputs["Specular IOR Level"].default_value = 1.0
            node.inputs["Coat Weight"].default_value = ${coatWeight}
            node.inputs["Coat Roughness"].default_value = 0.0
            node.inputs["Metallic"].default_value = 0.1
            node.inputs["IOR"].default_value = 1.8
            node.inputs["Transmission Weight"].default_value = ${transmission}

print(f"Polished {len(bpy.data.materials)} material(s)")
`;
  res = await sendToBlender(materialCode);
  if (res.status === 'error') throw new Error(`Material failed: ${res.message}`);
  console.log(`   ${res.result?.result?.trim() || 'done'}`);

  // Step 3: Add studio lighting
  console.log(`3. Adding ${preset} lighting...`);
  const lightCode = `
import bpy
import math

# Remove existing lights
for obj in [o for o in bpy.data.objects if o.type == "LIGHT"]:
    bpy.data.objects.remove(obj, do_unlink=True)

# Key light
key_data = bpy.data.lights.new(name="Key", type="AREA")
key_data.energy = ${lights.key}
key_data.size = 3
key_data.color = (1.0, 0.95, 0.9)
key = bpy.data.objects.new("Key", key_data)
bpy.context.collection.objects.link(key)
key.location = (2, -2, 3)
key.rotation_euler = (math.radians(45), 0, math.radians(45))

# Fill light
fill_data = bpy.data.lights.new(name="Fill", type="AREA")
fill_data.energy = ${lights.fill}
fill_data.size = 4
fill_data.color = (0.9, 0.95, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-2.5, -1, 2)
fill.rotation_euler = (math.radians(50), 0, math.radians(-45))

# Rim light
rim_data = bpy.data.lights.new(name="Rim", type="AREA")
rim_data.energy = ${lights.rim}
rim_data.size = 2
rim_data.color = (1.0, 1.0, 1.0)
rim = bpy.data.objects.new("Rim", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (0, 2, 2.5)
rim.rotation_euler = (math.radians(130), 0, 0)

# Bounce light
bounce_data = bpy.data.lights.new(name="Bounce", type="AREA")
bounce_data.energy = ${lights.bounce}
bounce_data.size = 5
bounce_data.color = (1.0, 1.0, 1.0)
bounce = bpy.data.objects.new("Bounce", bounce_data)
bpy.context.collection.objects.link(bounce)
bounce.location = (0, 0, -1)
bounce.rotation_euler = (math.radians(180), 0, 0)

# Subtle world background
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Strength"].default_value = 0.3
    bg.inputs["Color"].default_value = (0.15, 0.15, 0.18, 1.0)

print("4-point lighting added")
`;
  res = await sendToBlender(lightCode);
  if (res.status === 'error') throw new Error(`Lighting failed: ${res.message}`);
  console.log(`   ${res.result?.result?.trim() || 'done'}`);

  // Step 4: Set render engine + frame viewport
  console.log('4. Setting up viewport...');
  const viewportCode = `
import bpy

# EEVEE with ray tracing for smooth real-time reflections
bpy.context.scene.render.engine = "BLENDER_EEVEE"
try:
    bpy.context.scene.eevee.use_raytracing = True
except:
    pass

# Frame model in viewport
bpy.ops.object.select_all(action="SELECT")
for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        for space in area.spaces:
            if space.type == "VIEW_3D":
                space.shading.type = "RENDERED"
                break
        for region in area.regions:
            if region.type == "WINDOW":
                override = bpy.context.copy()
                override["area"] = area
                override["region"] = region
                with bpy.context.temp_override(**override):
                    bpy.ops.view3d.view_selected()
                break
        break

print("EEVEE ray tracing + rendered viewport ready")
`;
  res = await sendToBlender(viewportCode);
  if (res.status === 'error') throw new Error(`Viewport failed: ${res.message}`);
  console.log(`   ${res.result?.result?.trim() || 'done'}`);

  console.log();
  console.log('Done! Your model is polished and ready in Blender.');
}

run().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
