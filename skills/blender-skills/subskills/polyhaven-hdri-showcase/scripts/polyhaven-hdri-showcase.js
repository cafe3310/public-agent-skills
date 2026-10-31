#!/usr/bin/env node

const net = require('net');
const fs = require('fs');
const path = require('path');
const args = process.argv.slice(2);
const getArg = (n, d) => { const i = args.indexOf(`--${n}`); return i === -1 ? d : args[i + 1] || d; };

const output = getArg('output', null);
const presetName = getArg('preset', null);
const resolution = getArg('resolution', '1k');
const renderWidth = parseInt(getArg('render-width', '1920'), 10);
const renderHeight = parseInt(getArg('render-height', '1080'), 10);
const samples = parseInt(getArg('samples', '64'), 10);
const port = parseInt(getArg('port', '9876'), 10);

const hdriPresets = {
  studios:  ['studio_small_09', 'studio_small_08', 'studio_small_03', 'photo_studio_loft_hall'],
  outdoor:  ['kloppenheim_06_puresky', 'meadow_2', 'snowy_park_01', 'venice_sunset'],
  dramatic: ['industrial_sunset_02_puresky', 'royal_esplanade', 'abandoned_tiled_room', 'moonless_golf'],
};
hdriPresets.all = [...hdriPresets.studios, ...hdriPresets.outdoor, ...hdriPresets.dramatic];

const defaultHdris = ['studio_small_09', 'studio_small_08', 'royal_esplanade', 'kloppenheim_06_puresky', 'industrial_sunset_02_puresky', 'venice_sunset'];
const hdriList = getArg('hdris', null)
  ? getArg('hdris').split(',').map(h => h.trim())
  : (presetName ? hdriPresets[presetName] || defaultHdris : defaultHdris);

if (!output) {
  console.error('Usage: node polyhaven-hdri-showcase.js --output <directory>');
  console.error('Options: --hdris "id1,id2" --preset studios|outdoor|dramatic|all --resolution 1k');
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

  console.log('PolyHaven HDRI Showcase');
  console.log(`  HDRIs: ${hdriList.join(', ')}`);
  console.log(`  Output: ${absOutput}`);
  console.log(`  Render: ${renderWidth}x${renderHeight} @ ${samples} samples`);
  console.log();

  // Setup render settings
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

# Setup camera if none exists
if not any(o.type == 'CAMERA' for o in bpy.data.objects):
    bpy.ops.object.camera_add(location=(2.5, -2.5, 1.5))
    cam = bpy.context.active_object
    cam.name = 'Showcase_Camera'
    bpy.context.scene.camera = cam
    # Point at origin
    import mathutils
    direction = mathutils.Vector((0,0,0)) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Make sure world exists
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")

print("Render setup done")
` });

  for (let i = 0; i < hdriList.length; i++) {
    const hdriId = hdriList[i];
    console.log(`[${i + 1}/${hdriList.length}] ${hdriId}...`);

    // Download and apply HDRI
    let res = await send('download_polyhaven_asset', {
      asset_id: hdriId, asset_type: 'hdris', resolution, file_format: 'hdr'
    });
    if (res.result?.error) {
      console.log(`   Skipped: ${res.result.error}`);
      continue;
    }

    // Render
    const renderPath = path.join(absOutput, `${hdriId}.png`).replace(/\\/g, '\\\\');
    res = await send('execute_code', { code: `
import bpy
bpy.context.scene.render.filepath = "${renderPath}"
bpy.ops.render.render(write_still=True)
print("Rendered: ${hdriId}")
` });
    console.log(`   Saved: ${hdriId}.png`);
  }

  console.log();
  console.log(`Done! ${hdriList.length} renders saved to ${absOutput}`);
}

run().catch(err => { console.error(`Error: ${err.message}`); process.exit(1); });
