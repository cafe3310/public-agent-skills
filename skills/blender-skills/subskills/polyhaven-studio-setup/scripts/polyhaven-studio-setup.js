#!/usr/bin/env node

const net = require('net');
const args = process.argv.slice(2);
const getArg = (n, d) => { const i = args.indexOf(`--${n}`); return i === -1 ? d : args[i + 1] || d; };
const hasFlag = (n) => args.includes(`--${n}`);

const hdri = getArg('hdri', 'studio_small_09');
const ground = getArg('ground', null);
const resolution = getArg('resolution', '2k');
const strength = parseFloat(getArg('strength', '1.0'));
const rotation = parseFloat(getArg('rotation', '0'));
const groundSize = parseFloat(getArg('ground-size', '10'));
const port = parseInt(getArg('port', '9876'), 10);

if (hasFlag('list-hdris')) {
  console.log(`Popular Studio HDRIs:
  studio_small_09        Clean white studio
  studio_small_08        Warm studio
  photo_studio_loft_hall Loft photography studio
  studio_small_03        Soft studio lighting
  industrial_sunset_02_puresky  Golden hour
  kloppenheim_06_puresky Outdoor overcast soft
  royal_esplanade        Grand interior
  venice_sunset          Warm sunset
  snowy_park_01          Cool daylight
  meadow_2               Bright outdoor`);
  process.exit(0);
}

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
  console.log('PolyHaven Studio Setup');
  console.log(`  HDRI: ${hdri} (${resolution})`);
  if (ground) console.log(`  Ground: ${ground}`);
  console.log();

  // Step 1: Download and apply HDRI
  console.log('1. Downloading HDRI environment...');
  let res = await send('download_polyhaven_asset', {
    asset_id: hdri,
    asset_type: 'hdris',
    resolution: resolution,
    file_format: 'hdr'
  });
  if (res.status === 'error' || res.result?.error) {
    throw new Error(`HDRI download failed: ${res.message || res.result?.error}`);
  }
  console.log(`   Applied: ${hdri}`);

  // Step 2: Adjust HDRI strength and rotation
  console.log('2. Configuring environment...');
  res = await send('execute_code', { code: `
import bpy
import math

world = bpy.context.scene.world
if world and world.use_nodes:
    for node in world.node_tree.nodes:
        if node.type == 'BACKGROUND':
            node.inputs['Strength'].default_value = ${strength}
        if node.type == 'MAPPING':
            node.inputs['Rotation'].default_value[2] = math.radians(${rotation})

# Make sure we're in rendered mode to see the HDRI
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'RENDERED'
                space.shading.use_scene_world = True
                break

print("HDRI configured: strength=${strength}, rotation=${rotation}deg")
` });
  console.log(`   ${res.result?.result?.trim() || 'done'}`);

  // Step 3: Add ground plane with texture if requested
  if (ground) {
    console.log('3. Downloading ground texture...');
    res = await send('download_polyhaven_asset', {
      asset_id: ground,
      asset_type: 'textures',
      resolution: resolution,
      file_format: 'jpg'
    });
    if (res.status === 'error' || res.result?.error) {
      console.log(`   Warning: Ground texture failed: ${res.result?.error || res.message}`);
    } else {
      const matName = res.result?.material || ground;
      console.log(`   Downloaded: ${ground}`);

      console.log('4. Creating ground plane...');
      res = await send('execute_code', { code: `
import bpy

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=${groundSize}, location=(0, 0, -0.01))
plane = bpy.context.active_object
plane.name = "Studio_Ground"

# Assign the PolyHaven material
mat = bpy.data.materials.get("${matName}")
if mat:
    plane.data.materials.append(mat)
    print(f"Ground plane created with {mat.name}")
else:
    print("Ground plane created (no material found)")
` });
      console.log(`   ${res.result?.result?.trim() || 'done'}`);
    }
  }

  console.log();
  console.log('Studio setup complete!');
}

run().catch(err => { console.error(`Error: ${err.message}`); process.exit(1); });
