## 文档生成说明

本文档归纳基于 Model Context Protocol (MCP) 驱动 Blender 5.2.2 LTS 的整体能力模型、核心工具分类、Python API 执行规范及排错路径，形成标准化的 3D 自动化控制指南。

参考文档包括：
- [coordinates-and-scene-building.md](coordinates-and-scene-building.md)

---

## 一、 系统架构与通信机制

Blender MCP 为大型语言模型（Agent）与 3D 创作套件（Blender）之间架设了实时的双向控制通道：

```
┌─────────────────────────────────┐
│     Coding Agent (Client)       │
│   (Antigravity / agy-cli)       │
└────────────────┬────────────────┘
                 │ MCP JSON-RPC
                 ▼
┌─────────────────────────────────┐
│     Blender MCP Server Plugin   │
│  (mcp_to_blender_server.py)     │
└────────────────┬────────────────┘
                 │ 内置 Python (bpy)
                 ▼
┌─────────────────────────────────┐
│    Blender 5.2.2 LTS 运行实例    │
│  (3D Viewport / EEVEE / Cycles) │
└─────────────────────────────────┘
```

### 核心特性

1. **交互式图形界面直连**：与盲跑后台 headless 进程不同，MCP 服务直接挂载在用户当前打开的 Blender GUI 实例中。Agent 的每次几何修改、材质更新或视角切换，都会**实时呈现在用户屏幕上**（所见即所得）。
2. **多层级抽象工具集**：既提供了安全的无副作用探针（读取场景层级、检测材质丢失、视口截图），也提供了完整的底层 `bpy` 执行器（`execute_blender_code`）。
3. **内嵌离线文档支持**：集成了本地 RST 格式的 Blender Python API 参考与用户手册，支持 Agent 自主查阅 API 签名与枚举值。

---

## 二、 MCP 核心工具集分类参考

Blender MCP 注册的所有 Lazy-Loaded 工具可划分为四大核心领域：

### 1. 场景结构与资产探测工具（Inspection Tools）

在进行任何修改前，必须优先使用探针探测当前场景状态，严禁凭空假设对象名称或缺少配置：

- **`get_objects_summary`**：
  - **功能**：遍历输出当前场景的 Collection 层级树，以及每个集合内包含的物体（名称、类型、父级、材质槽、选中态、视口可见性）。
  - **适用场景**：进入场景后的首要探索、验证物体是否存在。
- **`get_object_detail_summary`**：
  - **参数**：`object_name`
  - **功能**：获取指定物体的详细数据（世界坐标矩阵、局部变换、顶点/面数、修改器列表 Modifiers、材质槽与约束）。
- **`get_blendfile_summary_*` 系列**：
  - `get_blendfile_summary_datablocks`：统计场景中所有 Mesh、Curve、Material、Texture 等数据块的引用计数（Users count）。
  - `get_blendfile_summary_missing_files`：快速检测工程中是否有丢失的外部纹理贴图或丢失的资产库引用。
  - `get_blendfile_summary_path_info`：获取当前 `.blend` 文件保存物理路径。

---

### 2. 视口截图与渲染预览工具（Viewport & Rendering）

- **`render_viewport_to_path`**：
  - **参数**：`output_path`（绝对路径）
  - **功能**：调用当前渲染引擎（EEVEE / Cycles）以当前视口参数快速离线光栅化一帧图像并写入指定文件。
  - **最佳实践**：用于在自动化建模过程中给 Agent 或用户即时确认几何形态与光影分布。
- **`render_thumbnail_to_path`**：
  - **参数**：`output_path`
  - **功能**：快速渲染小尺寸缩略图。
- **`get_screenshot_of_window_as_image` / `get_screenshot_of_area_as_image`**：
  - **功能**：捕获整个 Blender 窗口或指定工作区（如 3D Viewport、Shader Editor）的真实 UI 像素，用于排查界面操作与窗口状态。

---

### 3. UI 焦点与工作区控制工具（Navigation & Focus）

- **`jump_to_tab_by_name`**：切换工作区标签页（如 `'Layout'`, `'Modeling'`, `'Shading'`, `'Animation'`）。
- **`jump_to_view3d_object_by_name`**：在 3D 视口中将视图居中对齐到目标物体（类似快捷键 `Numpad .`）。

---

### 4. 核心代码执行器（Python Code Execution）

- **`execute_blender_code`**：
  - **参数**：`code`（Python 代码字符串）
  - **执行上下文**：直接在 Blender 进程的内置 Python 解释器中执行，完整暴露 `bpy`。
  - **数据回传约定**：**必须**在代码末尾将需要返回的 JSON 兼容数据赋值给局部变量 `result`（例如 `result = {"status": "ok", "count": 10}`）。如果不赋值给 `result`，工具返回结果将为空。

---

## 三、 `execute_blender_code` 编码核心规范

