#!/usr/bin/env node

const net = require('net');
const fs = require('fs');
const path = require('path');
const args = process.argv.slice(2);
const getArg = (n, d) => { const i = args.indexOf(`--${n}`); return i === -1 ? d : args[i + 1] || d; };

const objectName = getArg('object', null);
const output = getArg('output', null);
const presetName = getArg('preset', null);
const resolution = getArg('resolution', '2k');
const renderWidth = parseInt(getArg('render-width', '1920'), 10);
const renderHeight = parseInt(getArg('render-height', '1080'), 10);
const samples = parseInt(getArg('samples', '64'), 10);
const port = parseInt(getArg('port', '9876'), 10);

const texturePresets = {
  metals:  ['brushed_metal', 'rusty_metal', 'painted_metal_02', 'corrugated_iron'],
  woods:   ['wood_cabinet_worn_long', 'plywood', 'bark_brown_02', 'wood_floor'],
  stones:  ['marble_01', 'concrete_wall_003', 'rock_face', 'gravel_floor_02'],
  fabrics: ['fabric_pattern_07', 'leather_red_02', 'denim_fabric', 'burlap_01'],
};

const textureList = getArg('textures', null)
  ? getArg('textures').split(',').map(t => t.trim())
  : (presetName ? texturePresets[presetName] : null);

if (!objectName || !output || !textureList) {
  console.error('Usage: node polyhaven-material-swap.js --object <name> --textures "id1,id2" --output <dir>');
  console.error('       node polyhaven-material-swap.js --object <name> --preset metals --output <dir>');
  process.exit(1);
}

function send(type, params) {
  return new Promise((resolve, reject) => {
    const sock = new net.Socket();
    sock.setTimeout(180000);
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
  const absOutput = path.resolve(output);
  fs.mkdirSync(absOutput, { recursive: true });

  console.log('PolyHaven Material Swap');
  console.log(`  Object: ${objectName}`);
  console.log(`  Textures: ${textureList.join(', ')}`);
  console.log(`  Output: ${absOutput}`);
  console.log();

  // Setup render
  await send('execute_code', { code: `
import bpy
bpy.context.scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices: d.use = True
except: pass
bpy.context.scene.cycles.samples = ${samples}
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.resolution_x = ${renderWidth}
bpy.context.scene.render.resolution_y = ${renderHeight}
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Setup camera if needed
if not any(o.type == 'CAMERA' for o in bpy.data.objects):
    bpy.ops.object.camera_add(location=(2.5, -2.5, 1.5))
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam
    import mathutils
    direction = mathutils.Vector((0,0,0)) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

print("Render setup done")
` });

  // Store original material
  await send('execute_code', { code: `
import bpy
obj = bpy.data.objects.get("${objectName}")
if obj and obj.data.materials:
    bpy.context.scene["_original_mat"] = obj.data.materials[0].name
    print(f"Original material: {obj.data.materials[0].name}")
else:
    print("No original material found")
` });

  for (let i = 0; i < textureList.length; i++) {
    const texId = textureList[i];
    console.log(`[${i + 1}/${textureList.length}] ${texId}...`);

    // Download texture
    let res = await send('download_polyhaven_asset', {
      asset_id: texId, asset_type: 'textures', resolution, file_format: 'jpg'
    });
    if (res.result?.error) {
      console.log(`   Skipped: ${res.result.error}`);
      continue;
    }
    const matName = res.result?.material || texId;

    // Apply to object
    await send('execute_code', { code: `
import bpy
obj = bpy.data.objects.get("${objectName}")
mat = bpy.data.materials.get("${matName}")
if obj and mat:
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    print(f"Applied {mat.name}")
` });

    // Render
    const renderPath = path.join(absOutput, `${texId}.png`).replace(/\\/g, '\\\\');
    res = await send('execute_code', { code: `
import bpy
bpy.context.scene.render.filepath = "${renderPath}"
bpy.ops.render.render(write_still=True)
print("Rendered")
` });
    console.log(`   Saved: ${texId}.png`);
  }

  // Restore original material
  await send('execute_code', { code: `
import bpy
obj = bpy.data.objects.get("${objectName}")
orig_name = bpy.context.scene.get("_original_mat")
if obj and orig_name:
    mat = bpy.data.materials.get(orig_name)
    if mat and obj.data.materials:
        obj.data.materials[0] = mat
        print(f"Restored: {orig_name}")
` });

  console.log();
  console.log(`Done! ${textureList.length} variants rendered to ${absOutput}`);
}

run().catch(err => { console.error(`Error: ${err.message}`); process.exit(1); });
