## 文档生成说明

本文档复盘通过 MCP 自动化驱动 Blender 5.2.2 进行低多边形建筑场景搭建、运镜编排及渲染预览的全流程，提取程序化建模的关键排错经验，并厘清 Blender 中容易混淆的 XYZ 空间坐标、视角映射及摄影机局部轴向约定。

参考文档包括：
- [mcp-control-guide.md](mcp-control-guide.md)

---

## 一、 本次场景构建的实战经验与易错陷阱

在通过代码或 MCP 自动化调度 Blender 时，常见的典型踩坑点主要集中在版本 API 演进、几何图元对齐、共面穿模以及视口/渲染模式联动上：

### 1. Blender 5.x 动画数据结构演进（Slotted / Layered Actions）

- **踩坑现象**：
  在设置关键帧插值曲线（如将 Turntable 设为线性无缝平滑插值）时，直接调用老版本经典的 `obj.animation_data.action.fcurves`，会在 Blender 5.0+ 中直接抛出异常：
  ```text
  AttributeError: 'Action' object has no attribute 'fcurves'
  ```
- **核心原因**：
  Blender 从 4.4 / 5.0 开始重构了动画底层架构，引入了 **分层动画（Layered Actions）与插槽（Action Slots）**。F-Curve 不再平铺挂在 `Action` 根对象下，而是挂载于 `action.layers[...].strips[...].channelbags[...].fcurves`。
- **推荐解决方案**：
  编写跨版本兼容的曲线遍历工具函数：
  ```python
  def set_fcurves_interpolation(obj, interpolation='LINEAR'):
      if not obj.animation_data or not obj.animation_data.action:
          return
      act = obj.animation_data.action
      fcurves = []
      if hasattr(act, "fcurves"):
          # Legacy Actions (Blender < 5.0)
          fcurves.extend(act.fcurves)
      elif hasattr(act, "layers"):
          # Layered Actions (Blender 5.0+)
          for layer in act.layers:
              for strip in layer.strips:
                  if hasattr(strip, "channelbags"):
                      for bag in strip.channelbags:
                          fcurves.extend(bag.fcurves)
      for fc in fcurves:
          for kp in fc.keyframe_points:
              kp.interpolation = interpolation
  ```

---

### 2. 基础图元旋转替代真实几何的“非对称”陷阱

- **踩坑现象**：
  为快速构建人字形斜坡屋顶，若直接使用三棱柱 `primitive_cylinder_add(vertices=3)` 并旋转 90 度，侧面看往往会发现屋顶坡度前缓后陡、不对称，或脊线发生偏转。
- **核心原因**：
  Blender 的 `primitive_cylinder_add` 生成 3 边形时，其顶点默认分布在 XY 平面的外接圆上，坐标分别为 $(1, 0)$、$(-0.5, \frac{\sqrt{3}}{2})$、$(-0.5, -\frac{\sqrt{3}}{2})$。该等边三角形绕任意坐标轴旋转 90 度后，顶点朝向通常与正上方（$+Z$）存在夹角，无法直接充当严格对称的屋脊。
- **最佳实践**：
  对于对称建筑结构（如双坡屋顶、人字山墙、檐口出挑），优先使用显式顶点构建网格（`from_pydata`），彻底消除图元旋转带来的轴向扭曲与缩放耦合：
  ```python
  # 直接基于对称坐标定义屋顶：长度沿 X，坡度沿 Y，高度沿 Z
  verts = [
      (-2.2, -1.8, 2.35), # 前左檐口
      (-2.2,  1.8, 2.35), # 后左檐口
      (-2.2,  0.0, 3.65), # 左侧屋脊顶峰
      ( 2.2, -1.8, 2.35), # 前右檐口
      ( 2.2,  1.8, 2.35), # 后右檐口
      ( 2.2,  0.0, 3.65), # 右侧屋脊顶峰
  ]
  faces = [(0, 3, 5, 2), (1, 2, 5, 4), (0, 2, 1), (3, 4, 5), (0, 1, 4, 3)]
  ```

---

### 3. 共面重叠（Z-Fighting）与局部偏移容差

- **踩坑现象**：
  在墙面上贴门、窗户或石板路时，如果坐标直接设在墙体的理论外表面（例如墙厚 3.0，中心在 0，外壁在 $Y = -1.5$；若门厚 0.08，中心刚好放在 $-1.5$），在渲染时会发生剧烈的共面撕裂斑驳（Z-Fighting），甚至旋转时被墙体完全遮挡。