在编写自动化 `bpy` 脚本时，需严格遵守以下铁律：

### 1. 数据块与对象分离原则

Blender 采用 Datablock 机制：
- **`bpy.data.objects`** 负责空间位姿（Transform）、集合从属与修改器。
- **`bpy.data.meshes` / `bpy.data.materials`** 才是底层几何数据与着色数据。
- 删除对象时若未连带清理底层数据块，孤立数据块（Orphan Data）会继续滞留内存：
  ```python
  # 安全清理无引用数据块
  for block in bpy.data.meshes:
      if block.users == 0:
          bpy.data.meshes.remove(block)
  ```

### 2. 变换矩阵与依赖图更新（Dependency Graph）

许多只读属性（如 `matrix_world`、顶点世界坐标、动画求值状态）依赖后台依赖图的计算。在读取计算后属性前，必须显式触发刷新：
```python
bpy.context.view_layer.update()
```

### 3. 操作符（`bpy.ops`）与直接数据修改（`bpy.data`）的区别

- **优先使用 `bpy.ops`** 处理标准图元创建、修改器应用、视图变换（会自动建立上下文和默认命名）。
- **优先使用 `bpy.data`** 处理大批量顶点写入、材质节点连线、数据清理（避免操作符隐式改变当前激活项和选区状态）。

### 4. 视口交互模式与用户可见性保证

如果通过代码创建了运镜或材质，为了让用户能在屏幕上立即感知，应主动切换视口参数：
```python
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                # 切换到摄影机取景框视角
                space.region_3d.view_perspective = 'CAMERA'
                # 切换为材质着色模式 (MATERIAL / RENDERED)
                space.shading.type = 'MATERIAL'
```

---

## 四、 典型自动化工作流范例

### 范例 1：快速连通性与场景巡检

```python
import bpy

result = {
    "blender_version": bpy.app.version_string,
    "filepath": bpy.data.filepath or "(unsaved)",
    "active_workspace": bpy.context.workspace.name,
    "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
    "object_count": len(bpy.data.objects),
    "render_engine": bpy.context.scene.render.engine
}
```

### 范例 2：材质节点树创建与赋予（Principled BSDF）

```python
import bpy

def get_or_create_pbr_material(name, color_rgba, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color_rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat

cube = bpy.data.objects.get("Cube")
if cube:
    mat = get_or_create_pbr_material("Red_Glossy", (0.8, 0.1, 0.1, 1.0), roughness=0.2)
    cube.data.materials.clear()
    cube.data.materials.append(mat)

result = {"status": "material_assigned"}
```

### 范例 3：无缝 360° 环绕运镜动画（带父级 Rig 驱动）

```python
import bpy
import math

# 1. 建立瞄准空物体与旋转父级空物体
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1.5))
target = bpy.context.active_object
target.name = "Target_Centroid"

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "Orbit_Rig"

# 2. 创建并绑定摄像机
bpy.ops.object.camera_add(location=(0, -12.0, 5.0))
cam = bpy.context.active_object
cam.data.lens = 45.0
bpy.context.scene.camera = cam

# 瞄准约束：锁定摄像机自身 -Z 为拍摄光轴，+Y 为正上方
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'
cam.parent = rig

# 3. 为父级空物体打 360° 线性旋转关键帧
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 120
scene.render.fps = 24

rig.rotation_mode = 'XYZ'
rig.rotation_euler = (0, 0, 0)
rig.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
rig.rotation_euler = (0, 0, math.radians(360))
rig.keyframe_insert(data_path="rotation_euler", index=2, frame=121)

# 兼容 Blender 5.x 分层 Action 的线性曲线设置
act = rig.animation_data.action
fcurves = []
if hasattr(act, "fcurves"):
    fcurves.extend(act.fcurves)
elif hasattr(act, "layers"):
    for layer in act.layers:
        for strip in layer.strips:
            if hasattr(strip, "channelbags"):
                for bag in strip.channelbags:
                    fcurves.extend(bag.fcurves)
for fc in fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'

scene.frame_set(1)
result = {"status": "turntable_created", "frames": 120}
```

---

## 五、 排错与常见问题清单（FAQ）

1. **调用 MCP 工具报错 `Connection Refused` 或超时**：
   - 检查 Blender 是否处于打开状态，且 Preferences -> Add-ons 中已勾选并启用了 MCP 服务插件。
2. **`execute_blender_code` 返回为空**：
   - 检查 Python 脚本内部是否声明了 `result = {...}` 字典。未赋值给 `result` 变量时，结果不被序列化提取。
3. **调用 `bpy.ops` 报错 `Context Incorrect`**：
   - 某些操作符（如仅限 Edit 模式或 3D Viewport 激活的操作符）需要特定的 Context 覆写。应尽量改用底层 `bpy.data` 处理，或先调用模式切换操作符 `bpy.ops.object.mode_set(mode='OBJECT')`。
