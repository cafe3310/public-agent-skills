#!/usr/bin/env node

const net = require('net');
const args = process.argv.slice(2);
const getArg = (n, d) => { const i = args.indexOf(`--${n}`); return i === -1 ? d : args[i + 1] || d; };
const hasFlag = (n) => args.includes(`--${n}`);

const presetName = getArg('preset', null);
const resolution = getArg('resolution', '2k');
const port = parseInt(getArg('port', '9876'), 10);

const presets = {
  showroom:  { hdri: 'studio_small_09', ground: 'marble_01', pedestal: true },
  outdoor:   { hdri: 'kloppenheim_06_puresky', ground: 'concrete_wall_003', pedestal: false },
  minimal:   { hdri: 'studio_small_03', ground: null, pedestal: false },
  dramatic:  { hdri: 'industrial_sunset_02_puresky', ground: 'concrete_floor_02', pedestal: true },
};

const preset = presetName ? presets[presetName] : null;
const hdri = getArg('hdri', preset?.hdri || 'studio_small_09');
const ground = getArg('ground', preset?.ground || null);
const pedestal = hasFlag('pedestal') || preset?.pedestal || false;
const pedestalTexture = getArg('pedestal-texture', ground);
const props = getArg('props', null);

function send(type, params) {
  return new Promise((resolve, reject) => {
    const sock = new net.Socket();
    sock.setTimeout(120000);
    sock.connect(port, 'localhost', () => {
      sock.write(JSON.stringify({ type, params }));
    });
    let data = '';
    sock.on('data', c => {
      data += c.toString();
      try { const p = JSON.parse(data); sock.destroy(); resolve(p); } catch (_) {}
    });
    sock.on('timeout', () => { sock.destroy(); reject(new Error('timeout')); });
    sock.on('error', reject);
    sock.on('close', () => {
      if (data) try { resolve(JSON.parse(data)); } catch (_) { reject(new Error(data)); }
    });
  });
}

async function run() {
  console.log('PolyHaven Scene Builder');
  if (presetName) console.log(`  Preset: ${presetName}`);
  console.log(`  HDRI: ${hdri}`);
  if (ground) console.log(`  Ground: ${ground}`);
  if (pedestal) console.log(`  Pedestal: yes`);
  if (props) console.log(`  Props: ${props}`);
  console.log();

  // Step 1: HDRI
  console.log('1. Setting up HDRI environment...');
  let res = await send('download_polyhaven_asset', {
    asset_id: hdri, asset_type: 'hdris', resolution, file_format: 'hdr'
  });
  if (res.result?.error) console.log(`   Warning: ${res.result.error}`);
  else console.log(`   Applied: ${hdri}`);

  // Configure viewport
  await send('execute_code', { code: `
import bpy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'RENDERED'
                space.shading.use_scene_world = True
                break
print("Viewport configured")
` });

  // Step 2: Ground plane with texture
  if (ground) {
    console.log('2. Creating textured ground...');
    res = await send('download_polyhaven_asset', {
      asset_id: ground, asset_type: 'textures', resolution, file_format: 'jpg'
    });
    const groundMat = res.result?.material || ground;
    if (res.result?.error) {
      console.log(`   Warning: ${res.result.error}`);
    } else {
      await send('execute_code', { code: `
import bpy
bpy.ops.mesh.primitive_plane_add(size=15, location=(0, 0, -0.01))
plane = bpy.context.active_object
plane.name = "Scene_Ground"
mat = bpy.data.materials.get("${groundMat}")
if mat:
    plane.data.materials.append(mat)
    # Scale UVs for better tiling
    for node in mat.node_tree.nodes:
        if node.type == 'MAPPING':
            node.inputs['Scale'].default_value = (3, 3, 3)
print(f"Ground created with ${groundMat}")
` });
      console.log(`   Ground plane with ${ground}`);
    }
  }

  // Step 3: Pedestal
  if (pedestal) {
    console.log(`${ground ? '3' : '2'}. Adding pedestal...`);
    // Get product bounding box to size pedestal
    res = await send('execute_code', { code: `
import bpy
import math

# Find the product mesh (not ground/pedestal)
product = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'Ground' not in obj.name and 'Pedestal' not in obj.name:
        product = obj
        break

if product:
    dims = product.dimensions
    radius = max(dims.x, dims.y) * 0.7
    # Create pedestal cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=0.08,
        location=(product.location.x, product.location.y, product.location.z - dims.z / 2 - 0.04)
    )
    ped = bpy.context.active_object
    ped.name = "Pedestal"

    # Smooth shading
    bpy.ops.object.shade_smooth()

    # Apply texture if available
    mat = bpy.data.materials.get("${pedestalTexture || ground}")
    if mat:
        ped.data.materials.append(mat)
    else:
        # Create a simple dark glossy material
        mat = bpy.data.materials.new("Pedestal_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
        bsdf.inputs["Roughness"].default_value = 0.1
        bsdf.inputs["Metallic"].default_value = 0.3
        ped.data.materials.append(mat)

    print(f"Pedestal added: radius={radius:.2f}")
else:
    print("No product mesh found")
` });
    console.log(`   ${res.result?.result?.trim() || 'done'}`);
  }

  // Step 4: Props
  if (props) {
    const propList = props.split(',').map(p => p.trim());
    const step = (ground ? 3 : 2) + (pedestal ? 1 : 0) + 1;
    console.log(`${step}. Adding props...`);
    for (const prop of propList) {
      console.log(`   Downloading ${prop}...`);
      res = await send('download_polyhaven_asset', {
        asset_id: prop, asset_type: 'models', resolution, file_format: 'gltf'
      });
      if (res.result?.error) {
        console.log(`   Warning: ${prop} failed: ${res.result.error}`);
      } else {
        console.log(`   Added: ${prop} (${(res.result?.imported_objects || []).join(', ')})`);
      }
    }
  }

  console.log();
  console.log('Scene built!');
}

run().catch(err => { console.error(`Error: ${err.message}`); process.exit(1); });