- **规范标准**：
  - 次级贴附部件（门、窗框、小径）的几何中心必须外移：$Y_{\text{center}} = Y_{\text{wall\_surface}} - \text{half\_thickness} - \text{offset}$。
  - 保留至少 $0.02 \sim 0.05$ 单位的微小外凸间隙，既保证阴影计算正确，又避免深度缓冲精度问题。

---

### 4. 视口模式（Viewport）与摄影机预览状态脱节

- **踩坑现象**：
  场景和动画已经完全在后台建好，但用户在 Blender 主界面中按空格播放时，发现“画面没有颜色”、“摄影机在外面飞，没有看到跟随运镜”。
- **核心原因**：
  - 3D 视口处于 **自由透视视角（User Perspective）**，而非 **摄影机视角（Camera View）**。
  - 着色模式默认停留在 **实体模式（Solid Shading）**，材质节点树（Principled BSDF）的漫反射颜色、粗糙度与金属度在纯白模下不生效。
- **自动化联动方案**：
  在生成场景或运镜脚本末尾，主动遍历当前工作区的 3D 视口空间并切换：
  ```python
  for area in bpy.context.screen.areas:
      if area.type == 'VIEW_3D':
          for space in area.spaces:
              if space.type == 'VIEW_3D':
                  # 切入当前活动摄影机
                  space.region_3d.view_perspective = 'CAMERA'
                  # 开启材质预览或渲染预览
                  space.shading.type = 'MATERIAL' # 或 'RENDERED'
  ```

---

### 5. 渲染输出容器兼容性（FFMPEG Enum 限制）

- **踩坑现象**：
  直接在 Python 中设置 `scene.render.image_settings.file_format = 'FFMPEG'` 时，在部分平台的特定 Blender 编译版本下会抛出 `enum 'FFMPEG' not found` 错误。
- **最佳实践**：
  遵循工业级渲染流水线规范：先让 Blender 快速输出高质量 PNG 序列帧（利用多核 EEVEE 离线光栅化），随后调用宿主机 `ffmpeg` 编码为具备高兼容性的 `yuv420p` H.264 MP4 视频，速度更快且容器容错率最高。

---

## 二、 Blender 中 XYZ 轴与空间方向的绝对关系

理解 Blender 的坐标系是避免模型做反、朝向颠倒、镜头反拍的核心基石。

### 1. 世界坐标系（World Space）：右手系、Z 轴向上

Blender 采用标准的 **右手直角坐标系（Right-Handed Coordinate System, Z-Up）**：

| 轴向 | 方向对应 | 常用空间语义 | 视口轴线颜色 |
| :--- | :--- | :--- | :--- |
| **$+X$** | **右侧（Right）** | 东方（East） | 红色（Red） |
| **$-X$** | **左侧（Left）** | 西方（West） | 红色虚线/负向 |
| **$+Y$** | **后方 / 深处（Back / Depth）** | 北方（North）、物体的背面 | 绿色（Green） |
| **$-Y$** | **前方 / 朝向观察者（Front）** | 南方（South）、**物体的正面** | 绿色虚线/负向 |
| **$+Z$** | **上方（Up）** | 天空（Sky）、重力反方向 | 蓝色（Blue） |
| **$-Z$** | **下方（Down）** | 地面（Ground）、地心重力方向 | 蓝色虚线/负向 |

> **关键记忆点**：
> - **$+Z$ 永远向上（头顶是蓝轴）**。
> - **$-Y$ 是正面（面向屏幕前方的视角）**。
> - **$+X$ 永远向右（右手是红轴）**。

---

### 2. 标准预设视角与小键盘映射（Numpad Navigation）

Blender 的所有默认视角都严格基于上述轴向定义：

