#!/usr/bin/env node

const net = require('net');
const args = process.argv.slice(2);
const getArg = (n, d) => { const i = args.indexOf(`--${n}`); return i === -1 ? d : args[i + 1] || d; };
const hasFlag = (n) => args.includes(`--${n}`);

const objectName = getArg('object', null);
const texture = getArg('texture', null);
const resolution = getArg('resolution', '2k');
const scale = parseFloat(getArg('scale', '1.0'));
const port = parseInt(getArg('port', '9876'), 10);
const search = getArg('search', null);

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
  if (search) {
    console.log(`Searching PolyHaven textures for "${search}"...`);
    const res = await send('search_polyhaven_assets', { asset_type: 'textures', categories: search });
    if (res.result?.assets) {
      const assets = res.result.assets;
      console.log(`Found ${res.result.total_count} results (showing ${res.result.returned_count}):\n`);
      for (const [id, info] of Object.entries(assets)) {
        console.log(`  ${id.padEnd(35)} ${(info.categories || []).join(', ')}`);
      }
    } else {
      console.log('No results or error:', res.result?.error || res.message);
    }
    return;
  }

  if (!objectName || !texture) {
    console.error('Usage: node polyhaven-texture-apply.js --object <name> --texture <asset_id>');
    console.error('       node polyhaven-texture-apply.js --search <keyword>');
    process.exit(1);
  }

  console.log('PolyHaven Texture Apply');
  console.log(`  Object: ${objectName}`);
  console.log(`  Texture: ${texture} (${resolution})`);
  console.log();

  // Step 1: Download texture
  console.log('1. Downloading PBR texture set...');
  let res = await send('download_polyhaven_asset', {
    asset_id: texture,
    asset_type: 'textures',
    resolution: resolution,
    file_format: 'jpg'
  });
  if (res.status === 'error' || res.result?.error) {
    throw new Error(`Texture download failed: ${res.result?.error || res.message}`);
  }
  const matName = res.result?.material || texture;
  const maps = res.result?.maps || [];
  console.log(`   Material: ${matName}`);
  console.log(`   Maps: ${maps.join(', ')}`);

  // Step 2: Apply to object
  console.log('2. Applying to object...');
  res = await send('set_texture', {
    object_name: objectName,
    texture_id: matName
  });
  if (res.status === 'error' || res.result?.error) {
    // Fallback: assign manually
    res = await send('execute_code', { code: `
import bpy
obj = bpy.data.objects.get("${objectName}")
mat = bpy.data.materials.get("${matName}")
if obj and mat:
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    # Adjust UV scale
    for node in mat.node_tree.nodes:
        if node.type == 'MAPPING':
            node.inputs['Scale'].default_value = (${scale}, ${scale}, ${scale})
    print(f"Applied {mat.name} to {obj.name}")
else:
    print(f"Error: obj={'found' if obj else 'missing'}, mat={'found' if mat else 'missing'}")
` });
  }
  console.log(`   ${res.result?.result?.trim() || 'done'}`);

  console.log();
  console.log('Texture applied!');
}

run().catch(err => { console.error(`Error: ${err.message}`); process.exit(1); });
