#!/usr/bin/env node

/**
 * Blender Three.js Export
 *
 * Exports the current Blender scene as GLB and generates a standalone
 * Three.js HTML viewer with orbit controls and studio lighting.
 */

const net = require('net');
const fs = require('fs');
const path = require('path');

// --- CLI args ---
const args = process.argv.slice(2);
function getArg(name, def) {
  const i = args.indexOf(`--${name}`);
  if (i === -1) return def;
  return args[i + 1] || def;
}
const hasFlag = (name) => args.includes(`--${name}`);

const outputDir = getArg('output', null);
const modelName = getArg('name', 'model');
const port = parseInt(getArg('port', '9876'), 10);
const noRotate = hasFlag('no-rotate');
const bgColor = getArg('bg', '#111111');
const embed = hasFlag('embed');

if (!outputDir) {
  console.error('Usage: node blender-threejs-export.js --output <directory>');
  console.error('Options: --name model --port 9876 --no-rotate --bg "#111111" --embed');
  process.exit(1);
}

const absOutput = path.resolve(outputDir);
const glbPath = path.join(absOutput, `${modelName}.glb`);
const htmlPath = path.join(absOutput, `${modelName}.html`);

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

function generateHTML(glbFile) {
  const glbSrc = embed
    ? `data:model/gltf-binary;base64,${fs.readFileSync(glbPath).toString('base64')}`
    : `./${glbFile}`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${modelName}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: ${bgColor}; }
  canvas { display: block; width: 100%; height: 100%; }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"
  }
}
</script>
</head>
<body>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

// --- Scene ---
const scene = new THREE.Scene();
scene.background = new THREE.Color('${bgColor}');

// --- Camera ---
const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.01, 100);
camera.position.set(2.5, 1.8, 2.5);

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

// --- Controls ---
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.autoRotate = ${!noRotate};
controls.autoRotateSpeed = 1.5;
controls.minDistance = 0.5;
controls.maxDistance = 20;

// --- Lighting (studio setup) ---
const keyLight = new THREE.DirectionalLight(0xfff5e6, 3);
keyLight.position.set(3, 4, 2);
keyLight.castShadow = true;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xe6f0ff, 1.5);
fillLight.position.set(-3, 2, -1);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0xffffff, 2);
rimLight.position.set(0, 3, -3);
scene.add(rimLight);

const ambient = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambient);

// Subtle env for reflections
const pmremGenerator = new THREE.PMREMGenerator(renderer);
const envScene = new THREE.Scene();
envScene.background = new THREE.Color(0x222222);
const envMap = pmremGenerator.fromScene(envScene, 0.04).texture;
scene.environment = envMap;

// --- Load model ---
const loader = new GLTFLoader();
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/');
loader.setDRACOLoader(dracoLoader);

loader.load('${glbSrc}', (gltf) => {
  const model = gltf.scene;

  // Apply glossy material overrides
  model.traverse((child) => {
    if (child.isMesh) {
      if (child.material) {
        child.material.roughness = ${embed ? 0.05 : 0.05};
        child.material.clearcoat = 1.0;
        child.material.clearcoatRoughness = 0.0;
        child.material.envMapIntensity = 1.5;
        child.material.needsUpdate = true;
      }
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });

  scene.add(model);

  // Center and frame
  const box = new THREE.Box3().setFromObject(model);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  model.position.sub(center);
  controls.target.set(0, 0, 0);
  camera.position.set(size * 1.2, size * 0.8, size * 1.2);
  controls.update();
}, undefined, (err) => console.error('Load error:', err));

// --- Resize ---
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// --- Animate ---
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>`;
}

async function run() {
  console.log('Blender Three.js Export');
  console.log(`  Output: ${absOutput}`);
  console.log(`  Name: ${modelName}`);
  console.log(`  Embed: ${embed}`);
  console.log();

  // Create output dir
  fs.mkdirSync(absOutput, { recursive: true });

  // Step 1: Export GLB from Blender
  console.log('1. Exporting GLB from Blender...');
  const pyPath = JSON.stringify(glbPath);
  const exportCode = `
import bpy

# Select all mesh objects for export
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.data.objects:
    if obj.type == "MESH":
        obj.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=${pyPath},
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_image_format="AUTO",
    export_materials="EXPORT",
    export_texcoords=True,
    export_normals=True,
)

import os
size_mb = os.path.getsize(${pyPath}) / (1024 * 1024)
print(f"Exported GLB: {size_mb:.1f} MB")
`;
  let res = await sendToBlender(exportCode);
  if (res.status === 'error') throw new Error(`Export failed: ${res.message}`);
  console.log(`   ${res.result?.result?.trim() || 'done'}`);

  // Step 2: Generate HTML viewer
  console.log('2. Generating Three.js viewer...');
  const html = generateHTML(`${modelName}.glb`);
  fs.writeFileSync(htmlPath, html, 'utf-8');
  console.log(`   Written: ${htmlPath}`);

  console.log();
  console.log('Done!');
  console.log(`  GLB: ${glbPath}`);
  console.log(`  Viewer: ${htmlPath}`);
  console.log();
  console.log(`Open in browser: open "${htmlPath}"`);
}

run().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