| 快捷键 | 视角名称 | 观察方向 | 观察到的内容与轴向表现 |
| :--- | :--- | :--- | :--- |
| **Numpad 1** | **正视（Front）** | 从 $-Y$ 沿 $+Y$ 看过去 | **面对物体的正立面**。水平横轴为 $X$（左负右正），垂直纵轴为 $Z$（上正下负）。 |
| **Ctrl + Numpad 1** | **后视（Back）** | 从 $+Y$ 沿 $-Y$ 看过去 | 看到物体背面。水平横轴左为 $+X$，右为 $-X$。 |
| **Numpad 3** | **右侧视（Right）** | 从 $+X$ 沿 $-X$ 看过去 | **站在物体右侧**看过去。水平横轴左为 $+Y$（后），右为 $-Y$（前），纵轴为 $Z$。 |
| **Ctrl + Numpad 3** | **左侧视（Left）** | 从 $-X$ 沿 $+X$ 看过去 | 站在物体左侧看过去。 |
| **Numpad 7** | **顶视（Top）** | 从 $+Z$ 沿 $-Z$ 垂直俯瞰 | **平面俯视图**。上为 $+Y$（后），下为 $-Y$（前），左为 $-X$，右为 $+X$。 |
| **Ctrl + Numpad 7** | **底视（Bottom）** | 从 $-Z$ 沿 $+Z$ 仰视 | 仰视图。 |
| **Numpad 0** | **摄影机视角（Camera）** | 切换到当前活动摄像机的取景框 | |

---

### 3. 极其反直觉的局部坐标系：摄影机（Camera）与灯光（Light）

普通网格（如立方体、人物角色）的默认“正面”通常朝向自身局部坐标的 $-Y$。然而，**Blender 的摄影机和聚光灯有完全不同且反直觉的局部轴向约定**：

1. **摄影机的镜头注视方向是自身的局部 $-Z$ 轴**：
   - 摄影机的光轴前进方向不是 $Y$，而是 $-Z$（即沿着摄影机局部的 $-Z$ 射出视线）。
2. **摄影机的画面正上方是自身的局部 $+Y$ 轴**：
   - 画面向上对应局部的 $+Y$。
3. **摄影机的画面正右方是自身的局部 $+X$ 轴**：
   - 画面向右对应局部的 $+X$。

#### 为什么 `TRACK_TO` 约束必须配置为 `-Z` / `Y`？
当我们在代码中为摄影机添加注视目标（Track To Constraint）时：
```python
track = cam.constraints.new(type='TRACK_TO')
track.target = target_empty
track.track_axis = 'TRACK_NEGATIVE_Z'  # 核心：用摄像机的局部 -Z 轴精准对准目标
track.up_axis = 'UP_Y'                 # 核心：用摄像机的局部 +Y 轴保持向上
```
如果不配置或者误配置为 `TRACK_Y`，摄影机镜头会 90 度下折或反向背对物体，造成画面全黑或丢失目标。

---

## 三、 跨软件与引擎交互时的坐标系转换陷阱

在将 Blender 构建的场景导出为外部格式或载入游戏引擎时，必须警惕坐标系差异：

| 系统 / 格式 | 坐标手性 | 向上轴（Up Axis） | 前进/正面（Forward Axis） | 与 Blender 的转换关系 |
| :--- | :--- | :--- | :--- | :--- |
| **Blender** | **右手系** | **$+Z$** | **$-Y$** | 原生基准 |
| **glTF / GLB** | **右手系** | **$+Y$** | **$+Z$** | 旋转转换：$X \to X, Y \to Z, Z \to -Y$（Blender 导出器默认会自动勾选 `+Y Up`） |
| **Three.js** | **右手系** | **$+Y$** | **$+Z$** | 与 glTF 一致，载入 Blender 导出的 GLB 后默认立正 |
| **Unity** | **左手系** | **$+Y$** | **$+Z$** | 手性变化（需翻转一个轴），导入 FBX 时常出现 $-90^\circ$ 的 X 轴旋转补偿 |
| **Unreal Engine** | **左手系** | **$+Z$** | **$+X$** | 虽同为 $Z$-Up，但手性不同，正面在 $+X$，导入时需特别检查旋转骨骼 |

---

## 四、 总结与快速自查清单

在 Blender 中搭建任何场景时，心中需牢记三条法则：
1. **地平线在 $Z = 0$**：正数向上长，负数向下扎。
2. **大门向南开（$-Y$）**：主立面、门窗、角色面部默认摆在 $-Y$ 侧，这样按小键盘 `1` 就能一眼看到正脸。
3. **摄影机注视永远认准 $-Z$**：运镜绑定瞄准约束时，锁定 `-Z` 朝前，`Y` 朝上。
